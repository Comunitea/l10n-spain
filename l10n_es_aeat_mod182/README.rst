===============
AEAT modelo 182
===============



(Declaración De Donaciones)
Basado en la Orden EHA/3012/2008, de 20 de Octubre, por el que se aprueban los
diseños físicos y lógicos del 347.

De acuerdo con la normativa de la Hacienda Española, están obligados a
presentar el modelo 347:

* Todas aquellas personas físicas o jurídicas que no esten acogidas al régimen
  de módulos en el IRPF, de naturaleza pública o privada que desarrollen
  actividades empresariales o profesionales, siempre y cuando hayan realizado
  operaciones que, en su conjunto, respecto de otra persona o Entidad,
  cualquiera que sea su naturaleza o carácter, hayan superado la cifra de
  3.005,06 € durante el año natural al que se refiere la declaración. Para el
  cálculo de la cifra de 3.005,06 € se computan de forma separada las entregas
  de biene y servicios y las adquisiciones de los mismos.
* En el caso de Sociedades Irregulares, Sociedades Civiles y Comunidad de
  Bienes no acogidas el regimen de módulos en el IRPF, deben incluir las
  facturas sin incluir la cuantía del IRPF.
* En el caso de facturas de proveedor con IRPF, no deben ser presentadas en
  este modelo. Se presentan en el modelo 190. Desactivar en la ficha del
  proveedor la opción de "Incluir en el informe 347".

De acuerdo con la normativa, no están obligados a presentar el modelo 347:

* Quienes realicen en España actividades empresariales o profesionales sin
  tener en territorio español la sede de su actividad, un establecimiento
  permanente o su domicilio fiscal.
* Las personas físicas y entidades en régimen de atribución de rentas en
  el IRPF, por las actividades que tributen en dicho impuesto por el
  régimen de estimación objetiva y, simultáneamente, en el IVA por los
  régimenes especiales simplificados o de la agricultura, ganadería
  y pesca o recargo de equivalencia, salvo las operaciones que estén
  excluidas de la aplicación de los expresados regímenes.
* Los obligados tributarios que no hayan realizado operaciones que en su
  conjunto superen la cifra de 3.005,06 €.
* Los obligados tributarios que hayan realizado exclusivamente operaciones
  no declarables.
* Los obligados tributarios que deban informar sobre las operaciones
  incluidas en los libros registro de IVA (modelo 340) salvo que realicen
  operaciones que expresamente deban incluirse en el modelo 347.

(http://www.boe.es/boe/dias/2008/10/23/pdfs/A42154-42190.pdf)

**Table of contents**

.. contents::
   :local:

Installation
============

Para instalar este módulo, es necesario el módulo *account_tax_balance*,
disponible en:

https://github.com/OCA/account-financial-reporting

y donaciones

https://github.com/OCA/donation



Usage
=====

### 

* Tener productos marcados como donativo, establecer la clave y marcarlos como recibo de impuestos.
* Añadir donativos y validarlos en un año fiscal. Debe haber importe cálculado en el modelo de donativo o no se generará el recibo
* Generar los recibos anuales, esto agrupará los donativos por cliente.

Al generar el modelo, crear la exportación 182, asociando el modelo de exportación 182. Al darle a calcular, se procesaran todas las líneas de donativo, agrupando por cliente, si es en especie, clave 182, tipo bien, identificacion, nif patrimonio y nombre patrimonio.

Si existen errores en los detalles de las líneas se marcarán en rojo, y se indicarrá el mensaje de error.

Los campos de revociación y de ejercicio_revocación no se calculan. 

El campo recurrencia, se calcula solo para la naturaleza del declatante = 1 y clave sea A o B

o bien naturaleza declarante = 4 u clave G. Se mirarrá si existen líneas de exportación 182 en los dos ejercicios anteriores.

El tipo de bien, y el indicar el ISIN así como lo referente al patrimonio protergido se establece a nivel de línea de donacion




Para realizar una declaración del modelo 182:

#. Vaya a *Facturación > Declaraciones AEAT > Modelo 182*.
#. Pulse en el botón "Crear".
#. Seleccione el año para la declaración.
#. Seleccione la configuración de exportación del modelo 182.
#. Pulse en "Calcular".
#. Se generarán el modelo de detalles de las líneas
#. Se puede corregir los datos en las líneas por si hay algún error
#. Pulse en "Exportar" para generar el fichero de exportación.

Known issues / Roadmap
======================

* Hacer los iconos del 182
* El campo revocación será siempre Falso
* El campo ejercicio revocación será siempre false

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/l10n-spain/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/l10n-spain/issues/new?body=module:%20l10n_es_aeat_mod347%0Aversion:%2016.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Tecnativa
* PESOL

Contributors
~~~~~~~~~~~~

* Comunitea (http://www.comunitea.com)

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/l10n-spain <https://github.com/OCA/l10n-spain/tree/16.0/l10n_es_aeat_mod347>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
