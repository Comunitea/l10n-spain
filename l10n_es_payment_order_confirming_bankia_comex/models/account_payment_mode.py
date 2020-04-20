# (c) 2016 Soluntec Proyectos y Soluciones TIC. - Rubén Francés , Nacho Torró
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class PaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    is_conf_bankia_comex = fields.Boolean(compute="_compute_is_conf_bankia_comex")

    num_contract = fields.Char('Código activo de contrato:')
    linea_comex = fields.Char('Identificador línea:')

    @api.multi
    @api.depends('payment_method_id.code')
    def _compute_is_conf_bankia_comex(self):
        for record in self:
            record.is_conf_bankia_comex = record.payment_method_id.code == \
                'conf_bankia_comex'
