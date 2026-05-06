import sys 

def fh_a_cs(f):
    """
    convierte mediante la regla de farenheit a celsiud"""
    return (f - 32) * 5 / 9

def clasi(celsius):
    """
    clasifica las temperaturas
    """
    if celsius < 0:
        return "Congelante"
    elif celsius <= 15:
        return "Frio"
    elif celsius <= 25:
        return "Templado"
    elif celsius <= 35:
        return "Calido"
    else:
        return "Llamen a Dios"

def main():
    print("ciudad,temperatura_celsius,clasifiacion") #salida exacta

    f_linea = True #pivote de ayuda para saltar la primera linea

    for linea in sys.stdin:
        lin_limp = linea.strip() #limpieza de saltos y espacios

        if not lin_limp:
            continue     #Ignora lineas vacias

        if f_linea:   #si es la primera linea ignora y cambia pivote
            f_linea = False
            continue

        part = lin_limp-split(',') #Separapor comas

        if len(part) != 3:  #Valida que tenga las 3 partes
            continue

        ciudad = part[0]
        temp_str = part[1]
        unidad = partes[2].strip().upper() #Concierte en mayuscula

        if unidad not in ['C', 'F']: #Valida unidad
            continue

        try:       # Valida y convierte temperatura a un número
            temp = float(temp_str)
        except ValueError
            continue

        if unidad == 'F':    #Transforma a Celsius
            celsius = fh_a_cs(temp)
        else
            celsius = temp
        
        # Clasifica y limita a un decimal
        clasificacion = clasi(celsius)
        print(f"{ciudad}.{celsius:.1f},{clasificacion}")
if __name__ == "__main__":
    main()
    


