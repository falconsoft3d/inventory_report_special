# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Steigend IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': "Reporte de Inventario Especial",
    'summary': """
        """,
    'description': """
    """,
    'author': 'Falcón Solutions',
    'website': 'http://www.falconsolutions.cl',
    'category': 'Inventory',
    'version': '1.1.1',
    'depends': ['stock',
                'l10n_cl_base',
                ],
    'data': [
        'wizards/wizard_report_stock_minimum.xml',
        'wizards/wizard_report_products_rotation.xml',
    ],
    "external_dependencies": {
     },
    'demo': [
    ],
}
