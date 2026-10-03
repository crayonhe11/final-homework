"""知识地图与独立课程详情；双击进入，课程与自由练习分别导航。"""
import tkinter as tk
from tkinter import ttk
from .theme import BG, INK, MUTED, ACCENT, BORDER, rounded
from .scheduler import due_reviews
from .curriculum import CHAPTERS, INTRO_ID, INTRO_TEXT, course_states


class CourseView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent,padding=12)
        self.app=app
        self.selected=INTRO_ID
        self.states={}
        self.page='map'
        self.map_page=ttk.Frame(self)
        self.detail_page=ttk.Frame(self)
        hero=ttk.Frame(self.map_page,style='Card.TFrame',padding=(22,16));hero.pack(fill='x',pady=(0,12))
        ttk.Label(hero,text='PYTHON FOUNDATIONS',style='CardMuted.TLabel').pack(anchor='w')
        hero_row=ttk.Frame(hero,style='Card.TFrame');hero_row.pack(fill='x',pady=(6,0))
        ttk.Label(hero_row,text='把每一次理解，变成下一步进展。',style='CardTitle.TLabel').pack(side='left')
        ttk.Button(hero_row,text='继续学习  →',style='Primary.TButton',command=self.resume).pack(side='right')
        self.summary=tk.StringVar()
        ttk.Label(hero,textvariable=self.summary,style='CardMuted.TLabel').pack(anchor='w',pady=(7,0))
        metrics=ttk.Frame(self.map_page);metrics.pack(fill='x',pady=(0,12))
        self.metric_vars=[]
        for i,label in enumerate(('课程完成','已练习题目','待复习')):
            metrics.columnconfigure(i,weight=1)
            card=ttk.Frame(metrics,style='Card.TFrame',padding=(16,10));card.grid(row=0,column=i,sticky='ew',padx=(0,10 if i<2 else 0))
            var=tk.StringVar(value='0');self.metric_vars.append(var)
            ttk.Label(card,text=label,style='CardMuted.TLabel').pack(side='left')
            ttk.Label(card,textvariable=var,style='Metric.TLabel').pack(side='right')
        heading=ttk.Frame(self.map_page);heading.pack(fill='x',pady=(0,4))
        ttk.Label(heading,text='课程路线',font=('Arial',15,'bold')).pack(side='left')
        ttk.Label(heading,text='双击知识点进入  ·  未解锁课程也可预览',style='Muted.TLabel').pack(side='right')
        map_holder=ttk.Frame(self.map_page);map_holder.pack(fill='both',expand=True)
        self.map=tk.Canvas(map_holder,height=405,highlightthickness=0,bg=BG)
        self.map_scroll=ttk.Scrollbar(map_holder,orient='vertical',command=self.map.yview)
        self.map_scroll.pack(side='right',fill='y')
        self.map.configure(yscrollcommand=self.map_scroll.set)
        self.map.pack(side='left',fill='both',expand=True)
        self.map.bind('<MouseWheel>',self.scroll_map)
        self.map.bind('<Configure>',lambda e:self.draw_map())
        self.map.bind('<Button-1>',self.click_node)
        self.map.bind('<Double-Button-1>',self.open_node)
        self.map.bind('<Return>',lambda e:self.open_selected())
        self.map.bind('<Motion>',self.hover_node)
        bar=ttk.Frame(self.map_page);bar.pack(fill='x',pady=6)
        ttk.Button(bar,text='基础导学',command=lambda:self.select_lesson(INTRO_ID)).pack(side='left')
        ttk.Button(bar,text='打开所选课程',command=self.open_selected).pack(side='right',padx=6)
        self.map_note=tk.StringVar(value='第一次使用可先阅读基础导学；已学过的知识点也可直接打开进行自由练习。')
        ttk.Label(self.map_page,textvariable=self.map_note,wraplength=760,style='Muted.TLabel').pack(anchor='w',pady=5)

        nav=ttk.Frame(self.detail_page);nav.pack(fill='x')
        ttk.Button(nav,text='← 返回知识地图',command=self.show_map).pack(side='left')
        self.breadcrumb=tk.StringVar()
        ttk.Label(nav,textvariable=self.breadcrumb).pack(side='left',padx=12)
        self.free_button=ttk.Button(nav,text='直接练习本知识点 →',command=self.practice_selected)
        self.free_button.pack(side='right')
        self.heading=tk.StringVar()
        ttk.Label(self.detail_page,textvariable=self.heading,font=('Arial',20,'bold')).pack(anchor='w',pady=(16,8))
        self.goal=tk.StringVar()
        ttk.Label(self.detail_page,textvariable=self.goal,wraplength=820).pack(anchor='w',pady=(0,12))
        self.sections=ttk.Notebook(self.detail_page);self.sections.pack(fill='both',expand=True)
        theory=ttk.Frame(self.sections,padding=10)
        example=ttk.Frame(self.sections,padding=10)
        reflection=ttk.Frame(self.sections,padding=10)
        self.sections.add(theory,text='  概念讲解  ')
        self.sections.add(example,text='  代码示例  ')
        self.sections.add(reflection,text='  思考与过关要求  ')
        self.lesson=app.text_box(theory,height=10)
        self.example=app.text_box(example,height=10);self.example.configure(font=('Menlo',13),background='#20263d',foreground='#e6e9ff')
        self.reflection=app.text_box(reflection,height=10)
        actions=ttk.Frame(self.detail_page);actions.pack(fill='x',pady=(12,0))
        self.requirement=tk.StringVar()
        ttk.Label(actions,textvariable=self.requirement,wraplength=540).pack(side='left')
        self.start_button=ttk.Button(actions,style='Primary.TButton',command=self.start_selected)
        self.start_button.pack(side='right')
        self.prerequisite_button=ttk.Button(self.detail_page,text='查看下一步需要完成的课程',command=self.open_prerequisite)
        self.refresh();self.show_map()

    def refresh(self):
        self.states=course_states(self.app.questions,self.app.concepts,self.app.store.history(),self.app.store.lesson_reads())
        count=sum(s['passed'] for s in self.states.values())
        self.summary.set(f'基础导学 → 条件判断 → 循环 → 函数与返回值   ·   已过关 {count} / {len(self.states)}')
        known={r['question_id'] for r in self.app.store.history() if r['question_id'] in self.app.questions}
        self.metric_vars[0].set(f'{count} / {len(self.states)}')
        self.metric_vars[1].set(f'{len(known)} / {len(self.app.questions)}')
        self.metric_vars[2].set(str(len(due_reviews(self.app.questions,self.app.store.history()))))
        self.draw_map()
        if self.page=='detail': self.show_selected(reset=False)

    def scroll_map(self,event):
        self.map.yview_scroll(-1 if event.delta>0 else 1,'units')
        return 'break'

    def draw_map(self):
        self.map.delete('all')
        width=max(self.map.winfo_width(),350)
        columns=3 if width>=780 else 2 if width>=560 else 1
        gap=14;col=(width-gap*(columns-1))/columns
        colors={'已过关':('#e8f5ed','#2c8050'),'未解锁':('#f0f2f6','#8790a1'),
                '可学习':('#eeebff','#6555d9'),'学习中':('#fff1d8','#a97524')}
        for chapter,topic in enumerate(CHAPTERS):
            x=(chapter%columns)*(col+gap);base=(chapter//columns)*420
            nodes=sorted((cid for cid,m in self.app.concepts.items() if m['topic']==topic),key=lambda c:self.app.concepts[c].get('order',0))
            complete=sum(self.states[c]['passed'] for c in nodes)
            rounded(self.map,x+1,base+2,x+col-1,base+410,fill='white',outline=BORDER)
            self.map.create_text(x+16,base+24,anchor='w',text=f'0{chapter+1}  {topic}',font=('Arial',13,'bold'),fill=INK)
            self.map.create_text(x+16,base+47,anchor='w',text=f'{complete} / {len(nodes)} 关已完成',font=('Arial',10),fill=MUTED)
            self.map.create_line(x+16,base+65,x+col-16,base+65,fill='#eeebf7',width=4)
            if complete: self.map.create_line(x+16,base+65,x+16+(col-32)*complete/len(nodes),base+65,fill=ACCENT,width=4)
            for row,cid in enumerate(nodes):
                state=self.states[cid];badge,fg=colors[state['status']]
                y=base+80+row*64;tag='node_'+cid
                fill='#f8f7ff' if cid==self.selected else 'white'
                rounded(self.map,x+8,y,x+col-8,y+58,r=8,fill=fill,outline=ACCENT if cid==self.selected else '#edf0f5',width=1,tags=(tag,'card',f'border_{cid}'))
                self.map.create_oval(x+17,y+12,x+39,y+34,fill=badge,outline='',tags=tag)
                self.map.create_text(x+28,y+23,text='✓' if state['passed'] else str(row+1),font=('Arial',10,'bold'),fill=fg,tags=tag)
                label=self.app.concepts[cid]['label']
                self.map.create_text(x+48,y+16,anchor='w',text=label,font=('Arial',10,'bold'),fill=INK,width=max(100,col-70),tags=tag)
                self.map.create_text(x+48,y+43,anchor='w',text=state['status']+('  ·  '+str(state['solved'])+'/'+str(state['total']) if not state['locked'] else '  ·  可预览'),font=('Arial',10),fill=fg,tags=tag)
        rows=(len(CHAPTERS)+columns-1)//columns
        self.map.configure(scrollregion=(0,0,width,rows*420))

    def node_at(self,event):
        for item in reversed(self.map.find_overlapping(self.map.canvasx(event.x),self.map.canvasy(event.y),self.map.canvasx(event.x),self.map.canvasy(event.y))):
            for tag in self.map.gettags(item):
                if tag.startswith('node_'): return tag[5:]
        return None

    def click_node(self,event):
        cid=self.node_at(event)
        if not cid: return
        self.selected=cid
        self.map.focus_set()
        # 不在第一次单击时重建 Canvas 项，否则会破坏真实的双击事件识别。
        for item in self.map.find_withtag('card'):
            self.map.itemconfigure(item,outline=self.map.itemcget(item,'fill'))
        self.map.itemconfigure(f'border_{cid}',outline=ACCENT)
        self.map_note.set(self.app.concepts[cid]['label']+' · 双击进入；或使用右侧“打开所选课程”。')

    def open_node(self,event):
        cid=self.node_at(event)
        if cid: self.select_lesson(cid)
        return 'break'

    def hover_node(self,event):
        self.map.configure(cursor='hand2' if self.node_at(event) else '')

    def open_selected(self):
        self.select_lesson(self.selected)

    def select_lesson(self,cid):
        self.selected=cid
        self.page='detail'
        self.map_page.pack_forget();self.detail_page.pack(fill='both',expand=True)
        self.show_selected(reset=True)

    def show_map(self):
        self.page='map'
        self.detail_page.pack_forget();self.map_page.pack(fill='both',expand=True)
        self.refresh()

    def show_selected(self,reset=False):
        positions=[box.yview()[0] for box in (self.lesson,self.example,self.reflection)]
        self.prerequisite_button.pack_forget()
        if self.selected==INTRO_ID:
            self.breadcrumb.set('知识地图 / 基础导学')
            self.heading.set('开始之前，先认识这条学习路线')
            self.goal.set('准备：变量、类型、输出与缩进。导学不设置测验，阅读后进入第一课。')
            self.app.write(self.lesson,'概念讲解\n\n变量保存或引用值：count = 2。\n\n数字 2 与字符串 "2" 不同；True / False 表示真假，None 表示没有值。\n\nprint 显示结果；代码一般从上到下执行，缩进表示代码块。\n\n[] 表示列表；% 是取余运算。')
            self.app.write(self.example,'count = 2\ncount = count + 1\nprint(count)\n\n输出：\n3\n\n过程：保存 2 → 加 1 → 显示 3。')
            self.app.write(self.reflection,'学习路线\n\n条件判断 → 循环 → 函数与返回值\n\n每课：阅读讲解 → 查看示例 → 完成两题 → 解锁后续内容。\n\n闯关时两道不同题各自最近一次均独立答对才通过。使用提示后可以重新验证。\n\n直接练习属于自由练习，不授予闯关通过。过关不代表永久掌握。')
            self.requirement.set('读完后点击右侧按钮，进入第一课；无需在首页阅读大段文字。')
            self.start_button.configure(text='完成导学，进入第一课 →');self.start_button.state(['!disabled'])
            self.free_button.state(['disabled'])
        else:
            cid=self.selected;meta=self.app.concepts[cid];lesson=self.app.lessons[cid];state=self.states[cid]
            self.breadcrumb.set(f'知识地图 / {meta["topic"]} / {state["status"]}')
            self.heading.set(meta['label']);self.goal.set('学习目标：'+lesson['objective'])
            parents='、'.join(self.app.concepts[p]['label'] for p in meta.get('prerequisites',[])) or '本章起点'
            self.app.write(self.lesson,'概念讲解\n\n'+'\n\n'.join(lesson['explanations'])+'\n\n前置知识：'+parents)
            self.app.write(self.example,lesson['example_code']+'\n\n输出\n'+lesson['example_output']+'\n\n逐步理解\n'+lesson['walkthrough'])
            self.app.write(self.reflection,'先想一想\n\n'+lesson['reflection']+f'\n\n本关检查\n{state["total"]} 道不同题各自最近一次闯关作答都独立正确。\n当前：{state["solved"]}/{state["total"]} · {state["status"]}\n\n右上角可以直接进行本知识点自由练习，不影响章节解锁。')
            self.free_button.state(['!disabled'])
            if state['locked']:
                message='先完成基础导学。' if INTRO_ID not in self.app.store.lesson_reads() else '前置关卡尚未完成。'
                self.requirement.set(message+'可预览课程或直接自由练习；闯关需要先解锁。')
                self.start_button.configure(text='闯关尚未解锁');self.start_button.state(['disabled'])
                self.prerequisite_button.pack(anchor='w',pady=(6,0))
            else:
                self.requirement.set('本关已通过，可以复习。' if state['passed'] else '阅读后开始对应关卡；看过提示的题需要再独立验证。')
                self.start_button.configure(text='复习本知识点 →' if state['passed'] else '我已阅读，开始本关 →')
                self.start_button.state(['!disabled'])
        if reset: self.sections.select(0)
        else:
            for box,pos in zip((self.lesson,self.example,self.reflection),positions): box.yview_moveto(pos)

    def resume(self):
        self.refresh()
        if INTRO_ID not in self.app.store.lesson_reads(): return self.select_lesson(INTRO_ID)
        available=[c for c,s in self.states.items() if not s['locked'] and not s['passed']]
        cid=min(available,key=lambda c:self.app.concepts[c].get('order',0)) if available else min(self.app.concepts,key=lambda c:self.app.concepts[c].get('order',0))
        self.select_lesson(cid)

    def open_prerequisite(self):
        # “继续学习”找到当前可学的最早关卡，不把学生送到另一个锁定页。
        self.resume()

    def practice_selected(self):
        if self.selected!=INTRO_ID: self.app.practice_concept(self.selected)

    def start_selected(self):
        if self.app.pending: return
        if self.selected==INTRO_ID:
            self.app.store.mark_lesson_read(INTRO_ID);self.refresh()
            first=min(self.app.concepts,key=lambda c:self.app.concepts[c].get('order',0))
            self.select_lesson(first)
        else:
            self.refresh()
            if self.states[self.selected]['locked']: return
            self.app.store.mark_lesson_read(self.selected)
            self.app.start_lesson(self.selected)
