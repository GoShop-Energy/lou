from odoo import models, fields, api

class WarningWizard(models.TransientModel):
    _name = 'warning.wizard'
    _description = 'Warning for SO over 50k'
     
    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True)
    confirm = fields.Selection([('yes', 'Oui'), ('no', 'Non')], string="Confirmer?", required=True)
    additional_amount = fields.Float(string="Montant supplémentaire", help="Montant à ajouter si 'Oui' est sélectionné")

    def action_confirm_warning(self):
        sale_order = self.sale_order_id
        
        if self.confirm == 'yes':
            service_product = self.env['product.product'].search([('name', '=', 'Project Main d\'Oeuvre')], limit=1)
            if not service_product:
                raise UserError("Le produit 'Project Main d'Oeuvre' n'existe pas. Veuillez le créer.")
            
            # Add the product to the sale order with the specified price from the widget
            sale_order.write({
                'order_line': [(0, 0, {
                    'product_id': service_product.id,
                    'name': service_product.name,
                    'product_uom_qty': 1,
                    'price_unit': self.additional_amount or service_product.lst_price,  # Use input price or default product price
                })]
            })
            
        # Proceed with the sale order confirmation
        return sale_order.with_context({'force_confirm': True}).action_confirm()
