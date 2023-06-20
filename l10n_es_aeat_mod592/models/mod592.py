# Copyright 2023 Nicolás Ramos - (https://binhex.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re
import logging

from odoo import api, fields, models, exceptions, _

_logger = logging.getLogger(__name__)


class L10nEsAeatmod592Report(models.Model):
    _name = "l10n.es.aeat.mod592.report"
    _inherit = "l10n.es.aeat.report"
    _description = "AEAT 592 report"
    _aeat_number = "592"
    _period_quarterly = False
    _period_monthly = True
    _period_yearly = False

    number = fields.Char(default="592")
    total_manufacturer_entries_records = fields.Integer(
        compute="_compute_manufacturer_total_entries",
        string="Total entries records",
        store=True,
    )
    total_weight_manufacturer_records = fields.Float(
        compute="_compute_manufacturer_total_weight",
        string="Total weight records",
        store=True,
    )
    total_weight_manufacturer_non_reclyclable_records = fields.Float(
        compute="_compute_manufacturer_total_weight_non_reclyclable",
        string="Total weight records non reclyclable",
        store=True,
    )
    total_amount_manufacturer_records = fields.Float(
        compute="_compute_manufacturer_total_amount",
        string="Total amount manufacturer records",
        store=True,
    )
    total_acquirer_entries_records = fields.Integer(
        compute="_compute_acquirer_total_entries",
        string="Total entries records",
        store=True,
    )
    total_weight_acquirer_records = fields.Float(
        compute="_compute_acquirer_total_weight",
        string="Total weight records",
        store=True,
    )
    total_weight_acquirer_non_reclyclable_records = fields.Float(
        compute="_compute_acquirer_total_weight_non_reclyclable",
        string="Total weight records non reclyclable",
        store=True,
    )
    total_amount_acquirer_records = fields.Float(
        compute="_compute_acquirer_total_amount",
        string="Total amount acquirer records",
        store=True,
    )
    amount_plastic_tax = fields.Float(
        string="Amount tax for non recyclable", store=True, default=0.45
    )
    manufacturer_line_ids = fields.One2many(
        comodel_name="l10n.es.aeat.mod592.report.line.manufacturer",
        inverse_name="report_id",
        string="Mod592 Journal entries",
        copy=False,
        readonly=True,
    )
    acquirer_line_ids = fields.One2many(
        comodel_name="l10n.es.aeat.mod592.report.line.acquirer",
        inverse_name="report_id",
        string="Mod592 Journal entries",
        copy=False,
        readonly=True,
    )
    report_line_ids = fields.One2many(
        comodel_name="l10n.es.aeat.mod592.report.line",
        inverse_name="report_id",
        string="Mod592 Report Lines",
        copy=False,
        readonly=False,
    )

    company_plastic_type = fields.Selection(related="company_id.company_plastic_type")

    @api.depends("manufacturer_line_ids")
    def _compute_manufacturer_total_entries(self):
        for report in self:
            report.total_manufacturer_entries_records = len(
                report.manufacturer_line_ids
            )

    @api.depends("acquirer_line_ids")
    def _compute_acquirer_total_entries(self):
        for report in self:
            report.total_manufacturer_entries_records = len(report.acquirer_line_ids)

    @api.depends("manufacturer_line_ids.kgs")
    def _compute_manufacturer_total_weight(self):
        for report in self:
            report.total_weight_manufacturer_records = sum(
                report.mapped("manufacturer_line_ids.kgs")
            )

    @api.depends("acquirer_line_ids.kgs")
    def _compute_acquirer_total_weight(self):
        for report in self:
            report.total_weight_manufacturer_records = sum(
                report.mapped("acquirer_line_ids.kgs")
            )

    @api.depends("manufacturer_line_ids.no_recycling_kgs")
    def _compute_manufacturer_total_weight_non_reclyclable(self):
        for report in self:
            report.total_weight_manufacturer_non_reclyclable_records = sum(
                report.mapped("manufacturer_line_ids.no_recycling_kgs")
            )

    @api.depends("acquirer_line_ids.no_recycling_kgs")
    def _compute_acquirer_total_weight_non_reclyclable(self):
        for report in self:
            report.total_weight_manufacturer_non_reclyclable_records = sum(
                report.mapped("acquirer_line_ids.no_recycling_kgs")
            )

    @api.depends("manufacturer_line_ids.no_recycling_kgs")
    def _compute_manufacturer_total_amount(self):
        for report in self:
            total_amount = 0.0
            for line in report.manufacturer_line_ids:
                total_amount += line.no_recycling_kgs * self.amount_plastic_tax
                report.write(
                    {
                        "total_amount_manufacturer_records": total_amount,
                    }
                )

    @api.depends("acquirer_line_ids.no_recycling_kgs")
    def _compute_acquirer_total_amount(self):
        for report in self:
            total_amount = 0.0
            for line in report.acquirer_line_ids:
                total_amount += line.no_recycling_kgs * self.amount_plastic_tax
                report.write(
                    {
                        "total_amount_acquirer_records": total_amount,
                    }
                )

    # REGISTROS MANUFACTURER
    def _move_line_domain(self):

        return [
            ("parent_state", "=", "posted"),
            ("date", ">=", self.date_start),
            ("date", "<=", self.date_end),
            ("is_plastic_tax", "=", True),
        ]

    def _stock_move_domain(self):
        return [
            ("state", "=", "done"),
            ("date", ">=", self.date_start),
            ("date", "<=", self.date_end),
            ("is_plastic_tax", "=", True),
        ]

    def _create_592_details(self, move_lines):
        # line_values = []
        acquirer_values = []
        manofacturer_values = []
        for move_line in move_lines:
            # if move_line.move_id.move_type in (
            #     "in_invoice",
            #     "out_invoice",
            #     "out_refund",
            #     "in_refund",
            # ):

            # self._create_592_manufacturer_record_detail(move_line)
            # self._create_592_acquirer_record_detail(move_line)
            # line_values.append(self._get_report_vals(move_line))
            acquirer_values.append(self._get_report_acquirer_vals(move_line))
            manofacturer_values.append(self._get_report_manofacturer_vals(move_line))
                
            # if self.company_id.company_plastic_type == 'manufacturer':
            #     pass
            # if self.company_id.company_plastic_type == 'acquirer':
            #     pass
        # import ipdb; ipdb.set_trace()
        # if line_values:
        #     self.env['l10n.es.aeat.mod592.report.line'].\
        #         create(line_values)
        if acquirer_values:
            self.env['l10n.es.aeat.mod592.report.line.acquirer'].\
                create(acquirer_values)
        if manofacturer_values:
            self.env['l10n.es.aeat.mod592.report.line.manufacturer'].\
                create(manofacturer_values)

    # def _get_report_vals(self, move_line):
    #     vals = {
    #         "report_id": self.id,
    #         # "move_line_id": move_line.id,
    #         "stock_move_id": move_line.id,
    #         "date_done": move_line.date,
    #         "concept": move_line.product_plastic_concept_manufacturer,
    #         "product_key": move_line.product_plastic_type_key,
    #         "product_description": move_line.name,
    #         "fiscal_manufacturer": move_line.product_plastic_tax_regime_manufacturer,
    #         "proof": move_line.name,
    #         "supplier_document_type": move_line.partner_id.product_plastic_document_type
    #         or move_line.partner_id.property_account_position_id.product_plastic_document_type,
    #         "supplier_document_number": move_line.partner_id.vat,
    #         "supplier_social_reason": move_line.partner_id.name,
    #         "kgs": move_line.product_plastic_tax_weight,
    #         "no_recycling_kgs": move_line.product_plastic_weight_non_recyclable,
    #         "entry_note": False,
    #     }
    #     return vals

    def _get_report_acquirer_vals(self, move_line):
        vals =  {
            "report_id": self.id,
            # "move_line_id": move_line.id,
            "stock_move_id": move_line.id,
            "entry_number": move_line.name,
            "date_done": move_line.date,
            "concept": move_line.product_plastic_concept_manufacturer,
            "product_key": move_line.product_plastic_type_key,
            # "product_description": move_line.name,
            "fiscal_acquirer": move_line.product_plastic_tax_regime_manufacturer,
            "proof": move_line.product_plastic_tax_description,
            "supplier_document_type": move_line.partner_id.product_plastic_document_type or move_line.partner_id.property_account_position_id.product_plastic_document_type,
            "supplier_document_number": move_line.partner_id.vat,
            "supplier_social_reason": move_line.partner_id.name,
            "kgs": move_line.product_plastic_tax_weight,
            "no_recycling_kgs": move_line.product_plastic_weight_non_recyclable,
            "entry_note": False,
        }
        return vals

    def _get_report_manofacturer_vals(self, move_line):
        vals = {
                "report_id": self.id,
                # "move_line_id": move_line.id,
                "stock_move_id": move_line.id,
                "date_done": move_line.date,
                "concept": move_line.product_plastic_concept_manufacturer,
                "product_key": move_line.product_plastic_type_key,
                "product_description": move_line.name,
                "fiscal_manufacturer": move_line.product_plastic_tax_regime_manufacturer,
                "proof": move_line.name,
                "supplier_document_type": move_line.partner_id.product_plastic_document_type
                or move_line.partner_id.property_account_position_id.product_plastic_document_type,
                "supplier_document_number": move_line.partner_id.vat,
                "supplier_social_reason": move_line.partner_id.name,
                "kgs": move_line.product_plastic_tax_weight,
                "no_recycling_kgs": move_line.product_plastic_weight_non_recyclable,
                "entry_note": False,
            }
        return vals

    def _create_592_manufacturer_record_detail(self, move_line):
        return self.env["l10n.es.aeat.mod592.report.line.manufacturer"].create(
            {
                "report_id": self.id,
                # "move_line_id": move_line.id,
                "stock_move_id": move_line.id,
                "date_done": move_line.date,
                "concept": move_line.product_plastic_concept_manufacturer,
                "product_key": move_line.product_plastic_type_key,
                "product_description": move_line.name,
                "fiscal_manufacturer": move_line.product_plastic_tax_regime_manufacturer,
                "proof": move_line.name,
                "supplier_document_type": move_line.partner_id.product_plastic_document_type
                or move_line.partner_id.property_account_position_id.product_plastic_document_type,
                "supplier_document_number": move_line.partner_id.vat,
                "supplier_social_reason": move_line.partner_id.name,
                "kgs": move_line.product_plastic_tax_weight,
                "no_recycling_kgs": move_line.product_plastic_weight_non_recyclable,
                "entry_note": False,
            }
        )

    # def _create_592_acquirer_record_detail(self, move_line):
    #     return self.env["l10n.es.aeat.mod592.report.line.acquirer"].create(
    #         {
    #             "report_id": self.id,
    #             # "move_line_id": move_line.id,
    #             "stock_move_id": move_line.id,
    #             "entry_number": move_line.name,
    #             "date_done": move_line.date,
    #             "concept": move_line.product_plastic_concept_manufacturer,
    #             "product_key": move_line.product_plastic_type_key,
    #             # "product_description": move_line.name,
    #             "fiscal_acquirer": move_line.product_plastic_tax_regime_manufacturer,
    #             "proof": move_line.product_plastic_tax_description,
    #             "supplier_document_type": move_line.partner_id.product_plastic_document_type or move_line.partner_id.property_account_position_id.product_plastic_document_type,
    #             "supplier_document_number": move_line.partner_id.vat,
    #             "supplier_social_reason": move_line.partner_id.name,
    #             "kgs": move_line.product_plastic_tax_weight,
    #             "no_recycling_kgs": move_line.product_plastic_weight_non_recyclable,
    #             "entry_note": False,
    #         }
    #     )

    def _cleanup_report(self):
        """Remove previous partner records and partner refunds in report."""
        self.ensure_one()
        self.manufacturer_line_ids.unlink()
        self.acquirer_line_ids.unlink()

    def calculate(self):
        """Computes the records in report."""
        self.ensure_one()
        with self.env.norecompute():
            self._cleanup_report()
            # MOVIMIENTOS DE FACTURAS
            # move_lines = self.env["account.move.line"].search(self._move_line_domain())
            # self._create_592_details(move_lines)
            # MOVIMIENTOS DE STOCK
            stock_moves = self.env["stock.move"].search(self._stock_move_domain())
            self._create_592_details(stock_moves)
        self.recompute()
        return True

    def button_recover(self):
        """Clean children records in this state for allowing things like
        cancelling an invoice that is inside this report.
        """
        self._cleanup_report()
        return super().button_recover()

    def _check_report_lines(self):
        """Checks if all the fields of all the report lines
        (partner records and partner refund) are filled
        """
        # import ipdb; ipdb.set_trace()
        for item in self:
            for entries in item.manufacturer_line_ids:
                if not entries.entries_ok:
                    raise exceptions.UserError(
                        _(
                            "All entries records fields (Entrie number, VAT number "
                            "Concept, Key product, Fiscal regime, etc must be filled."
                        )
                    )

    def _write_sequence(self):
        """Checks if all the fields of all the report lines
        (partner records and partner refund) are filled
        """
        for item in self.manufacturer_line_ids:
            item.update(
                {
                    "entry_number": self.env["ir.sequence"].next_by_code(
                        "l10n.es.aeat.mod592.report.line.manufacturer"
                    )
                }
            )

    def get_report_file_name(self):
        return "{}{}C{}".format(
            self.year, self.company_vat, re.sub(r"[\W_]+", "", self.company_id.name)
        )

    def button_confirm(self):
        """Checks if all the fields of the report are correctly filled"""
        self._write_sequence()
        self._check_report_lines()

        return super(L10nEsAeatmod592Report, self).button_confirm()

    def export_xlsx_manufacturer(self):
        self.ensure_one()
        return self.env.ref(
            "l10n_es_aeat_mod592.l10n_es_aeat_mod592_xlsx_man"
        ).report_action(self)

    def export_csv_manufacturer(self):
        self.ensure_one()
        return self.env.ref(
            "l10n_es_aeat_mod592.l10n_es_aeat_mod592_csv_man"
        ).report_action(self)

    def export_xlsx_acquirer(self):
        self.ensure_one()
        return self.env.ref(
            "l10n_es_aeat_mod592.l10n_es_aeat_mod592_xlsx_acquirer"
        ).report_action(self)

    def export_csv_acquirer(self):
        self.ensure_one()
        return self.env.ref(
            "l10n_es_aeat_mod592.l10n_es_aeat_mod592_csv_acquirer"
        ).report_action(self)







    def view_action_mod592_report_line(self):
        action = self.env.ref(
            'l10n_es_aeat_mod592.action_l10n_es_aeat_mod592_report_line').read()[0]
        action['domain'] = [('id', 'in', self.report_line_ids.ids)]
        return action


# todo quitar
class l10nEsAeatMod592ReportLine(models.Model):
    _description = "AEAT 592 Manufacturer report"
    _name = "l10n.es.aeat.mod592.report.line"

    report_id = fields.Many2one(
        comodel_name="l10n.es.aeat.mod592.report", string="Mod592 Report")
    plastic_type = fields.Selection([
        ('manufacturer', _('Manufacturer')),
        ('acquirer', _('Acquirer'))], 
        string='Company Plastic Type', 
        default='manufacturer')

    # move_line_id = fields.Many2one(
    #     comodel_name="account.move.line", string="Journal Item", required=True
    # )
    sequence = fields.Integer(default=1)
    entry_number = fields.Char(_('Entrie number'), store=True, limit=20)



    date_done = fields.Date(_('Date'), store=True, limit=10)
    concept = fields.Selection(
        [
            ("1", _("(1) Initial existence")),
            ("2", _("(2) Manufacturing")),
            ("3", _("(3) Return of products for destruction or reincorporation into the manufacturing process")),
            ("4", _("(4) Delivery or making available of the products accounted for")),
            ("5", _("(5) Other cancellations of the products accounted for other than their delivery or availability")),
        ],
        string=_('Concept'), store=True, limit=1)

    product_key = fields.Selection(
        [
            ("A", _("(A) Non-reusable")),
            ("B", _("(B) Semi-finished")),
            ("C", _("(C) Plastic product intended to allow the closure")),
        ],
        string=_('Key product'), store=True, limit=1)
    product_description = fields.Char(
        _('Product description'), store=True, limit=30)
    fiscal_manufacturer = fields.Selection(
        [
            ("A", _("(A) Subjection and non-exemption ")),
            ("B", _("(B) Not subject to article 73 a) Law 7/2022, of April 8")),
            ("C", _("(C) Not subject to article 73 b) Law 7/2022, of April 8")),
            ("D", _("(D) Non-subjection article 73 c) Law 7/2022, of April 8")),
            ("E", _("(E) Not subject to article 73 d) Law 7/2022, of April 8")),
            ("F", _("(F) Exemption article 75 a) 1º Law 7/2022, of April 8")),
            ("G", _("(G) Exemption article 75 a) 2º Law 7/2022, of April 8")),
            ("H", _("(H) Exemption article 75 a) 3º Law 7/2022, of April 8")),
            ("I", _("(I) Exemption article 75 c) Law 7/2022, of April 8")),
            ("J", _("(J) Exemption article 75 g) 1º Law 7/2022, of April 8")),
            ("K", _("(K) Exemption article 75 g) 2º Law 7/2022, of April 8")),
        ],
        string=_("Fiscal regime manufacturer"), store=True, limit=5
    )

    proof = fields.Char(_('Supporting document'), store=True, limit=40)
    supplier_document_type = fields.Selection(
        [
            ("1", _("(1) NIF or Spanish NIE")),
            ("2", _("(2) Intra-Community VAT NIF")),
            ("3", _("(3) Others")),
        ],
        string=_('Supplier document type'), store=True, limit=1
    )
    supplier_document_number = fields.Char(
        _('Supplier document number'), store=True, limit=15)
    supplier_social_reason = fields.Char(
        _('Supplier name'), store=True, limit=150)
    kgs = fields.Float(_('Weight'), store=True, limit=17)
    no_recycling_kgs = fields.Float(
        _('Weight non reclycable'), store=True, limit=17)
    entry_note = fields.Text(
        _('Entries observation'), store=True, limit=200)
    stock_move_id = fields.Many2one(
        comodel_name="stock.move", string="Stock Move", required=True
    )
    entries_ok = fields.Boolean(
        compute="_compute_entries_ok",
        string="Entries OK",
        help="Checked if record is OK",
        compute_sudo=True
    )
    error_text = fields.Char(
        string="Error text",
        compute="_compute_entries_ok",
        store=True,
        compute_sudo=True,
    )

    @api.depends("supplier_document_number", "product_key", "supplier_social_reason", "entry_number", "fiscal_manufacturer", "supplier_document_type", "supplier_document_number")
    def _compute_entries_ok(self):
        """Checks if all line fields are filled."""
        for record in self:
            errors = []
            # if not record.supplier_document_number:
            #     errors.append(_("Without VAT"))
            if not record.product_key:
                errors.append(_("Without product key"))
            if not record.supplier_social_reason:
                errors.append(_("Without supplier name"))
            if not record.entry_number:
                errors.append(_("Without entrie number"))
            if not record.fiscal_manufacturer:
                errors.append(_("Without regime"))
            if not record.supplier_document_type:
                errors.append(_("Without supplier document"))
            if not record.supplier_document_number:
                errors.append(_("Without document number"))
            if not record.kgs > 0.0:
                errors.append(_("Without Weiht"))
            if not record.no_recycling_kgs > 0.0:
                errors.append(_("Without Weiht non recyclable"))

            # record.entries_ok = bool(not errors)
            record.entries_ok = True
            record.error_text = ", ".join(errors)

    # @api.model
    # def create(self, vals):
    #     for record in self:
    #         seq = self.env['ir.sequence'].next_by_code(
    #             'l10n.es.aeat.mod592.report.line.manufacturer')
    #         asiento = self.move_line.move_id.name
    #         record.write({
    #             'entry_number': str(seq + asiento),
    #         })
