# -*- coding: utf-8 -*-

{
    "name": "GSE Account",
    "summary": """
        Customisation of Account module for GoShop Energy""",
    "description": """
    """,
    "author": "Benjamin Kisenge",
    "website": "https://dev--glowing-faun-e9789d.netlify.app",
    "category": "Customizations",
    'version': '17.0.1.0.0',
    "license": "LGPL-3",
    "depends": [
        "base",
        "account",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "views/account_views.xml",
        "reports/account_report_views.xml",
    ],
}