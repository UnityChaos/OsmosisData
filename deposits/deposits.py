
import requests
import pandas as pd
import functools

api = lambda pid, start, end: "https://api-osmosis.imperator.co/tokens/v1/count/"+pid+"?range_start="+start+"&range_stop="+end


DAYS_SINCE_LAUNCH = 75


def load(url):
  try:
    df = pd.read_json(url)
  except:
    df = pd.DataFrame()
  return df


def multi_query(pid, step_size, nsteps):
  df = functools.reduce(lambda x,y: x.append(y), reversed([load(api(pid, str(i+1)+step_size, str(i)+step_size)) for i in range(nsteps)]))
  df.index = pd.DatetimeIndex(df['time'])
  return df



def get_counts(pid):
  r = multi_query(pid, "d", DAYS_SINCE_LAUNCH).drop(labels="time", axis=1).groupby(pd.Grouper(freq='360min')).first()
  f = open("Pool "+pid+".csv", "w")
  f.write(r.to_csv())
  f.close()  
  return r

if __name__ == "__main__":
  [get_counts(str(pid)) for pid in [1,2,3,4,5,6,7,8,9,10,13,15,22,42,183,197]]