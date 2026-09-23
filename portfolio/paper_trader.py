class PaperPortfolio:
    def __init__(self):
        self.positions={}

    def buy(self,symbol,qty):
        self.positions[symbol]=qty

    def snapshot(self):
        return self.positions
