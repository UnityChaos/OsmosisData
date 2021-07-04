import subprocess
import json

def export(fn, csv):
  f = open(fn, "w")
  f.write(csv)
  f.close()

node = "--node=tcp://192.168.1.40:26657"
query = ["osmosisd","query"]

call = lambda c: subprocess.run(c, capture_output=True)

do_fees = lambda: export("fees.csv", "\n".join([x["id"] + ", " + x["poolParams"]["swapFee"] for x in json.loads(call(query+["gamm","pools", node, "--output=json"]).stdout)["pools"]]))

do_total_staked = lambda: export("staked.csv", json.loads(call(query+["staking","pool",node, "--output=json"]).stdout)["bonded_tokens"])


#future:
#   trades
#   pool weightings
#   staking/lp incenive shares
#   ibc flows

if __name__ == "__main__":
  do_fees()
  do_total_staked()