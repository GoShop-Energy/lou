# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for order in self:
            if self.env.context.get('force_confirm', False):
                # Proceed with the standard confirmation process
                return super(SaleOrder, self).action_confirm()
            if order.amount_total > 50000:
                # Vérifier si un produit de type "Project Main d'Oeuvre" est présent
                has_project_mo_product = any(line.product_id.type == 'service' for line in order.order_line)
                
                if not has_project_mo_product:
                    # Appeler le wizard avec un message et une input
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
                    # Validation classique si "Project Main d'Oeuvre" est présent
                    return super(SaleOrder, self).action_confirm()
            else:
                # Validation classique si le montant est inférieur à 50k
                return super(SaleOrder, self).action_confirm()
