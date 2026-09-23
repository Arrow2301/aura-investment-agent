def validate(data):
    if data is None:
        return False

    if len(data) < 50:
        return False

    return True
