"""Sistema de Inventario Modular"""

from models.producto import Producto
from utils.validators import validar_producto
from utils.io import leer_inventario, escribir_reporte

ARCHIVO_INVENTARIO = "data/inventario.csv"
ARCHIVO_REPORTE = "outputs/reporte_inventario.csv"

def crear_productos(datos_raw):
    productos = []
    for datos in datos_raw:
        es_valido, error = validar_producto(
            datos.get('sku'), datos.get('nombre'), datos.get('categoria'),
            datos.get('precio'), datos.get('stock'), datos.get('stock_minimo')
        )
        if not es_valido:
            print(f"Advertencia: Ignorando registro invalido - {error}")
            continue
            
        producto = Producto(
            sku=datos['sku'], nombre=datos['nombre'], categoria=datos['categoria'],
            precio=float(datos['precio']), stock=int(datos['stock']), stock_minimo=int(datos['stock_minimo'])
        )
        productos.append(producto)
    return productos

def main():
    print("=" * 50)
    print("SISTEMA DE INVENTARIO - Reporte de Reorden")
    print("=" * 50)
    
    datos_raw = leer_inventario(ARCHIVO_INVENTARIO)
    productos = crear_productos(datos_raw)
    
    # Filtrar y ordenar
    necesitan_reorden = [p for p in productos if p.necesita_reorden()]
    necesitan_reorden = sorted(necesitan_reorden, key=lambda p: p.unidades_faltantes(), reverse=True)
    
    print("\nPRODUCTOS QUE NECESITAN REORDEN:")
    for p in necesitan_reorden:
        print(p)
    
    escribir_reporte(necesitan_reorden, ARCHIVO_REPORTE)
    print(f"\nReporte guardado en: {ARCHIVO_REPORTE}")

if __name__ == "__main__":
    main()