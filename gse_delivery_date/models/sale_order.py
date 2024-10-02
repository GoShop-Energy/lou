from odoo import api, models, fields
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_date_difference = fields.Char(
        string="Delivery Date Difference",
        compute="_compute_delivery_date_difference",
        store=True,
        help="Difference between estimated and actual delivery date in days, hours, minutes, and seconds."
    )
    all_tasks_done_date = fields.Datetime(
        string="All Tasks Completion Date",
        compute="_compute_all_tasks_done_date",
        store=True,
        help="Date when all tasks related to this sale order are completed"
    )
    picking_ids = fields.One2many(
        'stock.picking', 'origin', string='Pickings',
        readonly=True, copy=False, help='Related pickings'
    )

    @api.depends('picking_ids', 'picking_ids.scheduled_date', 'picking_ids.date_done')
    def _compute_delivery_date_difference(self):
        for order in self:
            total_difference = 0
            for picking in order.picking_ids:
                if picking.date_done and picking.scheduled_date:
                    time_difference = picking.date_done - picking.scheduled_date
                    total_difference += time_difference.total_seconds()
                    
            if total_difference:
                days = total_difference // (24 * 3600)
                total_difference %= (24 * 3600)
                hours = total_difference // 3600
                total_difference %= 3600
                minutes = total_difference // 60
                seconds = total_difference % 60
                order.delivery_date_difference = "{} days, {} hours, {} minutes, {} seconds".format(
                    int(days), int(hours), int(minutes), int(seconds)
                )
            else:
                order.delivery_date_difference = "No delivery yet"

    @api.depends('order_line.task_id', 'order_line.task_id.stage_id')
    def _compute_all_tasks_done_date(self):
        for order in self:
            done_tasks = [
                line.task_id.write_date
                for line in order.order_line
                if line.task_id and line.task_id.stage_id.fold
            ]
            if done_tasks:
                order.all_tasks_done_date = max(done_tasks)
            else:
                order.all_tasks_done_date = False