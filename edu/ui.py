import json
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .bank import load_bank, ROOT
from .engine import diagnose, recommend, progress, next_practice, learning_summary
from .scheduler import review_schedule, due_reviews
from .storage import Store
from .ai import AIHelper
from .curriculum import load_lessons, course_states, lesson_question
from .course_ui import CourseView
from .theme import apply_theme, BG, INK, MUTED, ACCENT


class App(tk.Tk):
    def __init__(self, db_path=None):
        super().__init__()
        self.title('知错 · Python 学习平台')
        self.geometry('1280x900')
        self.minsize(900, 740)
        self.configure(bg='#f3f5f9')
        self.questions, self.concepts = load_bank()
        self.lessons = load_lessons(self.concepts)
        self.course_concept = None
        self.store = Store(db_path or ROOT / 'runtime/learning.sqlite3')
        self.ai = AIHelper()
        self.pending = False
        self.events = queue.Queue()
        self.current = None
        self.submitted = False
        apply_theme(self)
        self.configure(bg=BG)
        self.sidebar=tk.Frame(self,bg='white',width=172)
        self.sidebar.pack(side='left',fill='y');self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar,text='知错  /  EDU',bg='white',fg=ACCENT,font=('Arial',20,'bold')).pack(anchor='w',padx=20,pady=(28,4))
        tk.Label(self.sidebar,text='PYTHON LEARNING',bg='white',fg=MUTED,font=('Arial',9)).pack(anchor='w',padx=21,pady=(0,35))
        tk.Label(self.sidebar,text='学习空间',bg='white',fg=MUTED,font=('Arial',10)).pack(anchor='w',padx=22,pady=(0,10))
        self.nav_buttons=[]
        for index,label in enumerate(('01   课程与地图','02   练习工作区','03   错题记录','04   学习进度')):
            button=tk.Button(self.sidebar,text=label,anchor='w',font=('Arial',12),bg='white',fg=INK,
                             activebackground='#eeeafd',activeforeground=ACCENT,relief='flat',bd=0,
                             padx=14,pady=13,cursor='hand2',command=lambda i=index:self.navigate(i))
            button.pack(fill='x',padx=10,pady=3);self.nav_buttons.append(button)
        tk.Label(self.sidebar,text='本地学习 · 自动保存\n一步一概念，逐章向前',justify='left',bg='white',fg=MUTED,font=('Arial',10),pady=24).pack(side='bottom',anchor='w',padx=20)
        outer=ttk.Frame(self,padding=(24,20,24,12));outer.pack(side='left',fill='both',expand=True)
        header=ttk.Frame(outer);header.pack(fill='x',pady=(0,14))
        self.page_title=tk.StringVar(value='我的学习路径')
        ttk.Label(header,textvariable=self.page_title,style='Title.TLabel').pack(side='left')
        ttk.Label(header,text='Python 入门  /  个人学习空间',style='Muted.TLabel').pack(side='right')
        self.tabs=ttk.Notebook(outer,style='Shell.TNotebook');self.tabs.pack(fill='both',expand=True)
        self.course=CourseView(self.tabs,self)
        self.tabs.add(self.course,text='  知识地图 · 学习闯关  ')
        self.practice=ttk.Frame(self.tabs,padding=15)
        self.review=ttk.Frame(self.tabs,padding=15)
        self.stats=ttk.Frame(self.tabs,padding=15)
        self.tabs.add(self.practice,text='  练习区  ')
        self.tabs.add(self.review,text='  错题与记录  ')
        self.tabs.add(self.stats,text='  学习进度  ')
        self.build_practice(); self.build_review(); self.build_stats()
        self.tabs.bind('<<NotebookTabChanged>>',lambda e:self.on_page_changed())
        self.status=tk.StringVar(value='本地保存 · 单人使用 · 30 道题 · '+('AI 已配置，需勾选启用' if self.ai.model else '规则模式'))
        ttk.Label(outer,textvariable=self.status,style='Muted.TLabel').pack(anchor='w',pady=(10,0))
        self.question_title.set('请先从知识地图学习，或选择主题后点击“自由练习下一题”。')
        self.submit_btn.state(['disabled']); self.hint_btn.state(['disabled'])
        self.write(self.code, '先学习，再练习。')
        self.write(self.feedback, '课程闯关从知识地图进入；自由练习不计入课程过关。')
        self.tabs.select(self.course)
        self.refresh()
        self.after(100,self.poll)

    @staticmethod
    def text_box(parent,height=5):
        frame=ttk.Frame(parent); frame.pack(fill='both',expand=True,pady=5)
        box=tk.Text(frame,height=height,wrap='word',font=('Arial',12),relief='flat',padx=16,pady=14,spacing1=3,spacing3=6,
                    background='white',foreground='#24344c')
        scrollbar=ttk.Scrollbar(frame,orient='vertical',command=box.yview)
        scrollbar.pack(side='right',fill='y')
        box.configure(yscrollcommand=scrollbar.set)
        box.pack(side='left',fill='both',expand=True)
        return box

    @staticmethod
    def write(box,value):
        box.configure(state='normal'); box.delete('1.0','end'); box.insert('1.0',value); box.configure(state='disabled')

    def navigate(self,index):
        self.tabs.select(index)
        if index==0: self.course.show_map()

    def on_page_changed(self):
        if not self.tabs.select(): return
        index=self.tabs.index(self.tabs.select())
        self.page_title.set(('我的学习路径','练习工作区','错题与学习记录','学习进度')[index])
        for i,button in enumerate(self.nav_buttons):
            button.configure(bg='#eeeafd' if i==index else 'white',fg=ACCENT if i==index else INK)
        self.refresh()

    def build_practice(self):
        row=ttk.Frame(self.practice);row.pack(fill='x',pady=(0,12))
        self.topic=tk.StringVar(value='条件判断')
        self.topics=ttk.Combobox(row,textvariable=self.topic,values=['条件判断','循环','函数与返回值'],state='readonly',width=14)
        self.topics.pack(side='left');self.topics.bind('<<ComboboxSelected>>',lambda e:self.next_question())
        ttk.Button(row,text='知识地图',command=self.return_to_map).pack(side='right',padx=(5,0))
        ttk.Button(row,text='本题讲解',command=self.open_current_lesson).pack(side='right',padx=5)
        self.next_btn=ttk.Button(row,text='下一题 →',command=self.next_question);self.next_btn.pack(side='right')
        self.question_title=tk.StringVar()
        ttk.Label(self.practice,textvariable=self.question_title,wraplength=730,style='Muted.TLabel').pack(anchor='w',pady=(0,12))
        workspace=ttk.Frame(self.practice);workspace.pack(fill='both',expand=True)
        workspace.columnconfigure(0,weight=3,uniform='pane');workspace.columnconfigure(1,weight=2,uniform='pane');workspace.rowconfigure(0,weight=1)
        left=ttk.Frame(workspace,style='Card.TFrame',padding=16);left.grid(row=0,column=0,sticky='nsew',padx=(0,10))
        right=ttk.Frame(workspace,style='Card.TFrame',padding=16);right.grid(row=0,column=1,sticky='nsew')
        ttk.Label(left,text='01  阅读代码',style='CardTitle.TLabel').pack(anchor='w',pady=(0,8))
        self.code=self.text_box(left,7);self.code.configure(font=('Menlo',13),background='#20263d',foreground='#e6e9ff',insertbackground='white')
        ttk.Label(left,text='02  选择完整输出',style='CardTitle.TLabel').pack(anchor='w',pady=(14,8))
        self.choice=tk.StringVar()
        self.options_frame=ttk.Frame(left,style='Card.TFrame');self.options_frame.pack(fill='x')
        self.option_buttons=[]
        for key in 'ABC':
            button=ttk.Radiobutton(self.options_frame,variable=self.choice,value=key)
            button.pack(fill='x',pady=4);self.option_buttons.append(button)
        ttk.Label(left,text='03  说说你的思路（可选）',style='CardTitle.TLabel').pack(anchor='w',pady=(14,4))
        self.reason=self.text_box(left,3)
        self.reason.configure(background='#f7f8fc')
        actions=ttk.Frame(left,style='Card.TFrame');actions.pack(fill='x',pady=(10,0))
        self.hint_btn=ttk.Button(actions,text='提示 1 / 2',command=self.show_hint);self.hint_btn.pack(side='left')
        self.submit_btn=ttk.Button(actions,text='提交答案 →',style='Primary.TButton',command=self.submit);self.submit_btn.pack(side='right')
        ttk.Label(right,text='反馈与下一步',style='CardTitle.TLabel').pack(anchor='w',pady=(0,8))
        ttk.Label(right,text='提交后查看解析与概念线索',style='CardMuted.TLabel').pack(anchor='w')
        self.feedback=self.text_box(right,14)
        self.recs=ttk.Frame(right,style='Card.TFrame');self.recs.pack(fill='x',pady=8)
        self.ai_enabled=tk.BooleanVar(value=False)
        self.ai_check=ttk.Checkbutton(self.practice,text='使用本地 AI 辅助分析理由',variable=self.ai_enabled)
        self.ai_check.pack(anchor='w',pady=(12,0))
        if not self.ai.model: self.ai_check.state(['disabled'])

    def build_review(self):
        bar=ttk.Frame(self.review); bar.pack(fill='x')
        self.only_wrong=tk.BooleanVar(value=True)
        ttk.Checkbutton(bar,text='只看答错记录',variable=self.only_wrong,command=self.refresh).pack(side='left')
        ttk.Button(bar,text='导出学习记录',command=self.export).pack(side='right')
        self.records=ttk.Treeview(self.review,columns=('q','choice','result','time'),show='headings',height=9)
        for key,label,width in [('q','题目',280),('choice','选择',60),('result','结果',70),('time','时间（本地）',180)]:
            self.records.heading(key,text=label); self.records.column(key,width=width)
        self.records.pack(fill='both',expand=True,pady=10)
        self.records.bind('<<TreeviewSelect>>',self.show_record)
        self.record_detail=self.text_box(self.review,9)
        ttk.Button(self.review,text='重新练习所选题目 →',style='Primary.TButton',command=self.retry).pack(anchor='e')

    def build_stats(self):
        self.summary=tk.StringVar()
        ttk.Label(self.stats,textvariable=self.summary).pack(anchor='w',pady=8)
        self.progress_table=ttk.Treeview(self.stats,columns=('topic','concept','attempts','rate','state','due'),show='headings',height=16)
        for key,label,width in [('topic','主题',95),('concept','概念',180),('attempts','次数',45),('rate','正确率',60),('state','近期表现',165),('due','下次复习',125)]:
            self.progress_table.heading(key,text=label); self.progress_table.column(key,width=width)
        self.progress_table.bind('<Double-1>',self.open_progress_lesson)
        self.progress_table.pack(fill='both',expand=True)
        ttk.Button(self.stats,text='开始到期复习 →',style='Primary.TButton',command=self.start_due_review).pack(anchor='e',pady=6)
        ttk.Label(self.stats,text='近期三次均独立答对且覆盖两道不同题才标为“初步稳定”；使用提示或旧记录未知时需重新验证。\n这些统计描述练习表现，不能证明概念已掌握或学习成绩已提高。',wraplength=850).pack(anchor='w',pady=12)

    def open_progress_lesson(self,event):
        cid=self.progress_table.identify_row(event.y)
        if cid in self.concepts:
            self.course.refresh();self.course.select_lesson(cid);self.tabs.select(self.course)

    def return_to_map(self):
        self.course.show_map()
        self.tabs.select(self.course)

    def practice_concept(self,cid):
        if self.pending or cid not in self.concepts: return
        history=self.store.history()
        attempted={r['question_id'] for r in history}
        last={r['question_id']:i for i,r in enumerate(history)}
        pool=[q for q in self.questions.values() if q['concept']==cid]
        if not pool: return
        pool.sort(key=lambda q:(q['id'] in attempted,last.get(q['id'],-1),q['difficulty'],q['id']))
        self.load_question(pool[0]['id'])
        self.write(self.feedback,'对应知识点自由练习：'+self.concepts[cid]['label']+'。本次不计入课程闯关。')

    def open_current_lesson(self):
        if self.current:
            self.course.refresh()
            self.course.select_lesson(self.current['concept'])
            self.tabs.select(self.course)

    def start_lesson(self,cid):
        if self.pending: return
        states=course_states(self.questions,self.concepts,self.store.history(),self.store.lesson_reads())
        state=states[cid]
        if state['locked'] or cid not in self.store.lesson_reads(): return
        if state['passed']:
            q=next(q for q in self.questions.values() if q['concept']==cid)
            self.load_question(q['id'])
        else:
            q=lesson_question(cid,self.questions,state)
            if q: self.load_question(q['id'],course_concept=cid)

    def continue_course(self):
        if self.pending or not self.course_concept: return
        states=course_states(self.questions,self.concepts,self.store.history(),self.store.lesson_reads())
        if not states[self.course_concept]['passed']:
            self.start_lesson(self.course_concept)
            return
        self.return_to_map()
        available=[c for c,state in states.items() if not state['locked'] and not state['passed']]
        if available:
            self.course.select_lesson(min(available,key=lambda c:self.concepts[c].get('order',0)))
        else:
            self.course.select_lesson(self.course_concept)

    def next_question(self):
        if self.pending: return
        item = next_practice(self.topic.get(), self.questions, self.store.history(), self.concepts,
                             exclude=(self.current or {}).get('id'))
        if item:
            self.load_question(item['question']['id'])
            self.write(self.feedback, item['reason'] + '\n选择答案后提交；选项中的 ↵ 表示换行。')

    def start_due_review(self):
        if self.pending: return
        due = due_reviews(self.questions, self.store.history())
        if due: self.load_question(due[0])
        else: messagebox.showinfo('复习计划', '暂时没有到期题目，可以继续学习新题。')

    def show_hint(self):
        if self.pending or self.submitted or self.current is None: return
        hints = self.current.get('hints', [self.current['hint']])
        self.hints_used = min(self.hints_used + 1, len(hints))
        self.write(self.feedback, '\n'.join(f'提示 {i+1}：{h}' for i, h in enumerate(hints[:self.hints_used]))
                   + '\n本次将记录为使用提示，请再用不同题目独立验证。')
        self.hint_btn.configure(text=f'提示 {min(self.hints_used+1,len(hints))} / {len(hints)}')
        if self.hints_used == len(hints): self.hint_btn.state(['disabled'])

    def load_question(self,qid,course_concept=None):
        if self.pending: return
        if course_concept is not None:
            states=course_states(self.questions,self.concepts,self.store.history(),self.store.lesson_reads())
            if (course_concept not in states or states[course_concept]['locked']
                    or course_concept not in self.store.lesson_reads()
                    or self.questions[qid]['concept'] != course_concept):
                return
        self.course_concept=course_concept
        self.current=self.questions[qid]; q=self.current
        self.topic.set(q['topic']); self.choice.set(''); self.submitted=False
        self.hints_used = 0
        self.hint_btn.configure(text=f'提示 1 / {len(q.get("hints", [q["hint"]]))}')
        self.question_title.set(f'{"课程闯关" if self.course_concept else "自由练习"}  /  {self.concepts[q["concept"]]["label"]}  /  难度 {q["difficulty"]}\n{q["prompt"]}')
        self.write(self.code,q['code'])
        for key,button in zip('ABC',self.option_buttons):
            button.configure(text=f'{key}.  '+q['options'][key].replace('\n','  ↵  ')); button.state(['!disabled'])
        self.reason.configure(state='normal'); self.reason.delete('1.0','end')
        self.submit_btn.state(['!disabled']); self.hint_btn.state(['!disabled'])
        self.write(self.feedback,'选择答案后提交。选项中的 ↵ 表示换行。')
        for child in self.recs.winfo_children(): child.destroy()
        self.tabs.select(self.practice)

    def submit(self):
        if self.pending or self.submitted or self.current is None: return
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
                self.store.save(q['id'],choice,reason,result,ai,hints_used=self.hints_used,course_concept=self.course_concept)
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
                if self.hints_used:
                    lines.append(f'本次使用 {self.hints_used} 级提示，需独立作答验证。')
                if result['concept']:
                    lines += ['规则诊断：可能涉及「'+self.concepts[result['concept']]['label']+'」。',result['evidence']]
                else: lines.append(result['evidence'])
                if ai['status']=='ok':
                    label='证据不足，暂不支持概念误区判断' if ai['concept']=='unknown' else '可能涉及「'+self.concepts[ai['concept']]['label']+'」'
                    lines += ['AI 辅助：'+label+'；依据你写的「'+ai['quote']+'」。']
                lines += ['正确答案：'+q['answer']+'；'+q['explanation'],ai['message'],'一次错误不能确定误区，请尝试不同题目。']
                self.write(self.feedback,'\n'.join(lines))
                if self.course_concept:
                    states=course_states(self.questions,self.concepts,self.store.history(),self.store.lesson_reads())
                    state=states[self.course_concept]
                    course_line=('本关已通过！回到地图查看新解锁内容。' if state['passed'] else
                                 f'本关独立正确 {state["solved"]}/{state["total"]}；继续完成本关检查。')
                    self.write(self.feedback,'\n'.join(lines+[course_line]))
                    ttk.Button(self.recs,text='查看通关与下一课' if state['passed'] else '继续本关练习',
                               command=self.continue_course).pack(anchor='w',pady=2)
                else:
                    for item in recommend(q,self.questions,self.store.history(),result['concept'],limit=2):
                        target=item['question']
                        ttk.Button(self.recs,text=item['reason']+' →',command=lambda qid=target['id']:self.load_question(qid)).pack(anchor='w',pady=2)
                self.status.set('作答已保存 · '+('AI 辅助结果已记录' if ai['status']=='ok' else ai['message']))
                self.refresh()
        self.after(100,self.poll)

    def refresh(self):
        if not hasattr(self,'records'): return
        from datetime import datetime
        self.course.refresh()
        history=self.store.history()
        self.history_by_id={str(r['id']):r for r in history}
        self.records.delete(*self.records.get_children())
        for r in reversed(history):
            if self.only_wrong.get() and r['correct']: continue
            self.records.insert('', 'end',iid=str(r['id']),values=(r['question_id'],r['choice'],'正确' if r['correct'] else '错误',datetime.fromisoformat(r['created_at']).astimezone().strftime('%m-%d %H:%M:%S')))
        self.progress_table.delete(*self.progress_table.get_children())
        from datetime import timezone
        schedule = review_schedule(history)
        now = datetime.now(timezone.utc)
        for row in progress(self.questions,history,self.concepts):
            rate=f'{row["correct"]/row["attempts"]:.0%}' if row['attempts'] else '—'
            due_dates = [v['due'] for qid,v in schedule.items() if qid in self.questions and self.questions[qid]['concept']==row['concept']]
            due = min(due_dates) if due_dates else None
            due_label = '待开始' if due is None else '已到期' if due <= now else due.astimezone().strftime('%m-%d %H:%M')
            self.progress_table.insert('','end',iid=row['concept'],values=(row['topic'],row['label'],row['attempts'],rate,row['state'],due_label))
        metrics = learning_summary(self.questions, history)
        first_rate = f'{metrics["first_correct"] / metrics["unique"]:.0%}' if metrics['unique'] else '—'
        self.summary.set(f'作答 {metrics["attempts"]} 次 · 已练 {metrics["unique"]}/{len(self.questions)} 题 · '
                         f'首次正确率 {first_rate} · 使用提示 {metrics["hinted"]} 次 · 到期 {metrics["due"]} 题')

    def show_record(self,event=None):
        selected=self.records.selection()
        if not selected: return
        r=self.history_by_id[selected[0]]; q=self.questions.get(r['question_id'])
        if q is None:
            self.write(self.record_detail, '题目已不在当前题库，原记录仍保留：\n'+json.dumps(r,ensure_ascii=False,indent=2))
            return
        try: ai=json.loads(r['ai_json'] or '{}')
        except (ValueError, TypeError): ai={'message':'旧 AI 记录无法解析'}
        self.write(self.record_detail,f'{q["code"]}\n\n你的选择：{r["choice"]}  正确答案：{q["answer"]}\n练习模式：{"课程闯关" if r.get("course_concept") else "自由练习 / 旧记录"}\n使用提示：{r.get("hints_used") if r.get("hints_used") is not None else "旧记录未知"}\n你的理由：{r["reason"] or "未填写"}\n解析：{q["explanation"]}\n提示：{q["hint"]}\nAI 记录：{json.dumps(ai,ensure_ascii=False)}')

    def retry(self):
        if self.pending: return
        selected=self.records.selection()
        if selected:
            qid=self.history_by_id[selected[0]]['question_id']
            if qid in self.questions: self.load_question(qid)
            else: messagebox.showinfo('题目已归档','该题已不在当前题库，记录仍可查看与导出。')

    def export(self):
        path=filedialog.asksaveasfilename(title='导出作答记录（包含你的文字理由）',defaultextension='.json',initialfile='learning-records.json',filetypes=[('JSON','*.json')])
        if path:
            try:
                from pathlib import Path
                Path(path).write_text(json.dumps(self.store.history(),ensure_ascii=False,indent=2),encoding='utf-8')
                messagebox.showinfo('导出完成','已保存全部作答记录。')
            except OSError as exc: messagebox.showerror('导出失败',str(exc))
