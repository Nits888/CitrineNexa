import json
import os
import ssl
import socket
from datetime import datetime

from globals import env, RESULTS_FILE


def fetch_cert_details(domain):
    """
    Fetch SSL certificate details for a domain.

    :param domain: The domain to fetch the certificate for.
    :return: A dictionary with certificate details.
    """
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=domain)
    conn.connect((domain, 443))
    cert = conn.getpeercert()

    return cert


def determine_expiry(cert):
    """
    Determine the expiry of a certificate.

    :param cert: The certificate details.
    :return: The expiry date of the certificate.
    """
    expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
    return expiry_date


def generate_rag_status(expiry_date):
    """
    Generate RAG status based on certificate expiry date.

    :param expiry_date: The expiry date of the certificate.
    :return: RAG status (Red, Amber, Green).
    """
    today = datetime.today()
    days_to_expiry = (expiry_date - today).days

    if days_to_expiry <= 10:
        return "Red"
    elif days_to_expiry <= 30:
        return "Amber"
    else:
        return "Green"


def main():
    config_path = os.path.join('../config', env, 'endpoints_config.json')
    with open(config_path, 'r') as file:
        config = json.load(file)

    certificates_data = {}  # Initialize as an empty dictionary

    for entry in config['endpoints']:
        app_name = entry['app_name']
        endpoint = entry['url']
        domain = endpoint.split("//")[-1]
        cert = fetch_cert_details(domain)
        expiry_date = determine_expiry(cert)
        rag_status = generate_rag_status(expiry_date)

        if app_name not in certificates_data:
            certificates_data[app_name] = {}

        certificates_data[app_name][endpoint] = {
            "issuer": cert['issuer'],
            "expiry_date": expiry_date.strftime('%Y-%m-%d'),
            "RAG_status": rag_status
        }

    with open(RESULTS_FILE, 'w') as file:
        json.dump(certificates_data, file, indent=4)


if __name__ == "__main__":
    main()