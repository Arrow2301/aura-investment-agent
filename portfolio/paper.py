class Portfolio:

    def __init__(self,capital):
        self.cash=capital
        self.positions={}

    def buy(self,symbol,qty,price):
        self.positions[symbol]={
            "qty":qty,
            "price":price
        }
