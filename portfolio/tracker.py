class Portfolio:
    def __init__(self,cash=100000):
        self.cash=cash
        self.positions={}

    def buy(self,symbol,qty):
        self.positions[symbol]=qty
