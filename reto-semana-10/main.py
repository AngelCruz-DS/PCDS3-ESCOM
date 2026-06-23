import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

# =====================================================================
# PARTE 1: ANÁLISIS ESTADÍSTICO BÁSICO
# =====================================================================
def estadisticas_basicas(precios: pd.Series) -> Dict:
    return {
        "precio_actual": float(precios.iloc[-1]),
        "precio_minimo": float(precios.min()),
        "precio_maximo": float(precios.max()),
        "precio_promedio": float(precios.mean()),
        "precio_mediana": float(precios.median()),
        "desviacion_std": float(precios.std()),
        "rango": float(precios.max() - precios.min()),
        "dias_analizados": len(precios)
    }

def calcular_rendimientos(precios: pd.Series) -> pd.Series:
    # pct_change calcula la diferencia porcentual con el valor anterior
    return precios.pct_change() * 100

def analisis_rendimientos(rendimientos: pd.Series) -> Dict:
    rend_limpios = rendimientos.dropna()
    if rend_limpios.empty:
        return {}
        
    mejor_fecha = rend_limpios.idxmax()
    peor_fecha = rend_limpios.idxmin()
    
    return {
        "rendimiento_total": float(rend_limpios.sum()),
        "rendimiento_promedio": float(rend_limpios.mean()),
        "mejor_dia": (mejor_fecha.strftime('%Y-%m-%d'), float(rend_limpios.max())),
        "peor_dia": (peor_fecha.strftime('%Y-%m-%d'), float(rend_limpios.min())),
        "dias_positivos": int((rend_limpios > 0).sum()),
        "dias_negativos": int((rend_limpios < 0).sum()),
        "volatilidad": float(rend_limpios.std())
    }

# =====================================================================
# PARTE 2: INDICADORES TÉCNICOS
# =====================================================================
def media_movil(precios: pd.Series, ventana: int) -> pd.Series:
    return precios.rolling(window=ventana).mean()

def bandas_bollinger(precios: pd.Series, ventana: int = 20, num_std: int = 2) -> Dict:
    sma = media_movil(precios, ventana)
    std = precios.rolling(window=ventana).std()
    return {
        "banda_superior": sma + (num_std * std),
        "banda_media": sma,
        "banda_inferior": sma - (num_std * std)
    }

def detectar_maximos_minimos(precios: pd.Series, ventana: int = 5) -> Dict:
    # Usamos center=True para comparar con N días antes y N días después
    ventana_total = ventana * 2 + 1
    max_locales = precios[precios == precios.rolling(window=ventana_total, center=True).max()]
    min_locales = precios[precios == precios.rolling(window=ventana_total, center=True).min()]
    return {
        "maximos": max_locales,
        "minimos": min_locales
    }

def clasificar_tendencia(precios: pd.Series, ventana: int = 10) -> str:
    ma = media_movil(precios, ventana)
    if len(ma) < 2 or pd.isna(ma.iloc[-1]) or pd.isna(ma.iloc[-2]):
        return "LATERAL"
        
    precio_actual = precios.iloc[-1]
    ma_actual = ma.iloc[-1]
    ma_anterior = ma.iloc[-2]
    
    if precio_actual > ma_actual and ma_actual > ma_anterior:
        return "ALCISTA"
    elif precio_actual < ma_actual and ma_actual < ma_anterior:
        return "BAJISTA"
    else:
        return "LATERAL"

# =====================================================================
# PARTE 3: SISTEMA DE ALERTAS
# =====================================================================
def generar_senales_trading(precios: pd.Series, ma_corta: int = 5, ma_larga: int = 20) -> pd.Series:
    corta = media_movil(precios, ma_corta)
    larga = media_movil(precios, ma_larga)
    senales = pd.Series("MANTENER", index=precios.index)
    
    cruce_arriba = (corta > larga) & (corta.shift(1) <= larga.shift(1))
    cruce_abajo = (corta < larga) & (corta.shift(1) >= larga.shift(1))
    
    senales.loc[cruce_arriba] = "COMPRA"
    senales.loc[cruce_abajo] = "VENTA"
    return senales

def alertas_precio(precios: pd.Series, umbral_cambio: float = 5.0) -> List[Dict]:
    rendimientos = calcular_rendimientos(precios).dropna()
    alertas = []
    
    for fecha, rend in rendimientos.items():
        if abs(rend) >= umbral_cambio:
            alertas.append({
                "fecha": fecha.strftime('%Y-%m-%d'),
                "tipo": "SUBIDA" if rend > 0 else "CAIDA",
                "cambio": rend
            })
    return alertas

def clasificar_volatilidad(rendimientos: pd.Series) -> str:
    std = rendimientos.std()
    if pd.isna(std): return "DESCONOCIDA"
    if std < 1.0: return "BAJA"
    elif std < 3.0: return "MEDIA"
    elif std < 5.0: return "ALTA"
    else: return "MUY ALTA"

def generar_reporte_completo(precios: pd.Series, nombre_accion: str) -> Dict:
    rendimientos = calcular_rendimientos(precios)
    senales = generar_senales_trading(precios)
    
    return {
        "nombre": nombre_accion,
        "periodo": {
            "inicio": precios.index[0].strftime('%Y-%m-%d'),
            "fin": precios.index[-1].strftime('%Y-%m-%d'),
            "dias": len(precios)
        },
        "estadisticas": estadisticas_basicas(precios),
        "rendimientos": analisis_rendimientos(rendimientos),
        "tendencia": clasificar_tendencia(precios),
        "volatilidad": clasificar_volatilidad(rendimientos),
        "senal_actual": str(senales.iloc[-1]),
        "alertas_recientes": alertas_precio(precios)
    }

# =================================