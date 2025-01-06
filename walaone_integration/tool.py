import frappe
from frappe.model.document import Document
import hashlib
import base64
import subprocess
import time



def test():
    doc = frappe.get_doc("WalaOne Transaction","WalaOne-11-8141")
    doc.sign_transaction()