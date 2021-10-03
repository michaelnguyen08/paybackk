# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero

class PartnerFIFAShare(models.Model):
    _name = 'res.fifa.investment.fund.partner.share'
    _description = 'Amount owned by partner in various FIFA'
    _rec_name = 'partner'
    
    partner_investment_id = fields.Many2one(comodel_name='res.fifa.investment.fund.partner.investments', 
                                            string='Partner Invested Amount', domain="[('partner', '=', partner)]", index=True, required=True)
    partner = fields.Many2one(comodel_name='res.partner', string='Partner', related='partner_investment_id.partner', index=True, store=True)
    fifa_lead = fields.Many2one(comodel_name='crm.lead', string='FIFA', related='fifa_id.lead_id', store=True, index=True)
    fifa_id = fields.Many2one(comodel_name='res.fifa', string='FIFA', index=True, required=True)
    currency = fields.Many2one(comodel_name='res.currency', string='Currency', related='partner_investment_id.currency')
    amount_owned = fields.Monetary(string='Invested Amount', currency_field='currency', compute='_percentage_owned')
    percentage_owned = fields.Float(string='% Owned', digits='Product Price', compute='_percentage_owned')
    
#     @api.onchange('partner')
#     def _set_partner_filter(self):
#         domain = {}
#         if self.partner:
#             domain['partner_investment_id'] = [('partner', '=', self.partner.id)]
    
    def _percentage_owned(self):
        for rec in self:
            percentage_owned = 0
            if rec.partner_investment_id:
                percentage_owned = rec.partner_investment_id.fund_investment_share
            rec.percentage_owned = percentage_owned
            rec.amount_owned = rec.fifa_id.value * (percentage_owned/100)
    
class PartnerInvestedAmount(models.Model):
    _name = 'res.fifa.investment.fund.partner.investments'
    _description = 'Amount invested by partner in various investment funds'
    _rec_name = 'name'
    
    name = fields.Char(string='Partner Investment', compute='_get_name')
    partner = fields.Many2one(comodel_name='res.partner', string='Investor', domain="[('is_investor', '=', True)]", required=True)
    investment_fund = fields.Many2one(comodel_name='res.fifa.investment.fund', string='Investment Fund', required=True, ondelete='cascade')
    amount_invested = fields.Monetary(string='Invested Amount', currency_field='currency')
    fund_investment_share = fields.Float(string='Partner Share', digits='Discount', compute='_get_partner_investment_share')
    partner_fifa_investments = fields.One2many(comodel_name='res.fifa.investment.fund.partner.share', inverse_name='partner_investment_id', string='Partner FIFA Investments')
    investment_count = fields.Integer(string='Investment Count', compute='_investment_count')
    total_amount = fields.Float(string='Total Amount', digits='Product Price', compute='_total_amount')
    currency = fields.Many2one(comodel_name='res.currency', string='Currency', related='investment_fund.currency_id')
    
    def _get_partner_investment_share(self):
        for rec in self:
            fund_investment_share = 0.0
            if rec.investment_fund and not float_is_zero(rec.investment_fund.total_amount, precision_digits=2):
                fund_investment_share = (rec.amount_invested/rec.investment_fund.total_amount)*100
            rec.fund_investment_share = fund_investment_share
    
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
    
class InvestmentFundPurchasedFiFA(models.Model):
    _name = 'res.fifa.investment.fund.purchased'
    _description = 'FIFA purchased with investment fund'
    
    fund_id = fields.Many2one(comodel_name='res.fifa.investment.fund', string='Fund', required=True)
    fifa_id = fields.Many2one(comodel_name='res.fifa', required=True)
    
    @api.constrains('fifa_id')
    def _fifa_purchase_constraint(self):
        purchased_fifa = self.search([('fifa_id', '=', self.fifa_id.id)])
        if purchased_fifa and len(purchased_fifa) >1:
            raise UserError('FIFA Already Purchased')
    
    @api.model
    def create(self, values):
        result = super().create(values)
        fifa_id = result.mapped('fifa_id')[0].id
        fund_ids = result.mapped('fund_id')
        for fund in fund_ids:
            for investment in fund.partner_investments:
                self.env['res.fifa.investment.fund.partner.share'].create({'partner_investment_id': investment.id, 'fifa_id': fifa_id})
        return result

class InvestmentFunds(models.Model):
    _name = 'res.fifa.investment.fund'
    _description = 'Partner Investment Funds'
    
    name = fields.Char(string='Fund Title/Name', required=True)
    partner_investments = fields.One2many(comodel_name='res.fifa.investment.fund.partner.investments', inverse_name='investment_fund', 
                                          string='Investment by Partners')
    state = fields.Selection(selection=[('draft', 'Draft'), ('confirmed', 'Confirmed/Active')], string='Status', default='draft')
    investment_count = fields.Integer(string='Investment Count', compute='_investment_count')
    total_amount = fields.Float(string='Total Amount', digits='Product Price', compute='_total_amount')
    lead_count = fields.Integer(string='Investment Count', compute='_lead_count')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    journal_entries = fields.One2many(comodel_name='account.move', inverse_name='investment_fund_id', string='Journal Entries')
    journal_entries_count = fields.Integer(string='Journal Entries Count', compute='_get_journal_entries_count')
    purchased_fifa = fields.One2many(comodel_name='res.fifa.investment.fund.purchased', inverse_name='fund_id', string='Purchased FIFA')
    purchased_fifa_value = fields.Monetary(string='Purchased FIFA Value', currency_field='currency_id', compute='_get_fund_amounts')
    remaining_amount = fields.Monetary(string='Remaining Amount', currency_field='currency_id', compute='_get_fund_amounts', store=True)
    
    @api.depends('purchased_fifa.fifa_id', 'total_amount')
    def _get_fund_amounts(self):
        for rec in self:
            purchased_fifa_value = 0.0
            if rec.purchased_fifa:
                purchased_fifa_value = sum(rec.mapped('purchased_fifa.fifa_id.value'))
            remaining_amount = rec.total_amount - purchased_fifa_value
            rec.purchased_fifa_value = purchased_fifa_value
            rec.remaining_amount = remaining_amount
            
    
    def _get_journal_entries_count(self):
        for rec in self:
            rec.journal_entries_count = len(rec.journal_entries)
    
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
            
#     def button_confirm_fund_investment(self):
#         self.ensure_one()
#         raise UserError('Under Construction')
    
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
    
    def action_view_journal_entry(self):
        journal_entries = self.mapped('journal_entries')
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        if len(journal_entries) > 1:
            action['domain'] = [('id', 'in', journal_entries.ids)]
        elif len(journal_entries) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = journal_entries.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'entry',
        }
        if len(self) == 1:
            context.update({
                'default_investment_fund_id': self.id,
                'default_invoice_origin': self.mapped('name'),
            })
        action['context'] = context
        return action
    
    def button_confirm_fund_investment(self):
        self.ensure_one()
        investment_debit_account = self.env.company.res_fifa_default_investment_debit_account
        investment_credit_account = self.env.company.res_fifa_default_investment_credit_account
        investment_journal = self.env.company.res_fifa_default_investment_journal
        if not investment_debit_account or not investment_credit_account:
            raise UserError('Kindly configure default investment journal, debit and credit accounts within settings!')
        self._create_account_move_journal_entry(investment_credit_account.id, investment_debit_account.id, journal_id=investment_journal.id)
        self.state = 'confirmed'
    
    def _create_account_move_journal_entry(self, credit_account_id, debit_account_id, journal_id):
        self.ensure_one()
        AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)

        move_lines = self._prepare_account_move_line(credit_account_id, debit_account_id)
        if move_lines:
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': 'Investment Fund (%s)' %self.name,
                'investment_fund_id': self.id,
                'move_type': 'entry',
            })
            new_account_move._post()
            
    def _prepare_account_move_line(self, credit_account_id, debit_account_id):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        self.ensure_one()
        move_lines = []
        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        debit_value = self.total_amount
        #credit_value = debit_value

        debit_line_vals = {
            'name': 'Investment Fund',
            'ref': 'Investment of partners',
            'debit': debit_value,
            'account_id': debit_account_id,
        }
        
        move_lines.append((0, 0, debit_line_vals))
        
        for investment in self.partner_investments: 
            credit_line_vals = {
                'name': investment.name,
                'ref': investment.name,
                'partner_id': investment.partner.id,
                'credit': investment.amount_invested,
                'account_id': credit_account_id,
                'partner_fund_investment_id': investment.id,
            }
            move_lines.append((0, 0, credit_line_vals))
        return move_lines    