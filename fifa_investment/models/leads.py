# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare 

class Lake(models.Model):
    _name = 'res.lake'
    _description = 'Contains details of a lake attached to the property'
    
    name = fields.Char(string='Lake Name')
    fifa_property_leads = fields.Many2many(comodel_name='crm.lead', string='FIFA Property Leads', compute='_get_property_leads')
    lake_size = fields.Selection(selection=[('small', 'Small'), ('medium', 'Medium'), ('large', 'large')], string='Lake Size', required=True)
    size_value = fields.Float(string='Size', digits='Product Unit of Measure')
    size_unit = fields.Many2one(comodel_name='uom.uom', string='Size Unit')
    
    def _get_property_leads(self):
        for rec in self:
            fifa_property_leads = []
            fifa_property_leads_found = self.env['crm.lead'].search([('lake_id', '=', rec.id)])
            if fifa_property_leads_found:
                fifa_property_leads.extend(fifa_property_leads.ids)
            rec.fifa_property_leads = fifa_property_leads
    

class SurroundingProperty(models.Model):
    _name = 'res.property.neighbor'
    _description = 'Surrounding property for a FIFA lead'
    
    _rec_name = 'value'
    
    value = fields.Monetary(string='Value', currency_field='currency_id', required=True)
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', related='fifa_lead.currency_id')
    fifa_lead = fields.Many2one(comodel_name='crm.lead', string='FIFA property Lead', required=True)
    screenshot = fields.Binary(string='Screenshot')
    qpublic_link = fields.Char(string='qPublic.net Link')
    
class Comparables(models.Model):
    _name = 'res.fifa.comparable.property'
    _description = 'FIFA comparable'
    
    _rec_name = 'address'
    
    address = fields.Text(string='Addresss')
    link = fields.Char(string='Link')
    state = fields.Selection(selection=[('active', 'Active'), ('pending', 'Pending'), ('closed', 'Closed')], string='State') 
                                        #active = → makes line green
                                        #Closed →  makes line red
    attached_status = fields.Selection(selection=[('detached', 'Detached'), ('attached', 'Attached'), ('lot', 'Lot')], string='Attached Status')
    fifa_lead = fields.Many2one(comodel_name='crm.lead', string='FIFA Lead')
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', related='fifa_lead.currency_id')
    value = fields.Monetary(string='Value', currency_field='currency_id')

class CheckListItem(models.Model):
    _name = 'site.checklist.items'
    _description = 'Checklist Items'
    
    checklist = fields.Many2one(comodel_name='site.checklist', string='Checklist')
    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string='Name/Title')
    
class CheckList(models.Model):
    _name = 'site.checklist'
    _description = 'Onsite Checklist'
    
    name = fields.Char(string='Checklist Name/Title')
    checklist_items = fields.One2many(comodel_name='site.checklist.items', string='Checklist Items', inverse_name='checklist')
    
class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.constrains('name')
    def _unique_name_constraint(self):
        self.ensure_one()
        record = self.search([('name', '=', self.name)])
        if len(record) > 1:
            raise ValidationError('Lead name needs to be unique, %s already exists!' %self.name)
    
    #TODO: figure out the mechanism to compute shares
    partner_share_ids = fields.One2many(comodel_name='res.fifa.investment.fund.partner.share', inverse_name='fifa_lead', string='Partner Shared')
    name = fields.Char(string='Parcel ID', tracking=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Owner')
    img_gmaps_street_view = fields.Binary(string='Google Maps Street View')
    fmls_gmls = fields.Char(string='FMLS/GMLS')
    fifa_ids = fields.One2many(comodel_name='res.fifa', inverse_name='lead_id', string="FIFA's" )
    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency')
    total_value = fields.Monetary(string='Total Value', currency_field='currency_id', compute='_total_fifa_value')
    fund_id = fields.Many2one(comodel_name='res.fifa.investment.fund', string='Investment Fund')
    property_value = fields.Monetary(string='Total Value', currency_field='currency_id')
    propert_value_exceeds_threshold = fields.Boolean(string='Property Value Over Defined Limit',  compute='_property_value_exceeds_threshold', 
                                                     help='Whether value of the property exceeds the threshold value, default value 135000, as defined in system properties')
    neighbouring_properties_value = fields.One2many(comodel_name='res.property.neighbor', inverse_name='fifa_lead', string='Neighboring Properties')
    lake_on_property = fields.Boolean(string='Lake on property', default=False)
    lake_id = fields.Many2one('res.lake')
    lake_position = fields.Selection(selection=[('font', 'Font'), ('middle', 'Middle'), ('back', 'Back')], string='Lake Position')
    lake_creates_flood_plain = fields.Boolean(string='Does Lake Create Flood Plain', default=False)
    has_water_way = fields.Boolean(string='Has a Water Way')
    acres = fields.Float(string='Acres', digits='Product Unit of Measure')
    flag_fifa_value_owed = fields.Boolean(string='FIFA Value Owed', compute='_flag_fifa_value_owed')
    flag_water_on_land = fields.Boolean(string='Water on Land')
    image_water_on_land = fields.Binary(string='Water on Land Image')
    flag_building_structure = fields.Boolean(string='Building/Structure On Parcel?', help='Is there a building/structure on the parcel?')
    flag_flood_plain = fields.Boolean(string='Flood Plain?')
    percentage_flood_plain = fields.Float(string='Percentage of Flood Plain', digits='Product Price')
    flag_land_locked = fields.Boolean(string='Land Locked')
    flag_lot_build_capable = fields.Boolean(string='Big Enough to Build On?')
    comparables_instruction = fields.Html(string='Note', default="<ul><li>Do not cross highways</li><li>Stay 0.5 miles in scope</li><li>Lasso draw around homes. 8 Streets / North  & South</li></ul>")
    comparables = fields.One2many(comodel_name='res.fifa.comparable.property', inverse_name='fifa_lead', string='Comparables')
    comparables_approximate_value = fields.Monetary(string='Approximate Auction Value', currency_field='currency_id', compute='_comparables_value')
    onsite_checklist = fields.Many2one(comodel_name='site.checklist', string='Onsite Checklist')
    #img_gmaps_st_view_128 = fields.Image("Image 128", compute='_compute_gmaps_stree_view_image_128')
    
    @api.onchange('street', 'zip', 'city', 'state_id', 'country_id')
    def onchange_partner_id_geo(self):
        address = {}
        if self.street:
            address['street'] = self.street
        if self.zip:
            address['zip'] = self.zip
        if self.city:
            address['city'] = self.city
        if self.state_id:
            address['state'] = self.state_id.name
        if self.country_id:
            address['country'] = self.country_id.name
        if address:
            result = self._geo_localize(**address)
            if result:
                self.customer_latitude = result[0]
                self.customer_longitude = result[1]
    
    def _comparables_value(self):
        for rec in self:
            comparables_approximate_value = 0
            if rec.comparables:
                comparables_approximate_value = sum(rec.mapped('comparables').mapped('value'))/len(rec.mapped('comparables'))
            rec.comparables_approximate_value = comparables_approximate_value
    
    
    def _flag_fifa_value_owed(self):
        for rec in self:
            flag_fifa_value_owed = False
            if float_compare(rec.property_value, 170000, precision_digits=3) > 1:
                flag_fifa_value_owed = True
            rec.flag_fifa_value_owed = flag_fifa_value_owed
    
    
    
    def _property_value_exceeds_threshold(self):
        threshold_value = float(self.env['ir.config_parameter'].sudo().get_param('highlight_property_threshold_value',default=0))
        for rec in self:
            propert_value_exceeds_threshold = False
            if float_compare(rec.property_value, threshold_value, precision_digits=3) > 0:
                propert_value_exceeds_threshold = True
            rec.propert_value_exceeds_threshold = propert_value_exceeds_threshold
    
    def _total_fifa_value(self):
        for rec in self:
            total_value = 0
            if rec.fifa_ids:
                total_value = sum(rec.mapped('fifa_ids.value'))
            rec.total_value = total_value
    
    