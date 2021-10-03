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
    
    
