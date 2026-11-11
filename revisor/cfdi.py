from dataclasses import dataclass, field
from decimal import Decimal
from defusedxml import ElementTree as ET

@dataclass
class Emisor:
  nombre: str
  rfc: str
  regimen: str

@dataclass
class Receptor:
  nombre: str
  rfc: str
  regimen: str
  codigo_postal: str
  uso_cfdi: str

@dataclass
class Impuesto:
  impuesto: str
  tipo_factor: str
  tasa: Decimal | None
  base: Decimal
  importe: Decimal

@dataclass
class Concepto:
  clave_prod_serv: str
  clave_unidad: str
  descripcion: str
  objeto_imp: str
  cantidad: Decimal
  valor_unitario: Decimal
  importe: Decimal
  traslados: list[Impuesto] = field(default_factory=list)
  retenciones: list[Impuesto] = field(default_factory=list)

@dataclass
class Cfdi:
  emisor: Emisor
  receptor: Receptor
  version: str
  fecha: str
  tipo: str
  forma_pago: str
  metodo_pago: str
  moneda: str
  exportacion: str
  subtotal: Decimal
  total_traslados:Decimal | None
  total_retenciones:Decimal | None
  total: Decimal
  uuid: str
  conceptos: list[Concepto]

#NameSpaces en los XML de los CFDI 4.0
NS = {
    "cfdi": "http://www.sat.gob.mx/cfd/4",
    "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital"
  }

#Helper para setear correctamente un valor a None o a Decimal, segun el caso.
def a_decimal(texto):
  return None if not texto else Decimal(texto)

#Itera sobre los impuestos y regresa un objeto
def leer_impuestos(etiqueta_concepto, ruta):

  lista = []

  for etiqueta_impuesto in etiqueta_concepto.findall(ruta, NS):
    impuesto= etiqueta_impuesto.get('Impuesto')
    tipo_factor= etiqueta_impuesto.get('TipoFactor')
    tasa= Decimal(etiqueta_impuesto.get('TasaOCuota'))
    base= Decimal(etiqueta_impuesto.get('Base'))
    importe= Decimal(etiqueta_impuesto.get('Importe'))

    impuesto_obj = Impuesto(
      impuesto=impuesto,
      tipo_factor=tipo_factor,
      tasa=a_decimal(tasa),
      base=base,
      importe= importe
    )

    lista.append(impuesto_obj)
    
  return lista

#Lee el xml, crea los objetos y las variables necesarias para regresar un objeto de la clase Cfdi
def leer_cfdi(ruta):
  raiz = ET.parse(ruta).getroot()

  emisor_etiqueta = raiz.find("cfdi:Emisor", NS)
  emisor_nombre = emisor_etiqueta.get("Nombre")
  emisor_rfc = emisor_etiqueta.get("Rfc")
  emisor_regimen = emisor_etiqueta.get("RegimenFiscal")

  emisor = Emisor(nombre = emisor_nombre, rfc = emisor_rfc, regimen = emisor_regimen)

  receptor_etiqueta = raiz.find("cfdi:Receptor", NS)
  receptor_nombre = receptor_etiqueta.get("Nombre")
  receptor_rfc = receptor_etiqueta.get("Rfc")
  receptor_regimen = receptor_etiqueta.get("RegimenFiscalReceptor")
  receptor_cp = receptor_etiqueta.get("DomicilioFiscalReceptor")
  receptor_uso = receptor_etiqueta.get("UsoCFDI")

  receptor = Receptor(nombre = receptor_nombre, rfc = receptor_rfc, regimen = receptor_regimen, codigo_postal = receptor_cp, uso_cfdi = receptor_uso)

  conceptos = []

  for etiqueta_concepto in raiz.findall("cfdi:Conceptos/cfdi:Concepto", NS):

    clave_prod_serv = etiqueta_concepto.get('ClaveProdServ')
    clave_unidad= etiqueta_concepto.get('ClaveUnidad')
    descripcion= etiqueta_concepto.get('Descripcion')
    objeto_imp= etiqueta_concepto.get('ObjetoImp')
    cantidad= Decimal(etiqueta_concepto.get('Cantidad'))
    valor_unitario= Decimal(etiqueta_concepto.get('ValorUnitario'))
    importe= Decimal(etiqueta_concepto.get('Importe'))
    traslados = leer_impuestos(etiqueta_concepto, "cfdi:Impuestos/cfdi:Traslados/cfdi:Traslado")
    retenciones = leer_impuestos(etiqueta_concepto, "cfdi:Impuestos/cfdi:Retenciones/cfdi:Retencion")

    concepto = Concepto(
      clave_prod_serv=clave_prod_serv,
      clave_unidad=clave_unidad,
      descripcion=descripcion,
      objeto_imp=objeto_imp,
      cantidad=cantidad,
      valor_unitario=valor_unitario,
      importe=importe,
      traslados=traslados,
      retenciones=retenciones
    )

    conceptos.append(concepto)

  version = raiz.get("Version")
  fecha = raiz.get("Fecha")
  tipo = raiz.get("TipoDeComprobante")
  forma_pago = raiz.get("FormaPago")
  metodo_pago = raiz.get("MetodoPago")
  moneda = raiz.get("Moneda")
  exportacion = raiz.get("Exportacion")
  subtotal = Decimal(raiz.get("SubTotal"))
  impuestos_globales = raiz.find("cfdi:Impuestos", NS)
  total_traslados = a_decimal(impuestos_globales.get("TotalImpuestosTrasladados")) if impuestos_globales is not None else None
  total_retenciones = a_decimal(impuestos_globales.get("TotalImpuestosRetenidos")) if impuestos_globales is not None else None
  total = Decimal(raiz.get("Total"))
  uuid = raiz.find("cfdi:Complemento/tfd:TimbreFiscalDigital", NS).get("UUID")
  cfdi = Cfdi(
    emisor=emisor,
    receptor=receptor,
    version=version,
    fecha=fecha,
    tipo=tipo,
    forma_pago=forma_pago,
    metodo_pago=metodo_pago,
    moneda=moneda,
    exportacion=exportacion,
    subtotal=subtotal,
    total_traslados=total_traslados,
    total_retenciones=total_retenciones,
    total=total,
    uuid=uuid,
    conceptos=conceptos)

  return cfdi