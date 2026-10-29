"""Opt-in paid evaluation. No requests unless --live is explicitly provided."""
import argparse
import csv
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.domain import LearningEngine, ROOT
from backend.ai import analyze, config

def main():
    parser=argparse.ArgumentParser(description='模拟理由评估集，标签仍需独立人工复核；--live会产生API费用')
    parser.add_argument('--live',action='store_true');args=parser.parse_args()
    engine=LearningEngine();cases=json.loads((ROOT/'submission/ai_cases.json').read_text(encoding='utf-8'));settings=config()
    if args.live and not settings.get('OPENAI_API_KEY'):parser.error('请先配置OPENAI_API_KEY')
    rows=[]
    for case in cases:
        baseline=engine.grade(case['question_id'],case['choice'])['feedback']['concept']
        feedback=analyze(engine,case['question_id'],case['choice'],case['reason'],settings) if args.live else None
        rows.append(dict(**case,rule_prediction=baseline,ai_prediction=feedback['concept'] if feedback else '',source=feedback['source'] if feedback else 'not_run',explanation=feedback['explanation'] if feedback else '',human_factual_score='',human_relevance_score='',reviewer=''))
    destination=ROOT/'evaluation-results';destination.mkdir(exist_ok=True)
    path=destination/('live.csv' if args.live else 'baseline.csv')
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    print(f'样例数：{len(rows)}；规则对预设标签一致：{sum(r["rule_prediction"]==r["expected"] for r in rows)}/{len(rows)}')
    if args.live:
        answered=[r for r in rows if r['source']=='ai']
        print(f'有效AI输出：{len(answered)}/{len(rows)}；有效输出中与预设标签一致：{sum(r["ai_prediction"]==r["expected"] for r in answered)}/{len(answered)}')
    print('模拟数据，非真实学生；标签未独立复核。不能据此证明提高学习成绩。')
    print(path)
if __name__=='__main__':main()
