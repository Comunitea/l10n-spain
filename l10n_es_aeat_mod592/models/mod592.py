# Copyright 2023 Nicolás Ramos - (https://binhex.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re
import logging

from odoo import api, fields, models, exceptions, _
from odoo.osv import expression
from pprint import pprint

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

    # ACQUIRER TOTALS
    total_acquirer_entries_records = fields.Integer(
        compute="_compute_totals_acquirer",
        string="Total entries records",
        store=False,
    )
    total_weight_acquirer_records = fields.Float(
        compute="_compute_totals_acquirer",
        string="Total weight records",
        store=False,
    )
    total_weight_acquirer_non_reclyclable_records = fields.Float(
        compute="_compute_totals_acquirer",
        string="Total weight records non reclyclable",
        store=False,
    )
    total_amount_acquirer_records = fields.Float(
        compute="_compute_totals_acquirer",
        string="Total amount acquirer records",
        store=False,
    )

    # MANUFACTURER TOTALS
    total_manufacturer_entries_records = fields.Integer(
        compute="_compute_totals_manufacturer",
        string="Total entries records",
        store=True,
    )
    total_weight_manufacturer_records = fields.Float(
        compute="_compute_totals_manufacturer",
        string="Total weight records",
        store=True,
    )
    total_weight_manufacturer_non_reclyclable_records = fields.Float(
        compute="_compute_totals_manufacturer",
        string="Total weight records non reclyclable",
        store=True,
    )
    total_amount_manufacturer_records = fields.Float(
        compute="_compute_totals_manufacturer",
        string="Total amount manufacturer records",
        store=True,
    )

    # Only for smart Buttons, Can not use total_manufacturer_entries_records
    # if appears twice in the same view
    num_lines_acquirer = fields.Integer(
        'Number of lines acquirer', compute='_compute_num_lines_acquirer')
    num_lines_manufacturer = fields.Integer(
        'Number of lines manufacturer', 
        compute='_compute_num_lines_manufacturer')

    company_plastic_type = fields.Selection(related="company_id.company_plastic_type")

    def _compute_totals_acquirer(self):
        for record in self:
            total_acquirer_entries_records = 0
            total_weight_acquirer_records = 0
            total_weight_acquirer_non_reclyclable_records = 0
            total_amount_acquirer_records = 0
            for acquirer_line in self.acquirer_line_ids:
                total_acquirer_entries_records += 1
                total_weight_acquirer_records += acquirer_line.kgs
                total_weight_acquirer_non_reclyclable_records += acquirer_line.no_recycling_kgs
                total_amount_acquirer_records += acquirer_line.no_recycling_kgs * record.amount_plastic_tax
            record.write({
                'total_acquirer_entries_records': total_acquirer_entries_records,
                'total_weight_acquirer_records': total_weight_acquirer_records,
                'total_weight_acquirer_non_reclyclable_records': total_weight_acquirer_non_reclyclable_records,
                'total_amount_acquirer_records': total_amount_acquirer_records,
            })

    def _compute_totals_manufacturer(self):
        for record in self:
            total_manufacturer_entries_records = 0
            total_weight_manufacturer_records = 0
            total_weight_manufacturer_non_reclyclable_records = 0
            total_amount_manufacturer_records = 0
            for manufacturer_line in self.manufacturer_line_ids:
                total_manufacturer_entries_records += 1
                total_weight_manufacturer_records += manufacturer_line.kgs
                total_weight_manufacturer_non_reclyclable_records += manufacturer_line.no_recycling_kgs
                total_amount_manufacturer_records += manufacturer_line.no_recycling_kgs * record.amount_plastic_tax
            record.write({
                'total_manufacturer_entries_records': total_manufacturer_entries_records,
                'total_weight_manufacturer_records': total_weight_manufacturer_records,
                'total_weight_manufacturer_non_reclyclable_records': total_weight_manufacturer_non_reclyclable_records,
                'total_amount_manufacturer_records': total_amount_manufacturer_records,
            })

    def _compute_num_lines_acquirer(self):
        for report in self:
            report.num_lines_acquirer = len(report.acquirer_line_ids)

    def _compute_num_lines_manufacturer(self):
        for report in self:
            report.num_lines_manufacturer = len(report.manufacturer_line_ids)

    def _cleanup_report(self):
        """Remove previous partner records and partner refunds in report."""
        self.ensure_one()
        self.manufacturer_line_ids.unlink()
        self.acquirer_line_ids.unlink()
    
    def get_acquirer_moves_domain(self):
        """
        Search intracomunitary incoming moves with plastic tax
        TODO: Date range search by invoice related date or day 15 of next month
        whathever is first
        """
        domain_base = [
            ("date", ">=", self.date_start),
            ("date", "<=", self.date_end),
            ("state", "=", "done"),
            ("picking_id.partner_id", "!=", False),
            ("company_id", "=", self.company_id.id),
            ("product_id.is_plastic_tax", "=", True),
        ]
        # Intracomunitary Adquisitions
        domain_concept_1 = [
            ("picking_code", "=", "incoming"),
            ("location_id.usage", "=", "supplier"),
            ("picking_id.partner_id.product_plastic_document_type", "=", '2'),
        ]
        # Deduction by: Non Spanish Shipping
        domain_concept_2 = [
            ("picking_code", "=", "outgoing"),
            ("location_dest_id.usage", "=", "customer"),
            ("picking_id.partner_id.product_plastic_document_type", "!=", '1'),
        ]
        # Deduction by: Scrap
        domain_concept_3 = [
            ("location_dest_id.scrap_location", "=", True),
        ]
        # Deduction by adquisition returns
        domain_concept_4 = [
            ("location_dest_id.usage", "=", 'supplier'),
            ("picking_code", "=", "outgoing"),
        ]

        domain = expression.AND([
            domain_base, expression.OR([
                domain_concept_1, domain_concept_2, 
                domain_concept_3, domain_concept_4])])
        pprint(domain)
        return domain

    def get_manufacturer_moves_domain(self):
        return [
            ("date", ">=", self.date_start),
            ("date", "<=", self.date_end),
            ("state", "=", "no_existe"),
            # ("state", "=", "done"),
            ("picking_code", "=", "outgoing"),
            ("company_id", "=", self.company_id.id),
            ("product_id.is_plastic_tax", "=", True),
        ]

    def _get_acquirer_moves(self):
        """Returns the stock moves of the acquirer."""
        self.ensure_one()
        moves = self.env["stock.move"].search(
            self.get_acquirer_moves_domain())
        return moves

    def _get_manufacturer_moves(self):
        """Returns the stock moves of the manufacturer."""
        self.ensure_one()
        moves = self.env["stock.move"].search(
            self.get_manufacturer_moves_domain())
        return moves

    def calculate(self):
        """Computes the records in report."""
        self.ensure_one()
        with self.env.norecompute():
            self._cleanup_report()
            if self.company_id.company_plastic_acquirer:
                acquirer_moves = self._get_acquirer_moves()
                # import ipdb; ipdb.set_trace()
                self._create_592_acquirer_details(acquirer_moves)

            if self.company_id.company_plastic_manufacturer:
                manufacturer_moves =  self._get_manufacturer_moves()
                self._create_592_manufacturer_details(manufacturer_moves)

        self.recompute()
        return True

    def _create_592_acquirer_details(self, move_lines):
        # line_values = []
        acquirer_values = []
        prefix = 'ADQ-'
        sequence = 0
        for move_line in move_lines:
            sequence += 1
            entry_number = prefix + str(sequence)
            acquirer_values.append(
                self._get_report_acquirer_vals(move_line, entry_number))

        if acquirer_values:
            self.env['l10n.es.aeat.mod592.report.line.acquirer'].\
                create(acquirer_values)
       
    def _create_592_manufacturer_details(self, move_lines):
        # line_values = []
        manufacturer_values = []
        prefix = 'FAB-'
        sequence = 0
        for move_line in move_lines:
            sequence += 1
            entry_number = prefix + str(sequence)
            manufacturer_values.append(
                self._get_report_manufacturer_vals(move_line, entry_number))

        if manufacturer_values:
            self.env['l10n.es.aeat.mod592.report.line.manufacturer'].\
                create(manufacturer_values)

    def _get_report_acquirer_vals(self, move_line, entry_number):
        partner = move_line.picking_id.partner_id
        product = move_line.product_id
        vals = {
            "report_id": self.id,
            "stock_move_id": move_line.id,

            "entry_number": entry_number,
            "date_done": move_line.date,
            # "concept": move_line.product_plastic_concept_manufacturer,
            "concept": move_line._get_acquirer_concept_move(),
            "product_key": product.product_plastic_type_key,
            "fiscal_acquirer": product.product_plastic_tax_regime_acquirer,
            # "proof": move_line.product_plastic_tax_description,
            "proof": move_line.name,
            "supplier_document_type": partner.product_plastic_document_type,
            "supplier_document_number": partner.vat,
            "supplier_social_reason": partner.name,
            "kgs": product.product_plastic_tax_weight,
            "no_recycling_kgs": product.product_plastic_weight_non_recyclable,
            "entry_note": False,
        }
        return vals

    def _get_report_manufacturer_vals(self, move_line, entry_number):
        partner = move_line.picking_id.partner_id
        product = move_line.product_id
        vals = {
            "report_id": self.id,
            "entry_number": entry_number,
            "stock_move_id": move_line.id,

            "date_done": move_line.date,
            # "concept": move_line.product_plastic_concept_manufacturer,
            "concept": "1",
            "product_key": product.product_plastic_type_key,
            "product_description": move_line.name,
            "fiscal_manufacturer": product.product_plastic_tax_regime_manufacturer,
            "proof": move_line.name,
            "supplier_document_type": partner.product_plastic_document_type,
            "supplier_document_number": partner.vat,
            "supplier_social_reason": partner.name,
            "kgs": product.product_plastic_tax_weight,
            "no_recycling_kgs": product.product_plastic_weight_non_recyclable,
            "entry_note": False,
        }
        return vals

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
        # self._write_sequence()
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

    def view_action_mod592_report_line_acquirer(self):
        action = self.env.ref(
            'l10n_es_aeat_mod592.action_l10n_es_aeat_mod592_report_line_acquirer').read()[0]
        action['domain'] = [('id', 'in', self.acquirer_line_ids.ids)]
        return action

    def view_action_mod592_report_line_manufacturer(self):
        action = self.env.ref(
            'l10n_es_aeat_mod592.action_l10n_es_aeat_mod592_report_line_manufacturer').read()[0]
        action['domain'] = [('id', 'in', self.manufacturer_line_ids.ids)]
        return action
