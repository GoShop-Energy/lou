# -*- coding: utf-8 -*-
from odoo import models, fields

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    general_budget_id = fields.Many2one(
        'crossovered.budget.lines', 
        string='Budgetary Position',
        ondelete='set null',
        help="The budgetary position related to this analytic line."
    )