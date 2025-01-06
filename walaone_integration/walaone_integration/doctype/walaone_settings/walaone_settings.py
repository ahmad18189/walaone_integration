import frappe
from frappe.model.document import Document
import hashlib
import base64
import subprocess
import time
import os
import requests
from frappe import _  # Import the translation function

def get_current_timestamp():
    """Returns the current timestamp as a string."""
    return str(int(time.time()))

class WalaOneSettings(Document):
    @frappe.whitelist()
    def get_loyalty_program_info(self):
        """Fetch loyalty program information from WalaOne API and update amount in the settings."""
        
        # Prepare endpoint and parameters
        endpoint = "/b2b/v1/info"
        params = {
            "language": "en",
            "timestamp": get_current_timestamp()
        }

        # Fetch private key and other details from the settings doctype
        domain = self.domain
        client_code = self.client_code
        private_key = self.private_key

        headers = {
            "Authorization": self.get_authorization_header(endpoint, params),  # Custom method to generate auth header
            "X-ClientCode": client_code,
            "Accept-Language": "en"
        }
        
        url = f"{domain}{endpoint}"
        
        # Make the API request
        response = requests.post(url, headers=headers, data=params)

        if response.status_code == 200:
            response_data = response.json()
            amount = response_data['data'].get('amount', '0.00')
            self.amount = amount  # Update the amount from the response
            self.save()
            frappe.msgprint(_('Loyalty program information fetched successfully.'))
        else:
            frappe.throw(_('Error fetching loyalty program information: ') + response.text)

    def get_authorization_header(self, endpoint, params):
        """Generates the Authorization header for the API request."""
        payload = self.prepare_payload(endpoint, params)
        payload_hash = hashlib.sha256(payload.encode()).hexdigest()
        payload_hash_bytes = bytes.fromhex(payload_hash)

        # Get the path for the private key (d7.pem) located in the site's private folder
        site_path = frappe.get_site_path('private')  # Private folder directory
        private_key_path = os.path.join(site_path, 'd7.pem')

        if not os.path.exists(private_key_path):
            frappe.throw(_('Private key file (d7.pem) is missing in the private folder.'))

        # Ensure the signature directory exists
        signature_dir = os.path.join(site_path, 'walaone')
        os.makedirs(signature_dir, exist_ok=True)  # Create the directory if it doesn't exist

        signature_path = os.path.join(signature_dir, 'signature.bin')

        # Sign the hash using OpenSSL via subprocess
        command = f"echo -n '{payload_hash}' | openssl rsautl -sign -inkey {private_key_path} -out {signature_path} -pkcs"
        subprocess.run(command, shell=True, capture_output=True)

        # Read the signature from the file
        with open(signature_path, 'rb') as f:
            signed_message = f.read()

        # Encode the signature in base64 and return as the authorization header
        return base64.b64encode(signed_message).decode()

    def prepare_payload(self, endpoint, params):
        """Prepare the payload with the necessary parameters."""
        payload = endpoint
        for key, val in sorted(params.items()):
            payload += f"{key}={val}"
        return payload
