from dataclasses import dataclass

OK, AVISO, ERROR = "ok", "aviso", "error"

RECEPTOR_RFC = "AAA010101AAA"
RECEPTOR_CP = "76000"
RECEPTOR_REGIMEN = "601"
USO_CFDI = "G03"

@dataclass
class Hallazgo:
    nivel: str      # ok, aviso o error
    campo: str      # qué se revisó, ej. "Tipo de comprobante"
    mensaje: str    # explicación

def comparar(campo: str, encontrado, esperado):
    nivel = OK if encontrado == esperado else ERROR
    mensaje = f"{campo}: {encontrado}" if nivel == OK else f"El campo {campo} es {encontrado} y se espera {esperado}" 
    return Hallazgo(nivel=nivel, campo=campo, mensaje=mensaje)

def revisar_receptor(cfdi):
    hallazgos = []
    hallazgos.append(comparar("RFC del receptor", cfdi.receptor.rfc, RECEPTOR_RFC))
    hallazgos.append(comparar("Código postal del receptor", cfdi.receptor.codigo_postal, RECEPTOR_CP))
    hallazgos.append(comparar("Régimen fiscal del receptor", cfdi.receptor.regimen, RECEPTOR_REGIMEN))
    hallazgos.append(comparar("Uso de CFDI", cfdi.receptor.uso_cfdi, USO_CFDI))

    return hallazgos
    
def validar(cfdi):
    hallazgos = []
    hallazgos += revisar_receptor(cfdi)
    return hallazgos
    