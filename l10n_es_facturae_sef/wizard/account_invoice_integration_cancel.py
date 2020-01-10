# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountInvoiceIntegrationCancel(models.TransientModel):
    _inherit = 'account.invoice.integration.cancel'
    _description = 'Cancels a created integration'

    sef_motive = fields.Char()
    method_code = fields.Char(related='integration_id.method_id.code')

    def cancel_values(self):
        res = super(AccountInvoiceIntegrationCancel, self).cancel_values()
        if self.method_code == 'sef':
            res['cancellation_motive'] = self.sef_motive
        return res
