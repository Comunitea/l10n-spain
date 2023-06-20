# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import csv

from odoo import fields, models



class Mod592CsvManufacturer(models.AbstractModel):
    _name = "report.l10n_es_aeat_mod592.l10n_es_aeat_mod592_csv_man"
    _description = "Mod592 CSV Manufacturer"
    _inherit = "report.report_csv.abstract"

    def generate_csv_report(self, writer, data, objects):
        writer.writeheader()
        for obj in objects.manufacturer_line_ids:
            writer.writerow({
                'entry_number': obj.entry_number,
                'date_done': obj.date_done,
                'concept': obj.concept,
                'product_key': obj.product_key,
                'product_description': obj.product_description,
                'fiscal_manufacturer': obj.fiscal_manufacturer,
                'proof': obj.proof,
                'supplier_document_type': obj.supplier_document_type,
                'supplier_document_number': obj.supplier_document_number,
                'supplier_social_reason': obj.supplier_social_reason,
                'kgs': obj.kgs,
                'no_recycling_kgs': obj.no_recycling_kgs,
                'entry_note': obj.entry_note or "",
            })

    def csv_report_options(self):
        res = super().csv_report_options()
        res["fieldnames"].append("entry_number")
        res["fieldnames"].append("date_done")
        res["fieldnames"].append("concept")
        res["fieldnames"].append("product_key")
        res["fieldnames"].append("product_description")
        res["fieldnames"].append("fiscal_manufacturer")
        res["fieldnames"].append("proof")
        res["fieldnames"].append("supplier_document_type")
        res["fieldnames"].append("supplier_document_number")
        res["fieldnames"].append("supplier_social_reason")
        res["fieldnames"].append("kgs")
        res["fieldnames"].append("no_recycling_kgs")
        res["fieldnames"].append("entry_note")
        res['delimiter'] = ';'
        res['quoting'] = csv.QUOTE_ALL
        return res


class Mod592CsvAcquirer(models.AbstractModel):
    _name = "report.l10n_es_aeat_mod592.l10n_es_aeat_mod592_csv_acquirer"
    _description = "Mod592 CSV Acquirer"
    _inherit = "report.report_csv.abstract"

    def generate_csv_report(self, writer, data, objects):
        writer.writeheader()
        for obj in objects.acquirer_line_ids:
            writer.writerow({
                'entry_number': obj.entry_number,
                'date_done': obj.date_done,
                'concept': obj.concept,
                'product_key': obj.product_key,
                'fiscal_acquirer': obj.fiscal_acquirer,
                'proof': obj.proof,
                'supplier_document_type': obj.supplier_document_type,
                'supplier_document_number': obj.supplier_document_number,
                'supplier_social_reason': obj.supplier_social_reason,
                'kgs': obj.kgs,
                'no_recycling_kgs': obj.no_recycling_kgs,
                'entry_note': obj.entry_note or "",
            })

    def csv_report_options(self):
        res = super().csv_report_options()
        res["fieldnames"].append("entry_number")
        res["fieldnames"].append("date_done")
        res["fieldnames"].append("concept")
        res["fieldnames"].append("product_key")
        res["fieldnames"].append("fiscal_acquirer")
        res["fieldnames"].append("proof")
        res["fieldnames"].append("supplier_document_type")
        res["fieldnames"].append("supplier_document_number")
        res["fieldnames"].append("supplier_social_reason")
        res["fieldnames"].append("kgs")
        res["fieldnames"].append("no_recycling_kgs")
        res["fieldnames"].append("entry_note")
        res['delimiter'] = ';'
        res['quoting'] = csv.QUOTE_ALL
        return res
