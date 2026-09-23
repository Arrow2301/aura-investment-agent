def score(features):
    total=sum(features.values())/len(features)
    action='BUY_CANDIDATE' if total>=75 else 'WATCH' if total>=50 else 'AVOID'
    return {'score':total,'action':action}
