from dataclasses import dataclass

OK, AVISO, ERROR = "ok", "aviso", "error"

# CONSTANTES RECEPTOR POSTERIORMENTE SE TOMAN DE CONFIG
RECEPTOR_RFC = "AAA010101AAA"
RECEPTOR_CP = "76000"
RECEPTOR_REGIMEN = "601"
USO_CFDI = "G03"
# CONSTANTES METODO Y FORMA DE PAGO POSTERIORMENTE SE TOMAN DE CONFIG
PAGOS_PERMITIDOS = {
    "PUE": ["03"],
    "PPD": ["99"],
}
# CONSTANTES CONCEPTO POSTERIORMENTE SE TOMAN DE CONFIG
CLAVE_PROD_SERV_PERMITIDAS = ["80141628", "80141600"]
UNIDAD_ESPERADA = "E48"
OBJETO_IMP_ESPERADO = "02"


@dataclass
class Hallazgo:
    nivel: str  # ok, aviso o error
    campo: str  # qué se revisó, ej. "Tipo de comprobante"
    mensaje: str  # explicación


def comparar(campo: str, encontrado, esperado):
    nivel = OK if encontrado == esperado else ERROR
    mensaje = (
        f"{campo}: {encontrado}"
        if nivel == OK
        else f"El campo {campo} es {encontrado} y se espera {esperado}"
    )
    return Hallazgo(nivel=nivel, campo=campo, mensaje=mensaje)


def revisar_receptor(cfdi):
    hallazgos = []
    hallazgos.append(comparar("RFC del receptor", cfdi.receptor.rfc, RECEPTOR_RFC))
    hallazgos.append(
        comparar("Código postal del receptor", cfdi.receptor.codigo_postal, RECEPTOR_CP)
    )
    hallazgos.append(
        comparar("Régimen fiscal del receptor", cfdi.receptor.regimen, RECEPTOR_REGIMEN)
    )
    hallazgos.append(comparar("Uso de CFDI", cfdi.receptor.uso_cfdi, USO_CFDI))

    return hallazgos


def revisar_pago(cfdi):
    hallazgos = []

    # Revisamos si el método de pago existe y si esta dentro de los permitidos, para mostrar Error
    if cfdi.metodo_pago not in PAGOS_PERMITIDOS:
        hallazgos.append(
            Hallazgo(
                nivel=ERROR,
                campo="Método de pago",
                mensaje=f"Método {cfdi.metodo_pago!r} no permitido; opciones: {', '.join(PAGOS_PERMITIDOS)}",
            )
        )

    # Mostramos error si la forma de pago no es la correcta para el método de pago
    elif cfdi.forma_pago not in PAGOS_PERMITIDOS[cfdi.metodo_pago]:
        hallazgos.append(
            Hallazgo(
                nivel=ERROR,
                campo="Forma de pago",
                mensaje=f"La forma de pago no coincide con el método {cfdi.metodo_pago}, se permite {', '.join(PAGOS_PERMITIDOS.get(cfdi.metodo_pago))}",
            )
        )

    else:
        hallazgos.append(
            Hallazgo(
                nivel=OK,
                campo="Método y forma de pago",
                mensaje=f"Método y forma de pago: {cfdi.metodo_pago!r} con {cfdi.forma_pago} ",
            )
        )

    if cfdi.metodo_pago == "PPD":
        hallazgos.append(
            Hallazgo(
                nivel=AVISO,
                campo="Método de pago",
                mensaje="Factura en PPD. Normalmente se pide PUE, revisar si se acepta asi.",
            )
        )

    return hallazgos


def revisar_conceptos(cfdi):
    hallazgos = []

    for indice, concepto in enumerate(cfdi.conceptos, start=1):
        campos_con_errores = []

        if concepto.clave_prod_serv not in CLAVE_PROD_SERV_PERMITIDAS:
            campos_con_errores.append("Clave de producto o servicio")

        if concepto.clave_unidad != UNIDAD_ESPERADA:
            campos_con_errores.append("Clave de unidad")

        if concepto.objeto_imp != OBJETO_IMP_ESPERADO:
            campos_con_errores.append("Objeto de impuesto")

        if not campos_con_errores:
            continue

        hallazgos.append(
            Hallazgo(
                nivel=ERROR,
                campo=f"Concepto {indice}",
                mensaje=f"Errores en {', '.join(campos_con_errores)}",
            )
        )

    if not hallazgos:
        cantidad_conceptos = len(cfdi.conceptos)
        hallazgos.append(
            Hallazgo(
                nivel=OK,
                campo="Conceptos",
                mensaje=f"{cantidad_conceptos} concepto{'' if cantidad_conceptos == 1 else 's'} sin errores",
            )
        )

    return hallazgos


def validar(cfdi):
    hallazgos = []
    hallazgos += revisar_receptor(cfdi)
    hallazgos += revisar_pago(cfdi)
    hallazgos += revisar_conceptos(cfdi)
    return hallazgos
