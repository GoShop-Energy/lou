# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"
    _description = "Extended Partner Model for Field Service usage"

    partner_service_id = fields.Many2one(
        'res.partner',
        string="Service Location",
        help="Select a service location related to this partner."
    )
    type = fields.Selection(
        selection_add=[("field_service", "Service Location")],
        help="Use to identify local service sites of the customer.",
    )
    field_service_type = fields.Selection(
        [
            ("solar", "Solar"),
            ("water_heater", "Water Heater"),
            ("genset", "Genset"),
            ("air_conditioning", "Air Conditioning"),
            ("other", "Other"),
        ],
        string="Type",
        help="Select the type of field service",
    )

    equipement_name = fields.Char(string="Equipement")
    other_description = fields.Char(string="Site Description")
    service_field_count = fields.Integer(compute="_compute_service_field_count")

    def _compute_service_field_count(self):
        for record in self:
            record.service_field_count = self.env["res.partner"].search_count(
                [("type", "=", "field_service"),("id", "in", self.child_ids.ids)]
            )

    def get_field_service(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Service Location",
            "view_mode": "tree,form",
            "res_model": "res.partner",
            "domain": [("type", "=", "field_service"),("id", "in", self.child_ids.ids)],
            "context": {
                "create": False,
                "view_mode": "tree,form",
                "target": "main",
            },
        }
