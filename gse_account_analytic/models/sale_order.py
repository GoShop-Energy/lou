# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        # create an analytic account when the sale order is confirmed
        for order in self:
            if not order.analytic_account_id:
                order._create_analytic_account()
        return super(SaleOrder, self)._action_confirm()

    # archive the analytic account when cancelling the sale order
    def action_cancel(self):
        for order in self:
            if order.analytic_account_id:
                order.analytic_account_id.active = False
        return super(SaleOrder, self).action_cancel()

    @api.depends("state", "order_line.invoice_status")
    def _compute_invoice_status(self):
        super(SaleOrder, self)._compute_invoice_status()
        for order in self:
            move = self.env["account.move"].search(
                [("invoice_origin", "=", order.name)], limit=1
            )
            if (
                move.payment_state == "paid"
                and order.delivery_status == "full"
                and order.invoice_status == "invoiced"
                and order.analytic_account_id
                and (not order.task_status or order.task_status == "finished")
            ):
                order.analytic_account_id.active = False
