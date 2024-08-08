import json
from io import BytesIO
from google.cloud.storage import Client
from odoo import api, models


class CloudStorageGoogleAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _generate_signed_url_google(self, blob):
        return blob.generate_signed_url(
            method="GET",
            expiration=self._get_expiry_date()
        )

    @api.model
    def _get_client_google(self):
        account_info = json.loads(
            self.env['ir.config_parameter'].sudo().get_param('google_cloud_account_info')
        )
        return Client.from_service_account_info(account_info)

    def _get_blob_google(self):
        bucket_name = self.env['ir.config_parameter'].sudo().get_param('google_cloud_bucket_name')
        blob_name = self._get_blob_name()
        client = self._get_client_google()
        return client.get_bucket(bucket_name).blob(blob_name)

    def _upload_file_google(self):
        blob = self._get_blob_google()
        with BytesIO(self.raw) as buffer:
            blob.upload_from_file(buffer, content_type=self.mimetype)
        return self._generate_signed_url_google(blob)
