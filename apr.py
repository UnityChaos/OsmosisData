import json
import urllib.request
import subprocess

j = json.load(open("state.json"))

locks = j["app_state"]["lockup"]["locks"]

denoms = list(set([x["coins"][0]["denom"] for x in locks if x["coins"][0]["denom"].startswith("gamm/pool/")]))

denom_to_pid = lambda denom: int(denom.split("/")[-1])

pids = [denom_to_pid(x) for x in denoms]

pool_total = {denom : int(j["app_state"]["gamm"]["pools"][denom_to_pid(denom)-1]["totalShares"]["amount"]) for denom in denoms}

factor = {denom_to_pid(denom) : {dur/86400: sum([int(x["coins"][0]["amount"]) for x in locks if x["coins"][0]["denom"] == denom and float(x["duration"][:-1])>=dur])/pool_total[denom] for du>

get_aprs = lambda x: {d : sum([float(y["apr_"+str(d)+"d"]) for y in x["apr_list"]]) for d in [1,7,14]}

ui_aprs = {x["pool_id"] : get_aprs(x) for x in json.loads(urllib.request.urlopen(urllib.request.Request("https://api-osmosis.imperator.co/apr/v1/all")).read().decode('utf-8'))}

nom_apr = {}
for pid in ui_aprs.keys():
  b = {}
  b[1] = ui_aprs[pid][1]/factor[pid][1]
  b[7] = b[1] + (ui_aprs[pid][7]-ui_aprs[pid][1])/factor[pid][7]
  b[14] = b[7] + (ui_aprs[pid][14]-ui_aprs[pid][7])/factor[pid][14]
  nom_apr[pid] = b

def export(fn, csv):
  f = open(fn, "w")
  f.write(csv)
  f.close()

export("nom_apr.csv","\n".join([str(p)+","+",".join([str(nom_apr[p][d]) for d in [1.0,7.0,14.0]]) for p in ui_aprs.keys()]))

