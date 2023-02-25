import os

from Certificate import certificateModel, Certificate
from peerConfig import *
import utils
import sync
import argparse

data: certificateModel = {
    "name": 'First Block',
    "parentName": "None",
    "registeredNumber": "None",
    "issuedDate": "01/01/1970",
    "stream": "None",
    "degree": "None",
    "institution": "None"
}


def mine_first_block():
    first_block = utils.create_new_block_from_prev(prev_block=None, data=Certificate(data))
    first_block.update_self_hash()
    while str(first_block.hash[0:NUM_ZEROS]) != '0' * NUM_ZEROS:
        first_block.nonce += 1
        first_block.update_self_hash()
    assert first_block.is_valid()
    return first_block


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generating Blockchain')
    parser.add_argument('--first', '-f', dest='first', default=False, action='store_true',
                        help='generate the first node ourselves')
    parser.add_argument('--port', '-p', default='5000',
                        help='what port we will run the node on')
    args = parser.parse_args()

    if not os.path.exists(CHAINDATA_DIR):
        os.mkdir(CHAINDATA_DIR)

    if args.first:
        if not os.listdir(CHAINDATA_DIR):
            first_block = mine_first_block()
            first_block.self_save()
            filename = "%s/data.txt" % CHAINDATA_DIR
            with open(filename, 'w') as data_file:
                data_file.write('Block mined by node on port %s' % args.port)
        else:
            print("Chaindata directory already has files. If you want to generate a first block, delete files and rerun")
    else:
        sync.sync(save=True)
