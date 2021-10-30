# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, MissingError
from odoo.tools.float_utils import float_compare 
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger('FIFA-Interest')

# class Lead(models.Model):
#     _inherit = 'crm.lead'
#     
#     interest_id = fields.Many2one(comodel_name='res.interest', string='Interest Applied')

class FIFA(models.Model):
    _inherit = 'res.fifa'
    
    interest_accrued = fields.One2many(comodel_name='res.interest.fifa', inverse_name='fifa_id', string='Interest Accrued')
    interest_id = fields.Many2one(comodel_name='res.interest', string='Interest Applied')
    interest_start_date = fields.Date(string='Interest Start Date', default=False)
    next_interest_date = fields.Date(string='Next Interest Due', compute='_get_next_interest_date', store=True)
    interest = fields.Monetary(string='Interest', currency_field='currency_id', compute='_get_interest')
    
    def _get_interest(self):
        for rec in self:
            interest = 0
            if rec.interest_accrued:
                interest = sum(rec.mapped('interest_accrued.interest_amount'))
            rec.interest = interest
    
    @api.depends('interest_start_date', 'purchase_date', 'interest_accrued', 'interest_accrued.date', 'interest_id', 'status')
    def _get_next_interest_date(self):
        for rec in self:
            next_interest_date = False
            if rec.status == 'purchased' and rec.interest_id:
                if rec.interest_accrued:
                    next_interest_date = max(rec.mapped('interest_accrued').filtered(lambda i: i.date <= fields.Date.today()).mapped('next_interest_date'))
                else:
                    interest_start_date = rec.interest_start_date if rec.interest_start_date else rec.purchase_date or rec.create_date
                    if interest_start_date:
                        rule_type = rec.interest_id.rule_type
                        interval = rec.interest_id.interval
                        if rule_type == 'daily':
                            next_delta = relativedelta(days=+interval)
                        elif rule_type == 'weekly':
                            next_delta = relativedelta(weeks=+interval)
                        elif rule_type == 'monthly':
                            next_delta = relativedelta(months=+interval)
                        elif rule_type == 'yearly':
                            next_delta = relativedelta(years=+interval)
                        next_interest_date = interest_start_date + next_delta
            rec.next_interest_date = next_interest_date
    
    def add_fifa_interest(self):
        for rec in self:
            _logger.info('Creating Interest (%s)', rec)
            interests_date = rec.next_interest_date
            rule_type = rec.interest_id.rule_type
            interval = rec.interest_id.interval
            if rule_type == 'daily':
                next_delta = relativedelta(days=+interval)
            elif rule_type == 'weekly':
                next_delta = relativedelta(weeks=+interval)
            elif rule_type == 'monthly':
                next_delta = relativedelta(months=+interval)
            elif rule_type == 'yearly':
                next_delta = relativedelta(years=+interval)
            else:
                raise MissingError('Missing interest re-computation/recurrency method')
            debt = rec.value
            if rec.interest_id.type == 'compound':
                debt += sum(rec.mapped('interest_accrued.interest_amount'))
            interest_amount = (rec.interest_id.rate * debt)/100
            existing_record_found = self.env['res.interest.fifa'].search([('date', '=', interests_date), ('fifa_id', '=', rec.id)])
            interest_rec_values = {'date': interests_date, 'fifa_id': rec.id, 'interest_amount': interest_amount}
            _logger.info(interest_rec_values)
            if existing_record_found:
                existing_record_found.write(interest_rec_values)
            else:
                self.env['res.interest.fifa'].create(interest_rec_values)
            anomalous_interest_records =  self.env['res.interest.fifa'].search([('date', '>', fields.Date.today()), ('fifa_id', '=', rec.id)])
            anomalous_interest_records.unlink()
            #rec.next_interest_date = interests_date + next_delta
    
    def action_view_accrued_interest(self):
        self.ensure_one()
        context = self._context.copy()
        context['default_fifa_id'] = self.id
        context['create': False]
        context['edit': False]
        return {
                'name':_("Interest Accured"),
                'view_mode': 'tree,form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'res.interest.fifa',
                #'res_id': partial_id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'domain': [('fifa_id', '=',self.id)],
                'context': context
                }

class FifaInterest(models.Model):
    _name = 'res.interest.fifa'
    
    fifa_id = fields.Many2one(comodel_name='res.fifa', string='FIFA')
    interest_id = fields.Many2one(comodel_name='res.interest', string='Interest', related='fifa_id.interest_id')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', related='fifa_id.currency_id')
    interest_amount = fields.Monetary(string='Interest', currency_field='currency_id')
    date = fields.Date('Date', default=fields.Date.today)
    next_interest_date = fields.Date(string='Next Interest Due', compute='_get_next_interest_date')
    
    @api.depends('date', 'interest_id')
    def _get_next_interest_date(self):
        for rec in self:
            next_interest_date = False
            if rec.interest_id:
                date = rec.date
                rule_type = rec.interest_id.rule_type
                interval = rec.interest_id.interval
                if rule_type == 'daily':
                    next_delta = relativedelta(days=+interval)
                elif rule_type == 'weekly':
                    next_delta = relativedelta(weeks=+interval)
                elif rule_type == 'monthly':
                    next_delta = relativedelta(months=+interval)
                elif rule_type == 'yearly':
                    next_delta = relativedelta(years=+interval)
                next_interest_date = date + next_delta
            rec.next_interest_date = next_interest_date 
    
class Interest(models.Model):
    _name = 'res.interest'
    #_name = "product.product"
    _description = "Interest"
    #_inherits = {'ir.cron': 'cron_id'}
    
#     @api.model
#     def default_get(self, fields_list):
#         result = super(Interest, self).default_get(fields_list)
#         result['doall'] = True
#         result['model_id'] = "fifa_investment.model_%s" % self._name
#         result['code'] = model.compute_interest_on_purchased_fifa()
#         return result

    def _default_company(self):
        return self.env.company.id
        
    
    name = fields.Char(copy=False, required=True)
    company_id = fields.Many2one("res.company", required=True, default=_default_company, readonly=True, states={"draft": [("readonly", False)]})
    #state = fields.Selection([("draft", "Draft"), ("posted", "Posted"), ("cancelled", "Cancelled"), ("closed", "Closed")], required=True, copy=False, default="draft",)
    #periods = fields.Integer(required=True, readonly=True, states={"draft": [("readonly", False)]}, help="Number of periods that the interest will last")
    type = fields.Selection([('simple', 'Regular'), ('compound', 'Compound')])
    #interval_type = fields.Selection([('minutes', 'Minutes'), ('hours', 'Hours'), ('days', 'Days'), ('weeks', 'Weeks'), ('months', 'Months')], string='Interval Unit', default='months')
    rule_type = fields.Selection([('daily', 'Day(s)'), ('weekly', 'Week(s)'), ('monthly', 'Month(s)'), ('yearly', 'Year(s)')], 
                                 'Recurrency', default='monthly', help="Interests Invoice automatically repeat at specified interval")
    interval = fields.Integer('Compute Every', default=1, help="Repeat Computation after this much intervals")
    rate = fields.Float('Interest Rate(%)', required=True, digits=(7, 4))
    
#     @api.onchange('rule_type', 'interval')
#     def _onchange_rule_type(self):
#         cron_interval_map = {'daily': 'days', 'weekly': 'weeks', 'monthly': 'months'}
#         interval_type = False
#         interval_number = 1
#         if self.rule_type and self.rule_type in cron_interval_map:
#             interval_type = cron_interval_map[self.rule_type]
#             interval_number = self.interval
#         elif self.rule_type == 'yearly':
#             interval_type = 'months'
#             interval_number = 12
#         self.interval_type = interval_type
#         self.interval_number = interval_number
        
    @api.model
    def compute_interest_on_purchased_fifa(self):
        _logger.info('Running Interest Invoices Cron Job')
        current_date = fields.Date.today()
        #self.add_fifa_interest()
        self.env['res.fifa'].search([('next_interest_date', '<=', current_date)]).add_fifa_interest()
    
    