from odoo import models, fields


class CloudStorageSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    azure_container_name = fields.Char('Container Name',
        config_parameter='azure_container_name')
    azure_connect_str = fields.Char('Connection String',
        config_parameter='azure_connect_str',
        help='Set your Azure storage account connection string',
    )

    google_cloud_bucket_name = fields.Char('Bucket Name',
        config_parameter='google_cloud_bucket_name')
    google_cloud_account_info = fields.Char('Json Key',
        config_parameter='google_cloud_account_info',
        help='Set your Google services account json key file content',
    )

    cloud_storage = fields.Selection(
        selection=[
            ('file', 'Odoo Filestore'),
            ('azure', 'Azure Blob Storage'),
            ('google', 'Google Cloud Storage'),
        ], string='Storage Type', required=True
    )

    def get_values(self):
        res = super().get_values()
        res['cloud_storage'] = self.env['ir.attachment']._cloud_storage()
        return res

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param('ir_attachment.cloud_storage', self.cloud_storage)
