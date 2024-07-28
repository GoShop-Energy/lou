# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class HrEmployeePrivate(models.Model):

    _inherit = "hr.employee"

    work_location_id = fields.Many2one('hr.work.location', 'Work Location')