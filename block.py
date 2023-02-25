import hashlib
import os
import json
import datetime as date
from Certificate import Certificate, certificateModel
import utils
from peerConfig import *


class Block(object):
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if key in BLOCK_VAR_CONVERSIONS:
                setattr(self, key, BLOCK_VAR_CONVERSIONS[key](value))
            else:
                setattr(self, key, value)
        if not hasattr(self, 'hash'):
            self.hash = self.update_self_hash()

        if not hasattr(self, 'nonce'):
            self.nonce = 'None'
        if not hasattr(self, 'hash'):
            self.hash = self.update_self_hash()

    def header_string(self):
        return str(self.index) + self.prev_hash + str(self.data) + str(self.timestamp) + str(self.nonce)

    def generate_header(index, prev_hash, data, timestamp, nonce):
        return str(index) + prev_hash + data + str(timestamp) + str(nonce)

    def update_self_hash(self):
        sha = hashlib.sha512()
        sha.update(self.header_string().encode())
        new_hash = sha.hexdigest()
        self.hash = new_hash
        return new_hash

    def self_save(self):
        index_string = str(self.index).zfill(4)
        filename = '%s%s.json' % (CHAINDATA_DIR, index_string)
        with open(filename, 'w') as block_file:
            json.dump(self.to_dict(), block_file)

    def to_dict(self):
        info = {}
        info['index'] = str(self.index)
        info['timestamp'] = str(self.timestamp)
        info['prev_hash'] = str(self.prev_hash)
        info['hash'] = str(self.hash)
        try:
            info['data'] = json.loads(str(self.data))
        except:
            info['data'] = self.data
        info['nonce'] = str(self.nonce)
        return info

    def is_valid(self):
        possible_hash = self.get_hash()
        self.update_self_hash()
        if str(self.hash[0:NUM_ZEROS]) == '0' * NUM_ZEROS and self.get_hash() == possible_hash:
            return True
        else:
            return False

    def get_index(self):
        return self.index

    def get_hash(self):
        return self.hash

    def get_data(self):
        return self.data

    def __repr__(self):
        return "Block<index: %s>, <hash: %s>" % (self.index, self.hash)

    def __eq__(self, other):
        return (self.index == other.index and
                self.timestamp == other.timestamp and
                self.prev_hash == other.prev_hash and
                self.hash == other.hash and
                self.data == other.data and
                self.nonce == other.nonce)

    def __ne__(self, other):
        return not self.__eq__(other)