
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


if __name__ == "__main__":
  prop_id = sys.argv[1]
  export("gauges.csv", to_csv(get_prop(prop_id)))