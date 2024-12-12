# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.tools import get_lang
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    use_custom_msg = fields.Boolean(string='Use Custom Message')

    def action_post(self):
        res = super(AccountMove, self).action_post()
        move_line = self.env["account.move.line"].search([("move_id", "=", self.id)])
        for line in move_line:
            for tax in line.tax_ids:
                transformed_args = [arg.id for arg in tax.allowed_journal]
                if self.journal_id.id not in transformed_args and tax.allowed_journal:
                    raise ValidationError(
                        f"{tax.name} - This tax is not allowed for this journal : {self.journal_id.name}."
                    )
        return res
    
    def _get_mail_template(self):
        """
        :return: the correct mail template based on the current move type and the alternate email template
        """
        res = super(AccountMove, self)._get_mail_template()
        gse_template = self.company_id.email_template_id
        if self.company_id.use_custom_msg and self.company_id.use_custom_msg and self.use_custom_msg and gse_template: 
            return next(iter(gse_template.get_external_id().values()), None)
        return res
    