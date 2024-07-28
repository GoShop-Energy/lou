# -*- coding: utf-8 -*-

{
    "name": "GSE Field Service",
    "summary": """
        Customisation of Field Service module for GoShop Energy""",
    "description": """
    """,
    "author": "Benjamin Kisenge",
    "website": "https://github.com/GoShop-Energy/field-service",
    "category": "Customizations",
    "version": "17.0.1.0",
    "license": "LGPL-3",
    "depends": [
        "base",
        "delivery",
        "industry_fsm",
        "industry_fsm_sale",
        "industry_fsm_stock",
        "industry_fsm_report",
        "product",
        "project",
        "sale_management",
        "sale_project",
        "sale_project_stock",
        "sale_timesheet", 
        "sale_timesheet_enterprise",
        "stock",
    ],
    "data": [
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "views/project_task_views.xml",
        "reports/project_report_views.xml",
    ],
    "images": [
        "static/src/img/location.png",
    ],
    "assets": {"web.assets_backend": []},
}