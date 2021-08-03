#!/usr/bin/env python

import os
from argparse import ArgumentParser
import json
from typing import List, Tuple
from bscscan import BscScan

API_KEY="hardcoded is bad"
API_KEY=os.getenv("BSCSCAN_API_KEY", API_KEY)

def get_contract_source_code(contract_address: str) -> List[Tuple]:
    bsc = BscScan(API_KEY)
    ret = []
    result = bsc.get_contract_source_code(contract_address)
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
        if file_path[0] == '/':
            # remove leading slash if any
            file_path = file_path[1:]
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


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--contract", help="Contract address", required=True)
    parser.add_argument("--output", help="Output directory", required=True)
    args = parser.parse_args()
    contract_codes = get_contract_source_code(args.contract)
    #print(contract_codes)
    ret = write_contract_source_code(contract_codes, args.output)
    print(f"{ret} contract files are saved")


