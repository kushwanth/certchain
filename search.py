import argparse
import meilisearch
import json, sync, utils, sys
from datetime import datetime
from flask import Flask, jsonify, request, Response
from flask_cors import CORS


search = Flask(__name__)
search.config['UPLOAD_EXTENSIONS'] = ['.png']
search.config['UPLOAD_PATH'] = '/tmp'
CORS(search)

client = meilisearch.Client('http://127.0.0.1:7700', 'BYheyhZOBbwQDy8octZ3Lyn_xpmieamMNNPni3VmTqY')
index = client.index('chain')
block_data = list()
local_chain = sync.sync_local()
file_path = "/tmp/cert.pdf"
index.update_searchable_attributes(['name','registeredNumber','issuedDate','stream','degree','institution'])

def generate_documents(blocks):
    try:
        block_data.clear()
        index.delete_all_documents()
        for block in blocks:
            temp = block['data']
            temp['id'] = block['hash']
            del temp['parentName']
            dt = datetime.strptime(temp['issuedDate'], "%d/%m/%Y")
            temp['issuedDate'] = dt.year
            block_data.append(temp)
        index.add_documents(block_data)
        return True
    except Exception as e:
        print(e)
        return False


@search.route('/refresh', methods=['GET'])
def refresh_data():
    local_chain = sync.sync_local()
    if local_chain.is_valid() is False:
        return jsonify(message='Chain is Invalid')
    blocks = local_chain.block_list_dict()
    if generate_documents(blocks) is False:
        return jsonify(message="failed")
    return jsonify(message="success")


@search.route('/validate', methods=['POST'])
def validate():
    request_file = request.files['file']
    if request_file.filename == '':
        return jsonify(message='upload a file')
    request_file.save(file_path)
    pdf_data = utils.validate_pdf(file_path)
    if pdf_data is False:
        return jsonify(message='Please Upload a Signed Certificate')
    pdf_hash = pdf_data.get('data').get('hash')
    block = local_chain.find_block_by_hash(pdf_hash)
    check_data = utils.check_data(pdf_data.get('data'), block.get_data())
    pdf_data['valid'] = check_data
    return Response(json.dumps(pdf_data), content_type="application/json")


@search.route('/search/<hash>', methods=['GET'])
def get_block(hash):
    if len(hash)!=128:
        return jsonify(message="Invalid Hash")
    local_chain = sync.sync_local()
    block = local_chain.find_block_by_hash(hash=hash)
    if block is False:
        return jsonify(message="Invalid Hash")
    return Response(json.dumps({"hash": hash, "data":block.get_data()}),  content_type="application/json")

@search.route('/search', methods=['POST'])
def search_data():
    local_chain = sync.sync_local()
    search_term = request.get_json()
    search_res = index.search(search_term['query'])
    return Response(json.dumps(search_res), content_type="application/json")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', default='5000')
    args = parser.parse_args()
    search.run(host='127.0.0.1', port=args.port, debug=True)

