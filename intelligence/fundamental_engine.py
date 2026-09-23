def analyze(info):
    score=50; signals=[]
    if info.get('roe',0)>0.15: score+=20; signals.append('Strong ROE')
    if info.get('profit_margin',0)>0.10: score+=15; signals.append('Good margins')
    if info.get('debt_equity',999)<100: score+=10
    return {'score':min(score,100),'signals':signals}
