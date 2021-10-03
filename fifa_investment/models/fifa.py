# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import logging
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
    
    name = fields.Char(string='FIFA', compute='_get_fifa_name')
    lead_id = fields.Many2one(comodel_name='crm.lead', string='FIFA Lead', tracking=True)
    year = fields.Selection(selection=_year_selection, string='Year', index=True, default=_default_year, tracking=True)
    fifa_type = fields.Many2one(comodel_name='res.fifa.type', string='Type', index=True, tracking=True)
    value = fields.Monetary(string='Value', currency_field='currency_id')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', related='lead_id.currency_id')
    status = fields.Selection(selection=[('available', 'Available'), ('purchased', 'Purchased'), ('sold', 'Sold')], string='Status', 
                              compute='_get_fifa_status', search='_status_search')
    
    def _get_fifa_status(self):
        for rec in self:
            status = 'available'
            fifa_purchased = self.env['res.fifa.investment.fund.purchased'].search([('fifa_id', '=', rec.id)], limit=1)
            if fifa_purchased:
                status = 'purchased'
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
        if value == 'available' and operator == '=':
            filter_operation = 'NOT IN'
        if value == 'purchased' and operator == '=':
            filter_operation = 'IN'
        sql_select_available_fifa = """SELECT array_agg(distinct fifa.id), count(fifa.id) from res_fifa fifa 
            WHERE fifa.id %s (SELECT fifa_id FROM res_fifa_investment_fund_purchased) %s""" %(filter_operation, lead_filter_str)
        self.env.cr.execute(sql_select_available_fifa)
        fifa_ids_found = self.env.cr.fetchone()
        fifa_ids = fifa_ids_found[0] if fifa_ids_found and fifa_ids_found[0] else []
        #operation = =, value = available, context = {'active_model': 'crm.lead', 'active_id': 31, 'active_ids': [31], 'default_lead_id': 31}
        _logger.info(fifa_ids)
        return [('id', 'in', fifa_ids)]
    
    
    