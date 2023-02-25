import datetime, logging, sys, time, json, hashlib, os, glob
import sync
import requests

from block import Block
from peerConfig import *
import utils

import apscheduler
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler(standalone=True)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def mine_for_block(chain=None, rounds=STANDARD_ROUNDS, start_nonce=0, timestamp=None):
    if not chain:
        chain = sync.sync_local()
    prev_block = chain.most_recent_block()
    return mine_from_prev_block(prev_block, rounds=rounds, start_nonce=start_nonce, timestamp=timestamp)


def mine_from_prev_block(prev_block, rounds=STANDARD_ROUNDS, start_nonce=0, timestamp=None):
    new_block = utils.create_new_block_from_prev(prev_block=prev_block, timestamp=timestamp)
    return mine_block(new_block, rounds=rounds, start_nonce=start_nonce)


def mine_block(new_block, rounds=STANDARD_ROUNDS, start_nonce=0):
    print("Mining for block %s. start_nonce: %s, rounds: %s" % (new_block.index, start_nonce, rounds))
    nonce_range = [i + start_nonce for i in range(rounds)]
    for nonce in nonce_range:
        new_block.nonce = nonce
        new_block.update_self_hash()
        if str(new_block.hash[0:NUM_ZEROS]) == '0' * NUM_ZEROS:
            print("block %s mined. Nonce: %s" % (new_block.index, new_block.nonce))
            assert new_block.is_valid()
            return new_block
    return None


def mine_for_block_listener(event):
    if event.job_id == 'mining':
        new_block, rounds, start_nonce, timestamp = event.retval
        if new_block:
            print("Mined a new block")
            new_block.self_save()
            broadcast_mined_block(new_block)
            sched.add_job(mine_from_prev_block, args=[new_block], kwargs={'rounds': STANDARD_ROUNDS, 'start_nonce': 0},
                          id='mining')
        else:
            print(event.retval)
            sched.add_job(mine_for_block,
                          kwargs={'rounds': rounds, 'start_nonce': start_nonce + rounds, 'timestamp': timestamp},
                          id='mining')
            sched.print_jobs()


def broadcast_mined_block(new_block):
    block_info_dict = new_block.__dict__
    for peer in PEERS:
        endpoint = "%s%s" % (peer[0], peer[1])
        try:
            r = requests.post(peer + 'mined', json=block_info_dict)
        except requests.exceptions.ConnectionError:
            print("Peer %s not connected" % peer)
            continue
    return True


def validate_possible_block(block: Block):
    possible_block = Block(block)
    if possible_block.is_valid():
        possible_block.self_save()
        sched.print_jobs()
        try:
            sched.remove_job('mining')
            print("removed running mine job in validating possible block")
        except apscheduler.jobstores.base.JobLookupError:
            print("mining job didn't exist when validating possible block")

        print("readding mine for block validating_possible_block")
        print(sched)
        print(sched.get_jobs())
        sched.add_job(mine_for_block, kwargs={'rounds': STANDARD_ROUNDS, 'start_nonce': 0},
                      id='mining')
        print(sched.get_jobs())
    else:
        return False

