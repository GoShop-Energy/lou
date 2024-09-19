from odoo import models, fields, api

class WarningWizard(models.TransientModel):
    _name = 'warning.wizard'
    _description = 'Warning for SO over 50k'
     
    sale_order_id = fields.Many2one('sale.order', string="Sale Order", required=True)
    confirm = fields.Selection([('yes', 'Oui'), ('no', 'Non')], string="Confirmer?", required=True)
    additional_amount = fields.Float(string="Montant supplémentaire")

    def action_confirm_warning(self):
        sale_order = self.sale_order_id
        if self.confirm == 'yes':
            # Logique pour ajouter le montant supplémentaire ou autre action
            if self.additional_amount:
                sale_order.amount_total += self.additional_amount
            # Ajouter d'autres actions si nécessaire
        else:
            # Si la confirmation est "Non", on confirme directement le Sale Order
             return sale_order.with_context({'force_confirm': True}).action_confirm()
        
        return {'type': 'ir.actions.act_window_close'}