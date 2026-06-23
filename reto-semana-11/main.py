import pandas as pd
import numpy as np
import os
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# =====================================================================
# PARTE 1: CARGA DE DATOS BASE
# =====================================================================

def cargar_datos() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Carga los datos de estudiantes, calificaciones y materias.
    """
    # Datos de estudiantes
    estudiantes = pd.DataFrame({
        'boleta': ['2021630001', '2021630002', '2021630003', '2021630004', '2021630005',
                   '2022630001', '2022630002', '2022630003', '2022630004', '2022630005',
                   '2023630001', '2023630002', '2023630003', '2023630004', '2023630005'],
        'nombre': ['Juan Pérez García', 'María López Ruiz', 'Pedro Sánchez Torres',
                   'Ana Martínez Díaz', 'Luis Rodríguez Vega', 'Carmen Flores Luna',
                   'Roberto Díaz Mora', 'Laura Torres Silva', 'Diego Ramírez Cruz',
                   'Sofía Vargas Romo', 'Carlos Mendoza Ríos', 'Patricia Ortiz León',
                   'Miguel Ángel Castro', 'Fernanda Reyes Paz', 'Andrés Guzmán Villa'],
        'semestre': [4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2],
        'carrera': ['CD'] * 15,
        'email': ['juan.perez@ipn.mx', 'maria.lopez@ipn.mx', 'pedro.sanchez@ipn.mx',
                  'ana.martinez@ipn.mx', 'luis.rodriguez@ipn.mx', 'carmen.flores@ipn.mx',
                  'roberto.diaz@ipn.mx', 'laura.torres@ipn.mx', 'diego.ramirez@ipn.mx',
                  'sofia.vargas@ipn.mx', 'carlos.mendoza@ipn.mx', 'patricia.ortiz@ipn.mx',
                  'miguel.castro@ipn.mx', 'fernanda.reyes@ipn.mx', 'andres.guzman@ipn.mx']
    })
    
    # Datos de materias
    materias = pd.DataFrame({
        'materia_id': ['MAT101', 'MAT102', 'PROG101', 'PROG102', 'EST101', 'EST102', 'BD101'],
        'nombre': ['Cálculo Diferencial', 'Cálculo Integral', 'Programación I',
                   'Programación II', 'Probabilidad', 'Estadística Inferencial',
                   'Bases de Datos'],
        'creditos': [8, 8, 6, 6, 6, 6, 6],
        'semestre_materia': [1, 2, 1, 2, 2, 3, 3]
    })
    
    # Generar calificaciones (simuladas)
    np.random.seed(42)
    calificaciones_data = []
    
    for boleta in estudiantes['boleta']:
        semestre = estudiantes[estudiantes['boleta'] == boleta]['semestre'].values[0]
        materias_cursadas = materias[materias['semestre_materia'] <= semestre]['materia_id'].tolist()
        
        for materia in materias_cursadas:
            base = np.random.uniform(5, 10)
            p1 = round(min(10, max(0, base + np.random.normal(0, 1))), 1)
            p2 = round(min(10, max(0, base + np.random.normal(0, 1))), 1)
            final = round(min(10, max(0, base + np.random.normal(0, 0.5))), 1)
            
            # Algunos valores nulos aleatorios para probar limpieza
            if np.random.random() < 0.05:
                p2 = np.nan
            
            calificaciones_data.append({
                'boleta': boleta,
                'materia_id': materia,
                'parcial_1': p1,
                'parcial_2': p2,
                'final': final
            })
    
    calificaciones = pd.DataFrame(calificaciones_data)
    
    return estudiantes, calificaciones, materias

def info_general(df_estudiantes: pd.DataFrame, df_calificaciones: pd.DataFrame) -> Dict:
    """
    Genera información general del sistema.
    """
    return {
        "total_estudiantes": len(df_estudiantes),
        "total_registros_calif": len(df_calificaciones),
        "semestres": sorted(df_estudiantes['semestre'].unique().tolist()),
        "materias_con_registros": df_calificaciones['materia_id'].nunique()
    }

def validar_datos(df_calificaciones: pd.DataFrame) -> Dict:
    """
    Valida la integridad de los datos.
    """
    # Detecta si hay alguna fila que contenga un NaN
    nulos = int(df_calificaciones.isna().any(axis=1).sum())
    
    # Revisa si hay calificaciones negativas o mayores a 10
    columnas_calif = ['parcial_1', 'parcial_2', 'final']
    fuera_rango = int(((df_calificaciones[columnas_calif] < 0) | 
                       (df_calificaciones[columnas_calif] > 10)).any(axis=1).sum())
    
    return {
        "registros_con_nulos": nulos,
        "calificaciones_fuera_rango": fuera_rango,
        "datos_validos": bool(nulos == 0 and fuera_rango == 0)
    }

    def buscar_estudiante(df_estudiantes: pd.DataFrame, criterio: str, valor: str) -> pd.DataFrame:
    """
    Busca estudiantes por diferentes criterios.
    """
    if criterio == 'nombre':
        # Búsqueda parcial ignorando mayúsculas/minúsculas
        return df_estudiantes[df_estudiantes['nombre'].str.contains(valor, case=False, na=False)]
    elif criterio == 'semestre':
        return df_estudiantes[df_estudiantes['semestre'] == int(valor)]
    elif criterio == 'boleta':
        return df_estudiantes[df_estudiantes['boleta'] == str(valor)]
    else:
        return pd.DataFrame()

def obtener_kardex(boleta: str, df_estudiantes: pd.DataFrame, 
                   df_calificaciones: pd.DataFrame, df_materias: pd.DataFrame) -> Dict:
    """
    Obtiene el kardex completo de un estudiante.
    """
    estudiante_df = df_estudiantes[df_estudiantes['boleta'] == boleta]
    
    if estudiante_df.empty:
        return {"estudiante": None, "materias": None, "promedio_general": 0.0,
                "creditos_cursados": 0, "materias_aprobadas": 0, "materias_reprobadas": 0}
    
    # Extraer los datos del estudiante como diccionario
    est_info = estudiante_df.iloc[0].to_dict()
    
    # Filtrar solo las calificaciones de esta boleta
    calif_est = df_calificaciones[df_calificaciones['boleta'] == boleta].copy()
    
    if calif_est.empty:
        return {"estudiante": est_info, "materias": None, "promedio_general": 0.0,
                "creditos_cursados": 0, "materias_aprobadas": 0, "materias_reprobadas": 0}
    
    # Unir calificaciones con el catálogo de materias (JOIN)
    kardex_df = pd.merge(calif_est, df_materias, on='materia_id', how='left')
    
    # Calcular el promedio por materia ignorando los NaNs
    kardex_df['promedio'] = kardex_df[['parcial_1', 'parcial_2', 'final']].mean(axis=1).round(2)
    
    # Cálculos globales
    promedio_general = kardex_df['promedio'].mean()
    aprobadas = int((kardex_df['promedio'] >= 6.0).sum())
    reprobadas = int((kardex_df['promedio'] < 6.0).sum())
    creditos = int(kardex_df['creditos'].sum())
    
    # Seleccionar solo las columnas que importan para mostrar
    cols_mostrar = ['materia_id', 'nombre', 'creditos', 'parcial_1', 'parcial_2', 'final', 'promedio']
    
    return {
        "estudiante": est_info,
        "materias": kardex_df[cols_mostrar],
        "promedio_general": promedio_general,
        "creditos_cursados": creditos,
        "materias_aprobadas": aprobadas,
        "materias_reprobadas": reprobadas
    }

def filtrar_por_rendimiento(df_calificaciones: pd.DataFrame, 
                            df_estudiantes: pd.DataFrame,
                            min_promedio: float = None,
                            max_promedio: float = None) -> pd.DataFrame:
    """
    Filtra estudiantes por rango de promedio.
    """
    df_calif_copia = df_calificaciones.copy()
    df_calif_copia['prom_materia'] = df_calif_copia[['parcial_1', 'parcial_2', 'final']].mean(axis=1)
    
    # Agrupar por estudiante y sacar su promedio general
    promedios = df_calif_copia.groupby('boleta')['prom_materia'].mean().reset_index()
    promedios.rename(columns={'prom_materia': 'promedio_general'}, inplace=True)
    
    # Unir con los datos del estudiante
    df_resultado = pd.merge(df_estudiantes, promedios, on='boleta', how='inner')
    
    # Aplicar los filtros si se especificaron
    if min_promedio is not None:
        df_resultado = df_resultado[df_resultado['promedio_general'] >= min_promedio]
    if max_promedio is not None:
        df_resultado = df_resultado[df_resultado['promedio_general'] <= max_promedio]
        
    return df_resultado.round(2)
