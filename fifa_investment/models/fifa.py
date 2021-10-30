# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging
from odoo.exceptions import UserError
_logger = logging.getLogger('FIFA')

class FIFAType(models.Model):
    _name = 'res.fifa.type'
    _description = 'FIFA Type'
    
    name = fields.Char(string='Type Name', required=True, tracking=True)

class FIFA(models.Model):
    _name = 'res.fifa'
    _description = 'FIFAs'
    _rec_name = 'lead_id'
    
    def _year_selection(self):
        year_min = datetime.now().year - 20
        sql_min_year = "SELECT min(year) FROM res_fifa"
        self.env.cr.execute(sql_min_year)
        min_year_found = self.env.cr.fetchone()
        if min_year_found and min_year_found[0]:
            if int(min_year_found[0]) < year_min:
                year_min = min_year_found[0]
        years_selection = [(str(num), str(num)) for num in range(year_min, (datetime.now().year)+1 )]
        return years_selection
    
    def _default_year(self):
        return str(datetime.now().year)
    
    def _get_fifa_name(self):
        for rec in self:
            name = '%s [%s] %s' %(rec.year, rec.fifa_type.name, rec.lead_id.name)
            rec.name = name
            
    def write(self, values):
        sensitive_fields = ['value', 'year', 'fifa_type']
        locked_records = self.filtered(lambda fifa: fifa.status != 'available')
        if locked_records:
            restrict_fields = list(set(sensitive_fields) & set(values.keys()))
            for field in restrict_fields:
                del values[field]
                _logger.warning('exclude sensitive field %s from write' %field)
                #raise UserError('Value of a purchased FIFA cannot be modified!')
        result = super().write(values)
        return result
        
    
    name = fields.Char(string='FIFA', compute='_get_fifa_name')
    lead_id = fields.Many2one(comodel_name='crm.lead', string='FIFA Lead', tracking=True)
    year = fields.Selection(selection=_year_selection, string='Year', index=True, default=_default_year, tracking=True)
    fifa_type = fields.Many2one(comodel_name='res.fifa.type', string='Type', index=True, tracking=True)
    #face_value = fields.Monetary(string='Value', currency_field='currency_id')
    value = fields.Monetary(string='Value', currency_field='currency_id')
    cost = fields.Monetary(string='Cost', currency_field='currency_id', help='Cost or purchase price for the FIFA')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', related='lead_id.currency_id')
    status = fields.Selection(selection=[('available', 'Available'), ('purchased', 'Purchased'), ('sold', 'Sold')], string='Status', 
                              compute='_get_fifa_status', search='_status_search')
    purchase_date = fields.Date(string='Purchase Date', compute='_get_fifa_purchase')
    fund_id = fields.Many2one('res.fifa.investment.fund', compute='_get_fifa_purchase')
    sale_price = fields.Monetary(string='Sale Price', currency_field='currency_id', help='Sale price for the FIFA', compute='_get_sale_price', inverse='_set_sale_price')
    modified_sale_price = fields.Monetary(string='Sale Price [User Defined]', currency_field='currency_id')
    user_edited_sale_price = fields.Boolean(string='User Edited Sale Price', default=False)
    sale_date = fields.Date(string='Sale Date', compute='_get_sale_date')
    purchase_ids = fields.One2many(comodel_name='res.fifa.investment.fund.purchased', inverse_name='fifa_id', string='FIFA Purchase')
    sale_ids = fields.One2many(comodel_name='res.fifa.investment.fund.sold', inverse_name='fifa_id', string='FIFA Purchase')
    
    def recompute_sale_price(self):
        self.ensure_one()
        self.user_edited_sale_price = False
    
    def _set_sale_price(self):
        for rec in self:
            if rec.sale_price:
                rec.modified_sale_price = rec.sale_price
                rec.user_edited_sale_price = True
    
    @api.depends('user_edited_sale_price', 'interest', 'cost', 'value')
    def _get_sale_price(self):
        for rec in self:
            sale_price = (rec.cost or rec.value) * 1.1
            if rec.user_edited_sale_price:
                sale_price = rec.modified_sale_price
            if rec.interest_accrued:
                sale_price = rec.value + rec.interest
            rec.sale_price = sale_price
    
    def _get_sale_date(self):
        for rec in self:
            fifa_sale_date = None
            sale_rec_found = self.env['res.fifa.investment.fund.sold'].search([('fifa_id', '=', rec.id)], limit=1)
            if sale_rec_found:
                fifa_sale_date = sale_rec_found.sale_date
            rec.sale_date = fifa_sale_date
    
    @api.depends('purchase_ids', 'purchase_ids.fifa_id')
    def _get_fifa_purchase(self):
        for rec in self:
            fifa_purchase_date = None
            fund_id = False
            purchase_rec_found = self.env['res.fifa.investment.fund.purchased'].search([('fifa_id', '=', rec.id)], limit=1)
            if purchase_rec_found:
                fifa_purchase_date = purchase_rec_found.purchase_date
                fund_id = purchase_rec_found.fund_id.id
            rec.purchase_date = fifa_purchase_date
            rec.fund_id = fund_id
    
    def _get_fifa_status(self):
        for rec in self:
            status = 'available'
            fifa_purchased = self.env['res.fifa.investment.fund.purchased'].search([('fifa_id', '=', rec.id)], limit=1)
            if fifa_purchased:
                status = 'purchased'
            fifa_sold = self.env['res.fifa.investment.fund.sold'].search([('fifa_id', '=', rec.id)], limit=1)
            if fifa_sold:
                status = 'sold'
            rec.status = status
            
    def _status_search(self, operator, value):
        _logger.info('operation = %s, value = %s, context = %s' %(operator, value, self._context))
        filter_operation = 'IN'
        lead_id = None
        criteria = []
        if self._context.get('active_model', '') == 'crm.lead':
            lead_id = self._context.get('active_id')
        elif self._context.get('default_lead_id', False):
            lead_id = self._context.get('default_lead_id')
        lead_filter_str = ''
        if lead_id:
            criteria.append(('lead_id', '=', lead_id))
            lead_filter_str = ' AND lead_id = %s' %lead_id
        if value == 'available' and operator == '=' or (value == 'purchased' and operator == '!='):
            filter_operation = 'NOT IN'
            filter_subquery = """SELECT fifa_id FROM res_fifa_investment_fund_purchased
                                    UNION
                                SELECT fifa_id FROM res_fifa_investment_fund_sold"""
        if value == 'purchased' and operator == '=' or (value == 'sold' and operator == '!='):
            filter_operation = 'IN'
            filter_subquery = """SELECT fifa_id FROM res_fifa_investment_fund_purchased
                                    EXCEPT
                                SELECT fifa_id FROM res_fifa_investment_fund_sold"""
        if value == 'sold' and operator == '=':
            filter_operation = 'IN'
            filter_subquery = "SELECT fifa_id FROM res_fifa_investment_fund_sold"
        sql_select_available_fifa = """SELECT array_agg(distinct fifa.id), count(fifa.id) from res_fifa fifa 
            WHERE fifa.id %s (%s) %s""" %(filter_operation, filter_subquery, lead_filter_str)
        self.env.cr.execute(sql_select_available_fifa)
        fifa_ids_found = self.env.cr.fetchone()
        fifa_ids = fifa_ids_found[0] if fifa_ids_found and fifa_ids_found[0] else []
        #operation = =, value = available, context = {'active_model': 'crm.lead', 'active_id': 31, 'active_ids': [31], 'default_lead_id': 31}
        _logger.info(fifa_ids)
        return [('id', 'in', fifa_ids)]
    
    
    