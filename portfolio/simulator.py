class PaperPortfolio:
    def __init__(self, capital=100000):
        self.cash=capital
        self.positions={}
        self.history=[]

    def buy(self,symbol,quantity,price):
        self.positions[symbol]={
            "quantity":quantity,
            "entry":price
        }
        self.history.append({"action":"BUY","symbol":symbol})
