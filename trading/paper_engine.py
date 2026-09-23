class PaperPortfolio:
    def __init__(self, capital=1000000):
        self.cash=capital
        self.positions={}

    def buy(self,symbol,qty,price):
        self.positions[symbol]=(qty,price)
