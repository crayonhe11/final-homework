"""默认仅检查配置；--live明确触发一次真实诊断请求。"""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from edu.ai import AIHelper
from edu.bank import load_bank


def main():
    p=argparse.ArgumentParser(description='Kimi连接检查；--live最多发起一次付费请求，无重试')
    p.add_argument('--live',action='store_true')
    p.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'runtime/ai-connection.json')
    args=p.parse_args();helper=AIHelper()
    if not helper.model: p.error('未配置模型或密钥；请填写api_config.json后再运行。')
    if not args.live:
        print('配置存在，尚未验证密钥有效性或网络。使用 --live 才会发送一次真实请求。');return
    q,c=load_bank();question=q['range_end_2']
    result=helper.analyze(question,'A','最后那个数5也要打印出来。',c)
    report={'provider':helper.provider,'model':helper.model,'request_limit':1,
            'api_response_received':result.get('response_received',False),
            'diagnosis_format_valid':result['status']=='ok',
            'feedback_format_valid':result.get('feedback',{}).get('status')=='ok',
            'result':result,'warning':'单次请求只验证连接与返回格式，不代表诊断质量合格。'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('连接与诊断返回成功。' if report['diagnosis_format_valid'] else '验证未通过：'+result.get('message','未知错误'))
    print('报告：'+str(args.output.resolve()))
    if not report['diagnosis_format_valid']: raise SystemExit(1)

if __name__=='__main__': main()
