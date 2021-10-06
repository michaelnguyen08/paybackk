# -*- coding: utf-8 -*-
{
    'name': "DDS - Investor Reports",

    'summary': """Adding 2 reports on the portal for investors to be able to view the details of the funds and their investments""",

    'description': """
        Adding 2 reports on the portal for investors to be able to view the details of the funds and their investments
    """,

    'author': "Dry Deck Solutions",
    # 'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '1.0',

    'depends': ['base','portal','fifa_investment'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/funds_allocation.xml',
        'views/fund_distribution.xml',
        'views/assets.xml'
    ],
}
