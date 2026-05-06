import sys

def main():
    productos = {} #El diccionario principal

    f_linea = True #pivote para ignorar el encabezado

    for linea in sys.stdin:   #lee y agrupa datos
        linea = linea.strip()

        if f_linea:
            f_linea = False #Ignora y cambia de pivote
            continue

        if not linea:
            continue

        partes = linea.split(",") #Seprar por comas

        if len(partes) != 4:  #Valida que esten las 4 columnas
            continue 

        producto = partes[1]

        try:   #Convierte cantidad a entero y precio a deecimal
            cantidad = int(partes[2])
            precio = float(partes[3])
        except ValueError:
            continue #Ignora si hay letras donde deberia haber numeros

        if producto not in productos: #crea diccionario si aun no existe
            productos[producto] = {
                "unidades": 0,
                "ingreso": 0.0
            }

        #suma los datos
        productos[producto]["unidades"] += cantidad
        productos[producto]["ingreso"] += (cantidad * precio)

    for prod in productos: #Calcula promedio de cada producto
        unidades = productos[prod]["unidades"]
        ingreso = productos[prod]["ingreso"]

        productos[prod]["promedio"] = ingreso / unidades if unidades > 0 else 0
        
    prod_ord = sorted( #Ordena de mayor a menor
        productos.items(),
        key=lambda x: x[1]["ingreso"], #"lambda" es una funcion anonima
        reverse=True #Ordena de manera descendente
    )

    print("producto,unidades_vendidas,ingreso_total,precio_promedio")
    for nombre, datos in prod_ord:
        unidades_final = datos["unidades"]
        ingreso_final = datos ["ingreso"]
        promedio_final = datos["promedio"]

        print(f"{nombre},{unidades_final},{ingreso_final:.2f},{promedio_final:.2f}")

if __name__ == "__main__":
    main()
    