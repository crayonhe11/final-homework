#!/usr/bin/env python3
"""启动入口：python3 main.py；命令行降级模式：python3 main.py --cli。"""
import argparse
from pathlib import Path
from edu.bank import load_bank, ROOT
from edu.engine import diagnose, recommend, next_practice
from edu.storage import Store


def cli(db_path):
    questions, concepts=load_bank(); store=Store(db_path)
    print('知错 · Python 入门概念练习（输入 q 退出）')
    topics=['条件判断','循环','函数与返回值']
    while True:
        text=input('选择主题 1 条件判断 / 2 循环 / 3 函数与返回值：').strip()
        if text.lower()=='q': return
        if text not in ('1','2','3'): continue
        topic=topics[int(text)-1]
        item=next_practice(topic,questions,store.history(),concepts)
        if item is None: continue
        print(item['reason']); question=item['question']
        while True:
            print('\n'+question['id']+'\n'+question['code'])
            for key,value in question['options'].items(): print(key,repr(value))
            choice=input('答案 A/B/C（q 退出）：').strip().upper()
            if choice=='Q': return
            if choice not in question['options']: continue
            reason=input('简短理由（可留空）：')[:1000]
            result=diagnose(question,choice)
            store.save(question['id'],choice,reason,result,{'status':'disabled','message':'命令行规则模式'})
            print('答对了。' if result['correct'] else '可能涉及：'+concepts[result['concept']]['label'])
            print(question['explanation'])
            rec=recommend(question,questions,store.history(),result['concept'],1)[0]
            if input('输入 y 继续针对性练习，其他键返回主题：').strip().lower()!='y': break
            print(rec['reason']); question=rec['question']


def main():
    parser=argparse.ArgumentParser(description='Python 错题概念诊断与练习推荐')
    parser.add_argument('--cli',action='store_true',help='使用命令行界面')
    parser.add_argument('--db',type=Path,default=ROOT/'runtime/learning.sqlite3',help='数据库路径')
    args=parser.parse_args()
    if args.cli:
        cli(args.db); return
    try:
        from edu.ui import App
        app=App(args.db)
    except ImportError:
        print('当前 Python 没有 Tkinter。请使用 python3 main.py --cli，或安装包含 Tk 的 Python。')
        return
    app.mainloop()

if __name__=='__main__': main()
