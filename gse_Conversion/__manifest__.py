# -*- coding: utf-8 -*-

{
    "name": "Gse conversion",
    "summary": """
        Customisation of Field Service module for GoShop Energy""",
    "description": """
    """,
    "author": "Magana Mwinja Asiati",
    "website": "https://github.com/GoShop-Energy/field-service",
    "category": "Customizations",
    "version": "0.1.8.7",
    "license": "LGPL-3",
    "depends": [
        "base",
        "delivery",
        "industry_fsm",
        "industry_fsm_report",
        "product",
        "project",
        "sale_management",
        "sale_project",
        "stock",
        "stock_enterprise",
        "mrp",
        "sale",
        "account",
    ],
    "data": [ 
        "views/sale_order.xml",
        "views/account_move.xml",
        "views/report_templates.xml",
    ],
    "images": [ ],
    "assets": {"web.assets_backend": []},
}