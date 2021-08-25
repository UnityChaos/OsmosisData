import sys
import subprocess
import json
import pandas as pd

def export(fn, csv):
  f = open(fn, "w")
  f.write(csv)
  f.close()


call = lambda c: subprocess.run(c, capture_output=True)
node = "--node=tcp://192.168.1.42:26657"

props = [2,6,9,15,18]

gauges_hist = [("2021-06-19T00:00:00.000000000Z", {})]

for p in props:
  pj = json.loads(call(["osmosisd", "query", "gov", "proposal", str(p), node, "--output=json"]).stdout)
  dt = pj["voting_end_time"]
  upd = {x["gauge_id"] : x["weight"] for x in pj["content"]["records"]}
  cur = gauges_hist[-1][1].copy()
  cur.update(upd)
  gauges_hist.append((dt, cur))


seq = list(reversed(gauges_hist))
gids = seq[0][1].keys()

df = pd.DataFrame(gauges_hist)
df.index = pd.DatetimeIndex(df[0])

res = df.asfreq("6h",method="pad").drop(labels=0, axis=1)

d = res.to_dict()[1]

csv = "\n".join([", ".join(["time"]+list(gids))] + [", ".join([str(t)]+[d[t].get(gid, "0") for gid in gids]) for t in d.keys()])

export("incentives.csv", csv)


export("gauge_history.csv", "\n".join([",".join(["Gauge ID"]+[s[0] for s in seq])] + [", ".join([gid] + [s[1].get(gid,"0") for s in seq]) for gid in gids]))