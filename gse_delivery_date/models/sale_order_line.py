from odoo import models, fields

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    task_id = fields.Many2one(
        'project.task', 
        string='Task', 
        help="Related task for this sale order line"
    )

