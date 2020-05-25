# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models, _, fields
from odoo.exceptions import UserError
import re


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
        if self.payment_method_id.code != 'conf_ibercaja':
            return super(AccountPaymentOrder, self).generate_payment_file()
        if self.date_prefered != 'fixed':
            raise UserError(_('Solo fecha fija'))
        self.num_records = 0
        self.num_records_10 = 0
        self.CODIGO_OPERACION = '56'
        txt_file = self._pop_cabecera_ibercaja()
        for line in self.bank_line_ids:
            txt_file += self._pop_detalle_ibercaja(line)
        txt_file += self._pop_totales_ibercaja(line, self.num_records)
        return str.encode(txt_file), self.name + '.TXT'

    def _pop_cabecera_ibercaja(self):

        
        CODIGO_REGISTRO = '04'

        cuenta = self.company_partner_bank_id.acc_number
        cuenta = cuenta.replace(' ', '')
        tipo_cuenta = self.company_partner_bank_id.acc_type
        if tipo_cuenta != 'iban':
           raise UserError(
              _("Error: El tipo de cuenta de %s debe tener formato IBAN.") % cuenta)
                
        entidad = cuenta[4:8]
        sucursal = cuenta[8:12]
        dc = cuenta[12:14]
        num_cuenta = cuenta[14:]

        all_text = ''

        for i in range(2):
            text = ''
            # Zona A. 2n. Código de registro
            text += CODIGO_REGISTRO
            # Zona B. 2n. Código de operacion '56'
            text += self.CODIGO_OPERACION
            # Zona C. 10n. Código de ordenante
            text += self.payment_mode_id.num_contract
            # Zona D. 12an. NIF ordenante.
            vat = self.convert_vat(self.company_partner_bank_id.partner_id)
            text += self.convert(vat, 12)
            ###################################################################
            # FIN DE LA PARTE FIJA
            ###################################################################
            if (i + 1) ==1:
                # Zona E. 3n. Número de Dato
                text += '001'
                # Zona F1. 6n. Fecha de envío del soporte
                fecha = fields.Date.from_string(self.date_scheduled).strftime('%d%m%y')
                text += fecha
                # Zona F2. 6n. Fecha de envío de las órdenes. A ceros porque se harán según lo indicado en cada factura.
                text += '0' * 6
                # Zona F3. 4n. Entidad de destino del soporte. 2085
                text += entidad
                # Zona F4. 4n. Oficina de la cuenta de cargo. 
                text += sucursal
                # Zona F5. 10n. Número de la cuenta de cargo. 
                text += num_cuenta
                # Zona F6. 1n. Detalle del cargo.
                text += '0'
                # Zona F7. 3an. Libre
                text += ' ' * 3
                # Zona F8. 2n. DC de la cuenta de cargo.
                text += dc
                # Zona G. 7an. Libre
                text += ' ' * 7
            if (i + 1) == 2:
                # Zona E. 3n. Número de dato.
                text += '002'
                # Zona F. 36an. Nombre del ordenante.
                text += self.convert(self.company_partner_bank_id.partner_id.name, 36)
            # Cierre de cada línea
            text = text.ljust(72) + '\r\n'
            all_text += text
            self.num_records += 1
        return all_text

    def _pop_detalle_ibercaja(self, line):
        CODIGO_REGISTRO = '06'
        all_text = ''
        for i in range(6):

            text = ''
            # cuenta bancaria beneficiario
            cuenta_benef = line['partner_bank_id']['acc_number']
            cuenta_benef = cuenta.replace(' ', '')
            tipo_cuenta = self.company_partner_bank_id.acc_type
            if tipo_cuenta != 'iban':
               raise UserError(
                   'La cuenta bancaria %s no tiene formato IBAN.', cuenta)
            entidad_benef = cuenta_benef[4:8]
            sucursal_benef = cuenta_benef[8:12]
            dc_benef = cuenta_benef[12:14]
            num_cuenta_benef = cuenta_benef[14:]

            # Zona A. 2n. Código de registro
            text += CODIGO_REGISTRO
            # Zona B. 2n. Código de operacion '56'
            text += self.CODIGO_OPERACION
            # Zona C. 10n. Código de ordenante
            text +=self.payment_mode_id.num_contract
            # Zona D. 12 an. Referencia del beneficiario. NIF beneficiario
            nif = line['partner_id']['vat']
            if not nif:
               raise UserError(
                     _("Error: El Proveedor %s no tiene \
                     establecido el NIF.") % line['partner_id']['name'])
            text += self.convert(nif[2:], 12)
            ###################################################################
            # FIN DE LA PARTE FIJA
            ###################################################################
            if (i + 1) == 1:
                self.num_records_10 += 1
                # Zona E. 3n. Número de dato. 
                text += '010'
                # Zona F1. 12n. Importe
                amount = "{:.2f}".format((abs(line.amount_currency)))
                amount = amount.replace('.', '')
                text += amount.rjust(12, '0')
                # Zona F2. 4n. Entidad de la cuenta del beneficiario.
                text += entidad_benef
                # Zona F3. 4n. Sucursal cuenta beneficario
                text += sucursal_benef
                # Zona F4. 10n. Número de cuenta del beneficiario
                text += num_cuenta_benef
                # Zona F5. 1n. Gastos por cuenta del ordenante
                text += '1'
                # Zona F6. 1n. Concepto de la Orden. Otros conceptos.
                text += '9'
                # Zona F7. 2an. Libre
                text += ' ' * 2
                # Zona F8. 2an. DC cuenta beneficiario
                text += dc_benef
                # Zona G. 7n. Vencimiento de la factura. Valor inmediato.
                text += '000001'.rjust(7,'0')
            if (i + 1)  == 2:
                # Zona E. 3n. Número de dato.
                text += '011'
                # Zona F. Nombre del beneficiario
                nombre_pro = line['partner_id']['name']
                text += self.convert(nombre_pro, 36)
            if (i + 1) == 3:
                # Zona E. 3n. Número de dato.
                text += '012'
                # Zona F. 36an. Domicilio del beneficiario.
                text += self.convert(line.partner_id.street, 36)
            if (i + 1) == 4:
                # Zona E. 3n. Número de dato.
                text += '014'
                # Zona F. Código postal y plaza del beneficiario.
                text += self.convert(line.partner_id.zip + " " + line.partner_id.city, 36)
            if (i + 1) == 5:
                # Zona E. 3n. Número de dato.
                text += '015'
                # Zona F. 36an. Provincia de la plaza del beneficiario
                text += self.convert(line.partner_id.state_id.name, 36)
            if (i + 1) == 6:
                # Zona E. 3n. Número de dato.
                text += '016'
                # Zona F. 36an. Número o referencia que figura en la factura. (Tomo el número de pago agrupado).
                text += self.convert(line.name, 36)
                # Zona G. 7n. Fecha de emisión de la factura ajustado a la derecha. Tomo como fecha la del pago agrupado.
                text += fields.Date.from_string(self.date_scheduled).strftime('%d%m%y').rjust(7,'0')
            
            # Cierre de cada línea
            text = text.ljust(72) + '\r\n'
            all_text += text 
            self.num_records += 1
        
        return all_text

    def _pop_totales_ibercaja(self, line, num_records):

        text = ''
        self.num_records += 1

        # Zona A. 2n. Código de registro
        text += '08'
        # Zona B. 2n. Codigo de operación
        text += self.CODIGO_OPERACION
        # Zona C. 10n. Código de ordenante.
        text += self.payment_mode_id.num_contract
        # Zona D. 23an. Libre
        text += ' ' * 12
        # Zona E. 3an. Libre
        text += ' ' * 3
        # Zona F1. 12n. Suma de importes
        text += self.convert(abs(self.total_company_currency), 12)
        # Zona F2. 8n. Suma de registros de tipo 1. número de dato '010'
        text += str(self.num_records_10).rjust(8, "0")
        # Zona F3. 10n. Número total de registros incluídos los de cabecera y totales.
        text += str(self.num_records_10).rjust(10, "0")
        # Zona F4. 6an. Libre
        text += ' ' * 6
        # Zona F5. 7an. Libre
        text += ' ' * 7

        text = text.ljust(72)+'\r\n'

        return text
