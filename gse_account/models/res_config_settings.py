# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    custom_invoice_message = fields.Html(related='company_id.custom_invoice_message', string="Custom Invoice Messages", readonly=False)
    use_custom_msg = fields.Boolean(related='company_id.use_custom_msg', string="Custom Message", readonly=False)
    use_alternate_template = fields.Boolean(related='company_id.use_alternate_template', readonly=False)
    email_template_id = fields.Many2one(related='company_id.email_template_id', string="Email Template", readonly=False)