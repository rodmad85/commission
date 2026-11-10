# Copyright 2026 Madooit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleCommissionRemoveItem(models.Model):
    _name = "sale.commission.remove.item"
    _description = "Sale Commission Remove Item"
    _order = "product_category_id, field_id, id"

    name = fields.Char(required=True)
    product_category_id = fields.Many2one(
        comodel_name="product.category",
        string="Product Category",
        required=True,
        help="Product category this exclusion rule applies to. "
        "It also applies to the child categories of the selected one.",
    )
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Sale Order Field",
        domain=[("model", "=", "sale.order")],
        required=True,
        help="Field of the sales order form used to evaluate the exclusion. "
        "All fields of the sale order form are available for selection.",
    )
    field_type = fields.Char(
        compute="_compute_field_type",
        store=True,
        readonly=True,
    )
    value = fields.Char(
        help="Value that, together with the selected product category and "
        "sale order field, removes the commission from the sale order line. "
        "For relational fields use the record id or its name.",
    )
    active = fields.Boolean(default=True)

    @api.depends("field_id")
    def _compute_field_type(self):
        for item in self:
            item.field_type = item.field_id.ttype if item.field_id else False

    @api.constrains("field_id")
    def _check_field_id(self):
        for item in self:
            if item.field_id and item.field_id.model != "sale.order":
                raise ValidationError(
                    _("The selected field must belong to the Sale Order model.")
                )

    def _values_match(self, order_value, configured_value, field_type):
        """Compare a value read from the sale order with the configured one."""
        if not configured_value:
            return False
        configured_value = configured_value.strip()
        if field_type == "many2one":
            if isinstance(order_value, models.BaseModel):
                return str(order_value.id) == configured_value or (
                    order_value.display_name == configured_value
                )
            return str(order_value) == configured_value
        if field_type == "many2many":
            ids = [str(record.id) for record in order_value]
            names = [record.display_name for record in order_value]
            return configured_value in ids or configured_value in names
        if field_type in ("char", "text", "html", "selection"):
            return str(order_value) == configured_value
        if field_type == "boolean":
            return (
                str(bool(order_value)) == configured_value
                or str(order_value) == configured_value
            )
        if field_type in ("float", "monetary", "integer"):
            try:
                return (
                    float_compare(
                        float(order_value or 0.0),
                        float(configured_value),
                        precision_digits=2,
                    )
                    == 0
                )
            except (TypeError, ValueError):
                return str(order_value) == configured_value
        if field_type in ("date", "datetime"):
            return str(order_value) == configured_value
        return str(order_value) == configured_value

    def _is_excluded(self, order_line):
        """Return True if the sale order line must not be commissioned."""
        self.ensure_one()
        if not order_line.product_id or not order_line.order_id:
            return False
        # Product category (include the selected category and its parents)
        categ = order_line.product_id.categ_id
        categ_ids = []
        while categ:
            categ_ids.append(categ.id)
            categ = categ.parent_id
        if self.product_category_id.id not in categ_ids:
            return False
        field_name = self.field_id.name
        order_value = order_line.order_id[field_name]
        return self._values_match(order_value, self.value, self.field_id.ttype)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    commission_removed = fields.Boolean(
        compute="_compute_commission_removed",
        store=True,
        readonly=True,
        help="Checked when a commission removal rule matches this line.",
    )

    @api.depends("order_id", "product_id")
    def _compute_commission_removed(self):
        items = self.env["sale.commission.remove.item"].search([("active", "=", True)])
        for line in self:
            line.commission_removed = any(item._is_excluded(line) for item in items)

    @api.depends(
        "order_id.partner_id",
        "order_id",
        "product_id",
        "commission_removed",
    )
    # pylint: disable=W8110
    def _compute_agent_ids(self):
        super()._compute_agent_ids()
        for line in self:
            if line.commission_removed:
                line.agent_ids = [(5, 0, 0)]
