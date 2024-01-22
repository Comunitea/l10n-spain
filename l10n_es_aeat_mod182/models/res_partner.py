
# Copyright 2024 Comunitea - Javier Colmenero Fernández
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    menor_14 = fields.Boolean('Menor de 14 años')
    entidad_rentas = fields.Boolean('Entidad en régimen de atribución de rentas')
    nif_representante = fields.Char('NIF Representante', size=9)
    
    naturaleza_declarado = fields.Selection([
        ('F', 'Persona Física'),
        ('J', 'Persona Jurídica'),
        ('E', 'Entidad en régimen de atribución de rentas')],
        string='Naturaleza del declarado', default='J', 
        compute='_compute_naturaleza_declarado', store=False)
    
    def _compute_naturaleza_declarado(self):
        for partner in self:
            if partner.entidad_rentas:
                partner.naturaleza_declarado = 'E'
            else:
                partner.naturaleza_declarado = 'J' if partner.is_company else 'F'
            
