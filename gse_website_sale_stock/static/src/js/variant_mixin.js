/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { Dialog } from "@web/core/dialog/dialog";
const { Component } = owl;

export class WarehouseSelectDialog extends Component {
    setup() {
        this.size = 'md';
        this.title = 'Select another warehouse';
    }

    _onConfirm() {
        const selectedWarehouse = $('input[name="gse_select_warehouse"]:checked');
        const whId = selectedWarehouse[0].value;
        const search = new URL(window.location).searchParams;
        search.set("gse_forced_warehouse_id", whId);
        window.location.search = search.toString();
        this.props.close();
    }
}

WarehouseSelectDialog.template = 'gse_website_sale_stock.popup_content_warehouse_select_dialog';
WarehouseSelectDialog.props = {
    qty: { type: Object },
    close: { type: Function },
};
WarehouseSelectDialog.components = { Dialog };


export class CompanySelectDialog extends Component {
    setup() {
        this.size = 'md';
        this.title = 'Select another country';
    }

    _onConfirm() {
        const selectedWarehouse = $('input[name="gse_select_company"]:checked');
        const companyDomain = selectedWarehouse[0].value;
        let currentUrl = new URL(window.location);
        window.location = currentUrl.href.replace(currentUrl.origin, companyDomain);
    }
}

CompanySelectDialog.template = 'gse_website_sale_stock.popup_content_company_select_dialog';
CompanySelectDialog.props = {
    companies: { type: Object },
    close: { type: Function },
};
CompanySelectDialog.components = { Dialog };

publicWidget.registry.WebsiteSale.include({
    events: Object.assign({}, publicWidget.registry.WebsiteSale.prototype.events, {
        'click .gse_change_company': '_onChangeCompanyClick',
        'click .gse_change_warehouse': '_onChangeWarehouseClick',
    }),
    init() {
        this._super(...arguments);
        this.dialogService = this.bindService("dialog");
    },
    _onChangeWarehouseClick(ev) {
        const gseWhQty = $(ev.target).data('gse-wh-qty');
        this.call("dialog", "add", WarehouseSelectDialog, {
            'qty': gseWhQty,
        });
    },

    _onChangeCompanyClick(ev) {
        const gseWebsiteCompanies = $(ev.target).data('gse-website-companies');
        this.call("dialog", "add", CompanySelectDialog, {
            'companies': gseWebsiteCompanies,
        });
    },
});
