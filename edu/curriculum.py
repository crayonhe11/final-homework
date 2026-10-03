"""课程地图与过关状态：导学 → 学习 → 两题独立验证 → 解锁。"""
import json
from .bank import ROOT

CHAPTERS = ('条件判断', '循环', '函数与返回值')
INTRO_ID = '__intro__'
INTRO_TEXT = '''Python 基础学习路线 · 课程导学

本课程覆盖三个主题、十五个知识点，不是完整的 Python 知识全集。
学习顺序：基础导学 → 条件判断 → 循环 → 函数与返回值。

开始前需要知道
• 变量用名字保存或引用值：count = 2。
• 数字 2 和字符串 "2" 不同；True/False 是布尔值，None 表示没有值。
• print(value) 将内容输出到屏幕；多个 print 通常各占一行。
• 代码默认从上向下执行，缩进表示属于同一个代码块，建议使用四个空格。
• [] 表示列表；% 是取余，n % 2 == 0 用来判断整数是否为偶数。

例子
count = 2
count = count + 1
print(count)

输出
3

观察：先保存 2，再读取旧值加 1，最后显示 3。

如何学习
1. 点击知识地图中的知识点，先读目标、讲解、示例与思考题。
2. 点击“我已阅读，开始闯关”，完成该关两道不同的选择题。
3. 两题各自最近一次闯关作答均正确且未使用提示，就完成本关。
4. 同章按前置关系解锁，完成整章后解锁下一章。

使用提示不会扣分，但需要再独立答题验证。自由练习不直接授予闯关通过。
课程过关是学习活动完成记录，不代表永久掌握；后续仍有到期复习。
'''


def load_lessons(concepts, path=None):
    lessons = json.loads((path or ROOT/'data/lessons.json').read_text(encoding='utf-8'))
    if set(lessons) != set(concepts): raise ValueError('课程讲解必须覆盖每个概念')
    for cid, lesson in lessons.items():
        fields = ('objective','example_code','example_output','walkthrough','reflection')
        if not isinstance(lesson,dict) or any(not isinstance(lesson.get(k),str) or not lesson[k].strip() for k in fields):
            raise ValueError(f'{cid}: 课程讲解不完整')
        paragraphs = lesson.get('explanations')
        if not isinstance(paragraphs,list) or not paragraphs or any(not isinstance(p,str) or not p.strip() for p in paragraphs):
            raise ValueError(f'{cid}: 缺少概念说明')
    return lessons


def requirements(cid, concepts):
    """章际门槛与章内前置关系合并。"""
    topic = concepts[cid]['topic']
    previous = set(CHAPTERS[:CHAPTERS.index(topic)])
    return set(concepts[cid].get('prerequisites', [])) | {key for key,m in concepts.items() if m['topic'] in previous}


def course_states(questions, concepts, history, reads):
    """从显式课程作答重建永久通关；后续复习错误不重新锁住章节。"""
    groups = {cid: {q['id'] for q in questions.values() if q['concept'] == cid} for cid in concepts}
    passed, latest = set(), {cid: {} for cid in concepts}
    for row in history:
        cid = row.get('course_concept')
        if cid not in concepts or cid not in reads or INTRO_ID not in reads: continue
        if not requirements(cid,concepts) <= passed: continue
        qid = row['question_id']
        if qid not in groups[cid]: continue
        latest[cid][qid] = bool(row['correct']) and row.get('hints_used') == 0
        if len(groups[cid]) >= 2 and all(latest[cid].get(qid,False) for qid in groups[cid]):
            passed.add(cid)
    states = {}
    for cid in concepts:
        missing = requirements(cid,concepts) - passed
        locked = INTRO_ID not in reads or bool(missing)
        count = sum(latest[cid].values())
        status = '已过关' if cid in passed else '未解锁' if locked else '学习中' if cid in reads else '可学习'
        states[cid] = {'status':status, 'passed':cid in passed, 'locked':locked,
                       'missing': sorted(missing,key=lambda k:concepts[k].get('order',0)),
                       'solved':count, 'total':len(groups[cid]), 'latest':latest[cid]}
    return states


def lesson_question(cid, questions, state):
    pool = sorted((q for q in questions.values() if q['concept'] == cid),key=lambda q:(q['difficulty'],q['id']))
    if state['locked'] or state['passed']: return None
    return next((q for q in pool if not state['latest'].get(q['id'],False)),None)


def lesson_text(cid, concepts, lessons, state):
    meta, lesson = concepts[cid], lessons[cid]
    parents = '、'.join(concepts[p]['label'] for p in meta.get('prerequisites',[])) or '本章起点'
    return '\n\n'.join([f'{meta["topic"]} · {meta["label"]}',
        f'学习目标：{lesson["objective"]}', f'知识关系：{parents} → 本知识点',
        '概念讲解\n'+'\n\n'.join(lesson['explanations']),
        '示例（不是闯关原题）\n'+lesson['example_code'],
        '示例输出\n'+lesson['example_output'], '逐步理解\n'+lesson['walkthrough'],
        '先想一想\n'+lesson['reflection'],
        f'本关检查：{state["total"]} 道不同题各自最近一次闯关作答均独立正确。\n进度：{state["solved"]}/{state["total"]} · {state["status"]}'])
