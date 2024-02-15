# -*- coding: utf-8 -*-
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        # create an analytic account when the sale order is confirmed
        for order in self:
            if not order.analytic_account_id:
                order._create_analytic_account()
            elif not order.analytic_account_id.active:
                order.analytic_account_id.active = True
        return super(SaleOrder, self)._action_confirm()

    # archive the analytic account when cancelling the sale order
    def action_cancel(self):
        for order in self:
            if order.analytic_account_id:
                order.analytic_account_id.active = False
        return super(SaleOrder, self).action_cancel()
