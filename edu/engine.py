"""确定性评分和可解释推荐；不执行题目或学生输入。"""

def diagnose(question, choice):
    if choice not in question['options']:
        raise ValueError('请选择有效选项')
    correct = choice == question['answer']
    mapping = question['misconceptions'].get(choice)
    return {'correct': correct, 'concept': None if correct else mapping['concept'],
            'evidence': '本次答案正确，仍需通过不同题目验证理解。' if correct else mapping['evidence'],
            'explanation': question['explanation'], 'hint': question['hint']}


def recommend(question, questions, history, concept=None, limit=3):
    """优先未做同概念，再同主题；题库耗尽后明确推荐复习。"""
    concept = concept or question['concept']
    attempted = {row['question_id'] for row in history}
    candidates = [q for q in questions.values() if q['id'] != question['id'] and q['topic'] == question['topic']]
    last_seen = {row['question_id']: i for i, row in enumerate(history)}
    candidates.sort(key=lambda q: (
        q['id'] in attempted, q['concept'] != concept,
        abs(q['difficulty'] - question['difficulty']), last_seen.get(q['id'], -1), q['id']))
    return [{'question': q, 'reason': ('复习题 · ' if q['id'] in attempted else '未做题 · ')
             + ('验证相同概念' if q['concept'] == concept else '同主题拓展（同概念未做题不足）')}
            for q in candidates[:limit]]


def progress(questions, history, concepts):
    result = []
    for cid, meta in concepts.items():
        records = [r for r in history if questions[r['question_id']]['concept'] == cid]
        recent = records[-3:]
        distinct_correct = {r['question_id'] for r in recent if r['correct']}
        state = '尚未练习' if not recent else ('仍需练习' if not all(r['correct'] for r in recent)
                else '初步稳定，继续巩固' if len(distinct_correct) >= 2 else '本次答对，待验证')
        result.append({'concept':cid, 'label':meta['label'], 'topic':meta['topic'], 'attempts':len(records),
                       'correct':sum(r['correct'] for r in records), 'state':state})
    return result
