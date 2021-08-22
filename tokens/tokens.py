
import requests
import pandas as pd

api = lambda pid, rng: "https://api-osmosis.imperator.co/tokens/v1/count/"+pid+"?range="+rng


def get_counts(pid, t1, t2):
  # f = open("Pool "+pid+".csv","w")
  # f.write("Time, "+t1+", "+t2+"\n")

  url = api(pid, "1mo")

  df = pd.read_json(url)
  df.index = pd.DatetimeIndex(df['time'])
  r = df.drop(labels="time", axis=1).groupby(pd.Grouper(freq='360min')).first()

  f = open("Pool "+pid+".csv", "w")
  f.write(r.to_csv())
  f.close()  


  # res = requests.get(url).json()
  # for r in res:
  #   f.write(r["time"]+", "+str(int(r[t1]))+", "+str(int(r[t2]))+"\n")
  # f.close()


# output a csv file for each pool
# row 1 should be time and name of each token
# following rows are the data values for the pool's token liquidity

if __name__ == "__main__":
  get_counts("1", "OSMO", "ATOM")
  get_counts("2", "OSMO", "ION")
  get_counts("3", "OSMO", "AKT")
  get_counts("4", "ATOM", "AKT")
  get_counts("5", "OSMO", "DVPN")
  get_counts("6", "ATOM", "DVPN")
  get_counts("7", "OSMO", "IRIS")
  get_counts("8", "ATOM", "IRIS")
  get_counts("9", "OSMO", "CRO")
  get_counts("10", "ATOM", "CRO")
  get_counts("13", "ATOM", "XPRT")
  get_counts("15", "OSMO", "XPRT")
  get_counts("22", "ATOM", "REGEN")
  get_counts("42", "OSMO", "REGEN")