# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models

class HrAttendance(models.Model):
    _inherit= "hr.attendance"

    work_location_id = fields.Many2one('hr.work.location', string='Work Location', related="employee_id.work_location_id", store=True)