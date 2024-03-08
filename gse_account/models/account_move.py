# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.tools import get_lang


class AccountMove(models.Model):
    _inherit = "account.move"

    use_custom_msg = fields.Boolean(string='Use Custom Message')

    def _get_mail_template(self):
        """
        :return: the correct mail template based on the current move type and the alternate email template
        """
        res = super(AccountMove, self)._get_mail_template()
        gse_template = self.company_id.email_template_id
        if self.company_id.use_custom_msg and self.company_id.use_custom_msg and self.use_custom_msg and gse_template: 
            return next(iter(gse_template.get_external_id().values()), None)
        return res