class PortfolioManager:

    def __init__(self, capital=1000000):
        self.cash = capital
        self.positions = {}

    def open_position(self, symbol, qty, price):
        self.positions[symbol] = {
            "quantity": qty,
            "entry": price
        }
