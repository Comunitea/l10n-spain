# Copyright 2004-2011 Pexego Sistemas Informáticos. (http://pexego.es)
# Copyright 2012 NaN·Tic  (http://www.nan-tic.com)
# Copyright 2013 Acysos (http://www.acysos.com)
# Copyright 2013 Joaquín Pedrosa Gutierrez (http://gutierrezweb.es)
# Copyright 2016 Tecnativa - Antonio Espinosa
# Copyright 2016 Tecnativa - Angel Moya <odoo@tecnativa.com>
# Copyright 2018 PESOL - Angel Moya <info@pesol.es>
# Copyright 2014-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "AEAT modelo 182",
    "version": "16.0.1.6.0",
    "author": "Tecnativa,PESOL,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-spain",
    "category": "Accounting",
    "license": "AGPL-3",
    "depends": [
        "account_tax_balance",
        "base_vat",
        "l10n_es",
        "l10n_es_aeat",
        "donation",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/mod_182_security.xml",
        "views/mod182_view.xml",
        "views/mod182_deduccion_view.xml",
        "views/res_partner.xml",
        "views/product_view.xml",
        "views/donation_view.xml",
        "views/res_country_state.xml",
        "data/aeat_export_mod182_partner_donation_data.xml",
        "data/aeat_export_mod182_data.xml",
        "data/mod182_deduccion_data.xml",
    ],
    "installable": True,
    "images": ["images/l10n_es_aeat_mod182.png"],
}
