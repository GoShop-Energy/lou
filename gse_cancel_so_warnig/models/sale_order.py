from odoo import api, fields, models
from odoo.addons.sale.models.sale_order import SaleOrder as OdooSaleOrder

class SaleOrder(models.Model):
    _inherit= 'sale.order'

    def action_cancel(self):
        return self._action_cancel()
    
    OdooSaleOrder.action_cancel = action_cancel