import base64
import zipfile
import io

from odoo import api, models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    @api.multi
    def to_zip(self, records, archive_name):
        model_name = "account.account_invoices"
        in_memory_zip = io.BytesIO()
        pdf_report_func = self.env.ref(model_name).sudo().render_qweb_pdf

        def pdf_map(record):
            file_name = "{}.{}".format(
                record.number,
                "pdf",
            )
            return {
                "name": file_name,
                "data": pdf_report_func([record.id])[0]
            }

        pdf_list = map(pdf_map, records)

        with zipfile.ZipFile(in_memory_zip, "a") as zip_archive:
            for pdf in pdf_list:
                zip_archive.writestr(pdf['name'], data=pdf['data'])

        archive_attachment = (
            self.env["ir.attachment"]
            .sudo()
            .create(
                {
                    "name": "{}-{}.{}".format("temporary", archive_name, "zip"),
                    "public": False,
                    "datas": base64.b64encode(in_memory_zip.getvalue()),
                    "type": "binary",
                }
            )
        )

        return {
            "type": "ir.actions.act_url",
            "url": archive_attachment.local_url,
        }
