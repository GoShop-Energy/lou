# -*- coding: utf-8 -*-

{
    "name": "Gse display conversion USD ",
    "summary": """
        create a new module  conversion in USD for GoShop Energy""",
    "description": """
    """,
    "author": "Magana Mwinja Asiati",
    "depends": [
        "sale",
        "account",
        "gse_custo"
    ],
    "data": [ 
        "views/sale_order.xml",
        "views/account_move.xml",
        "views/report_templates.xml",
    ],
    "images": [ ],
    "assets": {"web.assets_backend": []},
}