# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools import ormcache


def excel_col_number(col_name):
    """Excel column name to number"""
    n = 0
    for c in col_name:
        n = n * 26 + 1 + ord(c) - ord("A")
    return n - 1


class Mod592XlsxManufacturer(models.AbstractModel):
    _name = "report.l10n_es_aeat_mod592.l10n_es_aeat_mod592_xlsx_man"
    _description = "Mod592 Xlsx Manufacturer"
    _inherit = "report.report_xlsx.abstract"

    def format_boe_date(self, date):
        return fields.Datetime.to_datetime(date)

    @ormcache("self.id")
    def _get_undeductible_taxes(self, book):
        line = self.env.ref(
            "l10n_es_aeat_mod592.aeat_vat_book_map_line_p_iva_nd")
        return book.get_taxes_from_templates(line.tax_tmpl_ids)

    def _get_mod592_report_map_lines(self):
        return self.env["l10n.es.aeat.mod592.report.line.manufacturer"].search(
            [
                ("date", ">=", self.date_start),
                ("date", "<=", self.date_end),
            ]
        )

    def create_entries_sheet(self, workbook, book, draft_export):
        title_format = workbook.add_format(
            {"bold": 1, "border": 1, "align": "center", "valign": "vjustify"}
        )
        header_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vjustify",
                "fg_color": "#F2F2F2",
            }
        )
        subheader_format = workbook.add_format(
            {"bold": 1, "border": 1, "align": "center", "valign": "vjustify"}
        )
        decimal_format = workbook.add_format({"num_format": "0.00"})
        date_format = workbook.add_format({"num_format": "dd/mm/yyyy"})

        sheet = workbook.add_worksheet("APUNTES CONTABLES FABRICANTE")

        sheet.write("A1", "Número Asiento")
        sheet.write("B1", "Fecha Hecho Contabilizado")
        sheet.write("C1", "Concepto")
        sheet.write("D1", "Clave Producto")
        sheet.write("E1", "Descripción Producto")
        sheet.write("F1", "Régimen Fiscal")
        sheet.write("G1", "Justificante")
        sheet.write("H1", "Prov./Dest.: Tipo Documento")
        sheet.write("I1", "Prov./Dest.: Nº documento")
        sheet.write("J1", "Prov./Dest.: Razón social")
        sheet.write("K1", "Kilogramos")
        sheet.write("L1", "Kilogramos No Reciclados")
        sheet.write("M1", "Observaciones")
        last_col = "M"

        sheet.set_column("A:A", 20)
        sheet.set_column("B:B", 10, date_format)
        sheet.set_column("C:D", 3)
        sheet.set_column("E:E", 20)
        sheet.set_column("F:F", 5)
        sheet.set_column("G:G", 20)
        sheet.set_column("H:H", 3)
        sheet.set_column("I:I", 20)
        sheet.set_column("J:J", 20, decimal_format)
        sheet.set_column("K:L", 20, decimal_format)
        sheet.set_column("M:M", 20)
        next_col = excel_col_number(last_col) + 1

        return sheet

    def fill_entries_row_data(
        self, sheet, row, line, draft_export
    ):
        """Fill entries data"""

        sheet.write("A" + str(row), line.entry_number[:20])
        sheet.write("B" + str(row), self.format_boe_date(line.date_done))
        sheet.write("C" + str(row), line.concept[:1])
        sheet.write("D" + str(row), line.product_key[:1])
        sheet.write("E" + str(row), (line.product_description or "")[:30])
        sheet.write("F" + str(row), (line.fiscal_manufacturer or "")[:5])
        sheet.write("G" + str(row), (line.proof or "")[:40])
        sheet.write("H" + str(row), (line.supplier_document_type or "")[:1])
        sheet.write("I" + str(row),
                    (line.supplier_document_number or "")[:15])
        sheet.write("J" + str(row), (line.supplier_social_reason or "")[:150])
        sheet.write("K" + str(row), line.kgs)
        sheet.write("L" + str(row), line.no_recycling_kgs)
        sheet.write("M" + str(row), (line.entry_note or ""))

        # todo Error?
        # if draft_export:
        #     last_column = sheet.dim_colmax
        #     num_row = row - 1
        #     sheet.write(num_row, last_column)

    def generate_xlsx_report(self, workbook, data, objects):
        book = objects[0]
        draft_export = bool(book.state not in ["done", "posted"])
        received_sheet = self.create_entries_sheet(
            workbook, book, draft_export)
        lines = book.manufacturer_line_ids
        lines = lines.sorted(key=lambda l: (l.date_done, l.entry_number))
        row = 2
        for line in lines:
            self.fill_entries_row_data(
                received_sheet, row, line, draft_export
            )
            row += 1


class Mod592XlsxAcquirer(models.AbstractModel):
    _name = "report.l10n_es_aeat_mod592.l10n_es_aeat_mod592_xlsx_acquirer"
    _description = "Mod592 Xlsx Acquirer"
    _inherit = "report.report_xlsx.abstract"

    def format_boe_date(self, date):
        return fields.Datetime.to_datetime(date)

    @ormcache("self.id")
    def _get_undeductible_taxes(self, book):
        line = self.env.ref(
            "l10n_es_aeat_mod592.aeat_vat_book_map_line_p_iva_nd")
        return book.get_taxes_from_templates(line.tax_tmpl_ids)

    def _get_mod592_report_map_lines(self):
        return self.env["l10n.es.aeat.mod592.report.line.acquirer"].search(
            [
                ("date", ">=", self.date_start),
                ("date", "<=", self.date_end),
            ]
        )

    def create_entries_sheet(self, workbook, book, draft_export):
        title_format = workbook.add_format(
            {"bold": 1, "border": 1, "align": "center", "valign": "vjustify"}
        )
        header_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vjustify",
                "fg_color": "#F2F2F2",
            }
        )
        subheader_format = workbook.add_format(
            {"bold": 1, "border": 1, "align": "center", "valign": "vjustify"}
        )
        decimal_format = workbook.add_format({"num_format": "0.00"})
        date_format = workbook.add_format({"num_format": "dd/mm/yyyy"})

        sheet = workbook.add_worksheet("LIBRO EXISTENCIAS ADQUIRIENTE")

        sheet.write("A1", "Número Asiento")
        sheet.write("B1", "Fecha Hecho Contabilizado")
        sheet.write("C1", "Concepto")
        sheet.write("D1", "Clave Producto")
        sheet.write("E1", "Régimen Fiscal")
        sheet.write("F1", "Justificante")
        sheet.write("G1", "Prov./Dest.: Tipo Documento")
        sheet.write("H1", "Prov./Dest.: Nº documento")
        sheet.write("I1", "Prov./Dest.: Razón social")
        sheet.write("J1", "Kilogramos")
        sheet.write("K1", "Kilogramos No Reciclados")
        sheet.write("L1", "Observaciones")
        last_col = "L"

        sheet.set_column("A:A", 20)
        sheet.set_column("B:B", 10, date_format)
        sheet.set_column("C:D", 10)
        sheet.set_column("E:E", 20)
        sheet.set_column("F:F", 10)
        sheet.set_column("G:G", 20)
        sheet.set_column("H:H", 10)
        sheet.set_column("J:J", 20, decimal_format)
        sheet.set_column("K:L", 20, decimal_format)
        sheet.set_column("M:M", 20)
        next_col = excel_col_number(last_col) + 1

        return sheet

    def fill_entries_row_data(
        self, sheet, row, line, draft_export
    ):
        """Fill entries data"""

        sheet.write("A" + str(row), line.entry_number[:20])
        sheet.write("B" + str(row), self.format_boe_date(line.date_done))
        sheet.write("C" + str(row), line.concept[:1])
        sheet.write("D" + str(row), line.product_key[:1])
        sheet.write("E" + str(row), (line.fiscal_manufacturer or "")[:5])
        sheet.write("F" + str(row), (line.proof or "")[:40])
        sheet.write("G" + str(row), (line.supplier_document_type or "")[:1])
        sheet.write("H" + str(row),
                    (line.supplier_document_number or "")[:15])
        sheet.write("I" + str(row), (line.supplier_social_reason or "")[:150])
        sheet.write("J" + str(row), line.kgs)
        sheet.write("K" + str(row), line.no_recycling_kgs)
        sheet.write("L" + str(row), (line.entry_note or ""))

        # todo error?
        # if draft_export:
        #     last_column = sheet.dim_colmax
        #     num_row = row - 1
        #     sheet.write(num_row, last_column)

    def generate_xlsx_report(self, workbook, data, objects):
        book = objects[0]
        draft_export = bool(book.state not in ["done", "posted"])
        received_sheet = self.create_entries_sheet(
            workbook, book, draft_export)
        lines = book.manufacturer_line_ids
        lines = lines.sorted(key=lambda l: (l.date_done, l.entry_number))
        row = 2
        for line in lines:
            self.fill_entries_row_data(
                received_sheet, row, line, draft_export
            )
            row += 1
