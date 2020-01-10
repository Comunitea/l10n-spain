# © 2019 Comunitea
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sef_server = fields.Char(
        string="SEF server location",
        config_parameter="account.invoice.sef.server",
    )
    sef_user = fields.Char(
        string="SEF user", config_parameter="account.invoice.sef.user"
    )
    sef_password = fields.Char(
        string="SEF password", config_parameter="account.invoice.sef.password"
    )
