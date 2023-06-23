# Copyright 2023 Nicolás Ramos - (https://binhex.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2023 Javier Colmenero - (https://javier@comunitea.com)
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_acquirer_concept_move(self):
        self.ensure_one()
        concept = ""
        doc_type = self.picking_id.partner_id.product_plastic_document_type
        orig_loc_usage = self.location_id.usage
        dest_loc_usage = self.location_dest_id.usage
        dest_loc_scrap = self.location_dest_id.scrap_location
        # Intracomunitary Acquisitions
        if orig_loc_usage == 'supplier' and doc_type == "2":
            concept = "1"
        # Deduction by: Non Spanish Shipping
        elif dest_loc_usage == 'customer' and doc_type != "1":
            concept = "2"
        # Deduction by: Scrap
        elif dest_loc_scrap:
            concept = "3"
        # Deduction by: Adquisition returns
        elif dest_loc_usage == "supplier" and self.origin_returned_move_id:
            concept = "4"
        return concept

    def _get_manufacturer_concept_move(self):
        """
        """
        self.ensure_one()
        concept = ""
        doc_type = self.picking_id.partner_id.product_plastic_document_type
        # orig_loc_usage = self.location_id.usage
        dest_loc_usage = self.location_dest_id.usage
        dest_loc_scrap = self.location_dest_id.scrap_location

        # Initial Existence
        if dest_loc_scrap:
            concept = "3"
        # Sales to spanish customers
        elif dest_loc_usage == "customer" and doc_type == 1:
            concept = "4"
        return concept
