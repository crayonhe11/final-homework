import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_bank(questions, concepts):
    """内容验证失败时定位题号/概念；不执行题目代码。"""
    if not isinstance(questions, list) or not questions or not isinstance(concepts, dict) or not concepts:
        raise ValueError('题库及概念不能为空')
    for cid, meta in concepts.items():
        if not isinstance(meta, dict) or any(not isinstance(meta.get(k), str) or not meta[k].strip() for k in ('topic', 'label', 'hint')):
            raise ValueError(f'{cid}: 概念字段不完整')
        prerequisites = meta.get('prerequisites', [])
        if not isinstance(prerequisites, list) or any(not isinstance(p, str) or p not in concepts for p in prerequisites):
            raise ValueError(f'{cid}: 未知前置概念')
        if type(meta.get('order', 0)) is not int:
            raise ValueError(f'{cid}: 概念顺序必须是整数')
    visited, visiting = set(), set()

    def visit(cid):
        if cid in visiting: raise ValueError(f'{cid}: 前置概念存在循环依赖')
        if cid in visited: return
        visiting.add(cid)
        for parent in concepts[cid].get('prerequisites', []): visit(parent)
        visiting.remove(cid); visited.add(cid)
    for cid in concepts: visit(cid)
    seen = set()
    for q in questions:
        if not isinstance(q, dict): raise ValueError('题目必须是对象')
        for field in ('id', 'topic', 'concept', 'prompt', 'code', 'answer', 'explanation', 'hint'):
            if not isinstance(q.get(field), str) or not q[field].strip():
                raise ValueError(f'{q.get("id", "未知题")}: 缺少 {field}')
        qid = q['id']
        if qid in seen or q['concept'] not in concepts:
            raise ValueError(f'{qid}: 重复题号或未知概念')
        seen.add(qid)
        if q['topic'] != concepts[q['concept']]['topic']:
            raise ValueError(f'{qid}: 主题与概念不一致')
        if type(q.get('difficulty')) is not int or q['difficulty'] not in (1, 2):
            raise ValueError(f'{qid}: 难度必须为 1 或 2')
        options = q.get('options')
        if not isinstance(options, dict) or set(options) != set('ABC') or any(not isinstance(v, str) or not v for v in options.values()):
            raise ValueError(f'{qid}: 需要 A/B/C 三个文本选项')
        if len(set(options.values())) != 3 or q['answer'] not in options:
            raise ValueError(f'{qid}: 选项重复或答案无效')
        mapping = q.get('misconceptions')
        if not isinstance(mapping, dict) or set(mapping) != set(options) - {q['answer']}:
            raise ValueError(f'{qid}: 错误选项映射不完整')
        for item in mapping.values():
            if (not isinstance(item, dict) or not isinstance(item.get('concept'), str)
                    or item['concept'] not in concepts or not isinstance(item.get('evidence'), str)
                    or not item['evidence'].strip()):
                raise ValueError(f'{qid}: 误区或依据无效')
        hints = q.get('hints', [q['hint']])
        if not isinstance(hints, list) or not hints or any(not isinstance(h, str) or not h.strip() for h in hints):
            raise ValueError(f'{qid}: 分级提示不能为空')


def load_bank(data_dir=None):
    root = Path(data_dir) if data_dir else ROOT / 'data'
    questions = json.loads((root / 'questions.json').read_text(encoding='utf-8'))
    concepts = json.loads((root / 'concepts.json').read_text(encoding='utf-8'))
    validate_bank(questions, concepts)
    return {q['id']: q for q in questions}, concepts
