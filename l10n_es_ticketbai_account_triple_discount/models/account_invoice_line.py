from odoo import models
from odoo.addons.l10n_es_ticketbai_api.models.ticketbai_invoice import RefundType


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def tbai_get_value_descuento(self, price_unit):
        if self.discount2 or self.discount3:
            if RefundType.differences.value == self.invoice_id.tbai_refund_type:
                sign = -1
            else:
                sign = 1
            return "%.2f" % (sign * ((self.quantity * self.price_unit) - self.price_subtotal))
        else:
            return super().tbai_get_value_descuento(price_unit)

    def tbai_get_value_importe_total(self):
        if self.discount2 or self.discount3:
            tbai_maps = self.env["tbai.tax.map"].search([('code', '=', "IRPF")])
            irpf_taxes = self.invoice_id.company_id.get_taxes_from_templates(
                tbai_maps.mapped("tax_template_ids")
            )
            currency = self.invoice_id and self.invoice_id.currency_id or None
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0) * (1 - (self.discount2 or 0.0) / 100.0) * (1 - (self.discount3 or 0.0) / 100.0)
            taxes = (self.invoice_line_tax_ids - irpf_taxes).compute_all(
                price, currency, self.quantity, product=self.product_id,
                partner=self.invoice_id.partner_id)
            price_total = taxes['total_included'] if taxes else self.price_subtotal
            if currency and self.company_id and currency != self.company_id.currency_id:
                rate_date = self.invoice_id._get_currency_rate_date() or fields.Date.today()
                price_total = currency._convert(
                    price_total, self.company_id.currency_id, self.company_id, rate_date)
            if RefundType.differences.value == self.invoice_id.tbai_refund_type:
                sign = -1
            else:
                sign = 1
            return "%.2f" % (sign * price_total)
        else:
            return super().tbai_get_value_importe_total()
