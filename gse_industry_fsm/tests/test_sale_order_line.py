from odoo.tests.common import TransactionCase


class TestSaleOrderLine(TransactionCase):
    def setUp(self):
        super(TestSaleOrderLine, self).setUp()

        self.product = self.env["product.product"].create(
            {
                "name": "Screwdrivers Set",
            }
        )

        self.partner = self.env["res.partner"].create(
            {
                "name": "GoShop Energy",
            }
        )

        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )

        self.sale_order_line = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "product_id": self.product.id,
                "name": "Test Sale Order Line",
            }
        )

        self.project = self.env["project.task"].create(
            {
                "name": "Test Task Project",
            }
        )

        self.route_values = {
            "name": "Test Route",
            "warehouse_selectable": True,
        }

        self.view_location = self.env["stock.location"].search(
            [
                ("name", "=", "Your View Location Name"),
            ],
            limit=1,
        )

        self.lot_stock = self.env["stock.location"].search(
            [
                ("name", "=", "Your Lot Stock Name"),
            ],
            limit=1,
        )

    def test_timesheet_create_task_prepare_values(self):
        values = self.sale_order_line._timesheet_create_task_prepare_values(
            self.project
        )

        self.assertEqual(values.get("description"), self.sale_order.instruction)
        self.assertTrue(values.get("tag_ids"))
        self.assertIn("order_line_table", values)

    def test_prepare_default_tag_id_existing_tag(self):
        view_location = self.view_location
        lot_stock = self.lot_stock

        route = self.env["stock.route"].create(self.route_values)

        self.sale_order_line.warehouse_id = self.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse existing tag",
                "active": True,
                "company_id": self.env.company.id,
                "partner_id": self.env.company.partner_id.id,
                "view_location_id": view_location.id,
                "lot_stock_id": lot_stock.id,
                "code": "TEST",
                "route_ids": [(6, 0, [route.id])],
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
            }
        )

        tag_values = self.sale_order_line._prepare_default_tag_id()
        self.assertTrue(tag_values and tag_values[0] and tag_values[0][1])

    def test_prepare_default_tag_id_new_tag(self):
        view_location = self.view_location
        lot_stock = self.lot_stock

        route = self.env["stock.route"].create(self.route_values)
        self.sale_order_line.warehouse_id = self.env["stock.warehouse"].create(
            {
                "name": "New Test Warehouse",
                "active": True,
                "company_id": self.env.company.id,
                "partner_id": self.env.company.partner_id.id,
                "view_location_id": view_location.id,
                "lot_stock_id": lot_stock.id,
                "code": "TEST",
                "route_ids": [(6, 0, [route.id])],
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
            }
        )

        tag_values = self.sale_order_line._prepare_default_tag_id()
        self.assertTrue(tag_values and tag_values[0] and tag_values[0][1])

    def test_compute_order_line_table(self):
        self.sale_order_line.order_id.order_line = [
            (
                0,
                0,
                {
                    "product_id": self.product.id,
                    "name": "Test Product",
                    "product_uom_qty": 5,
                },
            ),
        ]
        order_line_table = self.sale_order_line._compute_order_line_table()

        self.assertIn("<table", order_line_table)
        self.assertIn("Test Product", order_line_table)
        self.assertIn("5", order_line_table)
