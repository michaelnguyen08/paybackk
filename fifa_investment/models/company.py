# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
import calendar
from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, RedirectWarning

class ResCompany(models.Model):
    _inherit = "res.company"

    res_fifa_default_investment_debit_account = fields.Many2one('account.account', string="Investment Default Debit Account", check_company=True,
        readonly=False, help="Investment Default Debit Account", tracking=True)
    
    res_fifa_default_investment_credit_account = fields.Many2one('account.account', string="Investment Default Credit Account", check_company=True,
        readonly=False, help="Investment Default Credit Account", tracking=True)
    
    res_fifa_default_investment_journal = fields.Many2one('account.journal', string="Investment Default Journal", check_company=True,
        readonly=False, help="Investment Default Journal", tracking=True)
    
    res_fifa_default_purchase_debit_account = fields.Many2one('account.account', string="Purchase FIFA Default Debit Account", check_company=True,
        readonly=False, help="Default Debit Account for purchase of FIFA's", tracking=True)
    
    res_fifa_default_purchase_credit_account = fields.Many2one('account.account', string="Purchase FIFA Default Credit Account", check_company=True,
        readonly=False, help="Default Credit Account for purchase of FIFA's", tracking=True)
    
    res_fifa_default_purchase_journal = fields.Many2one('account.journal', string="Purchase FIFA Default Journal", check_company=True,
        readonly=False, help="Default Journal for purchase of FIFA's", tracking=True)
    
    res_fifa_default_sale_debit_account = fields.Many2one('account.account', string="Sale FIFA Default Debit Account", check_company=True,
        readonly=False, help="Default Debit Account for sale of FIFA's", tracking=True)
    
    res_fifa_default_sale_credit_account = fields.Many2one('account.account', string="Sale FIFA Default Credit Account", check_company=True,
        readonly=False, help="Default Credit Account for sale of FIFA's", tracking=True)
    
    res_fifa_default_sale_journal = fields.Many2one('account.journal', string="Sale FIFA Default Journal", check_company=True,
        readonly=False, help="Default Journal for sale of FIFA's", tracking=True)
    
    
