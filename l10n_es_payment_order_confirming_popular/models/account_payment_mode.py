# (c) 2016 Soluntec Proyectos y Soluciones TIC. - Rubén Francés , Nacho Torró
# (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models


class PaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    conf_popular_type = fields.Selection(
        string='Tipo de pago', default='60',
        selection=[('60', 'Tranferencia'),
                   ('61', 'Cheques'),
                   ('70', 'Pagos confirmados')])
    is_conf_popular = fields.Boolean(compute="_compute_is_conf_popular")

    gastos = fields.Selection(
        string='Gastos de la operación a cuenta de', default='ordenante',
        selection=[('ordenante', 'Ordenante'),
                   ('beneficiario', 'Beneficiario')])

    forma_pago = fields.Selection(
        string='Forma de pago', default='C',
        selection=[('C', 'Cheque'),
                   ('T', 'Transferencia')])
    bank = fields.Selection(
        [('popular', 'Banco popular'), ('pastor', 'Banco pastor')],
        default='popular', required=True)

    @api.multi
    @api.depends('payment_method_id.code')
    def _compute_is_conf_popular(self):
        for record in self:
            record.is_conf_popular = record.payment_method_id.code == \
                'conf_popular'
