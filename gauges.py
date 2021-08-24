
import sys
import subprocess
import json


def export(fn, csv):
  f = open(fn, "w")
  f.write(csv)
  f.close()


call = lambda c: subprocess.run(c, capture_output=True)
node = "--node=tcp://192.168.1.42:26657"


get_prop = lambda n: json.loads(call(["osmosisd","query","gov","proposal",n,node,"--output=json"]).stdout)["content"]["records"]

to_csv = lambda l: "\n".join([x["gauge_id"]+", "+x["weight"] for x in l])


props = [2,6,9,15,18]

gauges_hist = [("2021-06-19T00:00:00", {})]

for p in props:
  pj = json.loads(call(["osmosisd", "query", "gov", "proposal", str(p), node, "--output=json"]).stdout)
  dt = pj["voting_end_time"]
  upd = {x["gauge_id"] : x["weight"] for x in pj["content"]["records"]}
  cur = gauges_hist[-1][1].copy()
  cur.update(upd)
  gauges_hist.append((dt, cur))


seq = list(reversed(gauges_hist))
gids = seq[0][1].keys()

csv = "\n".join([",".join(["Gauge ID"]+[s[0] for s in seq])] + [", ".join([gid] + [s[1].get(gid,"0") for s in seq]) for gid in gids])




if __name__ == "__main__":
  prop_id = sys.argv[1]
  export("gauges.csv", to_csv(get_prop(prop_id)))
  export("gauge_history.csv", csv)