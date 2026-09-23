class Memory:

    def __init__(self):
        self.records=[]

    def store(self,prediction,result):
        self.records.append({
            "prediction":prediction,
            "result":result
        })

    def accuracy(self):
        if not self.records:
            return 0

        return sum(
            1 for x in self.records
            if x["prediction"]==x["result"]
        )/len(self.records)
