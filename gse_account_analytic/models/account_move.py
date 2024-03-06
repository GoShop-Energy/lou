# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    source = fields.Char(string="Source so", compute="_compute_source")

    def _compute_source(self):
        # compute source based on ref
        for move in self:
            if move.ref:
                source = move.ref.split(" - ")[0]
                delivery = self.env["stock.picking"].search(
                    [("name", "=", source)], limit=1
                )
                so = self.env["sale.order"].search(
                    [("name", "=", delivery.origin)], limit=1
                )
                move.source = so.analytic_account_id.name
            else:
                move.source = "Unknown"

    # archive the analytic account when the invoice is fully paid
    @api.depends("amount_residual", "move_type", "state", "company_id")
    def _compute_payment_state(self):
        super(AccountMove, self)._compute_payment_state()
        source_orders = self.line_ids.sale_line_ids.order_id
        for move in self:
            if (
                move.payment_state == "paid"
                and source_orders.delivery_status == "full"
                and source_orders.invoice_status == "invoiced"
                and source_orders.analytic_account_id
                and (
                    not source_orders.task_status
                    or source_orders.task_status == "finished"
                )
            ):
                source_orders.analytic_account_id.active = False


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("move_id")
    def _compute_analytic_distribution(self):
        super(AccountMoveLine, self)._compute_analytic_distribution()
        source = ""
        for line in self:
            for l in line.move_id:
                source = l.source
            if line.journal_id.name == "Inventory Valuation":
                if line.journal_id.name == "Inventory Valuation":
                    analytic_account = self.env["account.analytic.account"].search(
                        [("name", "=", source)], limit=1
                    )
                    analytic_distribution = {}
                    if analytic_account:
                        analytic_distribution = {
                            str(analytic_account.id): 100.0,
                        }
                    line.analytic_distribution = analytic_distribution
