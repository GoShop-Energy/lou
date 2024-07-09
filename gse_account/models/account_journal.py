from odoo import fields, models

class AccountJournal(models.Model):
    _inherit = "account.journal"

    allowed_taxes = fields.Many2many(
        comodel_name="account.tax",
        relation="account_tax_journal_rel",
        column1="journal_id",
        column2="tax_id",
        string="Allowed Taxes",
    )
