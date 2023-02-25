import argparse
import json
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request, send_file, render_template, Response
from weasyprint import HTML
import utils
from block import Block
import mine
import sync
from peerConfig import *
from utils import *

app = Flask(__name__)

sync.sync(save=True)

sched = BackgroundScheduler(standalone=True)

@app.route('/certchain', methods=['GET'])
def blockchain():
    local_chain = sync.sync_local()
    blocks = json.dumps(local_chain.block_list_dict())
    return Response(blocks, content_type="application/json")

@app.route('/mined', methods=['POST'])
def mined():
    possible_block= request.get_json()
    mine.validate_possible_block(possible_block)
    return jsonify(received=True)

def render_template_with_data(data,hash):
    return render_template('certificate.html', data=data, hash=hash)


@app.route('/mine', methods=['POST'])
def mine_certficate():
    local_chain = sync.sync_local()
    raw_data = request.get_json()
    data = utils.format_data(raw_data)
    if data is None:
        return jsonify(message='Data is in InValid Format')
    last_added_block = local_chain.most_recent_block()
    if data==last_added_block.get_data():
        return jsonify(message='Duplicate Data')
    gen_cert_block = utils.create_new_block_from_prev(prev_block=last_added_block, data=data)
    new_cert_block = mine.mine_block(gen_cert_block)
    if new_cert_block is None:
        return jsonify(message='Failed to Mine Block')
    local_chain.add_block(new_cert_block)
    mine.broadcast_mined_block(new_cert_block)
    local_chain.self_save()
    template = render_template_with_data(new_cert_block.get_data(), new_cert_block.get_hash())
    certificate = "certificates/"+str(new_cert_block.get_index())+".pdf"
    HTML(string=template).write_pdf(target=certificate)
    utils.sign_pdf(certificate)
    return new_cert_block.get_hash()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Certchain Node')
    parser.add_argument('--port', '-p', default='5000')
    args = parser.parse_args()

    mine.sched = sched
    if args.mine:
        sched.add_job(mine.mine_for_block, kwargs={'rounds': STANDARD_ROUNDS, 'start_nonce': 0},
                      id='mining')
    sched.add_listener(mine.mine_for_block_listener, apscheduler.events.EVENT_JOB_EXECUTED)

    sched.start()

    app.run(host='127.0.0.1', port=args.port, debug=True)
