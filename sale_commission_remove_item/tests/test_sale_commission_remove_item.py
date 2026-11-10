# Copyright 2026 Madooit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleCommissionRemoveItem(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_category_model = cls.env["product.category"]
        cls.product_model = cls.env["product.product"]
        cls.partner_model = cls.env["res.partner"]
        cls.commission_model = cls.env["commission"]
        cls.remove_item_model = cls.env["sale.commission.remove.item"]
        cls.sale_order_model = cls.env["sale.order"]

        # Product category used by the exclusion rule
        cls.category = cls.product_category_model.create(
            {"name": "No Commission Category"}
        )
        # Product belonging to the category
        cls.product = cls.product_model.create(
            {
                "name": "Product No Commission",
                "categ_id": cls.category.id,
                "type": "consu",
            }
        )
        # Product belonging to another category (negative case)
        cls.other_category = cls.product_category_model.create(
            {"name": "Other Category"}
        )
        cls.other_product = cls.product_model.create(
            {
                "name": "Product Other",
                "categ_id": cls.other_category.id,
                "type": "consu",
            }
        )

        # Commission and agent used to generate commissions on sale lines
        cls.commission = cls.commission_model.create(
            {
                "name": "Test Commission",
                "commission_type": "fixed",
                "fix_qty": 10.0,
                "amount_base_type": "gross_amount",
            }
        )
        cls.agent = cls.partner_model.create(
            {
                "name": "Test Agent",
                "agent": True,
                "commission_id": cls.commission.id,
            }
        )
        cls.customer = cls.partner_model.create(
            {"name": "Test Customer", "agent_ids": [(4, cls.agent.id)]}
        )

    def _create_remove_item(self, field_name, field_value):
        field = self.env["ir.model.fields"].search(
            [("model", "=", "sale.order"), ("name", "=", field_name)],
            limit=1,
        )
        self.assertTrue(field, f"Field {field_name} not found on sale.order")
        return self.remove_item_model.create(
            {
                "name": "Remove commission rule",
                "product_category_id": self.category.id,
                "field_id": field.id,
                "value": field_value,
            }
        )

    def _create_order_line(self, order, product, agent_commission=True):
        line_vals = {
            "order_id": order.id,
            "product_id": product.id,
            "product_uom_qty": 1.0,
            "price_unit": 100.0,
        }
        if agent_commission:
            line_vals["agent_ids"] = [
                (0, 0, {"agent_id": self.agent.id, "commission_id": self.commission.id})
            ]
        return self.env["sale.order.line"].create(line_vals)

    def test_remove_commission_by_rule(self):
        """Commission must be removed when category + field value match."""
        self._create_remove_item("client_order_ref", "NO-COMMISSION")
        order = self.sale_order_model.create(
            {
                "partner_id": self.customer.id,
                "client_order_ref": "NO-COMMISSION",
            }
        )
        line = self._create_order_line(order, self.product)
        # Recompute agents so the exclusion rule is evaluated
        line._compute_agent_ids()
        self.assertTrue(line.commission_removed)
        self.assertEqual(line.agent_ids, self.env["sale.order.line.agent"])

    def test_commission_kept_when_field_value_differs(self):
        """Commission must be kept when the field value does not match."""
        self._create_remove_item("client_order_ref", "NO-COMMISSION")
        order = self.sale_order_model.create(
            {
                "partner_id": self.customer.id,
                "client_order_ref": "WITH-COMMISSION",
            }
        )
        line = self._create_order_line(order, self.product)
        line._compute_agent_ids()
        self.assertFalse(line.commission_removed)
        self.assertNotEqual(line.agent_ids, self.env["sale.order.line.agent"])

    def test_commission_kept_when_other_category(self):
        """Commission must be kept when the product is in another category."""
        self._create_remove_item("client_order_ref", "NO-COMMISSION")
        order = self.sale_order_model.create(
            {
                "partner_id": self.customer.id,
                "client_order_ref": "NO-COMMISSION",
            }
        )
        line = self._create_order_line(order, self.other_product)
        line._compute_agent_ids()
        self.assertFalse(line.commission_removed)
        self.assertNotEqual(line.agent_ids, self.env["sale.order.line.agent"])

    def test_commission_amount_zero_when_removed(self):
        """Commission amount must be zero when the line is excluded."""
        self._create_remove_item("client_order_ref", "NO-COMMISSION")
        order = self.sale_order_model.create(
            {
                "partner_id": self.customer.id,
                "client_order_ref": "NO-COMMISSION",
            }
        )
        line = self._create_order_line(order, self.product)
        line._compute_agent_ids()
        self.assertTrue(line.commission_removed)
        for agent_line in line.agent_ids:
            agent_line._compute_amount()
            self.assertEqual(agent_line.amount, 0.0)

    def test_form_create_line_with_matching_field(self):
        """Creating a line from the form with a matching field removes agents."""
        self._create_remove_item("client_order_ref", "NO-COMMISSION")
        order_form = Form(self.sale_order_model)
        order_form.partner_id = self.customer
        order_form.client_order_ref = "NO-COMMISSION"
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product
        order = order_form.save()
        line = order.order_line
        self.assertTrue(line.commission_removed)
        self.assertEqual(line.agent_ids, self.env["sale.order.line.agent"])
