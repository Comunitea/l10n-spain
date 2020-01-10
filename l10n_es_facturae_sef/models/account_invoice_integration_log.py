# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import io
import zipfile
from odoo import models, fields
import datetime
import pytz
import logging
import hashlib
from lxml import etree

try:
    from zeep import Client
    from zeep.wsse.username import UsernameToken
    from zeep.wsse.utils import WSU, get_unique_id
except (ImportError, IOError) as err:
    logging.info(err)
import base64


class AccountInvoiceIntegration(models.Model):
    _inherit = "account.invoice.integration.log"

    def connect_sef(self):
        user = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("account.invoice.sef.user", default=None)
        )
        password = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("account.invoice.sef.password", default=None)
        )
        timestamp_token = WSU.Timestamp()
        timestamp_token.attrib["Id"] = get_unique_id()

        today = datetime.datetime.utcnow()
        today = today.replace(tzinfo=pytz.utc, microsecond=0)
        timestamp_elements = [
            WSU.Created(today.strftime("%Y-%m-%dT%H:%M:%SZ")),
            WSU.Expires(
                (today + datetime.timedelta(minutes=10)).strftime(
                    "%Y-%m-%dT%H:%M:%SZ"
                )
            ),
        ]
        timestamp_token.extend(timestamp_elements)
        password = base64.b64encode(
            hashlib.md5(password.encode("utf-8")).digest()
        ).decode()
        # https://github.com/mvantellingen/python-zeep/pull/1037
        client = Client(
            wsdl=self.env["ir.config_parameter"]
            .sudo()
            .get_param("account.invoice.sef.server", default=None),
            wsse=UsernameToken(
                user,
                password,
                use_digest=True,
                timestamp_token=timestamp_token,
                use_zulu_timestamp=True,
            ),
        )
        return client

    def update_method(self):
        if self.integration_id.method_id == self.env.ref(
            "l10n_es_facturae_sef.integration_sef"
        ):
            client = self.connect_sef()
            response = client.service.SEF_Consulta_Estados(
                self.integration_id.register_number
            )
            if response.Resultado in ("OK", "KO"):
                response_file = io.BytesIO(response.MatrizArchivo)
                response_zip = zipfile.ZipFile(response_file)
                # Inside the zip file there is a folder and the xml response inside the folder.
                xml_files = [
                    x for x in response_zip.namelist() if x.endswith(".xml")
                ]
                if len(xml_files) != 1:
                    raise Exception()
                response_xml = response_zip.read(xml_files[0])
                root = etree.fromstring(response_xml)
                if response.Resultado == "OK":
                    estado_node = root.xpath(
                        "/SEF_Consulta_Estados/Consulta_Estados/Estado_Actual"
                    )
                    if not estado_node:
                        raise Exception()
                    estado_node = estado_node[0]
                    codigo_estado = estado_node.find("Codigo_Estado").text
                    self.integration_id.integration_status = (
                        "sef-" + codigo_estado
                    )
                    self.state = "sent"
                    return
                    self.result_code = response.resultado.codigo
                    self.log = response.resultado.descripcion
                else:
                    resultado_node = root.xpath(
                        "/SEF_Consulta_Estados/Cabecera/Resultado"
                    )
                    if not resultado_node:
                        raise Exception()
                    resultado_node = resultado_node[0]
                    codigo_respuesta = resultado_node.find(
                        "Codigo_Respuesta"
                    ).text
                    detalle_respuesta = resultado_node.find(
                        "Detalle_Respuesta"
                    ).text
                    self.state = "failed"
                    self.log = "{} - {}".format(
                        codigo_respuesta, detalle_respuesta
                    )
            else:
                self.state = "failed"
                self.log = response.Resultado

            return
        return super(AccountInvoiceIntegration, self).update_method()

    def cancel_method(self):
        # if self.integration_id.method_id == self.env.ref(
        #     "l10n_es_facturae_sef.integration_sef"
        # ):
        #     invoice = self.integration_id.invoice_id
        #     client = self.connect_sef()
        #     report = self.env.ref('l10n_es_facturae_sef.report_anulacion_factura')
        #     xml_anulacion = report.render_qweb_xml(self.ids, {})[0]
        #     import ipdb; ipdb.set_trace()
        #     response = client.service.SEF_Presentar_Propuestas_Anulacion(
        #         xml_anulacion
        #     )
        #     if response.Resultado in ('OK', 'KO'):
        #         import ipdb; ipdb.set_trace()
        #     else:
        #         self.state = 'failed'
        #         self.log = response.Resultado
        #     return
        #     import ipdb; ipdb.set_trace()
        #     self.result_code = response.resultado.codigo
        #     self.log = response.resultado.descripcion
        #     if self.result_code == "0":
        #         self.state = "sent"
        #         self.integration_id.state = "cancelled"
        #         self.integration_id.can_cancel = False
        #     else:
        #         self.state = "failed"
        #     return
        return super(AccountInvoiceIntegration, self).cancel_method()

    def send_method(self):
        if self.integration_id.method_id == self.env.ref(
            "l10n_es_facturae_sef.integration_sef"
        ):
            client = self.connect_sef()
            anexos_list = []
            if self.integration_id.attachment_ids:
                for attachment in self.integration_id.attachment_ids:
                    anexo = client.get_type("ns0:Adjunto")(
                        base64.b64decode(attachment.datas),
                        attachment.datas_fname,
                        attachment.mimetype,
                    )
                    anexos_list.append(anexo)
            anexos = client.get_type("ns0:ArrayOfAdjunto")(anexos_list)
            response = client.service.enviarFactura(
                base64.b64decode(self.integration_id.attachment_id.datas),
                anexos,
            )
            if response.Resultado in ("OK", "KO"):
                response_file = io.BytesIO(response.MatrizArchivo)
                response_zip = zipfile.ZipFile(response_file)
                response_xml = response_zip.read("RespuestaWS.xml")
                root = etree.fromstring(response_xml)
                if response.Resultado == "KO":
                    resultado_node = root.xpath(
                        "/SEF_Presentar_Factura/Cabecera/Resultado"
                    )
                    if not resultado_node:
                        raise Exception()
                    resultado_node = resultado_node[0]
                    codigo_respuesta = resultado_node.find(
                        "Codigo_Respuesta"
                    ).text
                    detalle_respuesta = resultado_node.find(
                        "Detalle_Respuesta"
                    ).text
                    self.integration_id.state = "failed"
                    self.state = "failed"
                    self.log = "{} - {}".format(
                        codigo_respuesta, detalle_respuesta
                    )
                else:

                    self.env["ir.attachment"].create(
                        {
                            "name": response.NombreArchivo,
                            "datas": base64.b64encode(response.MatrizArchivo),
                            "datas_fname": response.NombreArchivo,
                            "res_model": "account.invoice",
                            "res_id": self.integration_id.invoice_id.id,
                        }
                    )
                    factura_node = root.xpath("/SEF_Presentar_Factura/Factura")
                    if not factura_node:
                        raise Exception()
                    factura_node = factura_node[0]
                    self.integration_id.state = "sent"
                    self.integration_id.register_number = factura_node.find(
                        "CVE"
                    ).text
                    self.integration_id.can_update = True
                    self.integration_id.can_send = False
                    self.integration_id.can_cancel = True
                    self.state = "sent"
            else:
                # Error en la ejecución de la petición
                self.integration_id.state = "failed"
                self.state = "failed"
                self.log = response.Resultado
            return
        return super(AccountInvoiceIntegration, self).send_method()
