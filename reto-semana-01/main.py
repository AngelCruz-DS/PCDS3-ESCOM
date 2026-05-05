import sys

def lim_val(valor):
    """
    Limpia un valor individual:
    -Elimina caracteres no válidos
    """
    val_sin_esp = valor.strip() #Quita los espacios en blanco de ambos lados

    caracteres_validos = '0123456789.-' #Guarda los caracteres validos
    resultado = ''
    
    #Aqui revisa letra por letra
    for char in val_sin_esp:
        if char in caracteres_validos:
            resultado += char
    return resultado

def conv_ent(texto):
    """"
    Convierte texto a entero turncando decimales
    para textos vacios o invalidos da un 0
    """
    #Para cadenas vacias
    if not texto:
        return 0
    
    #red de seguridad
    try:
        numero = float(texto) #Convierte a numwro con decimales
        return int(numero) #trunca
    except ValueError:
        return 0 #0 en caso de error
    





def procc_lin(linea):
    """
    -quita los espacios en blanco de los extremos
    -Separa por comas
    -Limpia, trunca y suma cada valor
    """
    limpialineas = linea.strip() #Quita el salto de linea y espacios en los extremos

    if not limpialineas: 
        return 0 #lineas vacias dan 0
    
    elem = limpialineas.split(",") #Corta en cada coma
    sum_tot = 0

    for elem in elem:   #Pasamos cada "pedazo"
        limpio = lim_val(elem)
        numero = conv_ent(limpio)
        sum_tot += numero

    return sum_tot 

def main():
    """
    Lee el archivo linea por linea, procesa e imprime
    """
    for linea in sys.stdin:
        resultado = procc_lin(linea)
        print(resultado)

if __name__ == "__main__":
    main()
    








