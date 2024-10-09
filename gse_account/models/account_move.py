# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.tools import get_lang


class AccountMove(models.Model):
    _inherit = "account.move"

    use_custom_msg = fields.Boolean(string='Use Custom Message')

    tags_ids = fields.Many2many(
        'crm.lead.tag',  # Le modèle des tags CRM déjà utilisé par les Sales Orders
        'account_move_tag_rel',  # Nom de la table de relation Many2Many pour les factures
        'move_id',  # La clé étrangère de la facture dans la table de relation
        'tag_id',  # La clé étrangère vers 'crm.lead.tag' dans la relation
        string='Tags',
        help="Tags inherited from the Sales Order"
    )
    
    def _get_mail_template(self):
        """
        :return: the correct mail template based on the current move type and the alternate email template
        """
        res = super(AccountMove, self)._get_mail_template()
        gse_template = self.company_id.email_template_id
        if self.company_id.use_custom_msg and self.company_id.use_custom_msg and self.use_custom_msg and gse_template: 
            return next(iter(gse_template.get_external_id().values()), None)
        return res

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        # Appel de la méthode originale _prepare_invoice du modèle 'sale.order'
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        
        if self.tag_ids:
            valid_tag_ids = [tag.id for tag in self.tag_ids if tag.id]
            if valid_tag_ids:
                invoice_vals['tags_ids'] = [(6, 0, valid_tag_ids)]
        
        return invoice_vals