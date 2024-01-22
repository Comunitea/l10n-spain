
# Copyright 2024 Comunitea - Javier Colmenero Fernández
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    clave_mod182 = fields.Selection([
        ('A', 'Donativos no incluidos en actividades o programas prioritarios de mecenazgo'),
        ('B', 'Donativos incluidos en actividades o programas prioritarios de mecenazgo'),
        ('C', 'Aportación al patrionio de discapacitados'),
        ('D', 'Disposición al patrionio de discapacitados'),
        ('E', 'Gasto de dinero y consumo de bienes fungibles'),
        ('F', 'Cuotas de afiliación'),
        ('G', 'resto de donaciones y aportaciones percibidas')], 
        string='Clave Modelo 182', default="A")