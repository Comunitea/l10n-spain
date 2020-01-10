# © 2019 Comunitea
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class AccountInvoiceIntegration(models.Model):
    _inherit = "account.invoice.integration"

    integration_status = fields.Selection(
        selection_add=[
            ("sef-01", "Recibida"),
            ("sef-02", "Gestión"),
            ("sef-03", "Intervención"),
            ("sef-05", "Pagada"),
            ("sef-06", "Rechazada"),
            ("sef-08", "Anulada"),
            ("sef-09", "Contabilizada la obligación reconocida"),
        ]
    )
