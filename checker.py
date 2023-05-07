from types import NoneType
import json
import requests


cluster_nodes = "getClusterNodes0.json"
nodes_list = "nodes0.txt"


def get_rpc():
    with open(cluster_nodes, "r") as cn:
        n = json.load(cn)

    with open(nodes_list, "w") as w:
        w.write("")

    l = len(n["result"])

    for i in range(l):
        rpc = n["result"][i]["rpc"]
        if type(rpc) != NoneType:
            try:
                result = session.get("http://"+rpc, timeout=2)
            except Exception:
                print(f"({i}/{l}) \t {rpc} \t Timed out.")
            else:
                if result.status_code == 405 or "POST" in result.text:
                    with open(nodes_list, "a") as w:
                        w.write("http://"+rpc+"\n")


if __name__ == "__main__":
    session = requests.Session()
    get_rpc()
