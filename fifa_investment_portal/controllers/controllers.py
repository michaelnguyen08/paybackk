# # -*- coding: utf-8 -*-
from odoo import fields, http
from odoo.http import Controller, request, route
from odoo.tools.translate import _
from odoo.addons.portal.controllers.portal import CustomerPortal
class FundPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        values['partner'] = partner
        Funds = request.env['res.fifa.investment.fund.partner.investments']
        if 'funds_count' in counters:
            values['funds_count'] = Funds.search_count(
                [('partner', '=', partner.id)])
        return values

    @http.route('/my/funds', type='http', auth="user", website=True)
    def portal_my_funds(self, **kw):
        values = self._prepare_portal_layout_values()
        values.update({
            'user_id':request.env.user.partner_id,
            'page_name':'funds',
        })
        return request.render("fifa_investment_portal.portal_my_funds", values)
class FundDisPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        values['partner'] = partner
        Funds = request.env['res.fifa.investment.fund.partner.investments']
        if 'funds_dis_count' in counters:
            values['funds_dis_count'] = Funds.search_count(
                ['&',('partner', '=', partner.id),('partner_fifa_investments','!=',False)])
        return values
    @http.route('/my/funds_dis', type='http', auth="user", website=True)
    def portal_my_funds_dis(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        funds = request.env['res.fifa.investment.fund.partner.investments'].search([('partner','=',partner.id)])
        values.update({
            'page_name':'funds_dis',
            'funds':funds
        })
        return request.render("fifa_investment_portal.portal_my_funds_dis", values)
    @ http.route('/my/funds_dis/<int:fund_id>', type='http', auth="user", website=True)
    def portal_my_funds_dis_form(self, fund_id, **kw):
        values={}

        fund = request.env['res.fifa.investment.fund.partner.investments'].search([('id','=',fund_id)])
        values.update({
            'partner' : request.env.user.partner_id,
            'funds_dis':fund
        })
        values.update()
        return request.render("fifa_investment_portal.portal_my_funds_form", values)