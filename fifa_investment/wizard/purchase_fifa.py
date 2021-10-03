# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import json
import logging
from odoo.tools.float_utils import float_compare
_logger = logging.getLogger('FiFA-Purchase')

class FifaPurchase(models.TransientModel):
    _name = 'res.fifa.purchase.fund'
    _description = 'Fifa Purchase Fund'
    
    def _get_default_lead(self):
        lead_id = self._context.get('default_lead_id', False) or self._context.get('active_id')
        return lead_id
    
    lead_id = fields.Many2one(comodel_name='crm.lead', string='FIFA Lead', required=True, default=_get_default_lead)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', related='lead_id.currency_id')
    fund_id = fields.Many2one(comodel_name='res.fifa.investment.fund', string='Investment Fund', required=True, domain="[('remaining_amount', '>', 0)]")
    fund_remaining_amount = fields.Monetary(string='Fund Remaining', currency_field='currency_id', related='fund_id.remaining_amount')
    fifa_ids = fields.Many2many(comodel_name='res.fifa', relation='rel_fund_purchase_fifa', column1='purchase_id', column2='fifa_id', string='FIFA to Purchase', ondelete="cascade")
    fifa_value = fields.Monetary(string='FIFA Value', currency_field='currency_id', compute='_get_fifa_value')
    
    @api.depends('fifa_ids', 'fifa_ids.value')
    def _get_fifa_value(self):
        for rec in self:
            fifa_value = 0.0
            if rec.fifa_ids:
                fifa_value = sum(rec.mapped('fifa_ids.value'))
            rec.fifa_value = fifa_value
    
    @api.onchange('fund_id')
    def _onchange_fund(self):
        fifa_ids = []
        #Find the fifas which haven't been purchased yet
        if self.lead_id:
            fifa_found = self.env['res.fifa'].search([('lead_id', '=', self.lead_id.id), ('status', '=', 'available')])
            if fifa_found:
                fifa_ids.extend(fifa_found.ids)
        self.fifa_ids = [(6, 0, fifa_ids)]
            
    def action_purchase_fifa(self):
        self.ensure_one()
        if float_compare(self.fifa_value, self.fund_remaining_amount, precision_digits=3) > 0:
            raise UserError("Insufficient funds to purchase the selected FIFA's")
        purchased_fifa_vals = [] 
        for fifa in self.fifa_ids:
            purchased_fifa_vals.append((0, 0, {'fifa_id': fifa.id}))
        if purchased_fifa_vals:
            self.fund_id.write({'purchased_fifa': purchased_fifa_vals})
        else:
            raise Warning("Unable to process the selected FIFA's")
        
        purchase_debit_account = self.env.company.res_fifa_default_purchase_debit_account
        purchase_credit_account = self.env.company.res_fifa_default_purchase_credit_account
        purchase_journal = self.env.company.res_fifa_default_purchase_journal
        if not purchase_debit_account or not purchase_credit_account:
            raise UserError('Kindly configure default investment journal, debit and credit accounts within settings!')
        self._create_purchase_journal_entry(purchase_credit_account.id, purchase_debit_account.id, journal_id=purchase_journal.id)
    
    def _create_purchase_journal_entry(self, credit_account_id, debit_account_id, journal_id):
        self.ensure_one()
        AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)

        move_lines = self._prepare_account_move_line(credit_account_id, debit_account_id)
        if move_lines:
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': 'Purchase FIFA (%s)' %self.fund_id.name,
                'investment_fund_id': self.fund_id.id,
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
        credit_amount = self.fifa_value
        #credit_value = debit_value
        
        for fifa in self.fifa_ids:
            debit_line_vals = {
                'name': fifa.name,
                'ref': fifa.name,
                'debit': fifa.value,
                'account_id': debit_account_id,
                'fifa_id': fifa.id,
            }
            move_lines.append((0, 0, debit_line_vals))
         
        credit_line_vals = {
            'name': self.fund_id.name,
            'ref': self.fund_id.name,
            'credit': credit_amount,
            'account_id': credit_account_id,
        }
        move_lines.append((0, 0, credit_line_vals))
        return move_lines
        
    