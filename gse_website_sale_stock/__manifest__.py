# -*- coding: utf-8 -*-
{
    "name": "gse_website_sale_stock",
    "summary": """Customizations de l'ecommerce pour Goshop Energy""",
    "description": """""",
    "author": "Sébastien Bühl",
    "website": "http://www.buhl.be",
    "category": "Customizations",
    "version": "17.0.1.0",
    "license": "LGPL-3",

    # any module necessary for this one to work correctly
    "depends": [
        "website_sale_stock",
    ],
    "data": [
    ],
    "demo": [
        "data/demo.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "gse_website_sale_stock/static/src/js/variant_mixin.js",
            "gse_website_sale_stock/static/src/xml/website_sale_stock_product_availability.xml",
        ],
    },
}