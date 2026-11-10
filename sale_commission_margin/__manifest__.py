{
    'name': 'Margins in Sales Orders with Commissions',
    'version': '18.0.1.0.0',
    'category': 'Sales/Sales',
    'description': """
Bridge module between sale_margin and sale_commission_oca.
Subtracts commissions from the margin calculation in sales orders.
    """,
    'depends': [
        'sale_margin',
        'sale_commission_oca',
    ],
    'license': 'LGPL-3',
}
