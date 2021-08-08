import subprocess
import json


def export(fn, csv):
  f = open(fn, "w")
  f.write(csv)
  f.close()

call = lambda c: subprocess.run(c, capture_output=True)

node = "--node=tcp://192.168.1.42:26657"
output = "--output=json"
query = ["osmosisd","query"]

prop_id = "19"

depositors = lambda: [x["depositor"] for x in json.loads(call(query+["gov","deposits", prop_id, node, output]).stdout)["deposits"]]

addr_to_oper = lambda addr: call(["osmosisd","debug","bech32-convert","--prefix=osmovaloper", addr]).stderr.strip().decode("utf-8")

dep_vals = [addr_to_oper(x) for x in depositors()]

is_active = lambda x: x["jailed"]==False and x["status"]=="BOND_STATUS_BONDED"

all_vals = lambda: json.loads(call(query+["staking","validators", node, output, "--limit=200"]).stdout)["validators"]

active_vals = lambda: [x for x in all_vals() if is_active(x)]

did_deposit = lambda v: v["operator_address"] in dep_vals

op_addrs = lambda: [v["operator_address"] for v in active_vals()]

data = lambda: [", ".join([x["description"]["moniker"], x["tokens"], x["tokens"] if did_deposit(x) else "0"]) for x in active_vals()]


if __name__ == "__main__":
  export("fork_ready.csv", "\n".join(data()))