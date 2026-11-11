import sys
from defusedxml import ElementTree as ET

ruta = sys.argv[1]
raiz = ET.parse(ruta).getroot()

NS = {
  "cfdi": "http://www.sat.gob.mx/cfd/4",
  "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital"
}

emisorTag = raiz.find("cfdi:Emisor", NS)
emisorName = emisorTag.get("Nombre")
emisorRFC = emisorTag.get("Rfc")
emisorRegimen = emisorTag.get("RegimenFiscal")

receptorTag = raiz.find("cfdi:Receptor", NS)
receptorName = receptorTag.get("Nombre")
receptorRFC = receptorTag.get("Rfc")
receptorCP = receptorTag.get("DomicilioFiscalReceptor")
receptorRegimen = receptorTag.get("RegimenFiscalReceptor")
receptorUso = receptorTag.get("UsoCFDI")

timbreFiscalDigital = raiz.find("cfdi:Complemento", NS).find("tfd:TimbreFiscalDigital", NS)

print(f"Emisor - Nombre: {emisorName} RFC: {emisorRFC} Regimen fiscal: {emisorRegimen}")
print(f"Receptor - Nombre: {receptorName} RFC: {receptorRFC} Regimen fiscal: {receptorRegimen}")
print(f"Total: {raiz.get('Total')}")
print(f"UUID: {timbreFiscalDigital.get('UUID')}")