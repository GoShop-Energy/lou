# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class Website(models.Model):
    _inherit = 'website'

    def _get_warehouse_available(self):
        if request and request.session.get('GSE_FORCED_WAREHOUSE_ID'):
            gse_wh_id = int(request.session['GSE_FORCED_WAREHOUSE_ID'])
            if gse_wh_id in request.env['stock.warehouse'].sudo().search([('company_id', '=', self.company_id.id)]).ids:
                return gse_wh_id
            else:
                request.session.pop('GSE_FORCED_WAREHOUSE_ID')
        return super()._get_warehouse_available()