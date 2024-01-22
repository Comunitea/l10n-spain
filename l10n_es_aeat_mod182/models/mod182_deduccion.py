
# Copyright 2024 Comunitea - Javier Colmenero Fernández
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class Mod182Deduccion(models.Model):
    _name = "mod182.deduccion"

    name = fields.Char('Nombre', required=True)
    code = fields.Char('Código', required=True)
    state_ids = fields.One2many(
        'res.country.state', 'deduccion_id', string='States')
    deduccion = fields.Float('Deducción %')