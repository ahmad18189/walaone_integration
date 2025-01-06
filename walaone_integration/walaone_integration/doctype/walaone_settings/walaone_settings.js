frappe.ui.form.on('WalaOne Settings', {
    refresh: function(frm) {
        // Add a button to get loyalty program info
        frm.add_custom_button(__('Get Loyalty Program Info'), function() {
            frappe.call({
                method: 'get_loyalty_program_info',
                doc:frm.doc,
                callback: function(response) {
                    if (response.message) {
                        frappe.msgprint(__('Loyalty Program Info updated successfully.'));
                        frm.reload_doc();  // Reload the form to reflect changes
                    } else {
                        frappe.msgprint(__('Failed to fetch loyalty program info.'));
                    }
                }
            });
        });
    }
});
