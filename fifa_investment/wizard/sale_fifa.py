# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import json
import logging
from odoo.tools.float_utils import float_compare
_logger = logging.getLogger('FiFA-Sale')

class FifaSale(models.TransientModel):
    _name = 'res.fifa.sale'
    _description = 'Fifa Sale'
    
    def _get_default_lead(self):
        lead_id = self._context.get('default_lead_id', False) or self._context.get('active_id')
        return lead_id
    
    @api.onchange('lead_id')
    def _onchange_lead(self):
        fifa_ids = []
        #Find the fifas which haven't been purchased yet
        field_domains = {}
        if self.lead_id:
            fifa_found = self.env['res.fifa'].search([('lead_id', '=', self.lead_id.id), ('status', '=', 'purchased')])
            if fifa_found:
                fifa_ids.extend(fifa_found.ids)
            field_domains['fifa_id'] = [('id', 'in', fifa_ids)]
        #self.fifa_ids = [(6, 0, fifa_ids)]
        return {'domain': field_domains}
    
    lead_id = fields.Many2one(comodel_name='crm.lead', string='FIFA Lead', required=True, default=_get_default_lead)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', related='lead_id.currency_id')
    #fund_id = fields.Many2one(comodel_name='res.fifa.investment.fund', string='Investment Fund', required=True, domain="[('remaining_amount', '>', 0)]")
    fifa_ids = fields.Many2many(comodel_name='res.fifa', relation='rel_fund_sale_fifa', column1='sale_id', column2='fifa_id', 
                                string='FIFA to Sell', ondelete="cascade", domain="[('status', '=', 'purchased')]")
    fifa_sale_price = fields.Monetary(string='FIFA Sale Price', currency_field='currency_id', compute='_get_fifa_sale_price')
    sale_date = fields.Date(string='Sale Date')
    
    @api.depends('fifa_ids', 'fifa_ids.sale_price')
    def _get_fifa_sale_price(self):
        for rec in self:
            fifa_sale_price = 0.0
            if rec.fifa_ids:
                fifa_sale_price = sum(rec.mapped('fifa_ids.sale_price'))
            rec.fifa_sale_price = fifa_sale_price
                
    def action_sale_fifa(self):
        self.ensure_one()
        sold_fifa_vals = [] 
        for fifa in self.fifa_ids:
            sold_fifa_vals.append((0, 0, {'fifa_id': fifa.id, 'sale_date': self.sale_date}))
        if sold_fifa_vals:
            purchase_fund_found = self.env['res.fifa.investment.fund.purchased'].search([('fifa_id', '=', fifa.id)], limit=1)
            purchase_fund_found.fund_id.write({'sold_fifa': sold_fifa_vals})
        else:
            raise Warning("Unable to process the selected FIFA's")
        
        sale_debit_account = self.env.company.res_fifa_default_sale_debit_account
        sale_credit_account = self.env.company.res_fifa_default_sale_credit_account
        sale_journal = self.env.company.res_fifa_default_sale_journal
        if not sale_debit_account or not sale_credit_account:
            raise UserError('Kindly configure default investment journal, debit and credit accounts within settings!')
        self._create_sale_journal_entry(sale_credit_account.id, sale_debit_account.id, journal_id=sale_journal.id)
    
    def _create_sale_journal_entry(self, credit_account_id, debit_account_id, journal_id):
        self.ensure_one()
        AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)
        
        fund_ids = self.fifa_ids.mapped('fund_id')
        for fund in fund_ids:
            fund_sold_fifas = self.fifa_ids.filtered(lambda x: x.fund_id.id == fund.id)
            move_lines = self._prepare_account_move_line(credit_account_id, debit_account_id, fund, fund_sold_fifas)
            if move_lines:
                date = self._context.get('force_period_date', fields.Date.context_today(self))
                new_account_move = AccountMove.sudo().create({
                    'journal_id': journal_id,
                    'line_ids': move_lines,
                    'date': date,
                    'ref': 'Sale FIFA %s' % str(fund.name),
                    'investment_fund_id': fund.id,
                    'move_type': 'entry',
                })
                new_account_move._post()
            
    def _prepare_account_move_line(self, credit_account_id, debit_account_id, fund, fifa_recs):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        self.ensure_one()
        move_lines = []
        # the standard_price of the product may be in another decimal precision, or not compatible with the coinage of
        # the company currency... so we need to use round() before creating the accounting entries.
        debit_amount = sum(fifa_recs.mapped('sale_price'))
        #credit_value = debit_value
        debit_line_vals = {
            'name': fund.name,
            'ref': fund.name,
            'credit': debit_amount,
            'account_id': debit_account_id,
        }
        move_lines.append((0, 0, debit_line_vals))
        
        
        for fifa in fifa_recs:
            credit_line_vals = {
                'name': fifa.name,
                'ref': fifa.name,
                'debit': fifa.sale_price,
                'account_id': credit_account_id,
                'fifa_id': fifa.id,
            }
            move_lines.append((0, 0, credit_line_vals))
        return move_lines
        
    