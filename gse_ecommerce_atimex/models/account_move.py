# -*- coding: utf-8 -*-
from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("move_id")
    def _compute_analytic_distribution(self):
        super(AccountMoveLine, self)._compute_analytic_distribution()
        source = ""
        for line in self:
            for l in line.move_id:
                ref =  l.ref.split(" - ")[0] if l.ref else ""
                related_stock_picking = self.env["stock.picking"].search(
                    [("name", "=", ref)], limit=1
                )

                so = self.env["sale.order"].search(
                    [("name", "=", related_stock_picking.origin)], limit=1
                ) if related_stock_picking.origin else None

                source = so.analytic_account_id.name if so and so.analytic_account_id else ""
            analytic_account = self.env["account.analytic.account"].search(
                [("name", "=", source)], limit=1
            ) if source else None
            
            analytic_distribution = {}
            if analytic_account:
                analytic_distribution = {
                    str(analytic_account.id): 100.0,
                }
            line.analytic_distribution = analytic_distribution
