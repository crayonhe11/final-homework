import json
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .bank import load_bank, ROOT
from .engine import diagnose, recommend, progress
from .storage import Store
from .ai import AIHelper


class App(tk.Tk):
    def __init__(self, db_path=None):
        super().__init__()
        self.title('知错 · Python 概念诊断与练习')
        self.geometry('1100x850')
        self.minsize(900, 740)
        self.configure(bg='#f3f5f9')
        self.questions, self.concepts = load_bank()
        self.store = Store(db_path or ROOT / 'runtime/learning.sqlite3')
        self.ai = AIHelper()
        self.pending = False
        self.events = queue.Queue()
        self.current = None
        self.submitted = False
        style = ttk.Style(self)
        style.configure('TFrame', background='#f3f5f9')
        style.configure('TLabel', background='#f3f5f9', font=('Arial',12))
        style.configure('Title.TLabel', font=('Arial',23,'bold'), foreground='#203253')
        style.configure('TButton', font=('Arial',12), padding=6)
        style.configure('Treeview', rowheight=31, font=('Arial',11))
        outer=ttk.Frame(self,padding=22); outer.pack(fill='both',expand=True)
        ttk.Label(outer,text='知错 · Python 学习实验室',style='Title.TLabel').pack(anchor='w')
        ttk.Label(outer,text='理解一次错误，练习一个概念。诊断是线索，不是对能力的定论。').pack(anchor='w',pady=(6,14))
        self.tabs=ttk.Notebook(outer); self.tabs.pack(fill='both',expand=True)
        self.practice=ttk.Frame(self.tabs,padding=15)
        self.review=ttk.Frame(self.tabs,padding=15)
        self.stats=ttk.Frame(self.tabs,padding=15)
        self.tabs.add(self.practice,text='  开始练习  ')
        self.tabs.add(self.review,text='  错题与记录  ')
        self.tabs.add(self.stats,text='  学习进度  ')
        self.build_practice(); self.build_review(); self.build_stats()
        self.tabs.bind('<<NotebookTabChanged>>',lambda e:self.refresh())
        self.status=tk.StringVar(value='本地保存 · 单人使用 · 30 道题 · '+('AI 已配置，需勾选启用' if self.ai.model else '规则模式'))
        ttk.Label(outer,textvariable=self.status).pack(anchor='w',pady=(10,0))
        self.next_question()
        self.refresh()
        self.after(100,self.poll)

    @staticmethod
    def text_box(parent,height=5):
        box=tk.Text(parent,height=height,wrap='word',font=('Arial',12),relief='flat',padx=12,pady=10,
                    background='white',foreground='#24344c')
        box.pack(fill='both',expand=True,pady=5)
        return box

    @staticmethod
    def write(box,value):
        box.configure(state='normal'); box.delete('1.0','end'); box.insert('1.0',value); box.configure(state='disabled')

    def build_practice(self):
        row=ttk.Frame(self.practice); row.pack(fill='x')
        self.topic=tk.StringVar(value='条件判断')
        self.topics=ttk.Combobox(row,textvariable=self.topic,values=['条件判断','循环','函数与返回值'],state='readonly',width=20)
        self.topics.pack(side='left')
        self.topics.bind('<<ComboboxSelected>>',lambda e:self.next_question())
        self.next_btn=ttk.Button(row,text='下一道未做题',command=self.next_question); self.next_btn.pack(side='right')
        self.question_title=tk.StringVar()
        ttk.Label(self.practice,textvariable=self.question_title).pack(anchor='w',pady=(10,2))
        self.code=self.text_box(self.practice,6); self.code.configure(font=('Menlo',13),background='#e8edf5')
        self.choice=tk.StringVar()
        self.options_frame=ttk.Frame(self.practice); self.options_frame.pack(fill='x',pady=4)
        self.option_buttons=[]
        for key in 'ABC':
            button=ttk.Radiobutton(self.options_frame,variable=self.choice,value=key)
            button.pack(anchor='w',pady=3); self.option_buttons.append(button)
        ttk.Label(self.practice,text='为什么这样选？（可选，最多 1000 字）').pack(anchor='w',pady=(4,0))
        self.reason=self.text_box(self.practice,2)
        actions=ttk.Frame(self.practice); actions.pack(fill='x',pady=4)
        self.ai_enabled=tk.BooleanVar(value=False)
        self.ai_check=ttk.Checkbutton(actions,text='使用本地 AI 辅助分析理由',variable=self.ai_enabled)
        self.ai_check.pack(side='left')
        if not self.ai.model: self.ai_check.state(['disabled'])
        self.hint_btn=ttk.Button(actions,text='先看提示',command=lambda:self.write(self.feedback,'提示：'+self.current['hint']))
        self.hint_btn.pack(side='right',padx=6)
        self.submit_btn=ttk.Button(actions,text='提交答案',command=self.submit); self.submit_btn.pack(side='right')
        self.feedback=self.text_box(self.practice,7)
        self.recs=ttk.Frame(self.practice); self.recs.pack(fill='x')

    def build_review(self):
        bar=ttk.Frame(self.review); bar.pack(fill='x')
        self.only_wrong=tk.BooleanVar(value=True)
        ttk.Checkbutton(bar,text='只看答错记录',variable=self.only_wrong,command=self.refresh).pack(side='left')
        ttk.Button(bar,text='导出全部记录 JSON',command=self.export).pack(side='right')
        self.records=ttk.Treeview(self.review,columns=('q','choice','result','time'),show='headings',height=9)
        for key,label,width in [('q','题目',280),('choice','选择',60),('result','结果',70),('time','时间（本地）',180)]:
            self.records.heading(key,text=label); self.records.column(key,width=width)
        self.records.pack(fill='both',expand=True,pady=10)
        self.records.bind('<<TreeviewSelect>>',self.show_record)
        self.record_detail=self.text_box(self.review,9)
        ttk.Button(self.review,text='重新练习所选题目',command=self.retry).pack(anchor='e')

    def build_stats(self):
        self.summary=tk.StringVar()
        ttk.Label(self.stats,textvariable=self.summary).pack(anchor='w',pady=8)
        self.progress_table=ttk.Treeview(self.stats,columns=('topic','concept','attempts','rate','state'),show='headings',height=16)
        for key,label,width in [('topic','主题',110),('concept','概念',230),('attempts','次数',60),('rate','正确率',70),('state','近期表现',210)]:
            self.progress_table.heading(key,text=label); self.progress_table.column(key,width=width)
        self.progress_table.pack(fill='both',expand=True)
        ttk.Label(self.stats,text='近期表现取最近 3 次作答；至少两道不同题答对才标为“初步稳定”。\n这些统计描述练习表现，不能证明概念已掌握或学习成绩已提高。',wraplength=850).pack(anchor='w',pady=12)

    def next_question(self):
        if self.pending: return
        history=self.store.history(); done={r['question_id'] for r in history}
        pool=[q for q in self.questions.values() if q['topic']==self.topic.get()]
        fresh=[q for q in pool if q['id'] not in done]
        # 普通下一题优先首题，保留同概念变式给诊断后的针对性练习。
        fresh.sort(key=lambda q:(q['difficulty'],q['id']))
        if fresh: self.load_question(fresh[0]['id'])
        else:
            last={r['question_id']:i for i,r in enumerate(history)}
            pool.sort(key=lambda q:(q['id']==(self.current or {}).get('id'),last.get(q['id'],-1)))
            self.load_question(pool[0]['id'])
            self.write(self.feedback,'本主题未做题已用完，现进入复习。重复题的正确率不等于首次作答效果。')

    def load_question(self,qid):
        if self.pending: return
        self.current=self.questions[qid]; q=self.current
        self.topic.set(q['topic']); self.choice.set(''); self.submitted=False
        self.question_title.set(f'{q["topic"]} · {qid} · 难度 {q["difficulty"]} / 2   |   {q["prompt"]}')
        self.write(self.code,q['code'])
        for key,button in zip('ABC',self.option_buttons):
            button.configure(text=f'{key}.  '+q['options'][key].replace('\n','  ↵  ')); button.state(['!disabled'])
        self.reason.configure(state='normal'); self.reason.delete('1.0','end')
        self.submit_btn.state(['!disabled']); self.hint_btn.state(['!disabled'])
        self.write(self.feedback,'选择答案后提交。选项中的 ↵ 表示换行。')
        for child in self.recs.winfo_children(): child.destroy()
        self.tabs.select(self.practice)

    def submit(self):
        if self.pending or self.submitted: return
        choice=self.choice.get(); reason=self.reason.get('1.0','end-1c').strip()
        if not choice:
            messagebox.showinfo('还没选择答案','请先选择 A、B 或 C。'); return
        if len(reason)>1000:
            messagebox.showinfo('理由过长','请将理由缩短到 1000 字以内。'); return
        q=self.current; result=diagnose(q,choice)
        self.pending=True; self.set_busy(True)
        self.status.set('正在分析并保存，本地 AI 最多等待约 12 秒…' if self.ai_enabled.get() else '正在保存…')
        use_ai=self.ai_enabled.get()
        def work():
            ai=self.ai.analyze(q,choice,reason,self.concepts) if use_ai else {'status':'disabled','message':'本次使用规则诊断。'}
            self.events.put((q,choice,reason,result,ai))
        threading.Thread(target=work,daemon=True).start()

    def set_busy(self,busy):
        for button in [self.submit_btn,self.next_btn,self.hint_btn,*self.option_buttons]:
            button.state(['disabled' if busy else '!disabled'])
        self.topics.configure(state='disabled' if busy else 'readonly')
        self.reason.configure(state='disabled' if busy else 'normal')

    def poll(self):
        try:
            q,choice,reason,result,ai=self.events.get_nowait()
        except queue.Empty: pass
        else:
            try:
                self.store.save(q['id'],choice,reason,result,ai)
            except Exception as exc:
                self.pending=False; self.set_busy(False)
                self.status.set('保存失败，答案未提交。可以重试。')
                messagebox.showerror('保存失败',str(exc))
            else:
                self.pending=False; self.set_busy(False); self.submitted=True
                self.submit_btn.state(['disabled']); self.hint_btn.state(['disabled'])
                for button in self.option_buttons: button.state(['disabled'])
                self.reason.configure(state='disabled')
                lines=['✓ 本次答对' if result['correct'] else '本次答错 · 可以用下一题验证理解']
                if result['concept']:
                    lines += ['规则诊断：可能涉及「'+self.concepts[result['concept']]['label']+'」。',result['evidence']]
                else: lines.append(result['evidence'])
                if ai['status']=='ok':
                    label='证据不足，暂不支持概念误区判断' if ai['concept']=='unknown' else '可能涉及「'+self.concepts[ai['concept']]['label']+'」'
                    lines += ['AI 辅助：'+label+'；依据你写的「'+ai['quote']+'」。']
                lines += ['正确答案：'+q['answer']+'；'+q['explanation'],ai['message'],'一次错误不能确定误区，请尝试不同题目。']
                self.write(self.feedback,'\n'.join(lines))
                for item in recommend(q,self.questions,self.store.history(),result['concept'],limit=2):
                    target=item['question']
                    ttk.Button(self.recs,text=item['reason']+' → '+target['id'],command=lambda qid=target['id']:self.load_question(qid)).pack(anchor='w',pady=2)
                self.status.set('作答已保存 · '+('AI 辅助结果已记录' if ai['status']=='ok' else ai['message']))
                self.refresh()
        self.after(100,self.poll)

    def refresh(self):
        if not hasattr(self,'records'): return
        from datetime import datetime
        history=self.store.history()
        self.history_by_id={str(r['id']):r for r in history}
        self.records.delete(*self.records.get_children())
        for r in reversed(history):
            if self.only_wrong.get() and r['correct']: continue
            self.records.insert('', 'end',iid=str(r['id']),values=(r['question_id'],r['choice'],'正确' if r['correct'] else '错误',datetime.fromisoformat(r['created_at']).astimezone().strftime('%m-%d %H:%M:%S')))
        self.progress_table.delete(*self.progress_table.get_children())
        for row in progress(self.questions,history,self.concepts):
            rate=f'{row["correct"]/row["attempts"]:.0%}' if row['attempts'] else '—'
            self.progress_table.insert('','end',values=(row['topic'],row['label'],row['attempts'],rate,row['state']))
        correct=sum(r['correct'] for r in history)
        self.summary.set(f'累计作答 {len(history)} 次 · 答对 {correct} 次 · 已练习 {len({r["question_id"] for r in history})} / 30 道题')

    def show_record(self,event=None):
        selected=self.records.selection()
        if not selected: return
        r=self.history_by_id[selected[0]]; q=self.questions[r['question_id']]
        ai=json.loads(r['ai_json'])
        self.write(self.record_detail,f'{q["code"]}\n\n你的选择：{r["choice"]}  正确答案：{q["answer"]}\n你的理由：{r["reason"] or "未填写"}\n解析：{q["explanation"]}\n提示：{q["hint"]}\nAI 记录：{json.dumps(ai,ensure_ascii=False)}')

    def retry(self):
        if self.pending: return
        selected=self.records.selection()
        if selected: self.load_question(self.history_by_id[selected[0]]['question_id'])

    def export(self):
        path=filedialog.asksaveasfilename(title='导出作答记录（包含你的文字理由）',defaultextension='.json',initialfile='learning-records.json',filetypes=[('JSON','*.json')])
        if path:
            try:
                from pathlib import Path
                Path(path).write_text(json.dumps(self.store.history(),ensure_ascii=False,indent=2),encoding='utf-8')
                messagebox.showinfo('导出完成','已保存全部作答记录。')
            except OSError as exc: messagebox.showerror('导出失败',str(exc))
