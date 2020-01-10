# © 2019 Comunitea
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models, api, exceptions, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains(
        "facturae",
        "vat",
        "country_id",
        "state_id",
        "invoice_integration_method_ids",
    )
    def constrain_sef(self):
        sef = self.env.ref("l10n_es_facturae_sef.integration_sef")
        for record in self.filtered(
            lambda x: sef in x.invoice_integration_method_ids
        ):
            if not record.facturae:
                raise exceptions.ValidationError(
                    _("Facturae must be selected in order to send to sef")
                )
            if not record.vat:
                raise exceptions.ValidationError(
                    _("Vat must be defined in order to send to sef")
                )
            if not record.country_id:
                raise exceptions.ValidationError(
                    _("Country must be defined in order to send to sef")
                )
            if record.country_id.code_alpha3 == "ESP":
                if not record.state_id:
                    raise exceptions.ValidationError(
                        _(
                            "State must be defined in Spain in order to "
                            "send to sef"
                        )
                    )
