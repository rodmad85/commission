from odoo.fields import Command
from odoo.addons.sale.tests.common import SaleCommon


class TestSaleCommissionMargin(SaleCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.agent = cls.env['res.partner'].create({
            'name': 'Test Agent',
            'agent': True,
        })
        cls.commission = cls.env['commission'].create({
            'name': '10% Fixed Commission',
            'commission_type': 'fixed',
            'fix_qty': 10.0,
        })

    def _create_agent_line(self, order_line, agent=None, commission=None):
        self.env['sale.order.line.agent'].create({
            'object_id': order_line.id,
            'agent_id': (agent or self.agent).id,
            'commission_id': (commission or self.commission).id,
        })

    def test_margin_with_commission(self):
        self.product.standard_price = 700.0
        order = self.empty_order
        order.order_line = [
            Command.create({
                'price_unit': 1000.0,
                'product_uom_qty': 10.0,
                'product_id': self.product.id,
            }),
        ]
        line = order.order_line
        self._create_agent_line(line)
        order.action_confirm()
        commission_amount = sum(line.agent_ids.mapped('amount'))
        expected_margin = (1000.0 - 700.0) * 10.0 - commission_amount
        self.assertAlmostEqual(line.margin, expected_margin)
        self.assertAlmostEqual(order.margin, expected_margin)

    def test_margin_without_commission(self):
        self.product.standard_price = 500.0
        order = self.empty_order
        order.order_line = [
            Command.create({
                'price_unit': 1000.0,
                'product_uom_qty': 5.0,
                'product_id': self.product.id,
            }),
        ]
        line = order.order_line
        order.action_confirm()
        expected_margin = (1000.0 - 500.0) * 5.0
        self.assertAlmostEqual(line.margin, expected_margin)
        self.assertAlmostEqual(order.margin, expected_margin)

    def test_margin_multiple_agents(self):
        self.product.standard_price = 300.0
        agent2 = self.env['res.partner'].create({
            'name': 'Second Agent',
            'agent': True,
        })
        commission2 = self.env['commission'].create({
            'name': '5% Fixed Commission',
            'commission_type': 'fixed',
            'fix_qty': 5.0,
        })
        order = self.empty_order
        order.order_line = [
            Command.create({
                'price_unit': 500.0,
                'product_uom_qty': 10.0,
                'product_id': self.product.id,
            }),
        ]
        line = order.order_line
        self._create_agent_line(line, commission=self.commission)
        self._create_agent_line(line, agent=agent2, commission=commission2)
        order.action_confirm()
        total_commission = sum(line.agent_ids.mapped('amount'))
        expected_margin = (500.0 - 300.0) * 10.0 - total_commission
        self.assertAlmostEqual(line.margin, expected_margin)
        self.assertAlmostEqual(order.margin, expected_margin)
