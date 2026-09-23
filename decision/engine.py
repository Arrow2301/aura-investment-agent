def decide(t,f,s):
    total=(t+f+s)/3
    action='AVOID'
    if total>=75:
        action='BUY_CANDIDATE'
    elif total>=50:
        action='WATCH'
    return {
        'score':total,
        'action':action
    }
