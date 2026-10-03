"""维护者使用：生成固定题库。应用不执行本脚本或学生代码。"""
import json
from pathlib import Path

GROUPS = [
('条件判断','boundary','比较运算的等号边界','逐一检查 <、<=、>、>= 是否包含相等情况。',[
('x = 5\nprint(x > 5)', ['False','True','5'],0,'5 不大于 5，严格大于不包含相等。'),
('score = 60\nprint(score >= 60)', ['False','True','60'],1,'大于等于包含相等，因此结果是 True。')]),
('条件判断','branches','if / elif 分支互斥','在同一条 if / elif / else 链中，最多执行一个分支。',[
('x = 8\nif x > 5:\n    print("A")\nelif x > 3:\n    print("B")',['A\nB','B','A'],2,'第一个条件成立，后续 elif 不再执行。'),
('n = 12\nif n > 10:\n    print("大")\nelif n > 0:\n    print("正")\nelse:\n    print("其他")',['大','大\n正','正'],0,'n > 10 已成立，只输出“大”。')]),
('条件判断','and_or','and 与 or 的条件要求','布尔表达式中，and 要求两边都真，or 只要求至少一边为真。',[
('age = 15\nprint(age >= 18 and age <= 60)',['True','False','15'],1,'左侧条件为 False，and 的结果为 False。'),
('rain = False\ncold = True\nprint(rain or cold)',['False','True','None'],1,'cold 为 True，两个布尔值的 or 结果为 True。')]),
('条件判断','truthiness','空容器与非空字符串的真假','空字符串、空列表为假；非空字符串即使是 "0" 也为真。',[
('items = []\nif items:\n    print("有")\nelse:\n    print("无")',['有','[]','无'],2,'空列表在条件中为假，因此进入 else。'),
('text = "0"\nif text:\n    print("真")\nelse:\n    print("假")',['真','假','0'],0,'"0" 是非空字符串，在条件中为真。')]),
('条件判断','independent_if','独立 if 与分支链的区别','多个独立的 if 会分别判断，不具有 elif 的互斥性。',[
('x = 4\nif x > 0:\n    print("A")\nif x < 10:\n    print("B")',['A','A\nB','B'],1,'两个独立条件都成立，依次输出 A 和 B。'),
('n = 6\nif n % 2 == 0:\n    print("偶")\nif n % 3 == 0:\n    print("三")',['偶','三','偶\n三'],2,'6 同时能被 2 和 3 整除，两个 if 都执行。')]),
('循环','range_end','range 的结束边界','range 包含起点，不包含终点。',[
('for i in range(1, 4):\n    print(i)',['1\n2\n3','1\n2\n3\n4','0\n1\n2\n3'],0,'range(1, 4) 依次生成 1、2、3，不包含 4。'),
('for n in range(2, 5):\n    print(n)',['2\n3\n4\n5','2\n3\n4','0\n1\n2\n3\n4'],1,'起点为 2，终点 5 不包含在序列中。')]),
('循环','range_step','range 的步长','从起点开始，每次加上步长，在越过边界前停止。',[
('print(list(range(1, 7, 2)))',['[1, 2, 3, 4, 5, 6]','[1, 3, 5, 7]','[1, 3, 5]'],2,'从 1 开始每次加 2，7 是不包含的终点。'),
('print(list(range(6, 0, -2)))',['[6, 4, 2]','[6, 4, 2, 0]','[]'],0,'步长为 -2，生成 6、4、2，终点 0 不包含。')]),
('循环','accumulate','循环中的累加','跟踪变量每轮的旧值与新值，累加不会自动重置。',[
('total = 0\nfor n in range(1, 4):\n    total += n\nprint(total)',['3','6','10'],1,'total 依次为 1、3、6，循环结束后打印 6。'),
('total = 2\nfor n in [2, 4]:\n    total += n\nprint(total)',['6','4','8'],2,'初值 2，加 2 得 4，再加 4 得 8。')]),
('循环','break_continue','break 与 continue','break 退出当前循环；continue 跳过本轮剩余语句。',[
('for n in range(1, 4):\n    if n == 2:\n        break\n    print(n)',['1','1\n3','1\n2\n3'],0,'n 为 2 时 break 终止整个循环，仅打印过 1。'),
('for n in range(1, 4):\n    if n == 2:\n        continue\n    print(n)',['1','1\n3','1\n2\n3'],1,'n 为 2 时跳过 print，下一轮仍会打印 3。')]),
('循环','while_check','while 在每轮前检查条件','先判断条件，再执行循环体；初次条件为假时执行零次。',[
('n = 3\nwhile n < 3:\n    print(n)\n    n += 1\nprint("结束")',['3\n结束','无输出','结束'],2,'初始 3 < 3 为假，不进入循环，只打印“结束”。'),
('n = 1\nwhile n < 3:\n    print(n)\n    n += 1',['1\n2','1\n2\n3','2\n3'],0,'依次打印 1、2；n 变为 3 后不再进入循环。')]),
('函数与返回值','print_return','print 不等于 return','print 显示内容；没有 return 的函数默认返回 None。',[
('def f():\n    print(3)\nx = f()\nprint(x)',['3\n3','3\nNone','None'],1,'函数先打印 3，隐式返回 None，再打印 x 得到 None。'),
('def greet():\n    print("Hi")\nprint(greet())',['Hi','Hi\nHi','Hi\nNone'],2,'调用 greet 先打印 Hi，其返回值 None 随后被外层 print 打印。')]),
('函数与返回值','return_exit','return 立即结束函数','执行 return 后，函数中该次调用的后续语句不再执行。',[
('def f():\n    return 2\n    print(9)\nprint(f())',['2','9\n2','2\n9'],0,'return 2 立即结束函数，不执行 print(9)。'),
('def f(n):\n    if n > 0:\n        return "正"\n    return "其他"\nprint(f(1))',['正\n其他','正','其他'],1,'第一个 return 已结束调用，第二个 return 不执行。')]),
('函数与返回值','arguments','位置参数与传参','位置参数按调用顺序绑定，注意减法等运算的顺序。',[
('def sub(a, b):\n    return a - b\nprint(sub(2, 5))',['3','7','-3'],2,'a 绑定 2，b 绑定 5，2 - 5 = -3。'),
('def join(a, b):\n    return a + "-" + b\nprint(join("B", "A"))',['B-A','A-B','AB'],0,'a 为 B，b 为 A，连接后的字符串是 B-A。')]),
('函数与返回值','local_scope','局部变量与外部变量','函数内普通赋值创建局部绑定，不会改写同名外部变量。',[
('x = 10\ndef f():\n    x = 2\n    return x\nprint(f())\nprint(x)',['2\n2','2\n10','10\n10'],1,'函数内部 x 为 2，外部 x 保持 10。'),
('name = "外"\ndef f():\n    name = "内"\n    return name\nprint(f())\nprint(name)',['内\n内','外\n外','内\n外'],2,'局部 name 为“内”，外部 name 仍为“外”。')]),
('函数与返回值','missing_return','分支未执行 return 时返回 None','只有实际执行到的 return 决定返回值；走完函数仍无 return 则返回 None。',[
('def f(n):\n    if n > 0:\n        return n\nprint(f(0))',['None','0','False'],0,'0 > 0 为假，没有执行 return，默认返回 None。'),
('def check(n):\n    if n % 2 == 0:\n        return "偶"\nprint(check(3))',['奇','None','3'],1,'3 为奇数，条件不成立，没有显式返回值，因此返回 None。')]),
]

design = json.loads((Path(__file__).parent / 'learning_design.json').read_text(encoding='utf-8'))
bank=[]
concepts={}
for topic,cid,label,hint,rows in GROUPS:
    concepts[cid]={'topic':topic,'label':label,'hint':hint, 'order':len(concepts), 'prerequisites':design[cid]['prerequisites']}
    for i,(code,choices,answer,explanation) in enumerate(rows,1):
        options=dict(zip('ABC',choices))
        bank.append({'id':f'{cid}_{i}','topic':topic,'concept':cid,'difficulty':1 if i==1 else 2,
          'prompt':'下面代码的完整输出是什么？','code':code,'options':options,
          'answer':'ABC'[answer],'explanation':explanation,'hint':hint,
          'hints':[design[cid]['prompt'],hint],
          'misconceptions':{key:{'concept':cid,'evidence':f'你选择的输出为「{value.replace(chr(10), " / ")}」，与此处的执行规则不一致。'} for key,value in options.items() if key!='ABC'[answer]},
          'review_status':'答案经自动执行核验；概念标签待团队人工复核'})
root=Path(__file__).parent
(root/'questions.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'concepts.json').write_text(json.dumps(concepts,ensure_ascii=False,indent=2),encoding='utf-8')
