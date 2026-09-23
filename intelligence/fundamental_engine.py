def analyze(info):
    score=50; reasons=[]
    roe=info.get('returnOnEquity') or 0
    debt=info.get('debtToEquity') or 999
    growth=info.get('revenueGrowth') or 0
    if roe>0.15: score+=15; reasons.append('Strong ROE')
    if debt<100: score+=10; reasons.append('Controlled debt')
    if growth>0.1: score+=10; reasons.append('Revenue growth')
    return {'score':min(score,100),'signals':reasons}
