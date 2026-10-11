"""原创故事练习，借鉴 Exercism 的规格/骨架/测试分离方式，不复制题目。"""
import json
from pathlib import Path

TASKS = [
 dict(id='star_gate',topic='条件判断',concepts=['boundary','and_or','branches'],title='星港通行证',
 story='你是星港入口的程序员。飞船需要能量和通行证才能进入补给港。请帮门卫机器人作出决定。',
 objective='先检查能量：低于20返回 "充能"；否则有通行证返回 "放行"，没有则返回 "等待"。',
 function='gate_status',params=['energy','has_badge'],starter='def gate_status(energy, has_badge):\n    # 函数外壳已准备好，只需在这里写条件判断\n    pass\n',
 hints=['先处理能量不足的情况，再考虑通行证。','使用 if / elif / else，并用 return 返回文字。不要只 print。'],
 tests=[([10,True],'充能'),([20,True],'放行'),([20,False],'等待'),([0,False],'充能'),([19,True],'充能'),([80,False],'等待'),([100,True],'放行')],
 solution='def gate_status(energy, has_badge):\n    if energy < 20:\n        return "充能"\n    if has_badge:\n        return "放行"\n    return "等待"\n'),
 dict(id='forest_tickets',topic='条件判断',concepts=['boundary','branches'],title='森林列车售票员',
 story='精灵列车准备发车！售票机需要根据旅客年龄与会员身份算出车票价格。',
 objective='年龄小于6岁免费；6到17岁票价8；18岁及以上票价15。会员在非免费票价基础上减3。输入年龄为非负整数，member为布尔值。',
 function='ticket_price',params=['age','member'],starter='def ticket_price(age, member):\n    # 返回整数票价\n    pass\n',
 hints=['先按年龄确定基本票价，注意6岁和18岁的边界。','免费票保持0；只有非免费且是会员时才减3。'],
 tests=[([5,False],0),([6,False],8),([17,True],5),([18,False],15),([30,True],12),([0,True],0),([6,True],5),([18,True],12)],
 solution='def ticket_price(age, member):\n    if age < 6:\n        return 0\n    if age < 18:\n        price = 8\n    else:\n        price = 15\n    if member:\n        price -= 3\n    return price\n'),
 dict(id='robot_coins',topic='循环',concepts=['accumulate','break_continue'],title='探险机器人的金币袋',
 story='机器人在遗迹中拾取宝物。扫描器给出一串整数：正数是金币，零是空格，负数是陷阱。',
 objective='遍历 coins，把所有正数加起来，忽略零和负数，返回总金币数。空列表返回0。',
 function='collect_coins',params=['coins'],starter='def collect_coins(coins):\n    total = 0\n    # 在这里遍历并收集金币\n    return total\n',
 hints=['把累加器放在循环外初始化。','每轮判断 coin > 0，只在成立时更新 total。'],
 tests=[([[2,-3,0,5]],7),([[]],0),([[-4,-1]],0),([[1,1,1]],3),([[0,10,-10,20]],30),([[9]],9)],
 solution='def collect_coins(coins):\n    total = 0\n    for coin in coins:\n        if coin > 0:\n            total += coin\n    return total\n'),
 dict(id='rocket_countdown',topic='循环',concepts=['range_step','while_check','range_end'],title='火箭发射倒计时',
 story='发射台需要一个倒计时序列，播报机器人会按你返回的列表读出每个数字。',
 objective='输入非负整数 start，返回从 start 到 1 的递减列表，不包含0；start为0时返回空列表。可以使用range或while。',
 function='countdown',params=['start'],starter='def countdown(start):\n    numbers = []\n    # 用 numbers.append(数字) 添加每个倒计时数\n    return numbers\n',
 hints=['每轮减少1；停止时不把0放入结果。','range(start, 0, -1) 可以描述这段倒计时。'],
 tests=[([3],[3,2,1]),([0],[]),([1],[1]),([5],[5,4,3,2,1]),([2],[2,1]),([8],[8,7,6,5,4,3,2,1])],
 solution='def countdown(start):\n    numbers = []\n    for n in range(start, 0, -1):\n        numbers.append(n)\n    return numbers\n'),
 dict(id='moon_cafe',topic='函数与返回值',concepts=['arguments','print_return','return_exit'],title='月球咖啡馆结账',
 story='月球咖啡馆要把结账结果传给收银屏幕。打印金额还不够，收银机需要拿到函数返回的数字。',
 objective='返回 quantity * unit_price - coupon 的结果；金额不能为负，若计算结果小于0返回0。输入均为非负整数。',
 function='checkout',params=['quantity','unit_price','coupon'],starter='def checkout(quantity, unit_price, coupon):\n    # 计算金额并返回，不能只打印\n    pass\n',
 hints=['按顺序把三个参数代入表达式。','计算后检查是否小于0，两个路径都要返回值。'],
 tests=[([2,12,5],19),([0,12,5],0),([1,5,10],0),([3,10,0],30),([1,10,10],0),([2,0,0],0)],
 solution='def checkout(quantity, unit_price, coupon):\n    amount = quantity * unit_price - coupon\n    if amount < 0:\n        return 0\n    return amount\n'),
 dict(id='parcel_bot',topic='函数与返回值',concepts=['missing_return','branches','arguments'],title='云朵快递分拣站',
 story='快递机器人必须为每个包裹给出明确路线，不能让任何包裹因为缺少返回值而消失。',
 objective='weight是非负整数。fragile为真时总是返回 "轻放"；否则weight大于5返回 "货运"，其余返回 "普通"。',
 function='route_parcel',params=['weight','fragile'],starter='def route_parcel(weight, fragile):\n    # 每条执行路径都需要返回路线文字\n    pass\n',
 hints=['易碎条件优先于重量条件。','注意重量等于5时走哪条路径，并为最后一种情况写return。'],
 tests=[([2,True],'轻放'),([8,True],'轻放'),([6,False],'货运'),([5,False],'普通'),([0,False],'普通'),([20,False],'货运')],
 solution='def route_parcel(weight, fragile):\n    if fragile:\n        return "轻放"\n    if weight > 5:\n        return "货运"\n    return "普通"\n')
]
root=Path(__file__).parent
for task in TASKS:
    task['tests']=[{'args':args,'expected':expected} for args,expected in task['tests']]
    task['review_status']='原创初稿；程序参考解已核验，教育内容待团队复核'
(root/'coding_tasks.json').write_text(json.dumps(TASKS,ensure_ascii=False,indent=2),encoding='utf-8')
