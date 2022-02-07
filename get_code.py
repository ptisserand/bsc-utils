#!/usr/bin/env python

import os
from argparse import ArgumentParser
import json
from typing import List, Tuple
from dotenv import load_dotenv
import requests
from bscscan import BscScan

BSC="bsc"
FANTOM="ftm"
class Snowtrace(object):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_contract_source_code(self, address) -> List[Tuple]:
        ret = []
        url = f'https://api.snowtrace.io/api?module=contract&action=getsourcecode&address={address}&apikey={self.api_key}'
        resp = requests.get(url)
        if not resp.ok:
            return []
        result = resp.json()['result']
        for ee in result:
            raw_data = ee.get('SourceCode', '{}')
            sources = json.loads(raw_data)
            for kk in sources:
                ret.append((kk, sources[kk]['content']))
        return ret

class Binance(object):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.bsc = BscScan(api_key)
    
    def get_contract_source_code(self, address) -> List[Tuple]:
        ret = []
        result = self.bsc.get_contract_source_code(address)
        for ee in result:
            # I don't know why bscscan returned value with 2 { }
            raw_data = ee.get('SourceCode', '{{}}')
            if raw_data[0] == '{':
                data = json.loads(raw_data[1:-1])
                sources = data.get('sources', {})
                for kk in sources:
                    ret.append((kk, sources[kk]['content']))
            else:
                ret.append(("contract.sol", raw_data))
        return ret


def write_contract_source_code(contract_source_code: List[Tuple], output_directory: str) -> int:
    count = 0
    full_output_directory = os.path.realpath(output_directory)
    print(full_output_directory)

    for elem in contract_source_code:
        file_path = elem[0]
        content = elem[1]
        print(file_path)
        while file_path[0] == '/':
            # remove leading slash if any
            file_path = file_path[1:]
        # if a path is absolute in os.path.join it wins...
        # >>> os.path.join('a', 'b', '/tmp/c')
        # '/tmp/c'
        file_path = os.path.join(full_output_directory, file_path)
        full_path = os.path.realpath(file_path)
        if not full_path.startswith(full_output_directory):
            print("File path outside of failed: skipped")
            print(f"{full_path} {full_output_directory}")
            continue
        file_dir = os.path.dirname(full_path)
        os.makedirs(file_dir, exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)
        count += 1
    return count

def get_explorer(blockchain: str):
    if blockchain == BSC:
        api_key = os.getenv('BSCSCAN_API_KEY')
        return Binance(api_key)
    if blockchain == FANTOM:
        api_key = os.getenv('SNOWTRACE_API_KEY')
        return Snowtrace(api_key)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    parser = ArgumentParser()
    parser.add_argument("--contract", help="Contract address", required=True)
    parser.add_argument("--output", help="Output directory", required=True)
    parser.add_argument("--blockchain", default=BSC, nargs="?", choices=[BSC, FANTOM])
    args = parser.parse_args()
    explorer = get_explorer(args.blockchain)
    contract_codes = explorer.get_contract_source_code(args.contract)
    #print(contract_codes)
    ret = write_contract_source_code(contract_codes, args.output)
    print(f"{ret} contract files are saved")


