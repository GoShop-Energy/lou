# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError

class CustomMrpBom(models.Model):
    _inherit = 'mrp.bom'



    @api.onchange('bom_line_ids', 'product_qty')
    def onchange_bom_structure(self):
           if self.type == 'phantom' and self._origin and self.env['stock.move'].search([('bom_line_id', 'in', self._origin.bom_line_ids.ids)], limit=1):
                raise UserError(_(   'The product has already been used at least once, editing its structure may lead to undesirable behaviors. '
                'You should rather archive the product and create a new one with a new bill of materials.'))
            
   