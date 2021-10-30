# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare 
    
class AccountMove(models.Model):
    _inherit = 'account.move'

    investment_fund_id = fields.Many2one(comodel_name='res.fifa.investment.fund', string='Investment Fund')
    
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    partner_fund_investment_id = fields.Many2one(comodel_name='res.fifa.investment.fund.partner.investments', string='Partner Fund Investment')
    fifa_id = fields.Many2one(comodel_name='res.fifa', string='FIFA')
    