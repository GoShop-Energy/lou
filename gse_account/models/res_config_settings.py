# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    company_specific = fields.Html(related='company_id.company_specific', string="Custom Invoice Messages", readonly=False)
    use_custom_msg = fields.Boolean(related='company_id.use_custom_msg', string="Custom Message", readonly=False)
    use_another_template = fields.Boolean(related='company_id.use_another_template', readonly=False)
    email_template_id = fields.Many2one(related='company_id.email_template_id', string="Email Template", readonly=False)