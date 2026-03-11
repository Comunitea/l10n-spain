# Copyright 2023 Aures Tic - Almudena de la Puente <almudena@aurestic.es>
# Copyright 2023 Aures Tic - Jose Zambudio <jose@aurestic.es>
# Copyright 2026 Comunitea Servicios Tecnológicos S.L. - Vicente Ángel Gutiérrez <vicente@comunitea.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _validate_session(self):
        res = super()._validate_session()
        self.order_ids.send_sii()
        return res
