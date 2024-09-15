# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    gse_task_count = fields.Integer(compute='_compute_gse_task_count', string='Tasks')

    def _compute_gse_task_count(self):
        for user in self:
            user.gse_task_count = self.env['project.task'].search_count([('is_fsm', '=', True), ('display_project_id', '!=', False)])
