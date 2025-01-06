import frappe
from frappe.model.document import Document
from frappe.core.doctype.docfield.docfield import DocField

def create_doctype(name, fields):
    """
    Creates a DocType with the given name and fields.
    """
    # Create DocType
    doctype = frappe.new_doc("DocType")
    doctype.name = name
    doctype.module = "WalaOne Integration"
    doctype.issingle = 0
    doctype.custom = 1
    doctype.fields = []
    
    # Add fields to the doctype
    for field in fields:
        field_doc = frappe.get_doc({
            "doctype": "DocField",
            "fieldname": field['fieldname'],
            "fieldtype": field['fieldtype'],
            "label": field['label'],
            "mandatory": field.get('mandatory', 0)
        })
        doctype.append("fields", field_doc)

    doctype.save()
    frappe.db.commit()
    print(f"DocType '{name}' created successfully.")

def create_walaone_settings():
    """
    Creates the 'WalaOne Settings' DocType.
    """
    fields = [
        {'fieldname': 'domain', 'fieldtype': 'Data', 'label': 'API Domain'},
        {'fieldname': 'client_code', 'fieldtype': 'Data', 'label': 'Client Code'},
        {'fieldname': 'private_key', 'fieldtype': 'Text', 'label': 'Private Key'},
        {'fieldname': 'timestamp', 'fieldtype': 'Data', 'label': 'Timestamp'}
    ]
    create_doctype("WalaOne Settings", fields)

def create_transaction_doctype():
    """
    Creates the 'Transaction' DocType for handling transactions.
    """
    fields = [
        {'fieldname': 'transaction_type', 'fieldtype': 'Data', 'label': 'Transaction Type'},
        {'fieldname': 'amount', 'fieldtype': 'Currency', 'label': 'Amount'},
        {'fieldname': 'status', 'fieldtype': 'Select', 'label': 'Status', 'options': 'Pending\nCompleted\nFailed'},
        {'fieldname': 'reference_id', 'fieldtype': 'Data', 'label': 'Reference ID'},
        {'fieldname': 'timestamp', 'fieldtype': 'Data', 'label': 'Timestamp'}
    ]
    create_doctype("Transaction", fields)

def create_doctypes():
    """
    Create all required DocTypes.
    """
    create_walaone_settings()
    create_transaction_doctype()
    print("\nAll DocTypes have been created.")



# Create 'WalaOne Settings' DocType (Single)
def create_walaone_settings():
    if not frappe.db.exists("DocType", "WalaOne Settings"):
        doctype_settings = frappe.get_doc({
            "doctype": "DocType",
            "module": "WalaOne Integration",
            "name": "WalaOne Settings",
            "is_single": 1,  # Set the doctype as Single
            "fields": [
                {"fieldname": "domain", "fieldtype": "Data", "label": "API Domain"},
                {"fieldname": "client_code", "fieldtype": "Data", "label": "Client Code"},
                {"fieldname": "private_key", "fieldtype": "Text", "label": "Private Key"},
                {"fieldname": "timestamp", "fieldtype": "Data", "label": "Timestamp"},
            ],
        })
        doctype_settings.insert()

        frappe.db.commit()
        print("WalaOne Settings DocType created successfully.")
    else:
        print("WalaOne Settings DocType already exists.")