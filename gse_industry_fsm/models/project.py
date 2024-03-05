# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError

class ProjectTask(models.Model):
    _inherit = "project.task"

    sale_order_id = fields.Many2one(
        "sale.order",
        "Sales Order",
        store=True,
        help="Sales order to which the task is linked.",
    )
    order_line_table = fields.Html(string="Order Line Table")
    order_line = fields.One2many(
        comodel_name="sale.order.line",
        related="sale_order_id.order_line",
        readonly=False,
    )

    delivery_count = fields.Integer(related="sale_order_id.delivery_count")
    picking_ids = fields.One2many(related="sale_order_id.picking_ids")
    partner_id = fields.Many2one(related="sale_order_id.partner_id")
    partner_service_id = fields.Many2one("res.partner", string="Service Location" , readonly=False)

    def action_view_delivery(self):
        return self._get_action_view_picking(self.picking_ids)

    def _get_action_view_picking(self, pickings):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.action_picking_tree_all"
        )
        if len(pickings) > 1:
            action["domain"] = [("id", "in", pickings.ids)]
        elif len(pickings) == 1:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = pickings.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def action_fs_navigate(self):
        if not self.partner_service_id.city or not self.partner_service_id.country_id:
            return {
                "name": _("Service Location"),
                "type": "ir.actions.act_window",
                "res_model": "res.partner",
                "res_id": self.partner_service_id.id,
                "view_mode": "form",
                "view_id": self.env.ref(
                    "industry_fsm.view_partner_address_form_industry_fsm"
                ).id,
                "target": "new",
            }
        return self.partner_service_id.action_partner_navigate()
    
    @api.onchange("partner_id", "sale_order_id")
    def onchange_partner_service_id(self):
        for task in self:
            task.partner_service_id = task.partner_id.address_get(['field_service'])['field_service'] if task.partner_id else False

    @api.onchange("stage_id")
    def onchange_stage_id(self):
        if self.stage_id and self.stage_id.name == 'Done':
            user = self.env.user
            if not user.has_group('gse_access_rights.group_stock_validator'):
                raise AccessError("You don't have permission to perform this action.")
            
            if not self.is_task_done():
                raise AccessError("Mandory steps uncompleted.")
            

    def action_fsm_validate(self, stop_running_timers=False):
        """ If All product are delivered, if the Worksheet is completed, At least one timesheet entry is recorded for the task and user has privileges :
           Task can be mark as done.
        """
        user = self.env.user
        if not user.has_group('gse_access_rights.group_stock_validator'):
            raise AccessError("You don't have permission to perform this action. Kindly contact your administrator.")
        
        if not self.is_task_done():
            error_message = (
                "Access Error: Mandatory Steps Uncompleted.\n"
                "-----------------------------------------\n"
                "- Some products still need to be delivered.\n"
                "- The timesheets aren't completed."
            )
            raise AccessError(error_message)

        return super().action_fsm_validate(stop_running_timers)
    
    def is_task_done(self):
        for record in self:
            if record.sale_order_id:
                is_done = bool(record.timesheet_ids) and record.sale_order_id.delivery_status in ['full', False]
            else:
                is_done = False
        return is_done

    
