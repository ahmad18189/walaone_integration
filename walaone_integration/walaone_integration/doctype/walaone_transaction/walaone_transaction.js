frappe.ui.form.on('WalaOne Transaction', {
    refresh: function(frm) {
        // Add the Sign Transaction button
        frm.add_custom_button(__('Sign Transaction'), function() {
            if (!frm.doc.phone || !frm.doc.amount || !frm.doc.reference_id) {
                frappe.msgprint(__('Please fill in the required fields.'));
                return;
            }

            frappe.call({
                method: 'sign_transaction',
                doc: frm.doc,
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('authorization', r.message);
                        frappe.msgprint(__('Transaction signed successfully.'));
                    } else {
                        frappe.msgprint(__('Error in signing the transaction.'));
                    }
                }
            });
        });
    }
});
