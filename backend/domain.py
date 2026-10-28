"""Deterministic learning rules. No web framework, network or database dependency."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path

CHAPTERS = ['条件判断', '循环', '函数与返回值']
ROOT = Path(__file__).resolve().parents[1]

def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('时间格式不正确')
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if result.tzinfo is None:
            raise ValueError()
        return result.timestamp() * 1000
    except (ValueError, OverflowError):
        raise ValueError('时间格式不正确') from None

def empty_state():
    return dict(version=1, reads=[], attempts=[], drafts={}, codeAttempts=[])

def text(value, limit, name):
    if not isinstance(value, str) or len(value) > limit:
        raise ValueError(f'{name}必须为不超过{limit}字的文本')
    return value

class LearningEngine:
    def __init__(self, directory=ROOT / 'data'):
        self.questions, self.concepts, self.lessons, self.tasks = [
            json.loads((directory / (name + '.json')).read_text(encoding='utf-8'))
            for name in ['questions', 'concepts', 'lessons', 'coding_tasks']]
        self.bank = {q['id']: q for q in self.questions}
        self.task_bank = {t['id']: t for t in self.tasks}

    def question(self, qid):
        if not isinstance(qid, str) or qid not in self.bank:
            raise ValueError('题目不存在')
        return self.bank[qid]

    def grade(self, qid, choice):
        q = self.question(qid)
        if not isinstance(choice, str) or choice not in q['options']:
            raise ValueError('请选择有效选项')
        correct = choice == q['answer']
        misconception = q['misconceptions'].get(choice, {})
        feedback = dict(concept='none' if correct else misconception.get('concept', 'unknown'),
                        explanation=q['explanation'], hint=q['hint'], source='rule',
                        message='本次答对，继续用不同题目验证理解。' if correct else misconception.get('evidence', '理由不足，暂不判断误区。'))
        return dict(correct=correct, feedback=feedback)

    def validate_state(self, raw, importing=False):
        if not isinstance(raw, dict) or raw.get('version') != 1:
            raise ValueError('请选择 PySteps 版本1的备份')
        result = empty_state()
        for key, limit in [('reads', 16), ('attempts', 10000), ('codeAttempts', 2000)]:
            if not isinstance(raw.get(key), list) or len(raw[key]) > limit:
                raise ValueError(f'{key}格式不正确或记录过多')
        if not isinstance(raw.get('drafts'), dict):
            raise ValueError('代码草稿格式不正确')
        for cid in raw['reads']:
            if not isinstance(cid, str) or cid not in {'__intro__', *self.concepts}:
                raise ValueError('未知概念')
            if cid not in result['reads']:
                result['reads'].append(cid)
        ids = set()
        for row in raw['attempts']:
            if not isinstance(row, dict):
                raise ValueError('作答记录格式不正确')
            q = self.question(row.get('question_id'))
            graded = self.grade(q['id'], row.get('choice'))
            rid = text(row.get('id'), 80, '记录标识')
            if not rid or rid in ids:
                raise ValueError('记录标识为空或重复')
            ids.add(rid)
            reason = text(row.get('reason', ''), 1000, '理由')
            timestamp(row.get('created_at'))
            hints = row.get('hints_used', 1)
            if type(hints) is not int or not 0 <= hints <= len(q['hints']):
                raise ValueError('提示次数不正确')
            course = row.get('course_concept')
            if course is not None and course != q['concept']:
                raise ValueError('课程概念不匹配')
            feedback = graded['feedback']
            f = row.get('feedback')
            # Local learning notes are not exam credentials. Imports always use reviewed explanations.
            if not importing and isinstance(f, dict) and f.get('source') == 'ai':
                candidate = q['misconceptions'].get(row['choice'], {}).get('concept')
                if f.get('concept') in [candidate, 'unknown'] and isinstance(f.get('quote'), str) and f['quote'] and f['quote'] in reason and len(f['quote']) <= 200:
                    feedback = dict(source='ai', concept=f['concept'], quote=f['quote'],
                                    explanation=text(f.get('explanation'), 600, 'AI讲解'),
                                    hint=text(f.get('hint'), 240, 'AI提示'),
                                    message=text(f.get('message', ''), 300, 'AI说明'), personalized=f.get('personalized') is True)
            result['attempts'].append(dict(id=rid, question_id=q['id'], choice=row['choice'], reason=reason,
                correct=graded['correct'], diagnosis=feedback['concept'], created_at=row['created_at'],
                hints_used=hints, course_concept=course, feedback=feedback))
        for tid, source in raw['drafts'].items():
            if tid not in self.task_bank:
                raise ValueError('未知编程任务')
            result['drafts'][tid] = text(source, 20000, '代码')
        code_ids = set()
        for row in raw['codeAttempts']:
            if not isinstance(row, dict) or row.get('task_id') not in self.task_bank:
                raise ValueError('编程记录不正确')
            rid = text(row.get('id'), 80, '记录标识')
            if not rid or rid in code_ids:
                raise ValueError('编程记录标识重复')
            code_ids.add(rid)
            timestamp(row.get('created_at'))
            result['codeAttempts'].append(dict(id=rid, task_id=row['task_id'], source=text(row.get('source'), 20000, '代码'),
                passed=row.get('passed') is True, created_at=row['created_at'], details=text(row.get('details', ''), 4000, '结果')))
        return result

    def requirements(self, cid):
        c = self.concepts[cid]
        return set(c['prerequisites']) | {k for k, v in self.concepts.items() if CHAPTERS.index(v['topic']) < CHAPTERS.index(c['topic'])}

    def courses(self, state):
        passed, latest = set(), {}
        for row in state['attempts']:
            cid = row['course_concept']
            if not cid or cid not in state['reads'] or '__intro__' not in state['reads'] or not self.requirements(cid) <= passed:
                continue
            group = [q for q in self.questions if q['concept'] == cid]
            latest.setdefault(cid, {})[row['question_id']] = row['correct'] and row['hints_used'] == 0
            if len(group) >= 2 and all(latest[cid].get(q['id']) for q in group):
                passed.add(cid)
        return {cid: dict(passed=cid in passed, locked='__intro__' not in state['reads'] or not self.requirements(cid) <= passed,
                         read=cid in state['reads'], solved=sum(latest.get(cid, {}).values()), latest=latest.get(cid, {})) for cid in self.concepts}

    def schedule(self, attempts):
        result = {}
        for row in sorted(attempts, key=lambda r: timestamp(r['created_at'])):
            t, qid = timestamp(row['created_at']), row['question_id']
            prev = result.get(qid)
            if not row['correct']:
                result[qid] = dict(due=t + 600000, stage=0)
            elif row['hints_used'] != 0:
                due = min(prev['due'], t + 86400000) if prev and prev['due'] > t else t + 86400000
                result[qid] = dict(due=due, stage=0)
            elif not prev or t >= prev['due']:
                stage = min((prev['stage'] if prev else 0) + 1, 5)
                result[qid] = dict(due=t + [1, 3, 7, 14, 30][stage-1] * 86400000, stage=stage)
        return result

    def recommend(self, qid, diagnosis, state, now=None):
        q = self.question(qid)
        if diagnosis not in {*self.concepts, 'unknown', 'none'}:
            raise ValueError('未知诊断概念')
        now = now if now is not None else datetime.now(timezone.utc).timestamp() * 1000
        due, seen = self.schedule(state['attempts']), {r['question_id'] for r in state['attempts']}
        neutral = diagnosis == 'unknown'
        def key(item):
            known, target = item['id'] in seen, item['concept'] == diagnosis
            d = due.get(item['id'], {}).get('due', float('inf'))
            rank = 0 if not neutral and target and not known else (0 if neutral else 1) if d <= now else (1 if neutral else 2) if not known else 3
            return rank, d if rank == (0 if neutral else 1) else 0, -int(target) if not neutral else 0, item['difficulty'], item['id']
        return sorted([item for item in self.questions if item['topic'] == q['topic'] and item['id'] != qid], key=key)

    def summary(self, state):
        return dict(courses=self.courses(state), schedule=self.schedule(state['attempts']))
