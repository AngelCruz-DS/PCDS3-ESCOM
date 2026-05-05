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
    