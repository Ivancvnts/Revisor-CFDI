import sys
from revisor.cfdi import leer_cfdi

cfdi = leer_cfdi(sys.argv[1])

print(cfdi)