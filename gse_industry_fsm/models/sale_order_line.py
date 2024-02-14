# -*- coding: utf-8 -*-

from odoo import models, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_task_prepare_values(self, project):
        values = super(SaleOrderLine, self)._timesheet_create_task_prepare_values(project)
        values["tag_ids"] = self._prepare_default_tag_id()
        values["description"] = self.order_id.instruction
        values["order_line_table"] = self._compute_order_line_table()
        return values

    def _prepare_default_tag_id(self):
        self.ensure_one()
        if not self.warehouse_id:
            return []

        existing_tag = self.env["project.tags"].search([("name", "=", self.warehouse_id.name)], limit=1)
        if existing_tag:
            return [(4, existing_tag.id)]

        new_tag = self.env["project.tags"].create({"name": self.warehouse_id.name})
        return [(4, new_tag.id)]

    def _compute_order_line_table(self):
        html_lines = [
            '<table style="width:100%; border-collapse: collapse; border: 1px solid black;">',
            '<tr style="background-color: #f2f2f2;"><th style="border: 1px solid black; padding: 8px;">Product</th><th style="border: 1px solid black; padding: 8px;">Description</th><th style="border: 1px solid black; padding: 8px;">Quantity</th></tr>'
        ]

        for line in self.order_id.order_line:
            html_lines.append(f'<tr><td style="border: 1px solid black; padding: 8px;">{line.product_id.name}</td><td style="border: 1px solid black; padding: 8px;">{line.name}</td><td style="border: 1px solid black; padding: 8px;">{line.product_uom_qty}</td></tr>')

        html_lines.append("</table>")
        return ''.join(html_lines)
