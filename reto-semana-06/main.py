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

def validar_empleado(codigo: str) -> Dict:
    # Plantilla: EMP - Depto - Número(4 dígitos, no empieza con 0)
    patron = r'^EMP-([A-Z]{3})-([1-9]\d{3})$'
    match = re.match(patron, codigo)
    
    valido = False
    depto = None
    num = None
    
    if match:
        depto = match.group(1)
        num = match.group(2)
        if depto in DEPARTAMENTOS_VALIDOS:
            valido = True
            
    return {"valido": valido, "departamento": depto, "numero": num}

def validar_factura(codigo: str) -> Dict:
    # Plantilla: FAC - Serie(A-E) - 6 dígitos
    patron = r'^FAC-([A-E])-(\d{6})$'
    match = re.match(patron, codigo)
    
    valido = bool(match)
    return {
        "valido": valido, 
        "serie": match.group(1) if match else None, 
        "numero": match.group(2) if match else None
    }

def validar_codigo(codigo: str) -> Dict:
    #Detecta el tipo y valida 
    resultado = {"codigo": codigo, "tipo": "desconocido", "valido": False, "detalles": {}}
    
    if codigo.startswith("TEC-") or codigo.startswith("ALI-") or codigo.startswith("ROB-"):
        resultado["tipo"] = "producto"
        resultado.update({"detalles": validar_producto(codigo)})
    elif codigo.startswith("ENV-"):
        resultado["tipo"] = "envio"
        resultado.update({"detalles": validar_envio(codigo)})
    elif codigo.startswith("EMP-"):
        resultado["tipo"] = "empleado"
        resultado.update({"detalles": validar_empleado(codigo)})
    elif codigo.startswith("FAC-"):
        resultado["tipo"] = "factura"
        resultado.update({"detalles": validar_factura(codigo)})
        
    resultado["valido"] = resultado["detalles"].get("valido", False)
    return resultado

def procesar_lote(codigos: List[str]) -> Dict:
    res = {
        "total": len(codigos), "validos": 0, "invalidos": 0,
        "por_tipo": {t: {"total": 0, "validos": 0} for t in ["producto", "envio", "empleado", "factura", "desconocido"]},
        "detalle": []
    }
    
    for c in codigos:
        v = validar_codigo(c)
        tipo = v["tipo"]
        res["por_tipo"][tipo]["total"] += 1
        if v["valido"]:
            res["validos"] += 1
            res["por_tipo"][tipo]["validos"] += 1
        else:
            res["invalidos"] += 1
        res["detalle"].append(v)
    return res

def main():
    CODIGOS = [
        "TEC-0001-MX", "ENV-2024-03-15-001234", "EMP-VEN-1234", "FAC-A-123456",
        "tec-0001-MX", "ENV-2019-03-15-001234", "EMP-VEN-0123", "FAC-F-123456", "XXX-123"
    ]
    reporte = procesar_lote(CODIGOS)
    print(f"Total: {reporte['total']} | Válidos: {reporte['validos']} | Inválidos: {reporte['invalidos']}")
    for tipo, stats in reporte["por_tipo"].items():
        if stats["total"] > 0:
            print(f" - {tipo.capitalize()}: {stats['validos']}/{stats['total']} OK")

if __name__ == "__main__":
    main()