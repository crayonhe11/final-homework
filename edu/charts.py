"""真实作答记录的每日统计；缺失正确率不画成零。"""
import json
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from .coding import load_tasks


def daily_metrics(history, code_history, questions, tasks, days=30, topic='全部章节', now=None):
    now=now or datetime.now().astimezone()
    end=now.date();start=end-timedelta(days=days-1)
    rows={start+timedelta(days=i):{'date':start+timedelta(days=i),'questions':0,'correct':0,'submissions':0,'passed':0} for i in range(days)}
    for records,bank,key,is_code in [(history,questions,'question_id',False),(code_history,tasks,'task_id',True)]:
        for r in records:
            item=bank.get(r[key])
            if not item or topic not in ('全部章节',item['topic']): continue
            if is_code:
                if r['mode']!='submit': continue
                try:
                    if json.loads(r['result_json']).get('status')=='unavailable': continue
                except (ValueError,TypeError): continue
            try: day=datetime.fromisoformat(r['created_at']).astimezone(now.tzinfo).date()
            except (ValueError,TypeError): continue
            if day not in rows: continue
            row=rows[day]
            row['submissions' if is_code else 'questions']+=1
            row['passed' if is_code else 'correct']+=bool(r['passed' if is_code else 'correct'])
    return [{**r,'accuracy':100*r['correct']/r['questions'] if r['questions'] else None,
             'pass_rate':100*r['passed']/r['submissions'] if r['submissions'] else None} for r in rows.values()]


class ProgressCharts(ttk.Frame):
    def __init__(self,parent,app):
        super().__init__(parent,padding=12);self.app=app;self.tasks=load_tasks()
        bar=ttk.Frame(self);bar.pack(fill='x')
        self.days=tk.StringVar(value='30');self.topic=tk.StringVar(value='全部章节')
        for var,values,width in [(self.days,['7','30','90'],5),(self.topic,['全部章节','条件判断','循环','函数与返回值'],15)]:
            c=ttk.Combobox(bar,textvariable=var,values=values,width=width,state='readonly');c.pack(side='left',padx=5);c.bind('<<ComboboxSelected>>',lambda e:self.refresh())
        ttk.Label(bar,text='天 · 按本地日期统计').pack(side='left')
        self.canvas=tk.Canvas(self,bg='white',highlightthickness=0,height=390);self.canvas.pack(fill='both',expand=True,pady=10)
        self.canvas.bind('<Configure>',lambda e:self.refresh())
        self.note=tk.StringVar(value='移动到圆点查看当天数据。')
        ttk.Label(self,textvariable=self.note,wraplength=780).pack(anchor='w')
        ttk.Label(self,text='紫色：选择题；绿色：代码提交。示例运行与环境不可用不计入代码通过率；重复提交会计数。\n无作答日期的正确率留空。这些曲线描述练习表现，不代表已掌握知识。',wraplength=780).pack(anchor='w',pady=8)

    def refresh(self):
        rows=daily_metrics(self.app.store.history(),self.app.store.code_history(),self.app.questions,self.tasks,int(self.days.get()),self.topic.get())
        c=self.canvas;c.delete('all');w=max(c.winfo_width(),350);h=max(c.winfo_height(),300)
        for panel,(title,keys,maximum) in enumerate([('每天练习次数',('questions','submissions'),max(1,max(r['questions'] for r in rows),max(r['submissions'] for r in rows))),('正确率 / 测试通过率（%）',('accuracy','pass_rate'),100)]):
            top=panel*h/2+30;bottom=(panel+1)*h/2-28
            c.create_text(45,top-18,anchor='w',text=title,fill='#24344c')
            for fraction in (0,.5,1):
                y=bottom-(bottom-top)*fraction;c.create_line(45,y,w-20,y,fill='#e9ecf2');c.create_text(35,y,anchor='e',text=f'{maximum*fraction:g}',fill='#788198')
            for key,color in zip(keys,('#6555d9','#218768')):
                prev=None
                for i,r in enumerate(rows):
                    value=r[key];x=45+i*(w-65)/max(1,len(rows)-1)
                    if value is None: prev=None;continue
                    y=bottom-(bottom-top)*value/maximum
                    if prev: c.create_line(*prev,x,y,fill=color,width=2)
                    point=c.create_oval(x-3,y-3,x+3,y+3,fill=color,outline='')
                    label=f'{r["date"]} · 选择题 {r["correct"]}/{r["questions"]} 正确 · 代码 {r["passed"]}/{r["submissions"]} 通过'
                    c.tag_bind(point,'<Enter>',lambda e,text=label:self.note.set(text));prev=(x,y)
            for index,anchor in [(0,'w'),(len(rows)-1,'e')]:
                c.create_text(45 if index==0 else w-20,bottom+15,anchor=anchor,text=rows[index]['date'].strftime('%m-%d'),fill='#788198')
        if not any(r['questions'] or r['submissions'] for r in rows):
            c.create_text(w/2,h/2,text='这个时间段还没有练习记录，完成一次作答后即可查看。',fill='#6555d9')
