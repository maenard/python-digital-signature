from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import NameOID
from datetime import datetime
import json

def validate_pkcs12_password(p12_data, password):
    try:
        # Attempt to load the PKCS#12 file with the provided password
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(p12_data, password.encode(), default_backend())

        # Password is correct
        return {
            'private_key': private_key,
            'certificate': certificate,
            'additional_certificates': additional_certificates
        }  
    except Exception as e:
        return False  # Password is incorrect or another error occurred


def extract_name_attributes(name):
    attributes = {
        'CN': None,
        'OU': None,
        'O': None,
        'L': None,
        'ST': None,
        'C': None
    }

    for oid, attr_name in [(NameOID.COMMON_NAME, 'CN'),
                           (NameOID.ORGANIZATIONAL_UNIT_NAME, 'OU'),
                           (NameOID.ORGANIZATION_NAME, 'O'),
                           (NameOID.LOCALITY_NAME, 'L'),
                           (NameOID.STATE_OR_PROVINCE_NAME, 'ST'),
                           (NameOID.COUNTRY_NAME, 'C')]:
        attrs = name.get_attributes_for_oid(oid)
        if attrs:
            attributes[attr_name] = attrs[0].value

    return attributes

def extract_information(pkcs12_content):
    if not pkcs12_content:
        return "Invalid password or error occurred"

    private_key = pkcs12_content['private_key']
    certificate = pkcs12_content['certificate']
    additional_certificates = pkcs12_content['additional_certificates']

    info = {}

    # Extract information from private key
    if private_key:
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        info['private_key'] = private_key_pem

    # Extract information from certificate
    if certificate:
        cert_info = {
            'subject': extract_name_attributes(certificate.subject),
            'issuer': extract_name_attributes(certificate.issuer),
            'serial_number': certificate.serial_number,
            'not_valid_before': certificate.not_valid_before_utc,
            'not_valid_after': certificate.not_valid_after_utc,
            'certificate_pem': certificate.public_bytes(encoding=serialization.Encoding.PEM).decode()
        }
        info['certificate'] = cert_info

    # Extract information from additional certificates
    if additional_certificates:
        additional_cert_info = []
        for cert in additional_certificates:
            additional_cert_info.append({
                'subject': extract_name_attributes(cert.subject),
                'issuer': extract_name_attributes(cert.issuer),
                'serial_number': cert.serial_number,
                'not_valid_before': cert.not_valid_before_utc,
                'not_valid_after': cert.not_valid_after_utc
            })
        info['additional_certificates'] = additional_cert_info

    return info

# Define a custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)

p12_file_path = './test-files/maenard.p12'
password = 'password'

# Read the PKCS#12 file
with open(p12_file_path, 'rb') as p12_file:
    p12_data = p12_file.read()

content = validate_pkcs12_password(p12_data, password)
info = extract_information(content)
print(json.dumps({"success": True, "data": info}, indent=4, cls=DateTimeEncoder))
