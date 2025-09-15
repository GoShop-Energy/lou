# -*- coding: utf-8 -*-

import json

from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, parent_combination=False, only_template=False):
        combination_info = super()._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty,
            parent_combination=parent_combination, only_template=only_template)

        if combination_info['product_id']:
            product = self.env['product.product'].sudo().browse(combination_info['product_id'])
            website = self.env['website'].get_current_website()
            # Sudo to get website from other companies?
            all_website_companies = self.env['website'].sudo().search([('domain', '!=', False)]).company_id
            combination_info.update({
                'gse_warehouses_other_companies_qty_custo': json.dumps([{
                    'id': company.id,
                    'name': company.name,
                    'domain': company.website_id.domain,
                    'address': company.partner_id.with_context(html_format=True, show_address_only=True).name_get()[0][1],  # contact_address_complete,
                    'selected': website.company_id.id == company.id,
                } for company in all_website_companies]),
                'gse_warehouses_qty_custo': json.dumps([{
                    'id': wh.id,
                    'name': wh.name,
                    'address': wh.partner_id.with_context(html_format=True, show_address_only=True).name_get()[0][1],
                    'free_qty': product.with_context(warehouse=wh.id).free_qty,
                    'selected': website._get_warehouse_available() == wh.id,
                } for wh in self.env['stock.warehouse'].sudo().search([('company_id', '=', website.company_id.id)])]),
            })
        else:
            combination_info.update({
                'gse_warehouses_other_companies_qty_custo': [],
                'gse_warehouses_qty_custo': [],
            })

        return combination_info
