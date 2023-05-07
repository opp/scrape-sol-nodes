from requests import post
from json import loads
from sys import argv


node_file = argv[1]


def main():
    nodes_compare = []

    with open(node_file, 'r') as compare_to:
        line = compare_to.readline()
        while line:
            if line.startswith('['):
                nodes_compare = line
            line = compare_to.readline()

    nodes_compare = loads(nodes_compare)
    
    for i, node in enumerate(nodes_compare, start=1):
        try:
            res = post(node, timeout=1)
            print(f'pinged: rpc # {i} \t {node} \t {int(res.elapsed.total_seconds() * 100)}ms')
        except Exception as e:
            continue

main()