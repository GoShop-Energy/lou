from odoo import models, fields

class CrossoveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    analytic_line_ids = fields.One2many(
        'account.analytic.line', 
        'general_budget_id', 
        string="Analytic Lines"
    )
