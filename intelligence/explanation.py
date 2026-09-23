def explain(data):
    return [k for k,v in data.items() if isinstance(v,(int,float)) and v>70]
