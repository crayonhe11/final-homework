"""按章节组织的原创代码任务：编辑、草稿、示例运行、提交判题。"""
import io
import keyword
import queue
import threading
import tokenize
import tkinter as tk
from tkinter import ttk, messagebox
from .coding import load_tasks
from .runner import run_code
from .theme import ACCENT


class CodingLab(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent,padding=10)
        self.app=app;self.tasks=load_tasks();self.current_id=None
        self.running=False;self.events=queue.Queue();self.save_job=None;self.loading=False
        bar=ttk.Frame(self);bar.pack(fill='x',pady=(0,10))
        ttk.Label(bar,text='趣味代码实验室',font=('Arial',17,'bold')).pack(side='left')
        self.topic=tk.StringVar(value='条件判断')
        self.filter=ttk.Combobox(bar,textvariable=self.topic,values=['条件判断','循环','函数与返回值','全部章节'],state='readonly',width=15)
        self.filter.pack(side='right');self.filter.bind('<<ComboboxSelected>>',lambda e:self.filter_tasks())
        ttk.Label(self,text='无需先完成选择题。写代码 → 运行示例 → 提交所有测试。仅支持基础Python语法，无文件/网络/模块导入。',wraplength=880,style='Muted.TLabel').pack(anchor='w',pady=(0,10))
        panes=ttk.Frame(self);panes.pack(fill='both',expand=True)
        panes.columnconfigure(0,weight=2,uniform='lab');panes.columnconfigure(1,weight=3,uniform='lab');panes.rowconfigure(0,weight=1)
        left=ttk.Frame(panes,padding=10,style='Card.TFrame');left.grid(row=0,column=0,sticky='nsew',padx=(0,10))
        right=ttk.Frame(panes,padding=10,style='Card.TFrame');right.grid(row=0,column=1,sticky='nsew')
        self.tree=ttk.Treeview(left,show='tree',height=6,selectmode='browse');self.tree.pack(fill='x')
        self.tree.bind('<<TreeviewSelect>>',self.choose_task)
        self.description=app.text_box(left,12)
        self.hint_button=ttk.Button(left,text='查看思考提示',command=self.show_hint);self.hint_button.pack(anchor='w',pady=5)
        self.task_title=tk.StringVar(value='选择一个任务')
        ttk.Label(right,textvariable=self.task_title,style='CardTitle.TLabel').pack(anchor='w',pady=(0,6))
        self.editor=app.text_box(right,12)
        self.editor.configure(font=('Menlo',12),background='#20263d',foreground='#edf0ff',insertbackground='white',undo=True,wrap='none')
        # 横向滚动允许查看长代码；纵向滚动由text_box提供。
        xscroll=ttk.Scrollbar(right,orient='horizontal',command=self.editor.xview);xscroll.pack(fill='x')
        self.editor.configure(xscrollcommand=xscroll.set)
        self.editor.tag_configure('keyword',foreground='#c6a5ff');self.editor.tag_configure('string',foreground='#a6ddab');self.editor.tag_configure('comment',foreground='#8291aa')
        self.editor.tag_configure('errorline',background='#743d49')
        self.editor.bind('<Tab>',self.indent);self.editor.bind('<Return>',self.newline)
        self.editor.bind('<<Modified>>',self.on_modified)
        buttons=ttk.Frame(right,style='Card.TFrame');buttons.pack(fill='x',pady=8)
        self.reset_button=ttk.Button(buttons,text='恢复骨架',command=self.reset);self.reset_button.pack(side='left')
        self.run_button=ttk.Button(buttons,text='运行示例',command=lambda:self.run('example'));self.run_button.pack(side='left',padx=6)
        self.submit_button=ttk.Button(buttons,text='提交判题 →',style='Primary.TButton',command=lambda:self.run('submit'));self.submit_button.pack(side='right')
        self.result=app.text_box(right,7)
        self.status=tk.StringVar(value='草稿自动保存 · Tab缩进 · Enter自动缩进')
        ttk.Label(self,textvariable=self.status,style='Muted.TLabel').pack(anchor='w',pady=8)
        self.filter_tasks();self.after(100,self.poll)

    def open_topic(self,topic):
        if self.running: return
        if not self.save_draft(): return
        self.topic.set(topic);self.filter_tasks()

    def filter_tasks(self):
        if self.running: return
        if not self.save_draft(): return
        self.tree.delete(*self.tree.get_children())
        passed={r['task_id'] for r in self.app.store.code_history() if r['mode']=='submit' and r['passed']}
        first=None
        for chapter in ('条件判断','循环','函数与返回值'):
            if self.topic.get() not in (chapter,'全部章节'): continue
            parent=self.tree.insert('','end',iid='chapter_'+chapter,text=chapter,open=True)
            for tid,task in self.tasks.items():
                if task['topic']!=chapter: continue
                self.tree.insert(parent,'end',iid=tid,text=('✓ ' if tid in passed else '○ ')+task['title'])
                first=first or tid
        if first:
            self.tree.selection_set(first);self.load_task(first)

    def choose_task(self,event=None):
        if self.running: return
        selected=self.tree.selection()
        if selected and selected[0] in self.tasks and selected[0]!=self.current_id:
            self.load_task(selected[0])

    def load_task(self,tid):
        if self.running: return
        if not self.save_draft(): return
        self.current_id=tid;task=self.tasks[tid]
        self.task_title.set(task['title'])
        sample='\n'.join(f'{task["function"]}({", ".join(repr(a) for a in c["args"])}) → {c["expected"]!r}' for c in task['tests'][:2])
        self.app.write(self.description,task['story']+'\n\n你的任务\n'+task['objective']+'\n\n函数接口\n'+task['function']+'('+', '.join(task['params'])+')\n\n示例\n'+sample+'\n\n说明\n可以采用不同写法；按返回值判定，不按源码匹配。通过测试不等于穷尽所有可能输入。')
        draft=self.app.store.get_draft(tid)
        self.loading=True;self.editor.configure(state='normal');self.editor.delete('1.0','end');self.editor.insert('1.0',task['starter'] if draft is None else draft);self.editor.edit_reset();self.editor.edit_modified(False);self.loading=False
        self.highlight()
        self.app.write(self.result,'修改函数体后运行示例。提交会检查全部测试，并记录结果。')
        self.status.set('已载入草稿' if draft is not None else '已准备函数骨架；只需从函数体开始写')

    def indent(self,event):
        if self.running: return 'break'
        self.editor.insert('insert','    ');return 'break'

    def newline(self,event):
        if self.running: return 'break'
        line=self.editor.get('insert linestart','insert')
        spaces=len(line)-len(line.lstrip(' '))
        if line.rstrip().endswith(':'): spaces+=4
        self.editor.insert('insert','\n'+' '*spaces);return 'break'

    def on_modified(self,event=None):
        if not self.editor.edit_modified(): return
        self.editor.edit_modified(False)
        if self.loading: return
        if self.save_job: self.after_cancel(self.save_job)
        self.save_job=self.after(500,self.autosave)

    def autosave(self):
        self.save_job=None;self.highlight();self.save_draft()

    def save_draft(self):
        if self.current_id is None or self.loading: return True
        try:
            self.app.store.save_draft(self.current_id,self.editor.get('1.0','end-1c'))
        except Exception as exc:
            self.status.set('草稿保存失败：'+str(exc));return False
        self.status.set('草稿已保存 · Tab缩进 · Enter自动缩进')
        return True

    def highlight(self):
        for tag in ('keyword','string','comment','errorline'): self.editor.tag_remove(tag,'1.0','end')
        source=self.editor.get('1.0','end-1c')
        if len(source)>20000: return
        try:
            for token in tokenize.generate_tokens(io.StringIO(source).readline):
                tag='keyword' if token.type==tokenize.NAME and keyword.iskeyword(token.string) else 'string' if token.type==tokenize.STRING else 'comment' if token.type==tokenize.COMMENT else None
                if tag: self.editor.tag_add(tag,f'{token.start[0]}.{token.start[1]}',f'{token.end[0]}.{token.end[1]}')
        except (tokenize.TokenError,IndentationError,SyntaxError): pass

    def show_hint(self):
        if self.current_id:
            self.app.write(self.result,'思考提示\n\n'+'\n\n'.join(self.tasks[self.current_id]['hints'])+'\n\n提示仅辅助学习；代码任务不改变选择题课程的过关状态。')

    def reset(self):
        if self.running or not self.current_id: return
        if messagebox.askyesno('恢复骨架','将替换当前草稿；可用编辑器撤销操作恢复。'):
            self.editor.delete('1.0','end');self.editor.insert('1.0',self.tasks[self.current_id]['starter']);self.autosave()

    def run(self,mode):
        if self.running or not self.current_id: return
        self.save_draft();self.running=True
        tid=self.current_id;source=self.editor.get('1.0','end-1c')
        self.editor.configure(state='disabled');self.filter.configure(state='disabled')
        for button in (self.run_button,self.submit_button,self.reset_button): button.state(['disabled'])
        self.status.set('正在准备隔离环境并运行，请稍候…')
        self.app.write(self.result,'正在运行'+('前两个示例' if mode=='example' else '全部测试')+'…')
        def work():
            try: result=run_code(self.tasks[tid],source,mode)
            except Exception as exc: result={'status':'error','passed':False,'error':str(exc),'cases':[]}
            self.events.put((tid,source,mode,result))
        threading.Thread(target=work,daemon=True).start()

    def poll(self):
        try: tid,source,mode,result=self.events.get_nowait()
        except queue.Empty: pass
        else:
            self.running=False;self.editor.configure(state='normal');self.filter.configure(state='readonly')
            for button in (self.run_button,self.submit_button,self.reset_button): button.state(['!disabled'])
            try: self.app.store.save_code_attempt(tid,source,mode,result)
            except Exception as exc: save_status='结果保存失败：'+str(exc)
            else: save_status='结果已保存'
            if result['status']=='ok':
                n=sum(c['passed'] for c in result['cases']);total=len(result['cases'])
                lines=[f'{"示例" if mode=="example" else "全部测试"}：{n}/{total} 通过']
                if mode=='example': lines.append('示例通过不代表任务完成，请提交全部测试。')
                for i,c in enumerate(result['cases'],1):
                    lines.append(f'{"✓" if c["passed"] else "×"} 用例{i} 输入 {c["args"]!r}\n  期望 {c["expected"]!r}；实际 {c["actual"]!r}')
                if result.get('stdout'): lines.append('打印输出\n'+result['stdout'])
                self.app.write(self.result,'\n\n'.join(lines))
            else:
                line=result.get('line');self.app.write(self.result,('第'+str(line)+'行：' if line else '')+result.get('error','运行未完成'))
                if line:
                    self.editor.tag_add('errorline',f'{line}.0',f'{line}.end');self.editor.see(f'{line}.0')
            self.status.set(save_status+' · '+('任务通过' if mode=='submit' and result.get('passed') else '可以继续修改'))
            if mode=='submit' and result.get('passed'):
                self.tree.item(tid,text='✓ '+self.tasks[tid]['title'])
            self.tree.selection_set(tid)
            self.app.refresh()
        self.after(100,self.poll)
