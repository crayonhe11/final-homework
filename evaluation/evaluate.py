"""独立诊断比较；默认只评估规则，--ai 才调用已配置的本地模型。"""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from edu.bank import load_bank
from edu.engine import diagnose
from edu.ai import AIHelper


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--ai',action='store_true')
    parser.add_argument('--output',type=Path,default=Path(__file__).parent/'results.json')
    args=parser.parse_args()
    questions,concepts=load_bank(); helper=AIHelper()
    if args.ai and not helper.model: parser.error('请先设置 EDU_OLLAMA_MODEL 为本地已安装模型名。')
    cases=json.loads((Path(__file__).parent/'heldout.json').read_text(encoding='utf-8'))
    rows=[]
    for case in cases:
        q=questions[case['question_id']]; rule=diagnose(q,case['choice'])['concept']
        ai=helper.analyze(q,case['choice'],case['reason'],concepts) if args.ai else {'status':'not_run'}
        combined=ai['concept'] if ai['status']=='ok' else rule
        rows.append({**case,'rule':rule,'ai':ai,'combined':combined,
                     'rule_match':rule==case['expected'],'combined_match':combined==case['expected']})
    result={'dataset':'12 条模拟学生理由，开发完成后运行；标签未经独立教育专家验证。',
            'model':helper.model if args.ai else None,'count':len(rows),
            'rule_agreement':sum(r['rule_match'] for r in rows)/len(rows),
            'combined_agreement':sum(r['combined_match'] for r in rows)/len(rows) if args.ai else None,
            'ai_valid_count':sum(r['ai']['status']=='ok' for r in rows),
            'warning':'此结果仅为模拟标签一致率，不代表真实诊断准确率或学习成绩提升。', 'cases':rows}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'规则与模拟标签一致率：{result["rule_agreement"]:.1%}')
    print(f'AI 有效结果：{result["ai_valid_count"]}/{len(rows)}' if args.ai else 'AI 未运行；未生成 AI 效果结论。')
    print('报告：'+str(args.output.resolve()))

if __name__=='__main__': main()
