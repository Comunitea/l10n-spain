# Copyright 2023 Nicolás Ramos - (https://binhex.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2023 Javier Colmenero - (https://javier@comunitea.com)


from odoo import fields, models, _


class ResCompany(models.Model):

    _inherit = "res.company"

    company_plastic_acquirer = fields.Boolean(
        string='Company Plastic Acquirer', default=True)
    company_plastic_manufacturer = fields.Boolean(
        string='Plastic Manufacturer', default=True)
