import sys
from revisor.cfdi import leer_cfdi
from revisor.reglas import validar

cfdi = leer_cfdi(sys.argv[1])
for h in validar(cfdi):
  print(f"{h.nivel.upper():<6} {h.mensaje}")