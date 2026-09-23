from intelligence.scoring import calculate

def run():
    result = calculate(
        technical=70,
        momentum=60,
        risk=80,
        regime=60,
        quality=70
    )

    print(result)

if __name__ == "__main__":
    run()
