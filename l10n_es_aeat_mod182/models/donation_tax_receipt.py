
# Copyright 2024 Comunitea - Javier Colmenero Fernández
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# import datetime
# from calendar import monthrange

from odoo import _, api, fields, models


class DonationTaxReceipt(models.Model):
    _inherit = "donation.tax.receipt"

    # aeat_report_id = fields.Many2one(
    #     'l10n.es.aeat.mod182.report', string='AEAT Report')
    aeat_especie = fields.Boolean('En especie')