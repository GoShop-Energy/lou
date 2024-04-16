# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    company_currency_amount = fields.Monetary(string='Amount in Company Currency',compute='_compute_company_currency_amount', 
        currency_field='company_currency_id',)
    exchange_rate = fields.Float(string='Exchange Rate', compute='_compute_rate')
    exchange_rate_store = fields.Float(string='Exchange Rate', store=True)
    is_same_curr = fields.Boolean(string='same currency')
    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency', required = True)


    @api.depends('currency_id', 'company_id.currency_id', 'amount_total', 'exchange_rate' )
    def _compute_company_currency_amount(self):
        for order in self:
            if  order.currency_id != order.company_id.currency_id:
                order.company_currency_amount = order.amount_total * order.exchange_rate 
                
                order.is_same_curr = False
            else:
                order.company_currency_amount = order.amount_total
                order.is_same_curr = True

    def _compute_rate(self):
        for order in self:
            
            price_list = self.env["res.currency"].search([("name", "=", order.currency_id.name)])
            last_recod_rate = price_list.rate_ids.sorted('name', reverse=True)[0] if price_list.rate_ids else False
            rate_price_list =  last_recod_rate.inverse_company_rate if last_recod_rate != False else 1.0
            
            if order.state != "sale":
                order.exchange_rate = rate_price_list
                order.exchange_rate_store = rate_price_list
            else:
                order.exchange_rate = order.exchange_rate_store