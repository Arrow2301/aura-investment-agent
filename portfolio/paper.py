class PaperPortfolio:

    def __init__(self, capital):
        self.cash = capital
        self.positions = {}

    def buy(self, symbol, qty, price):
        self.positions[symbol] = {
            "quantity": qty,
            "entry": price
        }
