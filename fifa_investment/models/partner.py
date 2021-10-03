# -*- coding: utf-8 -*-

from odoo import models, fields, api    

class Partner(models.Model):
    _inherit = 'res.partner'

    is_investor = fields.Boolean(string='Is Investor')
    property_default_investment_debit_account = fields.Many2one(
        'account.account', string="Investment Default Debit Account", company_dependent=True, check_company=True,
        #domain="['|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",
        help="Investment Default Debit Account")
    property_default_investment_credit_account = fields.Many2one(
        'account.account', string="Investment Default Credit Account", company_dependent=True, check_company=True,
        #domain="['|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",
        help="Investment Default Credit Account")
    #partner_investments = fields.One2many(comodel_name='investment.fund.partner.amount', inverse_name='partner', string)
