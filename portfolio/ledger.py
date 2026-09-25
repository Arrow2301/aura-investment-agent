"""Deterministic long-only average-cost journal calculations."""
from collections import defaultdict


def summarize(rows):
    state = defaultdict(lambda: {'quantity': 0.0, 'cost': 0.0, 'realized_pnl': 0.0})
    for row in sorted(rows, key=lambda x: (x['traded_at'], x.get('id', 0))):
        item = state[row['symbol']]
        quantity, price = float(row['quantity']), float(row['price'])
        if quantity <= 0 or price <= 0:
            raise ValueError('Quantity and price must be positive')
        if row['side'] == 'BUY':
            item['cost'] += quantity * price
            item['quantity'] += quantity
        elif row['side'] == 'SELL':
            if quantity > item['quantity'] + 1e-9:
                raise ValueError(f"Sale exceeds open quantity for {row['symbol']}")
            average = item['cost'] / item['quantity']
            item['realized_pnl'] += quantity * (price - average)
            item['quantity'] -= quantity
            item['cost'] = item['quantity'] * average if item['quantity'] > 1e-9 else 0.0
        else:
            raise ValueError('Unknown side')
    return dict(state)
