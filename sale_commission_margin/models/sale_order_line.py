from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('price_subtotal', 'product_uom_qty', 'purchase_price', 'agent_ids.amount')
    def _compute_margin(self):
        for line in self:
            if line.qty_delivered and not line.product_uom_qty:
                calculated_subtotal = line.price_unit * line.qty_delivered
                line.margin = calculated_subtotal - (line.purchase_price * line.qty_delivered)
                line.margin_percent = calculated_subtotal and line.margin / calculated_subtotal
            else:
                line.margin = line.price_subtotal - (line.purchase_price * line.product_uom_qty)
                line.margin -= sum(line.agent_ids.mapped('amount'))
                line.margin_percent = line.price_subtotal and line.margin / line.price_subtotal
