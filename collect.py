import subprocess
import json

def export(fn, csv):
  f = open(fn, "w")
  f.write(csv)
  f.close()

node = "--node=tcp://192.168.1.42:26657"
query = ["osmosisd","query"]

get_height = lambda: int(json.loads(call(["osmosisd", "status", node]).stderr)["SyncInfo"]["latest_block_height"])

call = lambda c: subprocess.run(c, capture_output=True)

do_fees = lambda: export("fees.csv", "\n".join([x["id"] + ", " + x["poolParams"]["swapFee"] for x in json.loads(call(query+["gamm","pools", node, "--output=json"]).stdout)["pools"]]))

do_total_staked = lambda: export("staked.csv", json.loads(call(query+["staking","pool",node, "--output=json"]).stdout)["bonded_tokens"])

get_unclaimed = lambda h: json.loads(call(["osmosisd","query","claim","module-account-balance",node,"--height="+str(h), "--output=json"]).stdout)["moduleAccountBalance"][0]["amount"]

# do_unclaimed = lambda: export("unclaimed.csv", "\n".join([str(h) + ","+get_unclaimed(h) for h in range(1000, get_height(), 1000)]))

get_staked = lambda h: json.loads(call(query+["staking", "pool", node, "--output=json", "--height="+str(h)]).stdout)["bonded_tokens"]

get_total = lambda h: json.loads(call(query+["bank", "total", node, "--denom=uosmo", "--height="+str(h), "--output=json"]).stdout)["amount"]

do_staked_over_time = lambda: export("staked_over_time.csv", "\n".join([str(h) + "," + get_staked(h) + "," +get_total(h) + "," + get_unclaimed(h) for h in range(1000,get_height(),1000)]))

#future:
#   trades
#   pool weightings
#   staking/lp incenive shares
#   ibc flows

if __name__ == "__main__":
  print("fees")
  do_fees()
  print("total staked")
  do_total_staked()
  print("stake over time")
  do_staked_over_time()
  # print("unclaimed over time")
  # do_unclaimed()

