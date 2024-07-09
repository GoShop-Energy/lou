# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    allowed_journal = fields.Many2many("account.journal", string="Allowed Journals")
