from odoo import models, fields

class TimesheetsAnalysisReport(models.Model):
    _name = 'timesheets.analysis.report'
    _inherit = 'timesheets.analysis.report'  

    general_budget_id = fields.Many2one('crossovered.budget.lines', string='General Budget')

    def _compute_general_budget_id(self):
        for record in self:
            record.general_budget_id = record.analytic_account_id.general_budget_id