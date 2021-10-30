# -*- coding: utf-8 -*-
{
    'name': "FIFA Partner Investments",

    'summary': """
        Contains features which enable us to keep track of investments made by a partner.
        """,

    'description': """
        Keep track of the investments done by partner
    """,

    'author': "Dry Deck Solutions",
    #'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0.1.0.5',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'crm_maps', 'account'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/lead.xml',
        'views/fifa.xml',
        'views/fifa_comparable_property.xml',
        'views/fifa_neighboring_property.xml',
        'views/fund.xml',
        'views/lake.xml',
        'views/partner.xml',
        'views/interest.xml',
        'views/res_config_settings.xml',
        'wizard/views/purchase_fifa.xml',
        'wizard/views/sale_fifa.xml',
        'data/cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
}
