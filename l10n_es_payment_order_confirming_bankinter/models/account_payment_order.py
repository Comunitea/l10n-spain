# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, _, fields
from odoo.exceptions import UserError


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

    @api.multi
    def generate_payment_file(self):
        self.ensure_one()
        if self.payment_method_id.code != 'conf_bankinter':
            return super(AccountPaymentOrder, self).generate_payment_file()
        if self.date_prefered != 'fixed':
            raise UserError(_('Solo fecha fija'))
        self.num_records = 0
        txt_file = self._pop_cabecera_bk()
        for line in self.bank_line_ids:
            txt_file += self._pop_detalle_bk(line)
        txt_file += self._pop_totales_bk(line, self.num_records)
        return str.encode(txt_file), self.name + '.BK'

    def _pop_cabecera_bk(self):

        cuenta = self.company_partner_bank_id.acc_number
        cuenta = cuenta.replace(' ', '')
        tipo_cuenta = self.company_partner_bank_id.acc_type

        if tipo_cuenta == 'iban':
            cuenta = cuenta[4:8]
            sucursal = cuenta[8:12]
            dc= cuenta[12:14]
        else:
            raise UserError(
                'La cuenta bancaria %s no tiene formato IBAN.', cuenta)


        all_text = ''

        for i in range(1):
            text = ''
            # De 1 a 2. Código de registro
            text += '03'
            # De 3 a 4. Código de Dato.
            text += '60'
            # De 5 a 14. NIF presentador
            vat = self.convert_vat(self.company_partner_bank_id.partner_id)
            text += self.convert(vat, 10)
            # De 15 a 26. Libre
            text += ' ' * 12
            # De 27 a 29. Nümero de dato
            text += '001'
            # De 30 a 35. Fecha de envío
            fecha = fields.Date.from_string(self.date_scheduled).strftime('%y%m%d')
            text += fecha
            # De 36 a 41. Fecha de Emisión
            text += fecha
            # De 42 a 45. Entidad donde reside el contrato. Bankinter
            text += self.convert(cuenta, 4)
            # De 46 a 49. Sucursal de la cuenta.
            text += self.convert(sucursal, 4)
            # De 50 a 59. Número de contrato.
            text += self.convert(self.payment_mode_id.num_contract,10)
            # De 60 a 63. Libre
            text += ' ' * 4
            # De 64 a 65. Dígito de control
            text += self.convert(dc, 2)
            # De 66 a 72
            text = text.ljust(72) + '\r\n'

            all_text += text

        return all_text

    def _pop_detalle_bk(self, line):
        all_text = ''
        for i in range(12):
            # Me salto los opcionales
            if (i + 1) in [5, 6, 7]:
                continue
            text = ''
            # POS 1-26 FIJAS
            # 1 - 2 Código del Registro
            text += '06'
            # 3 - 4 Forma de pago
            if not self.payment_mode_id.conf_bankinter_type:
                raise UserError(
                    'El modo de pago no tiene establecida la forma de pago')
            if self.payment_mode_id.conf_bankinter_type == '56':
                text += '56'  # Transferencia
            elif self.payment_mode_id.conf_bankinter_type == '57':
                text += '57'  # Cheque
            # 5 - 14 Codigo ordenante
            vat = self.convert_vat(self.company_partner_bank_id.partner_id)
            text += self.convert(vat, 10)
            # 15 - 26 Referencia del Proveedor
            nif = line['partner_id']['vat']
            if not nif:
                raise UserError(
                    _("Error: El Proveedor %s no tiene \
                        establecido el NIF.") % line['partner_id']['name'])
            text += self.convert(nif, 12)
            ###################################################################
            # FIN DE LA PARTE FIJA
            ###################################################################
            if (i + 1) == 1:

                # 27 - 29 Numero de dato
                text += '010'
                # 30 - 41 Importe de la factura
                amount = "{:.2f}".format((abs(line.amount_currency)))
                amount = amount.replace('.', '')
                text += amount.rjust(12, '0')
                # 42 - 60 Libre
                text += 19 * ' '
                # 60 - 61 Signo importe factura
                text += ' ' if line.amount_currency>0 else '-'
                # 62 - 72 Libre
                text += 11 * ' '

            if (i + 1) == 2:
                # 27 - 29 Numero de dato
                text += '011'
                # 30 - 65 Nombre del proveedor
                nombre_pro = line['partner_id']['name']
                text += self.convert(nombre_pro, 36)
                # 66 - 72 Libre
                text += 7 * ' '

            if (i + 1) == 3:
                # 27 - 29 Numero de dato
                text += '012'
                # 30 - 65 Dirección del proveedor
                domicilio_pro = line['partner_id']['street']
                if not domicilio_pro:
                    raise UserError(
                        _("Error: El Proveedor %s no tiene\
                         establecido el Domicilio.\
                         ") % line['partner_id']['name'])
                text += self.convert(domicilio_pro, 36)
                # 66 - 72 Libre
                text += 7 * ' '

            if (i + 1) == 4:
                # 27 - 29 Numero de dato
                text += '014'
                # 30 - 34 CP, Ciudad
                cp_pro = line['partner_id']['zip']
                if not cp_pro:
                    raise UserError(
                        _("Error: El Proveedor %s no tiene establecido\
                         el C.P.") % line['partner_id']['name'])
                text += self.convert(cp_pro, 5)

                # 35 - 66 Ciudad
                ciudad_pro = line['partner_id']['city']
                if not ciudad_pro:
                    raise UserError(
                        _("Error: El Proveedor %s no tiene establecida\
                         la Ciudad.") % line['partner_id']['name'])
                text += self.convert(ciudad_pro, 32)
                # 67 - 72 Libre
                text += 6 * ' ' 

            # Optativo numero teléfono
            # if (i + 1) == 5: 
            #     # 27 - 29 Numero de dato
            #     text += '017'

            # Optativo email proveedor
            # if (i + 1) == 6:
            #     # 27 - 29 Numero de dato
            #     text += '170'

            # Optativo dirección email proveedor continuacion si no cabe
            # if (i + 1) == 7:
            #     # 27 - 29 Numero de dato
            #     text += '171'

            # Optativo dirección email proveedor continuacion si no cabe 2
            if (i + 1) == 8:
                # 27 - 29 Numero de dato
                text += '173'
                # 30 - 63 Num banco, Num sucursal, Num cuenta
                if self.payment_mode_id.conf_bankinter_type != '57':
                    cuenta = line['partner_bank_id']['acc_number']
                    cuenta = cuenta.replace(' ', '')
                    tipo_cuenta = self.company_partner_bank_id.acc_type
                    if tipo_cuenta != 'iban':
                        raise UserError(
                            'La cuenta bancaria %s no tiene formato IBAN.', cuenta)
                    text += self.convert(cuenta, 34)
                else:
                    cuenta = 34 * ' '
                    text += cuenta
                
                # 64 Libre
                text += ' '
                # 65 - 66 Código switf pais proveedor. 'ES' son todos pagos nacionales
                text += 'ES'
                # 67 - 72 Libre
                text += 6 * ' '
 
            if (i + 1) == 9:
                # 27 - 29 Numero de dato
                text += '174'
                # 30 - 40 Dirección Switf optativo
                if line.partner_bank_id.bank_id and \
                        line.partner_bank_id.bank_id.bic:
                    text += self.convert(line.partner_bank_id.bank_id.bic, 11)
                else:
                    text += 11 * ' '
                # 41 - 56 Optativo claves adicionales
                text += 16 * ' '
                # 52 - 72 Libre
                text += 16 * ' '

            if (i + 1) == 10:
                # 27 - 29 Numero de dato
                text += '175'
                # 30 Idioma
                text += 'E'
                # 31 - 72 Libre
                text += 35 * ' '

            if (i + 1) == 11:
                # 27 - 29 Numero de dato
                text += '018'
                # 30 - 35 Fecha vencimiento
                if not self.post_financing_date:
                    raise UserError(_('post-financing date mandatory'))
                text += fields.Date.from_string(self.post_financing_date).strftime('%y%m%d').ljust(8)
                # 36 - 51 Numero de factura. Sustituyo el número de factura por la referncia del pago agrupado
                text += self.convert(line.name, 16)
                # 52 - 65 Libre
                text += 14 * ' '
                # 66 - 72 Libre
                text += 7 * ' '

            if (i + 1) == 12:
                # 27 - 29 Numero de dato
                text += '019'
                # 30 - 41 Libre
                text += 12 * ' '
       
            text = text.ljust(72)+'\r\n'
            all_text += text
        self.num_records += 1
        return all_text

    def _pop_totales_bk(self, line, num_records):
        text = ''
        # 1 y 2 Código del registro
        text += '08'
        # 3 - 4 Codigo de dato
        text += '60'
        # 5 - 14 Codigo ordenante
        vat = self.convert_vat(self.company_partner_bank_id.partner_id)
        text += self.convert(vat, 10)
        # 15 - 29 Libre
        text += 15 * ' '
        # 30 - 41 Suma de importes
        text += self.convert(abs(self.total_company_currency), 12)
        # 42 - 49 Num de registros de dato 010
        num = str(self.num_records)
        text += num.zfill(8)

        # 50 - 59 Num total de registros
        total_reg = 1 + (self.num_records * 9) + 1
        total_reg = str(total_reg)
        text += total_reg.zfill(10)

        # 60 - 72 Libre
        text += 13 * ' '
        text = text.ljust(73)+'\r\n'

        return text
