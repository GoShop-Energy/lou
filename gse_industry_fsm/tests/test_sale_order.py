from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("-at_install", "post_install")
class TestSaleOrder(TransactionCase):
    def setUp(self):
        super(TestSaleOrder, self).setUp()

        self.company = self.env["res.company"].create({"name": "Test Company 1"})

        self.partner = self.env["res.partner"].create(
            {
                "name": "Test Customer",
                "type": "contact",
            }
        )

        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "company_id": self.company.id,
            }
        )

    def test_compute_has_service(self):
        service_product = self.env["product.product"].create(
            {
                "name": "Test Service",
                "type": "service",
                "service_tracking": "task_global_project",
            }
        )
        sale_order_line = self.env["sale.order.line"].create(
            {
                "order_id": self.sale_order.id,
                "product_id": service_product.id,
            }
        )

        self.sale_order._compute_has_service()
        self.assertTrue(self.sale_order.has_service)

    def test_compute_partner_service_id(self):
        field_service_child = self.env["res.partner"].create(
            {
                "name": "Field Service Child",
                "type": "field_service",
                "parent_id": self.partner.id,
            }
        )

        self.sale_order._compute_partner_service_id()
        self.assertEqual(self.sale_order.partner_service_id, field_service_child)

        field_service_child_2 = self.env["res.partner"].create(
            {
                "name": "Field Service Child 2",
                "type": "field_service",
                "parent_id": self.partner.id,
            }
        )

        self.sale_order._compute_partner_service_id()
        self.assertEqual(self.sale_order.partner_service_id, field_service_child)
