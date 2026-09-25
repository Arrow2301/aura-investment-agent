import math


def analyze(info):
    """Score only observed fields; missing vendor data is explicitly unknown."""
    thresholds = {'roe': (.15, 'Strong ROE'), 'profit_margin': (.10, 'Good margins'),
                  'revenue_growth': (.10, 'Revenue growth above 10%')}
    observed, signals = [], []
    for field, (threshold, label) in thresholds.items():
        value = info.get(field)
        if isinstance(value, (int, float)) and math.isfinite(value):
            observed.append(value > threshold)
            if value > threshold:
                signals.append(label)
    debt = info.get('debt_equity')
    if isinstance(debt, (int, float)) and math.isfinite(debt):
        observed.append(0 <= debt < 100)  # Yahoo expresses debt/equity as percent.
        if 0 <= debt < 100:
            signals.append('Debt/equity below 100%')
    return {'score': round(100 * sum(observed) / len(observed)) if observed else 0,
            'signals': signals or ['No positive fundamental factor confirmed'],
            'coverage': len(observed), 'valid': bool(observed)}
