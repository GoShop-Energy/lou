# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    company_currency_amount = fields.Monetary(string='Amount in Company Currency',compute='_compute_company_currency_amount', 
        currency_field='company_currency_id',)
    exchange_rate = fields.Float(string='Exchange Rate')

    is_same_curr = fields.Boolean(string='same currency')

    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency', require = True)
    @api.depends('currency_id', 'company_id.currency_id', 'amount_total')
    def _compute_company_currency_amount(self):
        for order in self:
            print('--',order.company_currency_id.symbol)
            price_list = self.env["res.currency"].search([("name", "=", order.currency_id.name)])
        
            last_recod_rate = price_list.rate_ids.sorted('name', reverse=True)[0] if price_list.rate_ids else False
            rate_price_list =  last_recod_rate.inverse_company_rate if last_recod_rate != False else 1.0
            order.exchange_rate = rate_price_list
            if  order.currency_id != order.company_id.currency_id:
                order.company_currency_amount = order.amount_total* rate_price_list
                
                order.is_same_curr = False
            else:
                order.company_currency_amount = order.amount_total
                order.is_same_curr = True


    
