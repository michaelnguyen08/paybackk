# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    property_value_threshold = fields.Float(string='Threshold for Property Value', default=135000, currency_field='currency_id',
                                               config_parameter='highlight_property_threshold_value', readonly=False, 
                                               help='Highlight property whose value exceeds this threshold limit, default threshold value is 135000')
    res_fifa_default_investment_debit_account = fields.Many2one(
        'account.account', string="Investment Default Debit Account", check_company=True,
        related="company_id.res_fifa_default_investment_debit_account", readonly=False,
        #domain="['|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",
        help="Investment Default Debit Account", tracking=True)
    res_fifa_default_investment_credit_account = fields.Many2one(
        'account.account', string="Investment Default Credit Account", check_company=True,
        related="company_id.res_fifa_default_investment_credit_account", readonly=False,
        #domain="['|', ('company_id', '=', False), ('company_id', '=', allowed_company_ids[0])]",
        help="Investment Default Credit Account", tracking=True)
    
    
    
