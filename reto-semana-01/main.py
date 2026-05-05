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
    pass








def main ():
    pass
if __name__ == "__main__":
    main()
