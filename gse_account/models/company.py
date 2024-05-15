# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = "res.company"

    use_custom_msg = fields.Boolean('Use Custom Message', config_parameter='account.use_custom_msg')
    custom_invoice_message = fields.Html(string='Custom Invoice Message', translate=True)
    use_alternate_template = fields.Boolean(string="Use Alternate Template", config_parameter='account.use_alternate_template') 
    email_template_id = fields.Many2one('mail.template', string="Email Template", domain="[('model_id.model', '=', 'account.move')]")