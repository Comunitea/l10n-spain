# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, _, fields
from odoo.exceptions import UserError
import time
import datetime


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    def strim_txt(self, text, size, separator=' '):
        """
        Devuelvo el texto con espacios al final hasta completar size
        """
        if text:
            if len(text) < size:
                relleno = size - len(text)
                text += relleno * separator
            elif len(text) > size:
                text = text[:size]
        return text

    @api.model
    def ensure_valid_ascii(self, text):
        res = text.upper()
        to_replace = {
            'Á': 'A',
            'É': 'E',
            'Í': 'I',
            'Ó': 'O',
            'Ú': 'U',
        }
        for letter in to_replace:
            res.replace(letter, to_replace[letter])
        return res

    @api.multi
    def generate_payment_file(self):
        self.ensure_one()
        if self.payment_method_id.code != 'conf_santander':
            return super(AccountPaymentOrder, self).generate_payment_file()
        if self.date_prefered != 'fixed':
            raise UserError(_('Solo fecha fija'))
        # ##################################################
        # ##################################################
        # Importe total de la remesa
        self.importe_remesa = 0
        # ##################################################
        # ##################################################
        self.num_records = 0

        txt_file = self._pop_cabecera_santander()
        grouped_lines = self._group_by_partner(self.bank_line_ids)
        for partner in grouped_lines:
            lines = grouped_lines[partner]
            for line in lines:
                txt_file += self._pop_detalle_santander(line)
        txt_file += self._pop_totales_santander()
        # txt_file = self.ensure_valid_ascii(txt_file)

        return str.encode(txt_file, encoding='cp1252', errors='replace'), self.name + '.TXT'

    def _get_fix_part_santander(self, cr):
        # OJO sólo se cuentan los registros de tipo 2.
        if cr == "2":
            self.num_records += 1

        text = ''
        # A1. 1 a 2 código del registro
        text += cr

        return text

    def _pop_cabecera_santander(self):

        all_text = ''
        text = self._get_fix_part_santander('1')
        # B1. De 2 a 5. Código Mnemotécnico de la operación.
        text += self.payment_mode_id.num_contract
        # B2. De 5 a 15. Código de cedente. No es obligatorio si se comunica el mnemotécnico
        text += ' ' * 10
        # B3. De 15 a 18. Número de operación. No es obligatorio si se comunica el mnemotécnico
        text += ' ' * 3
        # B4. De 18 a 40. Id cedente.
        vat = self.convert_vat(self.company_partner_bank_id.partner_id)
        text += self.convert(vat, 22)
        # B5. De 40 a 43. Sufijo
        text += self.payment_mode_id.sufix
        # B6. De 43 a 83. Nombre cedente
        text += self.convert(self.company_partner_bank_id.partner_id.name, 40)
        # C1. De 83 a 91. Fecha remesa
        date_file = fields.Date.from_string(self.date_scheduled).strftime('%Y%m%d')
        text += date_file
        # C2. De 91 a 107. Referencia de la remesa PAY\d{5}
        text += self.convert(self.name, 16)
        # C3. De 107 a 110. Moneda
        text += self.company_currency_id.name
        # D1. De 110 a 116. Reservado
        text += '0' * 6
        # D2. De 116 a 124. Reservado
        text += ' ' * 8
        # D3. De 124 a 140. Reservado
        text += ' ' * 16
        # E1. De 140 a 144. Reservado
        text += ' ' * 4
        # E2. De 144 a 174. Reservado
        text += ' ' * 30
        # E3. De 174 a 221. Reservado
        text += ' ' * 47
        # E4. De 221 a 233. Reservado
        text += ' ' * 12
        # F1. De 233 a 578. Libre
        text += ' ' * 345
        # F5. De 578 a 681
        text = text.ljust(681)+'\r\n'
        all_text = text

        return all_text

    def _group_by_partner(self, lines):
        grouped_lines = {}
        for l in lines:
            if l.partner_id not in grouped_lines:
                grouped_lines[l.partner_id] = []
            grouped_lines[l.partner_id] += l
        return grouped_lines

    def _pop_detalle_santander(self, line):
        """
        """
        all_text = ''
        for pl in line.payment_line_ids:
            text = ''
            inv = pl.move_line_id.invoice_id
            text += self._get_fix_part_santander('2')
            # B1. De 2 a 17. Cód Prov no es obligatorio si informamos el cif del proveedor
            text += ' ' * 15
            # B2. De 17 a 18. Tipo ID proveedor. NIF.
            text += '0'
            # B3. De 18 a 40. Id proveedor. NIF
            nif = line['partner_id']['vat']
            if not nif:
                raise UserError(
                    _("Error: El Proveedor %s no tiene \
                        establecido el NIF.") % line['partner_id']['name'])
            text += self.convert(nif[2:], 22)
            # B4. De 40 a 41. 'J' o 'P'
            text += 'J'
            # B5. De 41 a 71. Apellido 1 o Denominación social.
            name = line['partner_id']['name']
            text += self.convert(name, 30)
            # B6. De 71 a 101. Apellido 2
            text += ' ' * 30
            # B7. De 101 a 131. Nombre
            text += ' ' * 30
            # B8. De 131 a 133. País de residencia. Sólo es obligatorio si el proveedor no es residente.
            text += ' ' * 2
            # B9. De 133 a 135. Tipo Vía. Hay una tabla. Las marco como desconocida y ya se indica en la dirección.
            text += 'ZZ'
            # B10. De 135 a 175. Nombre de la vía pública del proveedor
            domicilio_pro = line['partner_id']['street']
            if not domicilio_pro:
                raise UserError(
                    _("Error: El Proveedor %s no tiene\
                     establecido el Domicilio.\
                     ") % line['partner_id']['name'])
            text += self.convert(domicilio_pro, 40)
            # B11. De 175 a 183. Número de domicilio. No indico nada porque ya está incluído en la dirección
            text += ' ' * 8
            # B12. De 183 a 223. Ampliación domicilio.
            text += ' ' * 40
            # B13. De 223 a 248. Población
            ciudad_pro = line['partner_id']['city']
            if not ciudad_pro:
                raise UserError(
                    _("Error: El Proveedor %s no tiene establecida\
                                                     la Ciudad.") % line['partner_id']['name'])
            text += self.convert(ciudad_pro, 25)
            # B14. De 248 a 256. Código postal
            cp_pro = line['partner_id']['zip']
            if not cp_pro:
                raise UserError(
                    _("Error: El Proveedor %s no tiene establecido\
                                    el C.P.") % line['partner_id']['name'])
            text += self.convert(cp_pro, 8)
            # B15. De 256 a 281. Provincia
            provincia = line['partner_id']['state_id']
            if not provincia:
                raise UserError(
                    _("Error: El Proveedor %s no tiene establecida\
                                     la provincia.") % line['partner_id']['name'])

            provincia = provincia.name
            text += self.convert(provincia, 25)
            # B16. De 281 a 283. País
            pais = line.partner_id.country_id
            if not pais:
                raise UserError(
                    _("Error: El Proveedor %s no tiene establecida\
                                 el Pais.") % line['partner_id']['name'])
            text += pais.code
            # B17. De 283 a 297. Teléfono
            text += ' ' * 14
            # B18. De 297 a 311. Fax
            text += ' ' * 14
            # B19. De 311 a 371. Email
            text += ' ' * 60
            # C1. De 371 a 372. Forma de Pago. 'T' Transferencia
            text += 'T'
            # C2. De 372 a 402. Datos bancarios. CCC no lo comunicamos porque vamos a indicar el IBAN.
            text += ' ' * 30
            # C3. De 402 a 414. BIC - SWIFT
            if line.partner_bank_id.bank_id and \
                    line.partner_bank_id.bank_id.bic:
                text += self.convert(line.partner_bank_id.bank_id.bic, 12)
            else:
                text += 12 * ' '
            # C4. De 414 a 461. IBAN
            cuenta = line.partner_bank_id.acc_number
            cuenta = cuenta.replace(' ', '')
            text += self.convert(cuenta, 47)
            # C5. De 461 a 464. Código moneda. Opcional si ya lo incluimos en el registro 1.
            text += ' ' * 3
            # D1. De 464 a 465. F - Factura y A - Abono
            text += 'F' if pl.amount_currency >= 0 else 'A'
            # D2. De 465 a 480. Número de documento.
            text += self.convert(pl.communication, 15)
            # D3. De 480 a 495. Importe del documento.
            self.importe_remesa += pl.amount_currency
            amount = "{:.2f}".format((abs(pl.amount_currency)))
            amount = amount.replace('.', '')
            text += amount.rjust(15, '0')
            # D4. De 495 a 503. Fecha de emisión
            if inv.date_invoice:
                fecha_factura = fields.Datetime.to_string(inv.date_invoice).replace('-', '')
                dia = fecha_factura[6:8]
                mes = fecha_factura[4:6]
                ano = fecha_factura[:4]
                fecha_factura = ano + mes + dia
            else:
                fecha_factura = fields.Date.from_string(
                    pl.move_line_id.
                        date).strftime('%Y%m%d')
            if inv.date_invoice > self.date_scheduled:
                raise UserError(
                    _("Error: La factura %s tiene una fecha mayor que \
                      La remesa") % inv.number)
            text += fecha_factura
            # D5. De 503 a 511. Fecha de pago al proveedor
            date_file = fields.Date.from_string(self.date_scheduled).strftime('%Y%m%d')
            text += date_file
            # D6. De 511 a 527. Referencia 1. Indico el número de pago agrupado L\d{5}
            text += self.convert(line.name, 16)
            # D7. De 527 a 547. Referencia 2
            text += ' ' * 20
            # E1. De 547 a 548. Tipo Campo
            text += ' '
            # E2. De 548 a 555. Código estadístico. No lo incluyo porque sólo hacemos pagos nacionales.
            text += ' ' * 7
            # E3. De 555 a 556. Segmentación. No lo utilizo porque hacemos confirming pronto pago
            text += ' '
            # E4. De 556 a 558. Idioma notificación
            text += ' ' * 2
            # F1. De 558 a 578. Zona libre
            text += ' ' * 20
            # G1. De 578 a 593. Importe original factura
            text += '0' * 15
            # G2. De 593 a 603. Reservado
            text += '0' * 10
            # G3. De 603 a 618. Reservado
            text += '0' * 15
            # G4. De 618 a 628. Reservado
            text += '0' * 10
            # G5. De 628 a 643. Reservado
            text += '0' * 15
            # G6. De 643 a 658. Reservado
            text += '0' * 15
            # G7. De 658 a 666. Reservado
            text += '0' * 8
            # G8. De 666 a 674. Fecha de postfinanciación
            date_post_finan = fields.Date.from_string(self.post_financing_date) \
                .strftime('%Y%m%d')
            text += date_post_finan
            # G9. De 674 a 678
            text += '0' * 4
            # H1. De 678 a 681
            text = text.ljust(681) + '\r\n'
            all_text += text

        return all_text

    def _pop_totales_santander(self):
        # A1. De 1 a 2.
        text = self._get_fix_part_santander('3')
        # A2. De 2 a 8. Número de registros
        text += str(self.num_records).rjust(6, "0")
        # A3. De 8 a 23. Total remesa
        text += str(round(self.importe_remesa, 2)).replace('.', '').rjust(15, '0')
        # A4. De 23 a 681. Libre
        text = text.ljust(681) + '\r\n'

        return text
