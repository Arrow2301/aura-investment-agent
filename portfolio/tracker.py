class Portfolio:
    def __init__(self,cash=100000):
        self.cash=cash
        self.positions={}

    def add(self,symbol,qty):
        self.positions[symbol]=qty
