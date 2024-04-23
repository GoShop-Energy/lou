# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    job_id = fields.Many2one('hr.job', compute='_compute_job_id',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", string='Job Position')

    def _compute_job_id(self):
        for user in self:
            user.job_id = user.employee_ids.job_id