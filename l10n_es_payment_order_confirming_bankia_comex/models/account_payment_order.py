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
        if self.payment_method_id.code != 'conf_bankia_comex':
            return super(AccountPaymentOrder, self).generate_payment_file()
        if self.date_prefered != 'fixed':
            raise UserError(_('Solo fecha fija'))
        # ##################################################
        # ##################################################
        # Importe total de la remesa
        self.importe_remesa = 0 # Total remesa. 
        self.num_records_60 = 0 # Contador registros con código de operación igual a 60
        self.num_records_33 = 0 # Contador registros con número de dato igual a 033
        self.num_records_total = 0 # Contador total de registros.
        # ##################################################
        # ##################################################

        txt_file = self._pop_cabecera_bankia_comex()
        grouped_lines = self._group_by_partner(self.bank_line_ids)
        for partner in grouped_lines:
            lines = grouped_lines[partner]
            for line in lines:
                txt_file += self._pop_detalle_bankia_comex_EUR(line)
        txt_file += self._pop_totales_bankia_comex()
        # txt_file = self.ensure_valid_ascii(txt_file)

        return str.encode(txt_file, encoding='cp1252', errors='replace'), self.name + '.TXT'

    def _get_fix_part_bankia_comex(self, cr, co):

        self.num_records_total += 1

        if co =='60':
            self.num_records_60 +=1

        text = ''
        # ZONA A. Código de registro. Long 2 
        text += cr
        # ZONA B. Código de operación. Long 2
        text += co
        # Zona C1. NIF del Ordenante. Long 9
        vat = self.convert_vat(self.company_partner_bank_id.partner_id)
        text += self.convert(vat, 9)
        # Zona C2. Sufijo. Long 3. Siempre '000'
        text += '000'

        return text

    def _pop_cabecera_bankia_comex(self):

        all_text = ''

        for i in range(6):

            text = self._get_fix_part_bankia_comex('03', '62')

            if (i + 1) == 1:
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

                # Zona D. (12). Número de contrato. 11 dígitos + 1 blanco.
                text += self.convert(self.payment_mode_id.num_contract, 12)
                # Zona E. (3). Número de dato. '001'
                text += '001'
                # Zona F1. (6). Fecha de envío del fichero
                date_file = fields.Date.from_string(self.date_scheduled).strftime('%d%m%Y')
                text += date_file
                # Zona F2. (6). Fecha de emisión de las órdenes.
                text += date_file
                # Zona F3. (4). Código entidad. 2038
                text += entidad
                # Zona F4. (4). Sucursal
                text += sucursal
                # Zona F5. (2). DC
                text += dc
                # Zona F6. (10). Número de cuenta
                text += num_cuenta
                # Zona F7. (1). Detalle cargo. "0".
                text += '0'

            if (i + 1) == 2:
                # Zona D. (12).  
                text += self.convert(self.payment_mode_id.linea_comex[6:] + self.name[3].rjust(5,'0') , 12)
                # Zona E. (3). Número de dato '002'
                text += '002'
                # Zona F. Nombre del Ordenante.
                text += self.convert(self.company_partner_bank_id.partner_id.name, 36)

            if(i + 1) == 3:
                # Zona D. (12). Blancos
                text += ' ' * 12
                # Zona E. (3). Número de dato. '003'
                text += '003'
                # Zona F. (36). Domicilio del ordenante.
                text += self.convert(self.company_id.street, 36)

            if(i + 1) == 4:
                # Zona D. (12). Libre
                text += ' ' * 12
                # Zona E. (3). Número de dato. '004'
                text += '004'
                # Zona F. (36). Localidad del ordenante
                text += self.convert(self.company_id.city, 36)

            if(i + 1) == 5:
                # Zona D. (12) Libre.
                text += ' ' * 12
                # Zona E. (3). Número de dato '005'
                text += '005'
                # Zona F. Número de línea comex
                text += self.convert(self.payment_mode_id.linea_comex, 36)

            text = text.ljust(72) + '\r\n'
            all_text += text
    
        return all_text

    def _group_by_partner(self, lines):
        grouped_lines = {}
        for l in lines:
            if l.partner_id not in grouped_lines:
                grouped_lines[l.partner_id] = []
            grouped_lines[l.partner_id] += l
        return grouped_lines

    def _pop_detalle_bankia_comex_EUR(self, line):

        """
        Genera el bloque cabecera y detalle de los registros de facturas intracomunitarias.
        Es decir, el pago se hace en EUROS.
        """
        
        all_text = ''

        # REGISTRO DE CABECERA DE FACTURAS EN EUROS.
        text = self._get_fix_part_bankia_comex('04', '60')
        # Zona D. (12). Libre
        text += ' ' * 12
        # Zona E. (3). Libre
        text += ' ' * 3

        text = text.ljust(72) + '\r\n'
        all_text += text

        # REGISTROS DETALLE FACTURAS EN EUROS
            
        for i in range(16):

            # PARTE COMÚN A TODOS LOS REGISTROS DE DETALLE

            registros = [1, 2, 3, 4, 6, 7, 10, 13, 16] # Registros que comunicamos.

            if (i + 1) in registros:
                text = self._get_fix_part_bankia_comex('06', '60')
                # Zona D. (12). Referencia del beneficiario.
                if(i + 1) != 10:
                    # PARA TODOS LOS REGISTROS EXCEPTO EL 10
                    nif_prov = line['partner_id']['vat']
                    if not nif_prov:
                        raise UserError(
                            _("Error: El Proveedor %s no tiene \
                                establecido el NIF.") % line['partner_id']['name'])

                    if nif_prov[0:2] == 'ES':
                        raise UserError(
                            _("Error: El NIF %s corresponde \
                                a un proveedor nacional.") % nif_prov)

                    text += self.convert(nif_prov, 12)
                else:
                    # REGISTRO 10
                    # Zona D. (12) Fecha de vencimiento (Postfinanciación) 
                    date_post_finan = fields.Date.from_string(self.post_financing_date) \
                            .strftime('%d%m%Y')
                    text += self.convert(date_post_finan, 12)

            # FIN PARTE COMUN

            if (i + 1) == 1:
                # Zona E. (3). '033'.
                text += '033'
                self.num_records_33 += 1
                # Zona F1. (2). Código país Banco beneficiario
                cuenta = line.partner_bank_id.acc_number
                cuenta = cuenta.replace(' ', '')
                if cuenta[0:2]=='ES':
                    raise UserError(
                        _("Error: Esta cuenta %s es nacional y estás preparando \
                        una remesa de pagos intracomunitarios.") % cuenta)
                else:
                    text += cuenta[0:2]
                # Zona F2. (2). Dígito de control del IBAN
                text += cuenta[2:4]
                # Zona F3. (30). Resto del número de cuenta del banco del beneficiario
                text += cuenta[4:]
                # Zona F4. (1). Siempre valor '7'
                text += '7'

            if (i + 1) == 2:
                # Zona E. (3). Número de dato '034'
                text += '034'
                # Zona F1. (12). Importe de la factura. Utilizo el importe del pago agrupado.
                self.importe_remesa += line.amount_currency
                amount = "{:.2f}".format((abs(line.amount_currency)))
                amount = amount.replace('.', '')
                text += amount.rjust(12, '0')
                # Zona F2. (1). Clave gastos, se informará siempre con un 3.
                text += '3'
                # Zona F3. (2). Clave ISO país beneficiario
                pais = line.partner_id.country_id
                if not pais:
                    raise UserError(
                        _("Error: El Proveedor %s no tiene establecida\
                        el Pais.") % line['partner_id']['name'])
                text += pais.code
                # Zona F4. (1). Pronto pago 'S'
                text += 'S'
                # Zona F5. (5). Libre
                text += ' ' * 5
                # Zona F6. (11). Dirección Swift banco beneficiario
                if line.partner_bank_id.bank_id and \
                    line.partner_bank_id.bank_id.bic:
                        text += self.convert(line.partner_bank_id.bank_id.bic,11)
                else:
                    raise UserError("El Bic de este pago %s es obligatrio." % line.name)
                    
            if (i + 1) == 3:
                # Zona E. (3). Número de dato '035'
                text += '035'
                # Zona F. (36). Nombre beneficiario
                text += self.convert(line.partner_id.name, 36)

            if (i + 1) == 4:
                # Zona E. (3). Número de dato '036'
                text += '036'
                # Zona F. (36). Domicilio del beneficiario
                text += self.convert(line.partner_id.street, 36)

            if (i + 1) == 6:
                # Zona E. (3). Número de dato '038'
                text += '038'
                # Zona F. (36). Código postal y localidad del beneficiario
                text += self.convert(line.partner_id.zip + " " + line.partner_id.city, 36)

            if (i + 1) == 7:
                # Zona E. Número de dato '039'
                text += '039'
                # Zona F. (36). País del beneficiario
                text += self.convert(line.partner_id.country_id.name, 36)

            if (i + 1) == 10:
                # Zona E. (3). Número de dato '042'
                text += '042'
                # Zona F1. (9) Fecha de emisión de la factura. Tomo el primer registro.
                fcha_fra = self.date_scheduled - datetime.timedelta(days = 2)
                text += self.convert(fcha_fra.strftime('%d%m%Y'), 9)
                # Zona F2. (13). Referencia del proveedor.
                text += self.convert(nif_prov, 13)
                # Zona F3. (12). Número de factura.
                text += self.convert(line.name, 12)

            if (i + 1) == 13:
                # Zona E. (3). Número de dato '045'
                text += '045'
                # Zona F. (36). Correo electrónico beneficiario
                email = line.partner_id.email
                if not email:
                    raise UserError(
                        _("Error: El Proveedor %s no tiene\
                                         email.\
                                         ") % line.partner_id.name)
                email = email.split(',')
                text += self.convert(email[0], 36)

            if (i + 1) == 16:
                # Zona E. (3). Número de dato '085'
                text += '085'
                # Zona F1. (2). Clase de Pago '01' Mercancía
                text += '01'
                # Zona F2. (38). Se completan con 0
                text += '0' * 38

            text = text.ljust(72) + '\r\n'
            all_text += text   

        return all_text

    def _pop_totales_bankia_comex(self):

        all_text =''

        # REGISTRO DE TOTALES FACTURAS EN EUROS

        text = self._get_fix_part_bankia_comex('08', '60')
        # Zona D. (12). Libre
        text += ' ' * 12
        # Zona E. (3). Libre
        text += ' ' * 3
        # Zona F1. (12)
        text += "{:.2f}".format(round(self.importe_remesa,2)).replace('.', '').rjust(12, '0')
        # Zona F2. Número de registros con número de dato 033
        text += str(self.num_records_33).rjust(8, "0")
        # Zona F3. Número de registros con número de dato 60
        text += str(self.num_records_60).rjust(10, "0")

        text = text.ljust(72) + '\r\n'
        all_text += text

        # REGISTRO TOTAL GENERAL

        text = self._get_fix_part_bankia_comex('09', '62')
        # Zona D. (12). Libre
        text += ' ' * 12
        # Zona E. (3). Libre
        text += ' ' * 3
        # Zona F1. (12). Importes de todas las facturas
        text += "{:.2f}".format(round(self.importe_remesa,2)).replace('.', '').rjust(12, '0')
        # Zona F2. (8) Número de registros 033
        text += str(self.num_records_33).rjust(8, "0")
        # Zona F3. (10). Número total de registros
        text += str(self.num_records_total).rjust(10, "0")

        text = text.ljust(72) + '\r\n'
        all_text += text

        return all_text
