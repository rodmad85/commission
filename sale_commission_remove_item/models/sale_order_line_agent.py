# Copyright 2026 Madooit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLineAgent(models.Model):
    _inherit = "sale.order.line.agent"

    @api.depends(
        "commission_id",
        "object_id.price_subtotal",
        "object_id.product_id",
        "object_id.product_uom_qty",
        "object_id.commission_removed",
    )
    # pylint: disable=W8110
    def _compute_amount(self):
        for line in self:
            if line.object_id.commission_removed:
                line.amount = 0.0
            else:
                super(SaleOrderLineAgent, line)._compute_amount()
