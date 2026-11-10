# Plan: Revisor de facturas CFDI 4.0 (comisiones)

Herramienta de apoyo en Python que revisa el XML (y cruza el PDF) de las facturas de comisión
que llegan al correo de comisiones. No automatiza nada: la revisión final sigue siendo manual.

## Qué debe revisar
- Receptor: nuestro RFC, razón social, C.P., régimen y Uso del CFDI (G03)
- Emisor: RFC válido y régimen acorde a persona moral o física
- Retenciones: moral = ninguna; física = 2/3 IVA; RESICO (626) = 2/3 IVA + 1.25 % ISR
- Forma y método de pago, objeto de impuesto (02), unidad (E48)
- Importes, impuestos y totales que cuadren; que venga timbrado (UUID)
- PDF: UUID, RFC emisor, RFC receptor y total coinciden con el XML

## Arquitectura (decisión)
El núcleo no sabe nada de Outlook. Recibe archivos (bytes), los desempaqueta recursivamente
(zip, eml, adjuntos) hasta encontrar XML y PDF, los revisa y genera el reporte.
Casos a cubrir: (1) PDF y XML adjuntos directos, (2) correo dentro de otro correo (.eml / .msg),
(3) carpeta .zip con PDF y XML. Un link de descarga no se cubre: se baja a mano.

```
RevisorCFDI/
├── entrada/       <- aquí caen los archivos (xml, pdf, zip, eml)
├── procesados/    <- originales ya revisados (se mueven, nunca se borran)
└── reportes/      <- un reporte HTML por paquete revisado
```
Flujo: entrada/ -> desempaquetar -> emparejar XML+PDF -> revisar -> reporte en reportes/ -> mover a procesados/
(guardar el UUID revisado para detectar facturas repetidas).
Outlook solo es otra forma de llenar entrada/; el resto no cambia.

## Etapas

### 1. Leer un XML
- Meta: script que reciba la ruta de un XML e imprima RFC emisor, RFC receptor, régimen, UsoCFDI y Total.
- Practico: ElementTree (o defusedxml, porque los XML son de terceros), namespaces, atributos.
- Pista: namespace CFDI 4.0 = http://www.sat.gob.mx/cfd/4

### 2. Modelar los datos
- Meta: convertir el XML en dataclasses (Cfdi, Concepto, Impuesto).
- Practico: dataclasses, type hints, Decimal para dinero (nunca float).

### 3. Reglas, una por una
- Meta: una función por regla (revisar_receptor, revisar_retenciones, revisar_pago...) que devuelva hallazgos con nivel ok / aviso / error.
- Empezar por las fáciles (receptor, G03, E48, pago) y dejar retenciones y totales al final.

### 4. Pruebas con pytest (a la par de la etapa 3)
- Casos: moral correcta, física 612, RESICO correcta, RESICO sin ISR, receptor equivocado.
- Truco: una función que genere XML de ejemplo con parámetros.

### 5. Configuración y CLI
- Meta: datos fiscales en config.yaml y comando `python -m revisor check factura.xml`.
- Practico: PyYAML, argparse, estructura de paquete (__init__.py, __main__.py).

### 6. PDF y reporte
- Meta: con pypdf, cruzar UUID, RFCs y total del PDF contra el XML; generar reporte HTML.
- Cuidado: escapar con html.escape todo lo que venga del XML.

### 7. Carpeta de entrada y desempaquetado
- Meta: `python -m revisor carpeta` recorre entrada/, desempaqueta zip y eml, revisa cada paquete, guarda el reporte en reportes/ y mueve el original a procesados/.
- Practico: pathlib, zipfile, el módulo email, recursión, manejo de errores por archivo (un archivo malo no debe tirar todo).
- Cuidado con zips: límite de archivos y de tamaño total descomprimido (zip bomba), no escribir a disco con nombres del zip, avisar si trae contraseña.
- .msg requiere la librería extract-msg (solo si hace falta).
- Opcional al final: modo "vigilar" con watchdog, o programarlo con el Programador de tareas de Windows.

### 8. Outlook (opcional, al final)
- Meta: un correo extra (con licencia) al que yo reenvío los correos de clientes; el programa baja los adjuntos a entrada/ y me manda el reporte a mí.
- Requiere registrar una app en Entra ID (permisos delegados Mail.Read y Mail.Send) y activar "Permitir flujos de cliente público".
- Inicio de sesión con código de dispositivo, como la cuenta del correo extra; puede correr en mi PC, no necesita servidor.
- El reporte se envía a una dirección fija con sendMail (nunca reply ni reply-all), así no llega a clientes ni a gente en copia.
- Solo procesar correos cuyo remitente esté en una lista permitida (yo).
- Si algún día debe correr 24/7: credenciales de aplicación acotadas al buzón y ejecutarlo en una VM o Azure Function.

## Para el portafolio
- Usar XML de ejemplo con RFCs ficticios; nunca subir facturas reales ni config.yaml (.gitignore: config.yaml, entrada/, procesados/, reportes/, token_cache.json).
- Commits pequeños por etapa.
- README con el problema que resuelve, ejemplo de salida y cómo correrlo.
- Aclarar que es una herramienta de apoyo y la validación final es manual.

## Avance
- [ ] Etapa 1
- [ ] Etapa 2
- [ ] Etapa 3
- [ ] Etapa 4
- [ ] Etapa 5
- [ ] Etapa 6
- [ ] Etapa 7 (carpeta y desempaquetado)
- [ ] Etapa 8 (Outlook)