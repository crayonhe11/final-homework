"""确定性评分、前置概念建议与可解释推荐；不执行题目或学生输入。"""
from .scheduler import due_reviews


def diagnose(question, choice):
    if choice not in question['options']:
        raise ValueError('请选择有效选项')
    correct = choice == question['answer']
    mapping = question['misconceptions'].get(choice)
    return {'correct': correct, 'concept': None if correct else mapping['concept'],
            'evidence': '本次答案正确，仍需通过不同题目验证理解。' if correct else mapping['evidence'],
            'explanation': question['explanation'], 'hint': question['hint']}


def recommend(question, questions, history, concept=None, limit=3, now=None):
    """未做同概念变式 → 到期题 → 同主题新题 → 提前复习；排除当前题。"""
    concept = concept or question['concept']
    attempted = {row['question_id'] for row in history}
    due = due_reviews(questions, history, now, question['topic'])
    due_order = {qid: i for i, qid in enumerate(due)}
    candidates = [q for q in questions.values() if q['id'] != question['id'] and q['topic'] == question['topic']]
    last_seen = {row['question_id']: i for i, row in enumerate(history)}

    def priority(q):
        if q['id'] not in attempted and q['concept'] == concept: return 0
        if q['id'] in due_order: return 1
        if q['id'] not in attempted: return 2
        return 3

    candidates.sort(key=lambda q: (priority(q), due_order.get(q['id'], len(due)),
        q['concept'] != concept, abs(q['difficulty'] - question['difficulty']),
        last_seen.get(q['id'], -1), q['id']))
    output = []
    for q in candidates[:max(0, limit)]:
        if q['id'] in due_order: reason = '复习题 · 已到复习时间'
        elif q['id'] in attempted: reason = '复习题 · 提前巩固，尚无其他未做或到期题'
        elif q['concept'] == concept: reason = '未做题 · 验证相同概念'
        else: reason = '未做题 · 同主题拓展（同概念未做题不足）'
        output.append({'question': q, 'reason': reason})
    return output


def progress(questions, history, concepts):
    result = []
    for cid, meta in concepts.items():
        records = [r for r in history if r['question_id'] in questions and questions[r['question_id']]['concept'] == cid]
        recent = records[-3:]
        independent = {r['question_id'] for r in recent if r['correct'] and r.get('hints_used', 0) == 0}
        if not recent: state = '尚未练习'
        elif not all(r['correct'] for r in recent): state = '仍需练习'
        elif any(r.get('hints_used', 0) != 0 for r in recent): state = '需独立作答验证'
        elif len(independent) >= 2: state = '初步稳定，继续巩固'
        else: state = '本次答对，待验证'
        result.append({'concept': cid, 'label': meta['label'], 'topic': meta['topic'],
                       'attempts': len(records), 'correct': sum(r['correct'] for r in records), 'state': state})
    return result


def next_practice(topic, questions, history, concepts, now=None, exclude=None):
    """到期复习优先；新题按前置概念与课程顺序建议，不强制锁题。"""
    pool = [q for q in questions.values() if q['topic'] == topic and q['id'] != exclude]
    if not pool: return None
    due = [qid for qid in due_reviews(questions, history, now, topic) if qid != exclude]
    if due: return {'question': questions[due[0]], 'reason': '到期复习 · 根据上次作答安排'}
    done = {r['question_id'] for r in history}
    fresh = [q for q in pool if q['id'] not in done]
    stable = {r['concept'] for r in progress(questions, history, concepts) if r['state'] == '初步稳定，继续巩固'}
    if fresh:
        def key(q):
            meta = concepts[q['concept']]
            missing = set(meta.get('prerequisites', [])) - stable
            return bool(missing), q['difficulty'], meta.get('order', 999), q['id']
        q = min(fresh, key=key)
        missing = set(concepts[q['concept']].get('prerequisites', [])) - stable
        reason = '新题 · 按概念学习顺序推荐'
        if missing: reason += '；建议先巩固：' + '、'.join(concepts[c]['label'] for c in sorted(missing))
        return {'question': q, 'reason': reason}
    last = {r['question_id']: i for i, r in enumerate(history)}
    return {'question': min(pool, key=lambda q: (last.get(q['id'], -1), q['id'])),
            'reason': '本主题暂无未做或到期题 · 可自愿提前复习'}


def learning_summary(questions, history, now=None):
    rows = [r for r in history if r['question_id'] in questions]
    first = {}
    for row in rows: first.setdefault(row['question_id'], row)
    return {'attempts': len(rows), 'correct': sum(r['correct'] for r in rows),
            'unique': len(first), 'first_correct': sum(r['correct'] for r in first.values()),
            'hinted': sum(r.get('hints_used') is not None and r['hints_used'] > 0 for r in rows),
            'due': len(due_reviews(questions, history, now)), 'archived': len(history) - len(rows)}
