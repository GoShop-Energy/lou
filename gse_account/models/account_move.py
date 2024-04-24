# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    is_valuation_move = fields.Boolean("Is Invetory Valuation", compute='_compute_is_valuation_move')

    @api.depends('journal_id')
    def _compute_is_valuation_move(self):
        for move in self:
            move.is_valuation_move = move.journal_id.name == 'Inventory Valuation'
             
