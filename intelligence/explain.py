def explain(features):
    output=[]
    for k,v in features.items():
        if v>=70:
            output.append(k+" positive")
        elif v<40:
            output.append(k+" weak")
    return output
