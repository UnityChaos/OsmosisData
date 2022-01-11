import subprocess
import json


def export(fn, csv):
  f = open(fn, "w")
  f.write(csv)
  f.close()

node = "--node=tcp://127.0.0.1:26657"
query = ["osmosisd","query"]

get_height = lambda: int(json.loads(call(["osmosisd", "status", node]).stderr)["SyncInfo"]["latest_block_height"])

call = lambda c: subprocess.run(c, capture_output=True)

