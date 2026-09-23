def calculate(technical,fundamental,quality,risk,regime,valuation):
    score=(technical*.25+fundamental*.25+quality*.20+risk*.15+regime*.10+valuation*.05)
    return {'score':round(score,2),
            'action':'BUY_CANDIDATE' if score>=75 else 'WATCH' if score>=50 else 'AVOID',
            'confidence':round(score,2)}
