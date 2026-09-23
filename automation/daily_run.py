from intelligence.scoring import calculate
from intelligence.explainer import explain

def run():
    features={
        "technical":70,
        "momentum":65,
        "quality":60,
        "risk":75,
        "regime":65
    }

    result=calculate(features)

    print(result)
    print(explain(features))

if __name__=="__main__":
    run()
