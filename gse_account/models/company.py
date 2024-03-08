# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = "res.company"

    use_custom_msg = fields.Boolean('Custom Invoice Messages', config_parameter='account.use_custom_msg')
    company_specific = fields.Html(string='Company Specific', translate=True)
    use_another_template = fields.Boolean(string="Use Another Email Template", config_parameter='account.use_another_template') 
    email_template_id = fields.Many2one('mail.template', string="Email Template", domain="[('model_id.model', '=', 'account.move')]")