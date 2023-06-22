# Copyright 2023 Nicolás Ramos - (https://binhex.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_acquirer_concept_move(self):
        self.ensure_one()
        concept = ""
        code = self.picking_code
        doc_type = self.picking_id.partner_id.product_plastic_document_type
        orig_loc_usage = self.location_id.usage
        dest_loc_usage = self.location_dest_id.usage
        dest_loc_scrap = self.location_dest_id.scrap_location
        # Intracomunitary Acquisitions
        if code == "incoming" and orig_loc_usage == 'supplier' \
                and doc_type == "2":
            concept = "1"
        # Deduction by: Non Spanish Shipping
        elif code == "outgoing" and dest_loc_usage == 'customer' \
                and doc_type != "1":
            concept = "2"
        # Deduction by: Scrap
        elif dest_loc_scrap:
            concept = "3"
        # Deduction by: Adquisition returns
        elif dest_loc_usage == "supplier" and code == "outgoing":
            concept = "4"
        return concept
