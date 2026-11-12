from dataclasses import replace
from pathlib import Path

import pytest

from revisor.cfdi import leer_cfdi
from revisor.reglas import AVISO, ERROR, OK, revisar_pago, revisar_receptor

EJEMPLOS = Path(__file__).parent.parent / "ejemplos"

@pytest.fixture
def cfdi_moral():
  return leer_cfdi(EJEMPLOS / "moral_correcta.xml")

def niveles(hallazgos):
  return [h.nivel for h in hallazgos]

#TEST DE METODO Y FORMA DE PAGO
def test_pago_correcto(cfdi_moral):
  assert niveles(revisar_pago(cfdi_moral)) ==[OK]

@pytest.mark.parametrize("metodo, forma, esperado", [
    pytest.param("PUE", "03", [OK], id="pue_con_03_ok"),
    pytest.param("PPD", "99", [OK, AVISO], id="ppd_con_99_ok_y_aviso"),
    pytest.param("PPD", "03", [ERROR, AVISO], id="ppd_con_03_error_y_aviso"),
    pytest.param("PUE", "04", [ERROR], id="pue_con_forma_no_permitida"),
    pytest.param("XYZ", "03", [ERROR], id="metodo_inventado"),
    pytest.param(None, "03", [ERROR], id="sin_metodo"),
    pytest.param("PUE", None, [ERROR], id="sin_forma"),
])
def test_pago(cfdi_moral, metodo, forma, esperado):
    cfdi = replace(cfdi_moral, metodo_pago=metodo, forma_pago=forma)
    assert niveles(revisar_pago(cfdi)) == esperado

def test_receptor_correcto(cfdi_moral):
  assert niveles(revisar_receptor(cfdi_moral)) ==[OK, OK, OK, OK]

#TEST DE RECEPTOR
@pytest.mark.parametrize("atributo, valor, campo_error", [
    pytest.param("rfc", "ESTOESTAMALMUYMAL", "RFC del receptor", id="rfc_incorrecto"),
    pytest.param("regimen", "602", "Régimen fiscal del receptor", id="regimen_incorrecto"),
    pytest.param("codigo_postal", "76001", "Código postal del receptor", id="cp_incorrecto"),
    pytest.param("uso_cfdi", "G04", "Uso de CFDI", id="uso_cfdi_incorrecto"),
    pytest.param("uso_cfdi", None, "Uso de CFDI", id="uso_cfdi_none"),
])
def test_receptor_incorrecto(cfdi_moral, atributo, valor, campo_error):
    cfdi = replace(cfdi_moral, receptor=replace(cfdi_moral.receptor, **{atributo: valor}))
    hallazgos = revisar_receptor(cfdi)
    errores = [h.campo for h in hallazgos if h.nivel == ERROR]
    assert errores == [campo_error]

