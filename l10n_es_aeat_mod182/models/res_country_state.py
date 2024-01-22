
# Copyright 2024 Comunitea - Javier Colmenero Fernández
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    deduccion_id = fields.Many2one('mod182.deduccion', string='Deducción CC.AA')
    deduccion_mod182 = fields.Float('% Deducción')