# -*- coding: utf-8 -*-
from odoo import api, models, fields


class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    price_unit = fields.Float(string='Unit Price', compute='_compute_price_unit', store=True)

    @api.depends('order_id')
    def _compute_price_unit(self):
        for record in self:
            if record.order_id:
                # Fetch the related purchase order line
                order_line = self.env['purchase.order.line'].search([('order_id', '=', record.order_id.id)], limit=1)
                record.price_unit = order_line.price_unit if order_line else 0.0

    def _select(self):

        return super(PurchaseReport, self)._select() + ", l.price_unit"
          
    def _group_by(self):

        return super(PurchaseReport, self)._group_by() + ", l.price_unit"