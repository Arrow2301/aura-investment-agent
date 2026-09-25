import math


def analyze(info):
    checks = [('roe', lambda x: x > .12, 'ROE above 12%'),
              ('profit_margin', lambda x: x > .08, 'Profit margin above 8%'),
              ('debt_equity', lambda x: 0 <= x < 75, 'Debt/equity below 75%')]
    seen, signals = [], []
    for key, criterion, label in checks:
        value = info.get(key)
        if isinstance(value, (int, float)) and math.isfinite(value):
            passed = criterion(value)
            seen.append(passed)
            if passed:
                signals.append(label)
    return {'score': round(100 * sum(seen) / len(seen)) if seen else 0,
            'signals': signals or ['No quality factor confirmed'],
            'coverage': len(seen), 'valid': bool(seen)}
