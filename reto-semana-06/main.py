import re
from typing import Dict, List

# Listas de confianza
DEPARTAMENTOS_VALIDOS = ['VEN', 'ADM', 'TEC', 'LOG', 'RHH']
SERIES_VALIDAS = ['A', 'B', 'C', 'D', 'E']

def validar_producto(codigo: str) -> Dict:
    # Plantilla: 3 letras - 4 números - 2 letras país
    patron = r'^([A-Z]{3})-(\d{4})-([A-Z]{2})$'
    match = re.match(patron, codigo)
    
    valido = bool(match)
    return {
        "valido": valido,
        "categoria": match.group(1) if match else None,
        "numero": match.group(2) if match else None,
        "pais": match.group(3) if match else None
    }

def validar_envio(codigo: str) -> Dict:
    # Plantilla: ENV - Año(2020-2030) - Mes(01-12) - Dia(01-31) - 6 dígitos
    patron = r'^ENV-(202[0-9]|2030)-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])-(\d{6})$'
    match = re.match(patron, codigo)
    
    valido = bool(match)
    return {
        "valido": valido,
        "fecha": f"{match.group(1)}-{match.group(2)}-{match.group(3)}" if match else None,
        "secuencial": match.group(4) if match else None
    }