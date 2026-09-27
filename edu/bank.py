import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_bank():
    questions = json.loads((ROOT / 'data/questions.json').read_text(encoding='utf-8'))
    concepts = json.loads((ROOT / 'data/concepts.json').read_text(encoding='utf-8'))
    seen = set()
    for q in questions:
        if q['id'] in seen or q['concept'] not in concepts:
            raise ValueError('重复题号或未知概念')
        seen.add(q['id'])
        if q['answer'] not in q['options'] or set(q['misconceptions']) != set(q['options']) - {q['answer']}:
            raise ValueError('答案或误区映射不完整')
        for item in q['misconceptions'].values():
            if item['concept'] not in concepts:
                raise ValueError('未知误区')
    return {q['id']: q for q in questions}, concepts
