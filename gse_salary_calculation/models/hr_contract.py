# -*- coding: utf-8 -*-
from odoo import api, fields, models, _ 

class Contract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Contract Form extension'

    def open_salary_calculation_wizard(self): 
        return {
            'name': 'Salary Calculation',
            'type': 'ir.actions.act_window',
            'res_model': 'salary.calculation.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('gse_salary_calculation.view_salary_calculation_wizard_form').id,
            'target': 'new', 
            'context': {
                'current_contract_id': self.id,  # Pass the ID of the current contract
            },
        }