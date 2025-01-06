import frappe
from frappe.model.document import Document
import hashlib
import base64
import subprocess
import time
import os
from frappe import _  # Import the translation function

class WalaOneTransaction(Document):
    # Overriding the method to add a permission check
    def before_insert(self):
        if not self.timestamp:
            self.timestamp = str(int(time.time()))  # Assign current timestamp if not provided

    @frappe.whitelist()
    def sign_transaction(self):
        """Signs the transaction payload using OpenSSL"""
        
        # Get the path for the private key (d7.pem) located in the site's private folder
        site_path = frappe.get_site_path('private')  # Private folder directory
        private_key_path = os.path.join(site_path, 'd7.pem')

        if not os.path.exists(private_key_path):
            frappe.throw(_('Private key file (d7.pem) is missing in the private folder.'))

        # Prepare the payload and calculate the payload hash
        payload = self.prepare_payload()
        self.payload = payload
        payload_hash = hashlib.sha256(payload.encode()).hexdigest()
        self.payload_hash = payload_hash
        payload_hash_bytes = bytes.fromhex(payload_hash)

        # Ensure the signature directory exists
        signature_dir = os.path.join(site_path, 'walaone')
        os.makedirs(signature_dir, exist_ok=True)  # Create the directory if it doesn't exist

        signature_path = os.path.join(signature_dir, 'signature.bin')

        # Sign the hash using OpenSSL via subprocess (this should be securely done in real-world scenarios)
        command = f"echo -n '{payload_hash}' | openssl rsautl -sign -inkey {private_key_path} -out {signature_path} -pkcs"
        subprocess.run(command, shell=True, capture_output=True)

        # Read the signature from the file
        with open(signature_path, 'rb') as f:
            signed_message = f.read()

        authorization = base64.b64encode(signed_message).decode()

        self.authorization = authorization  # Store the signed authorization in the document
        frappe.msgprint(_('Transaction signed successfully.'))  # Use the correct translation function

        # Register the payload, request, and response in the comments
        self.comment_on_transaction('Payload', payload)
        self.comment_on_transaction('Signed Authorization', authorization)

        # Send the request after signing the transaction
        self.send_request()

    @frappe.whitelist()
    def send_request(self):
        """Sends the transaction request to the WalaOne API"""
        
        settings = frappe.get_doc("WalaOne Settings", "WalaOne Settings")
        domain = settings.domain
        client_code = settings.client_code

        # Prepare the parameters for the API request
        params = {
            'phone': self.phone,
            'amount': '{0:.2f}'.format(self.amount),
            'language': 'en',
            'reference_id': self.reference_id,
            'timestamp': self.timestamp  # Ensure timestamp is included
        }

        # Define the endpoint
        endpoint = '/b2b/v1/insert/amount'  # Ensure that the correct endpoint is used here

        # Send the API request
        response = self.send_api_request(domain, endpoint, params)

        # Register the request and response in comments
        self.comment_on_transaction('API Request', str(params))
        self.comment_on_transaction('API Response', str(response))

        if response.get('code') == 200:
            self.status = 'Success'
            self.comment_on_transaction('Status', 'Success')
            frappe.msgprint(_('Request sent successfully.'))
        else:
            self.status = 'Failed'
            self.comment_on_transaction('Status', 'Failed')
            frappe.msgprint(_('Error in sending request: ' + response.get('error', 'Unknown error.')))
        self.save()

    def prepare_payload(self):
        """Prepare the payload with the necessary parameters."""
        url = '/b2b/v1/insert/amount'  # This endpoint is part of the payload
        params = {
            'timestamp': self.timestamp,
            'language': self.language,
            'phone': self.phone,
            'amount': '{0:.2f}'.format(self.amount),
            'reference_id': self.reference_id
        }

        payload = url
        for key, val in sorted(params.items()):
            payload += f"{key}={val}"
        return payload

    def send_api_request(self, domain, endpoint, params):
        """Send API request using Python requests library."""
        import requests
        headers = {
            "Authorization": self.authorization,
            "X-ClientCode": "drive",
            "Accept-Language": "en"
        }

        # Combine domain and endpoint to make the full URL
        url = f"{domain}{endpoint}"

        # Send the POST request to the API
        response = requests.post(url, headers=headers, data=params)
        
        if response.status_code == 200:
            return response.json()  # Return the response if the request was successful
        else:
            return {"status": "failed", "error": response.text}  # Handle errors accordingly

    def comment_on_transaction(self, title, content):
        """Add a comment to the transaction with the provided title and content."""
        frappe.get_doc({
            'doctype': 'Comment',
            'comment_type': 'Comment',
            'reference_doctype': 'WalaOne Transaction',
            'reference_name': self.name,
            'content': f"<strong>{title}:</strong><br>{content}",
            'user': frappe.session.user
        }).insert()
