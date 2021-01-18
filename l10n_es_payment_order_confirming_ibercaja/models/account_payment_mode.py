# (c) 2016 Soluntec Proyectos y Soluciones TIC. - Rubén Francés , Nacho Torró
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class PaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    num_contract = fields.Char('Número  de contrato: ')

    is_conf_ibercaja = fields.Boolean(compute="_compute_is_conf_ibercaja")

    @api.multi
    @api.depends('payment_method_id.code')
    def _compute_is_conf_ibercaja(self):
        for record in self:
            record.is_conf_ibercaja = record.payment_method_id.code == \
                'conf_ibercaja'
