def calculate_aura_score(
    technical,
    fundamental,
    quality,
    risk
):

    technical_score = technical.get(
        "score",
        0
    )

    fundamental_score = fundamental.get(
        "score",
        0
    )

    quality_score = quality.get(
        "score",
        0
    )

    risk_score = risk.get(
        "score",
        0
    )


    aura_score = (
        technical_score * 0.25 +
        fundamental_score * 0.25 +
        quality_score * 0.20 +
        risk_score * 0.15 +
        50 * 0.10 +
        50 * 0.05
    )


    if aura_score >= 80:
        action = "BUY_CANDIDATE"

    elif aura_score >= 65:
        action = "WATCH"

    else:
        action = "AVOID"


    confidence = min(
        round(aura_score),
        95
    )


    return {

        "aura_score": round(
            aura_score,
            2
        ),

        "action": action,

        "confidence": confidence,

        "components": {

            "technical": technical_score,

            "fundamental": fundamental_score,

            "quality": quality_score,

            "risk": risk_score

        }
    }def calculate(technical,fundamental,quality,risk,regime,valuation):
    score=technical*.25+fundamental*.25+quality*.20+risk*.15+regime*.10+valuation*.05
    return {'score':round(score,2),'action':'BUY_CANDIDATE' if score>=75 else 'WATCH','confidence':round(score,2)}
