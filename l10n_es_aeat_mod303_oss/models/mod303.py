# -*- coding: utf-8 -*-
# Copyright 2021 PESOL - Angel Moya
# Copyright 2021 FactorLibre - Rodrigo Bonilla <rodrigo.bonilla@factorlibre.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0

from openerp import api, fields, models


class L10nEsAeatMod303Report(models.Model):
    _inherit = "l10n.es.aeat.mod303.report"

    @api.multi
    def _get_tax_code_lines(self, codes, periods=None, include_children=True):
        """Don't populate results for fields 79-99 for reports different from
        last of the year one or when not exonerated of presenting model 390.
        """
        if self.env.context.get('field_number', 0) in (123, 126):
            oss_codes = self.env['account.tax.code'].search([('code', '=like',
                                                              'BASE-EU-VAT%')])
            codes.extend(oss_codes.mapped('code'))
        res = super(L10nEsAeatMod303Report, self)._get_tax_code_lines(
            codes, periods=periods, include_children=include_children,
        )
        if 126 <= self.env.context.get('field_number', 0) <= 127:
            if (self.exonerated_390 == '2' or not self.has_operation_volume
                    or self.period_type not in ('4T', '12')):
                return self.env['account.move.line']
        return res

    @api.multi
    def _get_move_line_domain(self, codes, periods=None,
                              include_children=True):
        """Changes periods to full year when the summary on last report of the
        year for the corresponding fields. Only field number is checked as
        the complete check for not bringing results is done on
        `_get_tax_code_lines`.
        """
        if 126 <= self.env.context.get('field_number', 0) <= 127:
            fiscalyear_code = fields.Date.from_string(
                periods[:1].date_stop
            ).year
            date_start = "%s-01-01" % fiscalyear_code
            date_stop = "%s-12-31" % fiscalyear_code
            periods = self.env["account.period"].search([
                ('date_start', '>=', date_start),
                ('date_stop', '<=', date_stop),
                ('special', '=', False)
            ])
        return super(L10nEsAeatMod303Report, self)._get_move_line_domain(
            codes, periods=periods, include_children=include_children
        )
