# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            if self.env.context.get('force_confirm', False):
                return super(SaleOrder, self).action_confirm()

            if order.amount_total > 50000:
                has_project_mo_product = any(line.product_id.type == 'service' for line in order.order_line)
                
                if not has_project_mo_product:
                    # Trigger the wizard
                    return {
                        'name': 'Montant supérieur à 50k',
                        'type': 'ir.actions.act_window',
                        'res_model': 'warning.wizard',
                        'view_mode': 'form',
                        'target': 'new',
                        'view_id': self.env.ref('gse_sale.warning_wizard_form').id,
                        'context': {
                            'default_sale_order_id': self.id
                        }
                    }
                else:
                    return super(SaleOrder, self).action_confirm()
            else:
                return super(SaleOrder, self).action_confirm()
