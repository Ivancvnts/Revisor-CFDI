from dataclasses import dataclass
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
class Cfdi:
  emisor: Emisor
  receptor: Receptor
  subtotal: Decimal
  total: Decimal
  uuid: str

def leer_cfdi(ruta):
  raiz = ET.parse(ruta).getroot()

  NS = {
    "cfdi": "http://www.sat.gob.mx/cfd/4",
    "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital"
  }

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

  subtotal = Decimal(raiz.get("SubTotal"))
  total = Decimal(raiz.get("Total"))
  uuid = raiz.find("cfdi:Complemento", NS).find("tfd:TimbreFiscalDigital", NS).get("UUID")
  cfdi = Cfdi(emisor=emisor, receptor=receptor, subtotal=subtotal, total=total, uuid=uuid)

  return cfdi