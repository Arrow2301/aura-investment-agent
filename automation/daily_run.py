from market.universe import SYMBOLS
from market.downloader import download
from intelligence.scorer import score
from core.database import insert

def run():
    for symbol in SYMBOLS:
        data=download(symbol)
        if data is not None and len(data)>200:
            s=score(data)
            insert("stock_analysis", {
                "symbol":symbol,
                "technical_score":s,
                "fundamental_score":0,
                "sentiment_score":0,
                "overall_score":s,
                "action":"WATCH",
                "confidence":50,
                "reason":"Technical scan"
            })
            print(symbol,s)

if __name__=="__main__":
    run()
