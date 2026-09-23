class Portfolio:
    def __init__(self): self.positions=[]
    def add(self,symbol,qty,price): self.positions.append({'symbol':symbol,'qty':qty,'price':price})
