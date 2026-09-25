"""Deterministic long-only average-cost journal calculations."""
from collections import defaultdict


def summarize(rows):
    state = defaultdict(lambda: {'quantity': 0.0, 'cost': 0.0, 'realized_pnl': 0.0,
                                 'closed_exits': 0, 'winning_exits': 0, 'lots': []})
    for row in sorted(rows, key=lambda x: (x['traded_at'], x.get('id', 0))):
        item = state[row['symbol']]
        quantity, price = float(row['quantity']), float(row['price'])
        if quantity <= 0 or price <= 0:
            raise ValueError('Quantity and price must be positive')
        if row['side'] == 'BUY':
            item['cost'] += quantity * price
            item['quantity'] += quantity
            item['lots'].append({'quantity': quantity, 'stop': row.get('stop_price'),
                                 'target': row.get('target_price')})
        elif row['side'] == 'SELL':
            if quantity > item['quantity'] + 1e-9:
                raise ValueError(f"Sale exceeds open quantity for {row['symbol']}")
            average = item['cost'] / item['quantity']
            pnl = quantity * (price - average)
            item['realized_pnl'] += pnl
            item['closed_exits'] += 1
            item['winning_exits'] += int(pnl > 0)
            remaining = quantity
            while remaining > 1e-9:
                lot = item['lots'][0]
                consumed = min(remaining, lot['quantity'])
                lot['quantity'] -= consumed
                remaining -= consumed
                if lot['quantity'] < 1e-9:
                    item['lots'].pop(0)
            item['quantity'] -= quantity
            item['cost'] = item['quantity'] * average if item['quantity'] > 1e-9 else 0.0
        else:
            raise ValueError('Unknown side')
    for item in state.values():
        stops = [float(l['stop']) for l in item['lots'] if l['stop'] is not None]
        targets = [float(l['target']) for l in item['lots'] if l['target'] is not None]
        item['stop'] = max(stops) if stops else None
        item['target'] = min(targets) if targets else None
    return dict(state)
