# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    is_inv_val = fields.Boolean("Is Invetory Valuation", compute='_compute_is_inv_val')

    def _compute_is_inv_val(self):
        for move in self:
            move.is_inv_val = True if move.journal_id.name == 'Inventory Valuation' else False
             
