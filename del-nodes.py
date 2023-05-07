from time import sleep
from asyncio import run
from json import loads, dump
from sys import argv
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.rpc.types import TokenAccountOpts
from solana.rpc.core import RPCException
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.memo.instructions import MemoParams, create_memo
from spl.memo.constants import MEMO_PROGRAM_ID
from pathlib import Path

compare_to_file = argv[1]
_WALLET = PublicKey('zzz')

async def main():
    nodes_compare = []

    with open(compare_to_file, 'r') as compare_to:
        line = compare_to.readline()
        while line:
            if line.startswith('['):
                nodes_compare = line
            line = compare_to.readline()

    nodes_compare = loads(nodes_compare)
    print(f'initial node count: {len(nodes_compare)} \n')

    for i, node in enumerate(nodes_compare):
        client = AsyncClient(endpoint=node, timeout=1)
        try:
            balance = (await client.get_balance(_WALLET)).value
            if balance == 0:
                nodes_compare.pop(i)
                print(f'{node} \t improper balance: {balance} \t deleted'.expandtabs(16))
                continue
        except Exception as e:
            nodes_compare.pop(i)
            print(f'{node} \t failed to connect \t deleted'.expandtabs(16))
            continue
        await client.close()

    print(f'\nnode count after balance check: {len(nodes_compare)} \n')
    sleep(10)

    for i, node in enumerate(nodes_compare):
        client = AsyncClient(endpoint=node, timeout=1)
        try:
            token_count = len((await client.get_token_accounts_by_owner(owner=_WALLET, opts=TokenAccountOpts(program_id=TOKEN_PROGRAM_ID, encoding="base64"))).value)
            if token_count == 0:
                nodes_compare.pop(i)
                print(f'{node} \t improper token count ({token_count}) \t deleted'.expandtabs(16))
        except Exception as e:
            nodes_compare.pop(i)
            print(f'{node} \t failed to connect \t deleted'.expandtabs(16))
            continue
        await client.close()

    print(f'\nnode count after token count check: {len(nodes_compare)} \n')
    sleep(10)

    _keypair = Keypair().generate()
    for i, node in enumerate(nodes_compare):
        client = AsyncClient(endpoint=node, timeout=1)
        try:
            tx = Transaction().add(
                create_memo(
                    MemoParams(
                        program_id=MEMO_PROGRAM_ID,
                        message=bytes('test', encoding='utf8'),
                        signer=_keypair.public_key
                    )
                )
            )
            await client.send_transaction(tx, _keypair)
        except RPCException as rpcErr:
            print(f'{node} sent a tx. tx message {rpcErr.with_traceback}')
            continue
        except Exception as err:
            print(f'{node} did not send a tx. err: {err}')
            nodes_compare.pop(i)
            continue
        await client.close()

    print(f'\nnode count after tx check: {len(nodes_compare)} \n')

    nodes_compare = list(set(nodes_compare))
    
    file_name = compare_to_file.split('/')
    cleaned_up_nodes = Path(f'./cleaned_up_nodes/cleaned_up_{file_name[1]}')
    
    with open(cleaned_up_nodes, 'w') as write_working:
        dump(nodes_compare, write_working)


if __name__ == '__main__':
    run(main())