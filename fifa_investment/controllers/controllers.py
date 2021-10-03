# -*- coding: utf-8 -*-
# from odoo import http


# class PartnerInvestment(http.Controller):
#     @http.route('/partner_investment/partner_investment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_investment/partner_investment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_investment.listing', {
#             'root': '/partner_investment/partner_investment',
#             'objects': http.request.env['partner_investment.partner_investment'].search([]),
#         })

#     @http.route('/partner_investment/partner_investment/objects/<model("partner_investment.partner_investment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_investment.object', {
#             'object': obj
#         })
