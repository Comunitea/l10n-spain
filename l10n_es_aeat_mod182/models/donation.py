
# Copyright 2024 Comunitea - Javier Colmenero Fernández
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# import datetime
# from calendar import monthrange

from odoo import _, api, fields, models


class DonationLine(models.Model):
    _inherit = "donation.line"

    # aeat_report_id = fields.Many2one(
    #     'l10n.es.aeat.mod182.report', string='AEAT Report')
    tipo_bien = fields.Selection(
        [('I', 'Inmueble'), ('V', 'Valores mobiliarios'), ('O', 'otros')],
        string="Tipo de bien")
    identificacion_bien = fields.Char('Identificación del bien')
    nif_patrimonio_protegido = fields.Char('NIF patrimonio protegido')
    nombre_patrimonio_protegido = fields.Char('Nombre patrimonio protegido')