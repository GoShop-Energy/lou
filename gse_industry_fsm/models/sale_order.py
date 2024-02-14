# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}

class SaleOrder(models.Model):
    _inherit = "sale.order"

    instruction = fields.Html(
        string="Service Instructions",
        store=True,
        readonly=False,
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        related="order_line.product_id",
        string="Product",
    )

    service_tracking = fields.Selection(
        related="product_id.service_tracking", string="Service Tracking"
    )

    has_service = fields.Boolean(
        string="Has Service Product", compute="_compute_has_service", store=True
    )

    parent_id = fields.Many2one("res.partner")
    partner_service_id = fields.Many2one(
        comodel_name='res.partner',
        string="Service Location",
        compute='_compute_partner_service_id',
        store=True, readonly=False, required=True, precompute=True,
        states=LOCKED_FIELD_STATES,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    
    terms_type = fields.Selection(related="company_id.terms_type")

    @api.depends("order_line.product_id.type", "order_line.product_id.service_tracking")
    def _compute_has_service(self):
        for order in self:
            order.has_service = any(
                line.product_id.type == "service" and line.product_id.service_tracking != "no"
                for line in order.order_line
            )

    @api.depends('partner_id')
    def _compute_partner_service_id(self):
        for order in self:
            order.partner_service_id = order.partner_id.address_get(['field_service'])['field_service'] if order.partner_id else False