
# Copyright 2024 Comunitea - Javier Colmenero Fernández
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# import datetime
# from calendar import monthrange

from odoo import _, api, exceptions, fields, models
from odoo.addons.l10n_es_aeat.models.spanish_states_mapping import SPANISH_STATES


# KEY_TAX_MAPPING = {
#     "A": "l10n_es_aeat_mod347.aeat_mod347_map_a",
#     "B": "l10n_es_aeat_mod347.aeat_mod347_map_b",
# }


class L10nEsAeatMod182Report(models.Model):
    _inherit = "l10n.es.aeat.report"
    _name = "l10n.es.aeat.mod182.report"
    _description = "Modelo AEAT 182"
    _period_yearly = True
    _period_quarterly = False
    _period_monthly = False
    _aeat_number = "182"

    number = fields.Char(default="182")

    company_vat_mod182 = fields.Char(
        string="NIF COMPAÍA 2",
        size=9,
        compute="_compute_company_vat_mod182",
    )

    donation_amount = fields.Monetary(
        string='Importe donación', compute='_compute_donation_amount')
    naturaleza_declarante = fields.Selection([
        ('1', 'Entidad beneficiaria'),
        ('2', 'Fundación'),
        ('3', 'Titular patrimonio protegido'),
        ('4', 'Partidos políticos, federaciones...')],
        string='Naturaleza de la declaración', default='1', required=True)

    line_ids = fields.One2many(
        'l10n.es.aeat.mod182.report.line', 
        'report_id', string='Líneas Modelo 182')
    lines_count = fields.Integer('# Líneas', compute='_compute_lines_count')

    def _compute_lines_count(self):
        for report in self:
            report.lines_count = len(report.line_ids)

    def _compute_company_vat_mod182(self):
        for report in self:
            nif = report.company_id.vat
            nif2 = nif[1:] + nif[0]
            report.company_vat_mod182 = nif2.zfill(9)

    def _compute_donation_amount(self):
        for report in self:
            report.donation_amount = sum(report.line_ids.mapped('amount'))

    def get_line_details_grouped(self, receipts):
        res = {}
        for line in receipts.mapped('donation_ids.line_ids'):
            group_key = (
                line.donation_id.partner_id, 
                line.in_kind, 
                line.product_id.clave_mod182,
                line.tipo_bien,
                line.identificacion_bien,
                line.nif_patrimonio_protegido,
                line.nombre_patrimonio_protegido,
            )
            if group_key not in res:
                res[group_key] = self.env['donation.line']
            res[group_key] |= line
        return res

    def _get_ccaa_mapping(self):
        res = {}
        mod182_deduction = self.env['mod182.deduccion'].search([])
        for ded in mod182_deduction:
            for state in ded.state_ids:
                codigo_provincia = SPANISH_STATES.get(state.code)
                if not codigo_provincia:
                    continue
                res[codigo_provincia] = ded
        return res
    
    def get_recurrence_old_lines(self, partner):
        year_1 = self.year - 1
        year_2 = self.year - 2
        domain_base = [
            ('partner_id', '=', partner.id),
            ('report_id.state', 'in', ['done', 'posted']),
        ]
        domain = domain_base + [('report_id.year', '=', year_1)]
        old_lines = self.env['l10n.es.aeat.mod182.report.line'].search(domain)
        if old_lines:
            domain = domain_base + [('report_id.year', '=', year_2)]
            old_lines = self.env['l10n.es.aeat.mod182.report.line'].search(domain)
            if old_lines:
                return True
        return False

    def calculate(self):
        res = super().calculate()
        self.line_ids.unlink()
        domain = [
            ('company_id', '=', self.company_id.id)
        ]
        if self.date_start:
            domain.append(('date', '>=', self.date_start))
        if self.date_end:
            domain.append(('date', '<=', self.date_end))
        receipts = self.env['donation.tax.receipt'].search(domain)

        grouped_lines = self.get_line_details_grouped(receipts)

        ccaa_mapping = self._get_ccaa_mapping()

        lines_vals_list = []
        for key in grouped_lines:
            donation_lines = grouped_lines[key]
            partner, in_kind, clave_mod182, tipo_bien, identificacion_bien, \
                nif_patrimonio_protegido, nombre_patrimonio_protegido = key

            codigo_provincia = SPANISH_STATES.get(partner.state_id.code)

            # % DEDUCCION PROVINCIA
            deduccion_mod182 = 0.0
            if self.naturaleza_declarante in ['1', '2', '4']:
                deduccion_mod182 = partner.state_id.deduccion_mod182

            # DEDUCCIONES CCAA
            deduccion_ccaa = 0.0
            codigo_ccaa = 0.0
            ded = ccaa_mapping.get(codigo_provincia, False)
            if ded and self.naturaleza_declarante in ['1', '2']:
                codigo_ccaa = ded.code
                deduccion_ccaa = ded.deduccion

            # TIPO BIEN
            if clave_mod182 not in ['C', 'D']:
                tipo_bien = ''

            # Recurrencia:
            recurrencia = False
            if (self.naturaleza_declarante == '1' and \
                    clave_mod182 in ['A', 'B']) or \
                    (self.naturaleza_declarante == '4' and clave_mod182 == 'G'):
                recurrencia = self.get_recurrence_old_lines(partner)

            vals = {
                'report_id': self.id,
                'partner_id': partner.id,
                'codigo_provincia': codigo_provincia,
                'clave_mod182': clave_mod182,
                'deduccion_mod182': deduccion_mod182,
                'amount': sum(donation_lines.mapped('amount')),
                'aeat_especie': in_kind,
                'codigo_ccaa': codigo_ccaa,
                'deduccion_ccaa': deduccion_ccaa,
                'naturaleza_declarado': partner.naturaleza_declarado,
                'revocacion': False,  # TODO
                'ejerecicio_revocacion': 0,  # TODO
                'tipo_bien': tipo_bien,
                'identificacion_bien': identificacion_bien if tipo_bien else '',
                'recurrencia': recurrencia,
                'nif_patrimonio_protegido': '',
                'nombre_patrimonio_protegido': '',
            }
            lines_vals_list.append(vals)
        
        self.env['l10n.es.aeat.mod182.report.line'].create(lines_vals_list)
        return res
    
    # def button_export(self):
    #     self.ensure_one()
    #     if any(line.state == 'error' for line in self.line_ids):
    #         raise exceptions.UserError(
    #             _('Existen líneas con errores, por favor, corríjalos antes de exportar.'))
    #     return super().button_export()

    def button_cancel(self):
        self.line_ids.unlink()
        return super().button_cancel()

    def view_action_mod182_lines(self):
        action = self.env.ref(
            'l10n_es_aeat_mod182.action_l10n_es_aeat_mod182_report_line').read()[0]
        action['domain'] = [('id', 'in', self.line_ids.ids)]
        return action


class L10nEsAeatMod182ReportLine(models.Model):
    _name = "l10n.es.aeat.mod182.report.line"
    _description = "Detalle modelo 182"

    report_id = fields.Many2one(
        'l10n.es.aeat.mod182.report',
        string='Report', readonly=True, required=True, ondelete='cascade')
    currency_id = fields.Many2one(
        'res.currency', related='report_id.currency_id')
    clave_mod182 = fields.Selection([
        ('A', 'Donativos no incluidos en actividades o programas prioritarios de mecenazgo'),
        ('B', 'Donativos incluidos en actividades o programas prioritarios de mecenazgo'),
        ('C', 'Aportación al patrionio de discapacitados'),
        ('D', 'Disposición al patrionio de discapacitados'),
        ('E', 'Gasto de dinero y consumo de bienes fungibles'),
        ('F', 'Cuotas de afiliación'),
        ('G', 'resto de donaciones y aportaciones percibidas')],
        string='Clave Modelo 182')
    partner_id = fields.Many2one(
        'res.partner', string='Declarado', required=True)
    nif_declarado = fields.Char(
        string='N.I.F. Declarado', size=9, related='partner_id.vat')
    nif_representante = fields.Char(
        string='N.I.F Representante', size=9, compute='compute_nif_representante')
    codigo_provincia = fields.Char(string='Código provincia')
    aeat_especie = fields.Boolean(string='Especie')
    deduccion_mod182 = fields.Float('Deducción (%)')
    codigo_ccaa = fields.Integer('Código CCAA')
    deduccion_ccaa = fields.Float('Deducción CCAA (%)')
    amount = fields.Monetary(string='Amount')
    naturaleza_declarado = fields.Selection([
        ('F', 'Persona Física'),
        ('J', 'Persona Jurídica'),
        ('E', 'Entidad en régimen de atribución de rentas')],
        string='Naturaleza del declarado', default=False)
    revocacion = fields.Boolean(string='Revocación')
    ejerecicio_revocacion = fields.Integer('Ejercicio revocación')
    tipo_bien = fields.Selection(
        [('I', 'Inmueble'), ('V', 'Valores mobiliarios'), ('O', 'otros')],
        string="Tipo de bien")
    identificacion_bien = fields.Char('Identificación del bien')
    recurrencia = fields.Boolean('Recurrencia')
    nif_patrimonio_protegido = fields.Char('NIF patrimonio protegido')
    nombre_patrimonio_protegido = fields.Char('Nombre patrimonio protegido')
    state = fields.Selection(
        [('error', 'Error'), ('ok', 'Ok')], string='Estado',
        compute='_compute_errors', store=True)
    error_txt = fields.Text(
        'Mensaje de error', compute='_compute_errors', store=True)

    @api.depends(
        'nif_representante', 'codigo_provincia', 'clave_mod182', 
        'naturaleza_declarado'
    )
    def _compute_errors(self):
        for line in self:
            error_txt = ''
            if not line.nif_declarado:
                error_txt += f' - El declarado {line.partner_id.name} no tiene el campo N.I.F. Declarado\n'
            if line.partner_id.menor_14 and not line.nif_representante:
                error_txt += f' - El declarado {line.partner_id.name} es menor de 14 años y no tiene el campo N.I.F. Representante\n'
            if not line.codigo_provincia:
                error_txt += f' - El declarado {line.partner_id.name} no tiene el campo Código provincia\n'
            if not line.clave_mod182:
                error_txt += f' - El declarado {line.partner_id.name} no tiene el campo Clave Modelo 182.\n'
            if not line.naturaleza_declarado:
                error_txt += f' - El declarado {line.partner_id.name} no tiene el campo Naturaleza declarado.\n'
            if line.tipo_bien and not line.identificacion_bien:
                error_txt += f' - El declarado {line.partner_id.name} tiene el campo Tipo de bien y no tiene el campo Identificación del bien.\n'
            line.error_txt = error_txt
            line.state = 'ok' if not error_txt else 'error'

    def compute_nif_representante(self):
        for line in self:
            line.nif_representante = line.partner_id.nif_representante if \
                line.partner_id.menor_14 else ''
