import json
from google.cloud.storage import Client
from google.auth.credentials import AnonymousCredentials
from odoo import api, models


class CloudStorageGoogleAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _generate_signed_url_google(self, blob):
        bucket = self.env['ir.config_parameter'].sudo().get_param('google_cloud_bucket_name')
        account_info = json.loads(
            self.env['ir.config_parameter'].sudo().get_param('google_cloud_account_info')
        )
        return f"{account_info['api_endpoint']}/storage/v1/b/{bucket}/o/{blob.name}?alt=media"

    @api.model
    def _get_client_google(self):
        account_info = json.loads(
            self.env['ir.config_parameter'].sudo().get_param('google_cloud_account_info')
        )
        return Client(
            credentials=AnonymousCredentials(),
            project="test",
            client_options=account_info,
        )
