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

    existing_cert_details = {}  # Initialize as an empty dictionary

    # Check if the results file already exists
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as result_file:
            existing_cert_details = json.load(result_file)

    for entry in config['endpoints']:
        app_name = entry['app_name']
        endpoint = entry['url']
        domain = endpoint.split("//")[-1]
        cert = fetch_cert_details(domain)
        expiry_date = determine_expiry(cert)
        rag_status = generate_rag_status(expiry_date)

        existing_entry = existing_cert_details.get(app_name, {}).get(endpoint)

        if existing_entry:
            # Update existing entry if there are changes
            if (existing_entry['issuer'] != cert['issuer'] or
                    existing_entry['expiry_date'] != expiry_date.strftime('%Y-%m-%d') or
                    existing_entry['RAG_status'] != rag_status):
                existing_entry.update({
                    "issuer": cert['issuer'],
                    "expiry_date": expiry_date.strftime('%Y-%m-%d'),
                    "RAG_status": rag_status
                })
        else:
            # Create a new entry
            if app_name not in existing_cert_details:
                existing_cert_details[app_name] = {}
            existing_cert_details[app_name][endpoint] = {
                "issuer": cert['issuer'],
                "expiry_date": expiry_date.strftime('%Y-%m-%d'),
                "RAG_status": rag_status
            }

    with open(RESULTS_FILE, 'w') as file:
        json.dump(existing_cert_details, file, indent=4)


if __name__ == "__main__":
    main()
