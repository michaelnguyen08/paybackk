# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
class PartnerFIFAShare(models.Model):
    _name = 'res.fifa.investment.fund.partner.share'
    _description = 'Amount owned by partner in various FIFA'
    _rec_name = 'partner'
    
    partner_investment_id = fields.Many2one(comodel_name='res.fifa.investment.fund.partner.investments', 
                                            string='Partner Invested Amount', domain="[('partner', '=', partner)]", index=True)
    partner = fields.Many2one(comodel_name='res.partner', string='Partner', related='partner_investment_id.partner', index=True)
    fifa_lead = fields.Many2one(comodel_name='crm.lead', string='FIFA', index=True, required=True)
    currency = fields.Many2one(comodel_name='res.currency', string='Currency', related='partner_investment_id.currency')
    amount_owned = fields.Monetary(string='Invested Amount', currency_field='currency')
    percentage_owned = fields.Float(string='% Owned', digits='Product Price', compute='_percentage_owned')
    
#     @api.onchange('partner')
#     def _set_partner_filter(self):
#         domain = {}
#         if self.partner:
#             domain['partner_investment_id'] = [('partner', '=', self.partner.id)]
    
    def _percentage_owned(self):
        for rec in self:
            percentage_owned = 0
            if rec.fifa_lead:
                percentage_owned = (float(rec.amount_owned)/float(rec.fifa_lead.total_value)) * 100
            rec.percentage_owned = percentage_owned
    
class PartnerInvestedAmount(models.Model):
    _name = 'res.fifa.investment.fund.partner.investments'
    _description = 'Amount invested by partner in various investment funds'
    _rec_name = 'name'
    
    name = fields.Char(string='Partner Investment', compute='_get_name')
    partner = fields.Many2one(comodel_name='res.partner', string='Investor', domain="[('is_investor', '=', True)]", required=True)
    investment_fund = fields.Many2one(comodel_name='res.fifa.investment.fund', string='Investment Fund', required=True)
    amount_invested = fields.Monetary(string='Invested Amount', currency_field='currency')
    partner_fifa_investments = fields.One2many(comodel_name='res.fifa.investment.fund.partner.share', inverse_name='partner_investment_id', string='Partner FIFA Investments')
    currency = fields.Many2one(comodel_name='res.currency', string='Currency')
    investment_count = fields.Integer(string='Investment Count', compute='_investment_count')
    total_amount = fields.Float(string='Total Amount', digits='Product Price', compute='_total_amount')
    
    def _get_name(self):
        for rec in self:
            name = ''
            if rec.investment_fund:
                name += rec.investment_fund.name
            if rec.partner:
                name += ' - ' + rec.partner.name
            if rec.amount_invested:
                name += ' ' + str(rec.amount_invested)
            rec.name = name
    
    def _investment_count(self):
        for rec in self:
            investment_count = 0
            if rec.partner_fifa_investments:
                investment_count = len(rec.partner_fifa_investments)
            rec.investment_count = investment_count 
    
    def _total_amount(self):
        for rec in self:
            total_amount = 0
            if rec.partner_fifa_investments:
                total_amount = sum(rec.mapped('partner_fifa_investments.amount_owned'))
            rec.total_amount = total_amount
    
    def action_partner_investments(self):
        self.ensure_one()
        context = self._context.copy()
        context['default_partner_investment_id'] = self.id
        context['default_partner'] = self.partner.id
        return {
                'name':_("Partner FIFA's Ownership"),
                'view_mode': 'tree,form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'res.fifa.investment.fund.partner.share',
                #'res_id': partial_id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'domain': [('partner_investment_id', '=',self.id)],
                'context': context
                }
    

class InvestmentFunds(models.Model):
    _name = 'res.fifa.investment.fund'
    _description = 'Partner Investment Funds'
    
    name = fields.Char(string='Fund Title/Name', required=True)
    partner_investments = fields.One2many(comodel_name='res.fifa.investment.fund.partner.investments', inverse_name='investment_fund', 
                                          string='Investment by Partners')
    state = fields.Selection(selection=[('draft', 'Draft'), ('confirmed', 'Confirmed/Active')], string='Status')
    investment_count = fields.Integer(string='Investment Count', compute='_investment_count')
    total_amount = fields.Float(string='Total Amount', digits='Product Price', compute='_total_amount')
    lead_count = fields.Integer(string='Investment Count', compute='_lead_count')
    
    def _lead_count(self):
        for rec in self:
            lead_count = 0
            if rec.partner_investments:
                lead_count = len(rec.mapped('partner_investments.partner_fifa_investments.fifa_lead'))
            rec.lead_count = lead_count
    
    def _investment_count(self):
        for rec in self:
            investment_count = 0
            if rec.partner_investments:
                investment_count = len(rec.partner_investments)
            rec.investment_count = investment_count 
    
    def _total_amount(self):
        for rec in self:
            total_amount = 0
            if rec.partner_investments:
                total_amount = sum(rec.mapped('partner_investments.amount_invested'))
            rec.total_amount = total_amount
            
    def button_confirm_fund_investment(self):
        self.ensure_one()
        raise UserError('Under Construction')
    
    def action_fund_investments(self):
        self.ensure_one()
        context = self._context.copy()
        context['default_investment_fund'] = self.id
        return {
                'name':_("Partner Investment"),
                'view_mode': 'tree,form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'res.fifa.investment.fund.partner.investments',
                #'res_id': partial_id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'domain': [('investment_fund', '=',self.id)],
                'context': context
                }
    
    def action_view_leads(self):
        self.ensure_one()
        context = self._context.copy()
        action = self.env['ir.actions.act_window']._for_xml_id('crm.crm_lead_opportunities')
#         if self.is_company:
#             action['domain'] = [('partner_id.commercial_partner_id.id', '=', self.id)]
#         else:
#             action['domain'] = [('partner_id.id', '=', self.id)]
        action_dict = {
                'name':_("Leads"),
                #'view_mode': 'tree,form',
                #'view_id': False,
                #'view_type': 'form',
                #'res_model': 'crm.lead',
                #'res_id': partial_id,
                #'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'domain': [('id', 'in', self.mapped('partner_investments.partner_fifa_investments.fifa_lead.id'))],
                'context': context
                }
        action.update(action_dict)
        return action
