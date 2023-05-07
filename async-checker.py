from types import NoneType
from json import load, dump
from aiohttp import ClientSession
from asyncio import run
from sys import argv


cluster_nodes = argv[1]
nodes_list = argv[2]


async def get_rpc():
    with open(cluster_nodes, 'r') as cn:
        n = load(cn)

    with open(nodes_list, 'w') as w:
        w.write(f'{nodes_list} - rpcs collected from {cluster_nodes}\n\n')

    l = len(n['result'])
    responsive_nodes = []
    
    async with ClientSession() as session:
        for i in range(l):
            rpc = n['result'][i]['rpc']
            if type(rpc) != NoneType:
                rpc_url = 'http://' + rpc
                try:
                    async with session.get(rpc_url, timeout = 1) as rget:
                        if 'POST' in await rget.text():
                            async with session.get(rpc_url + '/health', timeout = 1) as rget2:
                                if 'behind' in await rget2.text() or 'ok' not in await rget2.text():
                                    continue
                                responsive_nodes.append(f'http://{rpc}')
                                await print(f'[{i}/{l}] \t {rpc_url} \t Responded.'.expandtabs(8))
                except Exception:
                    continue
    
    responsive_nodes = list(set(responsive_nodes))
    with open(nodes_list, 'a') as w:
        dump(responsive_nodes, w)


if __name__ == '__main__':
    run(get_rpc())
