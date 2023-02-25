from peerConfig import *
import datetime,io, re, json
import block, fitz 
from pyhanko.sign import signers
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from oscrypto import keys
from pyhanko_certvalidator import ValidationContext
from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign.validation import validate_pdf_signature
from cryptography import x509

cert_file = open("keys/cert.pem", 'r').readlines()
cert_data = "".join(cert_file)
root_cert = keys.parse_certificate(cert_data.encode())
vc = ValidationContext(trust_roots=[root_cert])
pdf_text_template = "(.*)' '(.*) ' 'Certificate of Completion ' 'This certificate is presented to ' '(.*)' 'with (.*) for passing' '(.*)' '(.*)' 'awarded on (.*)' '(.*)' '"


def is_valid_chain(blockchain):
    for b in blockchain:
        if not b.is_valid():
            return False
    return True

def dict_from_block_attributes(**kwargs):
    info = {}
    for key in kwargs:
        if key in BLOCK_VAR_CONVERSIONS:
            info[key] = BLOCK_VAR_CONVERSIONS[key](kwargs[key])
        else:
            info[key] = kwargs[key]
    return info


def create_new_block_from_prev(prev_block=None, data=None, timestamp=None):
    if not prev_block:
        index = 0
        prev_hash = ''
    else:
        index = int(prev_block.index) + 1
        prev_hash = prev_block.hash

    if not data:
        filename = '%sdata.txt' % (CHAINDATA_DIR)
        with open(filename, 'r') as data_file:
            data = data_file.read()

    if not timestamp:
        timestamp = datetime.datetime.utcnow().strftime('%Y/%m/%d-%H:%M:%S.%f')

    nonce = 0
    block_info_dict = dict_from_block_attributes(index=index, timestamp=timestamp, data=data, prev_hash=prev_hash,
                                                 nonce=nonce)
    new_block = block.Block(block_info_dict)
    return new_block


def find_valid_nonce(find_block, data=None):
    find_block.nonce = 0
    find_block.update_self_hash()
    if not find_block.data:
        find_block.data = data
    while str(find_block.hash[0:NUM_ZEROS]) != '0' * NUM_ZEROS:
        find_block.nonce += 1
        find_block.update_self_hash()
    assert find_block.is_valid()
    return find_block

def validate_string(s):
    words = s.split()
    for word in words:
        if not word.isalpha():
            return False
    return True

def validate_data(data):
    for k,v in data.items():
        if k=="issuedDate":
            date_format = "%d/%m/%Y"
            if datetime.datetime.strptime(v, date_format) is False:
                return False
        elif k =="registeredNumber":
            if v.isalnum() is False:
                return False
        else:
            if (0 < len(v) < 100 and validate_string(v)) is False:
                return False
    return True

def format_data(data):
    formatted_data: certificateModel = {}
    if validate_data(data):
        for k,v in data.items():
            if k=="issuedDate" or k=="registeredNumber":
                formatted_data[k] = v
            else:
                formatted_data[k] = str(v).upper()
        return formatted_data
    else:
        return None

def sign_pdf(pdf_path):
    cms_signer = signers.SimpleSigner.load(key_file='keys/private-key.pem',cert_file='keys/cert.pem')
    pdf_name_path = pdf_path.split(".")
    signed_pdf_path = pdf_name_path[0]+"-signed."+pdf_name_path[1]
    with open(pdf_path, 'rb') as doc:
        w = IncrementalPdfFileWriter(doc)
        out = signers.PdfSigner(
            signers.PdfSignatureMetadata(field_name='BlockSignature'),
            signer=cms_signer,
        ).sign_pdf(w)
        with open(signed_pdf_path, 'wb') as f:
            f.write(out.getbuffer())
            f.close()
        doc.close()

def format_cert_data(sig_cert_data):
    issuer_data = dict()
    for kv in str(sig_cert_data.issuer.human_friendly).split(","):
        temp =kv.split(":")
        issuer_data[temp[0]] = temp[1]
    sig_cert_data_fmt = {
        'issuer': issuer_data,
        'sha1': sig_cert_data.sha1.hex(),
        'publicKey': sig_cert_data.public_key.sha256.hex()
    }
    return sig_cert_data_fmt

def validate_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as doc:
            r = PdfFileReader(doc)
            sig = r.embedded_signatures[0]
            status = validate_pdf_signature(sig, vc)
        sig_cert_data: x509.Certificate = status.signing_cert
        sig_pdf_data_fmt = format_cert_data(sig_cert_data)
        sig_pdf_data_fmt.update({'signingTime':status.signer_reported_dt.isoformat() ,'sigIntact':status.intact,'sigCoverage': str(status.coverage), 'sigValid': status.valid, 'summary': status.summary()})
        sig_pdf_data_fmt['data'] = get_pdf_data(pdf_path)
        return sig_pdf_data_fmt
    except:
        return False

def get_pdf_data(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    text = page.get_text().split('\n')
    pdf_data = dict()
    try:
        institute_index = text.index('Certificate of Completion ')
        temp = ""
        for t in range(institute_index):
            temp += text[t]
            temp +=" "
        pdf_data['institution'] = temp.strip()
        for t in range(institute_index+2,institute_index+8):
            if t== institute_index+2:
                pdf_data['name'] = text[t].strip()
            elif t== institute_index+3:
                m = re.match("with (.*) for passing", text[t])
                pdf_data['registeredNumber'] = m.group(1).strip()
            elif t== institute_index+4:
                pdf_data['stream'] = text[t].strip()
            elif t == institute_index+5:
                pdf_data['degree'] = text[t].strip()
            elif t == institute_index+6:
                m = re.match("awarded on (.*)", text[t])
                pdf_data['issuedDate'] = m.group(1).strip()
            elif t == institute_index+7:
                pdf_data['hash'] = text[t].strip()
            else:
                pass
    except:
        pass
    return pdf_data

def check_data(pdf_data,block_data):
    temp_pdf_data, temp_block_data = pdf_data.copy(), block_data.copy()
    del temp_block_data['parentName']
    del temp_pdf_data['hash']
    return temp_pdf_data==temp_block_data
    

    