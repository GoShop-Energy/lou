import datetime
import logging
import requests
from base64 import b64encode
from odoo import api, models

_logger = logging.getLogger(__name__)

EXPIRY_DATE = datetime.datetime(2200, 1, 1)


class CloudStorageAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _cloud_storage(self):
        return self.env['ir.config_parameter'].sudo().get_param('ir_attachment.cloud_storage', 'file')

    @api.model
    def _get_expiry_date(self):
        return EXPIRY_DATE

    def _get_blob_name(self):
        # id as a prefix so that the blob name is unique
        return f"{self.id}/{self.name}"

    def _upload_file(self):
        self.ensure_one()
        try:
            upload_file = getattr(self, f"_upload_file_{self._cloud_storage()}")
        except AttributeError:
            raise NotImplementedError()
        return upload_file()

    def _allowed_to_move(self):
        # must be binary but not field attachment
        # must have a res_id to make sure it is not an asset
        self.ensure_one()
        return bool(self.type == "binary" and not self.res_field and self.res_id and self.raw)

    def move_to_cloud(self):
        if self._cloud_storage() == 'file':
            return

        for attach in self.filtered(lambda a: a._allowed_to_move()):

            # mark local file to possibly garbage-collect it
            self._file_delete(attach.store_fname)
            try:
                attach.write({
                    'type': 'url',
                    'url': attach._upload_file(),
                    'datas': False,
                    'store_fname': False,
                    'mimetype': attach.mimetype,
                })
                _logger.info(f"{attach} moved to {self._cloud_storage()}")

            except Exception as e:
                _logger.error(str(e))

    def _post_add_create(self):
        # hook after file upload in chatter
        super()._post_add_create()
        self.move_to_cloud()

    def _get_raw(self):
        self.ensure_one()
        if self._cloud_storage() == "file" or self.type == "binary":
            return self.raw
        try:
            return requests.get(self.url).content
        except Exception as e:
            _logger.error(str(e))
            return False

    def _compute_datas(self):
        # use context get_datas = False to prevent fetching from cloud
        # e.g. attachment list views
        res = super()._compute_datas()
        if self.env.context.get('get_datas', True):
            for attach in self.filtered(lambda a: not a.datas):
                attach.datas = b64encode(attach._get_raw() or b'')
        return res
