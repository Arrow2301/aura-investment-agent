def calculate_aura_score(
    technical,
    fundamental,
    quality,
    risk,
    regime=None,
    valuation=None
):

    technical_score = technical.get("score", 0)
    fundamental_score = fundamental.get("score", 0)
    quality_score = quality.get("score", 0)
    risk_score = risk.get("score", 0)

    regime_score = 50
    valuation_score = 50

    if regime:
        regime_score = regime.get("score", 50)

    if valuation:
        valuation_score = valuation.get("score", 50)


    aura_score = (
        technical_score * 0.25 +
        fundamental_score * 0.25 +
        quality_score * 0.20 +
        risk_score * 0.15 +
        regime_score * 0.10 +
        valuation_score * 0.05
    )


    # A high composite score cannot turn an objectively unattractive setup into
    # a buy candidate. Risk levels are observations, not targets to manipulate.
    risk_eligible = risk.get("eligible", True)

    if aura_score >= 80 and risk_eligible:
        action = "BUY_CANDIDATE"

    elif aura_score >= 65:
        action = "WATCH"

    else:
        action = "AVOID"


    return {

        "aura_score": round(aura_score, 2),

        "action": action,

        "confidence": round(aura_score),

        "components": {
            "technical": technical_score,
            "fundamental": fundamental_score,
            "quality": quality_score,
            "risk": risk_score,
            "regime": regime_score,
            "valuation": valuation_score
        },
        "risk_eligible": risk_eligible
    }
