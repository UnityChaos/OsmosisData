import json
import urllib.request

#Free alpha for anyone who knows how to run "osmosisd export &> state.json"

j = json.load(open("state.json"))

locks = j["app_state"]["lockup"]["locks"]

denoms = list(set([x["coins"][0]["denom"] for x in locks if x["coins"][0]["denom"].startswith("gamm/pool/")]))

denom_to_pid = lambda denom: int(denom.split("/")[-1])

pids = [denom_to_pid(x) for x in denoms]

pool_total = {denom : int(j["app_state"]["gamm"]["pools"][denom_to_pid(denom)-1]["totalShares"]["amount"]) for denom in denoms}

factor = {denom_to_pid(denom) : {dur/86400: sum([int(x["coins"][0]["amount"]) for x in locks if x["coins"][0]["denom"] == denom and float(x["duration"][:-1])>=dur])/pool_total[denom] for dur in [86400,604800,1209600]} for denom in denoms}

get_aprs = lambda x: {d : max([float(y["apr_"+str(d)+"d"]) for y in x["apr_list"]]) for d in [1,7,14]}

ui_aprs = {x["pool_id"] : get_aprs(x) for x in json.loads(urllib.request.urlopen(urllib.request.Request("https://api-osmosis.imperator.co/apr/v1/all")).read().decode('utf-8'))}

real_aprs = {pid : {d : ui_aprs[pid][d]/factor[pid][d] for d in [1,7,14]} for pid in ui_aprs.keys()}

def export(fn, csv):
  f = open(fn, "w")
  f.write(csv)
  f.close()

export("real_apr.csv","\n".join([str(p)+","+",".join([str(real_aprs[p][d]) for d in [1.0,7.0,14.0]]) for p in ui_aprs.keys()]))

gauges = j["app_state"]["incentives"]["gauges"]

external = [",".join([g["coins"][0]["amount"],g["coins"][0]["denom"],g["distribute_to"]["denom"],g["distribute_to"]["duration"],g["filled_epochs"],g["id"],g["num_epochs_paid_over"],g["start_time"]]) for g in gauges if g["is_perpetual"]==False]



export("external_gauges.csv","\n".join(external))