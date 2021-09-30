import sys
import subprocess
import json
import pandas as pd

def export(fn, csv):
  f = open(fn, "w")
  f.write(csv)
  f.close()


call = lambda c: subprocess.run(c, capture_output=True)

pid = 42

voters = {v["voter"] : v["option"] for v in json.loads(call(["osmosisd", "q", "gov", "votes", str(pid), "--output=json", "--limit=5000"]).stdout)["votes"]}

def get_delegations(v):
  try:
    r = call(["osmosisd", "q", "staking", "delegations", v, "--output=json"])
    ds = json.loads(r.stdout)
    return ds["delegation_responses"]
  except:
    return []

delegations = {v : {x["delegation"]["validator_address"] : int(x["balance"]["amount"]) for x in get_delegations(v)} for v in voters}

convert_valoper = lambda valoper: call(["osmosisd", "debug", "bech32-convert", valoper, "--prefix=osmo"]).stderr.decode("utf-8").strip()

validators = {convert_valoper(v["operator_address"]) : int(v["tokens"]) for v in json.loads(call(["osmosisd", "q", "staking", "validators", "--output=json"]).stdout)["validators"]}

get_data = lambda v: [v,True if v in validators else False, sum(delegations[v].values()), validators[v] - sum([delegations[d].get(v,0) for d in delegations]) if v in validators else 0, voters[v]]

export("participation.csv", "\n".join([",".join([str(x) for x in get_data(v)]) for v in voters]))

#shares
#delegators vote share including self bond
#validators voting on behalf of delegators

# per validator, get their total voting power
# 3 values
# self bond, direct voting delegators, indirect voting for delegators

#then we can compare across validators and total

# address, is_validator, direct vote, indirect vote, vote option
