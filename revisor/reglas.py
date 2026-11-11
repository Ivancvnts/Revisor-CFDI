from dataclasses import dataclass

OK, AVISO, ERROR = "ok", "aviso", "error"

RECEPTOR_RFC = "AAA010101AAA"
RECEPTOR_CP = "76000"
RECEPTOR_REGIMEN = "601"
USO_CFDI = "G03"

PAGOS_PERMITIDOS = {
    "PUE": ["03"],
    "PPD": ["99"],
}

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

def revisar_pago(cfdi):
    hallazgos = []

    #Revisamos si el método de pago existe y si esta dentro de los permitidos, para mostrar Error
    if cfdi.metodo_pago not in PAGOS_PERMITIDOS :
        hallazgos.append(Hallazgo(nivel=ERROR, campo="Método de pago", mensaje=f"Método {cfdi.metodo_pago!r} no permitido; opciones: {', '.join(PAGOS_PERMITIDOS)}"))
    
    #Mostramos error si la forma de pago no es la correcta para el método de pago
    elif cfdi.forma_pago not in PAGOS_PERMITIDOS[cfdi.metodo_pago]:
        hallazgos.append(Hallazgo(nivel=ERROR, campo="Forma de pago", mensaje=f"La forma de pago no coincide con el método {cfdi.metodo_pago}, se permite {', '.join(PAGOS_PERMITIDOS.get(cfdi.metodo_pago))}"))

    else:
        hallazgos.append(Hallazgo(nivel=OK, campo="Método y forma de pago", mensaje=f"Método y forma de pago: {cfdi.metodo_pago!r} con {cfdi.forma_pago} "))

    if cfdi.metodo_pago == 'PPD':
        hallazgos.append(Hallazgo(nivel=AVISO, campo="Método de pago", mensaje="Factura en PPD. Normalmente se pide PUE, revisar si se acepta asi."))

    return hallazgos

def validar(cfdi):
    hallazgos = []
    hallazgos += revisar_receptor(cfdi)
    hallazgos += revisar_pago(cfdi)
    return hallazgos