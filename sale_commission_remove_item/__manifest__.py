# Copyright 2026 Madooit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Commission Remove Item",
    "summary": "Remove commission from sale order lines by rule",
    "version": "18.0.1.0.0",
    "author": "Madooit,Odoo Community Association (OCA)",
    "category": "Sales Management",
    "license": "AGPL-3",
    "depends": [
        "sale",
        "sale_commission_oca",
    ],
    "website": "https://github.com/OCA/commission",
    "maintainers": ["rodmad85"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_commission_remove_item_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
