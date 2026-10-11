"""独立诊断比较；默认只评估规则，--ai 才调用已配置的模型（云API可能收费）。"""
import argparse
import json
import sys
import hashlib
import time
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from edu.bank import load_bank
from edu.engine import diagnose, recommend
from edu.ai import AIHelper, PROMPT_VERSION


def macro_f1(rows, key):
    labels={r['expected'] for r in rows}|{r[key] for r in rows}
    scores=[]
    for label in labels:
        tp=sum(r['expected']==label and r[key]==label for r in rows)
        fp=sum(r['expected']!=label and r[key]==label for r in rows)
        fn=sum(r['expected']==label and r[key]!=label for r in rows)
        scores.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
    return sum(scores)/len(scores) if scores else 0


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--ai',action='store_true',help='执行真实AI评估，云端会产生API用量')
    parser.add_argument('--max-calls',type=int,default=12,help='本次请求上限；超出则在调用前停止')
    parser.add_argument('--dataset',type=Path,default=Path(__file__).parent/'heldout.json')
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'runtime/evaluation-results.json')
    args=parser.parse_args()
    questions,concepts=load_bank(); helper=AIHelper()
    if args.ai and not helper.model: parser.error('请先在api_config.json中配置Kimi密钥和模型，或设置EDU_OLLAMA_MODEL。')
    cases=json.loads(args.dataset.read_text(encoding='utf-8'))
    if not isinstance(cases,list) or not cases: parser.error('评估集必须为非空JSON数组')
    ids=set();eligible=0
    for case in cases:
        if not isinstance(case,dict) or case.get('id') in ids or not case.get('id'): parser.error('样例ID必须非空且唯一')
        ids.add(case['id']);q=questions.get(case.get('question_id'))
        if q is None or case.get('choice') not in q['options'] or not isinstance(case.get('reason'),str) or len(case['reason'])>1000:
            parser.error('样例题号、选项或理由不合法')
        if 'expected' not in case or case['expected'] not in (None,'unknown',q['concept']): parser.error('样例人工标签不在当前诊断范围内')
        eligible+=bool(case['reason'].strip() and case['choice']!=q['answer'])
    if args.ai and (args.max_calls<1 or eligible>args.max_calls): parser.error('样例请求数超过--max-calls上限；尚未发起调用')
    if args.ai: print(f'开始真实评估：最多{eligible}次请求，无自动重试。',flush=True)
    rows=[]
    for case in cases:
        q=questions[case['question_id']]; rule=diagnose(q,case['choice'])['concept']
        started=time.monotonic()
        ai=helper.analyze(q,case['choice'],case['reason'],concepts) if args.ai else {'status':'not_run'}
        combined=ai['concept'] if ai['status']=='ok' else rule
        baseline=recommend(q,questions,[],rule,limit=2)
        adapted=recommend(q,questions,[],rule,limit=2,ai=ai)
        rows.append({**case,'rule_recommendations':[r['question']['id'] for r in baseline],
                     'ai_recommendations':[{'id':r['question']['id'],'reason':r['reason'],'strategy':r['strategy']} for r in adapted],
                     'human_review':{'knowledge_correct':None,'quote_supports_diagnosis':None,'feedback_helpful':None,'recommendation_relevant':None,'reviewer':None,'notes':None},'latency_seconds':round(time.monotonic()-started,4),'rule':rule,'ai':ai,'combined':combined,
                     'rule_match':rule==case['expected'],'combined_match':combined==case['expected']})
    result={'dataset':str(args.dataset.resolve()),
            'dataset_sha256':hashlib.sha256(args.dataset.read_bytes()).hexdigest(),
            'dataset_note':'内置数据为12条模拟理由，未经独立教育复核；外部数据的来源与盲评记录须另附。',
            'model':helper.model if args.ai else None,'provider':helper.provider if args.ai else None,
            'prompt_version':PROMPT_VERSION,'eligible_count':eligible,'count':len(rows),
            'rule_agreement':sum(r['rule_match'] for r in rows)/len(rows),
            'combined_agreement':sum(r['combined_match'] for r in rows)/len(rows) if args.ai else None,
            'ai_valid_count':sum(r['ai']['status']=='ok' for r in rows),
            'feedback_valid_count':sum(r['ai'].get('feedback',{}).get('status')=='ok' for r in rows),
            'ai_valid_rate_eligible':sum(r['ai']['status']=='ok' for r in rows)/eligible if args.ai and eligible else None,
            'improved_ids':[r['id'] for r in rows if not r['rule_match'] and r['combined_match']] if args.ai else [],
            'regressed_ids':[r['id'] for r in rows if r['rule_match'] and not r['combined_match']] if args.ai else [],
            'recommendation_changed_count':sum(r['rule_recommendations']!=[v['id'] for v in r['ai_recommendations']] for r in rows),
            'token_usage':{k:sum(r['ai'].get('usage',{}).get(k,0) for r in rows) for k in ('prompt_tokens','completion_tokens','total_tokens')},
            'usage_reported_count':sum(bool(r['ai'].get('usage')) for r in rows),
            'human_review_status':'未完成；格式通过不能证明诊断或讲解正确',
            'ai_status_counts':dict(Counter(r['ai']['status'] for r in rows)),
            'rule_macro_f1':macro_f1(rows,'rule'),
            'combined_macro_f1':macro_f1(rows,'combined') if args.ai else None,
            'warning':'此结果仅为模拟标签一致率，不代表真实诊断准确率或学习成绩提升。', 'cases':rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'规则与模拟标签一致率：{result["rule_agreement"]:.1%}')
    print(f'AI 有效结果：{result["ai_valid_count"]}/{len(rows)}' if args.ai else 'AI 未运行；未生成 AI 效果结论。')
    if args.ai:
        print(f'组合方案标签一致率：{result["combined_agreement"]:.1%}；宏F1：{result["combined_macro_f1"]:.3f}')
        print(f'讲解格式与依据检查通过：{result["feedback_valid_count"]}/{eligible}；推荐题号变化：{result["recommendation_changed_count"]}例')
    print('报告：'+str(args.output.resolve()))

if __name__=='__main__': main()
