# Copyright 2015 Creu Blanca
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Envío de Factura-e a SEF",
    "version": "12.0.1.0.0",
    "author": "Comunitea, "
              "Odoo Community Association (OCA)",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/l10n-spain",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_facturae",
        "report_xml",
    ],
    "data": [
        "data/sef_data.xml",
        "views/res_config_views.xml",
        'views/sef_templates.xml',
        'wizard/account_invoice_integration_cancel_view.xml'
    ],
    "external_dependencies": {
        "python": [
            "zeep",
            "xmlsec"
        ]
    },
    "installable": True,
}
