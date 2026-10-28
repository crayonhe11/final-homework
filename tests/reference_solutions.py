"""Repository-owned examples for testing the six original coding exercises."""
SOLUTIONS = {
 'star_gate': "def gate_status(energy, has_badge):\n    if energy < 20: return '充能'\n    if has_badge: return '放行'\n    return '等待'",
 'forest_tickets': "def ticket_price(age, member):\n    if age < 6: return 0\n    price = 8 if age < 18 else 15\n    return price - 3 if member else price",
 'robot_coins': "def collect_coins(coins):\n    total = 0\n    for coin in coins:\n        if coin > 0: total += coin\n    return total",
 'rocket_countdown': "def countdown(start):\n    return list(range(start, 0, -1))",
 'moon_cafe': "def checkout(quantity, unit_price, coupon):\n    return max(0, quantity * unit_price - coupon)",
 'parcel_bot': "def route_parcel(weight, fragile):\n    if fragile: return '轻放'\n    if weight > 5: return '货运'\n    return '普通'",
}
