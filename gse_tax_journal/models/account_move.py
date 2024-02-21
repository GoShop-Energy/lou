
# -*- coding: utf-8 -*-
from odoo import models
from odoo.exceptions import  ValidationError

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super(AccountMove, self).action_post()
        move_line = self.env['account.move.line'].search([('move_id', '=', self.id)])
        for line in move_line:
            for tax in line.tax_ids:
                transformed_args = [arg.id for arg in tax.allowed_journal]
                if self.journal_id.id not in transformed_args and tax.allowed_journal:
                    raise ValidationError(f"{tax.name} - This tax is not allowed for this journal : {self.journal_id.name}.")         
        return res

