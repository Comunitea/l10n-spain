# -*- coding: utf-8 -*-
# Copyright 2018 Comunitea - Omar Castiñeira <omar@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields


class AccountInvoiceTax(models.Model):

    _inherit = "account.invoice.tax"

    @api.multi
    def _get_company_curr_amounts(self):
        for tax in self:
            if tax.invoice_id.currency_id != \
                    tax.invoice_id.company_id.currency_id:
                currency = tax.invoice_id.currency_id.\
                    with_context(date=tax.invoice_id.date_invoice)
                tax.base_company = currency.\
                    compute(tax.base, tax.invoice_id.company_id.currency_id)
                tax.amount_company = currency.\
                    compute(tax.amount, tax.invoice_id.company_id.currency_id)
            else:
                tax.base_company = tax.base
                tax.amount_company = tax.amount

    base_company = fields.Monetary(string='Base in company currency',
                                   compute="_get_company_curr_amounts")
    amount_company = fields.Monetary(string='Amount in company currency',
                                     compute="_get_company_curr_amounts")
