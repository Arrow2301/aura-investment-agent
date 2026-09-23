class PaperTrader:

    def __init__(self, capital=1000000):
        self.cash = capital
        self.positions = {}

    def buy(self, symbol, qty, price):
        cost = qty * price
        if cost <= self.cash:
            self.cash -= cost
            self.positions[symbol] = {
                "quantity": qty,
                "entry": price
            }

    def summary(self):
        return {
            "cash": self.cash,
            "positions": self.positions
        }
