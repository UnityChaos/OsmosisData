import subprocess
import json

def export(fn, csv):
  f = open(fn, "w")
  f.write(csv)
  f.close()

node = "--node=tcp://192.168.1.42:26657"
query = ["osmosisd","query"]

call = lambda c: subprocess.run(c, capture_output=True)

do_fees = lambda: export("fees.csv", "\n".join([x["id"] + ", " + x["poolParams"]["swapFee"] for x in json.loads(call(query+["gamm","pools", node, "--output=json"]).stdout)["pools"]]))

do_total_staked = lambda: export("staked.csv", json.loads(call(query+["staking","pool",node, "--output=json"]).stdout)["bonded_tokens"])

def get_unclaimed(h):
  r = call(["osmosisd","query","claim","module-account-balance",node,"--height="+str(h), "--output=json"])
  # print(r)
  return json.loads(r.stdout)["moduleAccountBalance"][0]["amount"]

do_unclaimed = lambda: export("unclaimed.csv", "\n".join([str(h) + ","+get_unclaimed(h) for h in range(1000, 251000, 1000)]))

#future:
#   trades
#   pool weightings
#   staking/lp incenive shares
#   ibc flows

if __name__ == "__main__":
  do_fees()
  do_total_staked()
  # do_unclaimed()

