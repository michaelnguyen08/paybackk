# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

class FIFAType(models.Model):
    _name = 'res.fifa.type'
    _description = 'FIFA Type'
    
    name = fields.Char(string='Type Name', required=True, tracking=True)

class InvestmentFunds(models.Model):
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
    
    lead_id = fields.Many2one(comodel_name='crm.lead', string='FIFA Lead', tracking=True)
    year = fields.Selection(selection=_year_selection, string='Year', index=True, default=_default_year, tracking=True)
    type = fields.Many2one(comodel_name='res.fifa.type', string='Type', index=True, tracking=True)
    value = fields.Monetary(string='Value', currency_field='currency_id')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', related='lead_id.currency_id')
    
    
    
    