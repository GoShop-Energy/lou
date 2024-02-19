# -*- coding: utf-8 -*-
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


@tagged("-at_install", "post_install")
class TestProjectTask(TransactionCase):
    def setUp(self):
        super(TestProjectTask, self).setUp()

        self.sale_order = self.env["sale.order"].create(
            {
                "name": "Test Sale Order",
                "partner_id": self.env.ref("base.partner_demo").id,
            }
        )

        self.project_task = self.env["project.task"].create(
            {
                "name": "Test Project Task",
                "sale_order_id": self.sale_order.id,
            }
        )

    def test_get_action_view_picking(self):
        pickings = self.env["stock.picking"].search([("id", "=", False)])

        action = self.project_task._get_action_view_picking(pickings)
        self.assertEqual(action["type"], "ir.actions.act_window_close")

        delivery = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "partner_id": self.sale_order.partner_id.id,
            }
        )
        action = self.project_task._get_action_view_picking(delivery)
        self.assertEqual(action["res_model"], "stock.picking")
        self.assertEqual(
            action["views"], [(self.env.ref("stock.view_picking_form").id, "form")]
        )
        self.assertEqual(action["res_id"], delivery.id)

        delivery2 = self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "partner_id": self.sale_order.partner_id.id,
            }
        )
        action = self.project_task._get_action_view_picking(delivery | delivery2)
        self.assertEqual(action["domain"], [("id", "in", (delivery | delivery2).ids)])

    def test_action_fs_navigate(self):
        action = self.project_task.action_fs_navigate()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "res.partner")
        self.assertEqual(action["res_id"], self.project_task.partner_service_id.id)
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(
            action["view_id"],
            self.env.ref("industry_fsm.view_partner_address_form_industry_fsm").id,
        )
        self.assertEqual(action["target"], "new")
