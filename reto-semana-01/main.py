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

def procc_lin(linea):
    pass
def main ():
    pass
if __name__ == "__main__":
    main()
    