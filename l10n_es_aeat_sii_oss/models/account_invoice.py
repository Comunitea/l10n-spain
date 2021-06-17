# Copyright 2021 FactorLibre - Rodrigo Bonilla <rodrigo.bonilla@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_sii_map_lines_code_apply(self):
        return ['SFENS', 'NotIncludedInTotal']

    @api.multi
    def _get_sii_taxes_map(self, codes):
        """Return the codes that correspond to that sii map line codes.

        :param self: Single invoice record.
        :param codes: List of code strings to get the mapping.
        :return: Recordset with the corresponding codes
        """
        taxes = super()._get_sii_taxes_map(codes)
        sii_map_lines_code_apply = self._get_sii_map_lines_code_apply()
        if any([x for x in codes if x in sii_map_lines_code_apply]):
            taxes |= self.env['account.tax'].search([
                ('oss_country_id', '!=', False)])
        return taxes
