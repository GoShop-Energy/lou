# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockReport(models.Model):
    _inherit = 'stock.report'
    
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        readonly=True,
        auto_join=True,
        index=True,
        required=True,
        check_company=True,
        help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations."
    )
    def _select(self):
        select_str = """
            sm.id as id,
            sp.name as picking_name,
            sm.location_id as location_id,
            sp.date_done as date_done,
            sp.creation_date as creation_date,
            sp.scheduled_date as scheduled_date,
            sp.partner_id as partner_id,
            sp.is_backorder as is_backorder,
            sp.delay as delay,
            sp.delay > 0 as is_late,
            sp.cycle_time as cycle_time,
            spt.code as picking_type_code,
            spt.name as operation_type,
            p.id as product_id,
            sm.reference as reference,
            sm.picking_id as picking_id,
            sm.state as state,
            sm.product_qty as product_qty,
            sm.company_id as company_id,
            cat.id as categ_id
        """

        return select_str