# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Expend this method to create an analytic account when the sale order is fully delivered
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        so = self.env["sale.order"].search([("name", "=", self.origin)], limit=1)
        move = self.env["account.move"].search(
            [("invoice_origin", "=", so.name)], limit=1
        )
        if (
            move.payment_state == "paid"
            and so.delivery_status == "full"
            and so.invoice_status == "invoiced"
            and so.analytic_account_id
            and (not so.task_status or so.task_status == "finished")
        ):
            so.analytic_account_id.active = False
        return res
