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

def calcular_promedio_materia(df_calificaciones: pd.DataFrame, materia_id: str) -> Dict:
    """Calcula estadísticas de una materia específica."""
    df_mat = df_calificaciones[df_calificaciones['materia_id'] == materia_id].copy()
    if df_mat.empty:
        return {}
        
    df_mat['promedio'] = df_mat[['parcial_1', 'parcial_2', 'final']].mean(axis=1)
    total = len(df_mat)
    aprobados = (df_mat['promedio'] >= 6.0).sum()
    
    return {
        "materia": materia_id,
        "inscritos": total,
        "promedio_parcial1": df_mat['parcial_1'].mean(),
        "promedio_parcial2": df_mat['parcial_2'].mean(),
        "promedio_final": df_mat['final'].mean(),
        "promedio_general": df_mat['promedio'].mean(),
        "tasa_aprobacion": (aprobados / total) * 100 if total > 0 else 0.0,
        "calificacion_maxima": df_mat['promedio'].max(),
        "calificacion_minima": df_mat['promedio'].min()
    }

def ranking_estudiantes(df_calificaciones: pd.DataFrame, 
                        df_estudiantes: pd.DataFrame,
                        top_n: int = 10) -> pd.DataFrame:
    """Genera ranking de los mejores estudiantes."""
    df_calif = df_calificaciones.copy()
    df_calif['promedio'] = df_calif[['parcial_1', 'parcial_2', 'final']].mean(axis=1)
    
    promedios = df_calif.groupby('boleta')['promedio'].mean().reset_index()
    ranking = pd.merge(promedios, df_estudiantes[['boleta', 'nombre', 'semestre']], on='boleta')
    ranking = ranking.sort_values(by='promedio', ascending=False).head(top_n)
    
    ranking['promedio'] = ranking['promedio'].round(2)
    ranking.insert(0, 'Posición', range(1, len(ranking) + 1))
    
    return ranking[['Posición', 'nombre', 'semestre', 'promedio']]

def estadisticas_por_semestre(df_estudiantes: pd.DataFrame,
                              df_calificaciones: pd.DataFrame) -> pd.DataFrame:
    """Calcula métricas agrupadas por semestre."""
    df_calif = df_calificaciones.copy()
    df_calif['promedio'] = df_calif[['parcial_1', 'parcial_2', 'final']].mean(axis=1)
    
    prom_est = df_calif.groupby('boleta')['promedio'].mean().reset_index()
    df_completo = pd.merge(df_estudiantes, prom_est, on='boleta')

    stats = df_completo.groupby('semestre').agg(
        Estudiantes=('boleta', 'count'),
        Promedio=('promedio', 'mean')
    )
    
    aprobados = df_completo[df_completo['promedio'] >= 6.0].groupby('semestre')['boleta'].count()
    stats['Tasa Aprob. (%)'] = ((aprobados / stats['Estudiantes']) * 100).fillna(0)
    
    return stats.round(2)


# =====================================================================
# PARTE 4: IDENTIFICACIÓN DE RIESGO Y REPORTES
# =====================================================================

def identificar_estudiantes_riesgo(df_calificaciones: pd.DataFrame,
                                   df_estudiantes: pd.DataFrame,
                                   umbral_promedio: float = 7.0,
                                   max_reprobadas: int = 2) -> pd.DataFrame:
    """Identifica alumnos con riesgo académico."""
    df_calif = df_calificaciones.copy()
    df_calif['promedio'] = df_calif[['parcial_1', 'parcial_2', 'final']].mean(axis=1)
    
    promedios = df_calif.groupby('boleta')['promedio'].mean()
    reprobadas = df_calif[df_calif['promedio'] < 6.0].groupby('boleta').size()
    
    df_riesgo = pd.DataFrame({'Promedio': promedios})
    df_riesgo['Reprobadas'] = reprobadas
    df_riesgo['Reprobadas'] = df_riesgo['Reprobadas'].fillna(0).astype(int)
    
    riesgo_mask = (df_riesgo['Promedio'] < umbral_promedio) | (df_riesgo['Reprobadas'] > max_reprobadas)
    df_riesgo = df_riesgo[riesgo_mask].reset_index()
    
    def determinar_motivo(row):
        if row['Promedio'] < umbral_promedio and row['Reprobadas'] > max_reprobadas:
            return 'Ambos'
        elif row['Promedio'] < umbral_promedio:
            return 'Bajo promedio'
        return 'Mat. reprob.'
            
    df_riesgo['Motivo'] = df_riesgo.apply(determinar_motivo, axis=1)
    resultado = pd.merge(df_riesgo, df_estudiantes[['boleta', 'nombre']], on='boleta')
    
    return resultado[['boleta', 'nombre', 'Promedio', 'Reprobadas', 'Motivo']].round(2)

def generar_reporte_academico(df_estudiantes: pd.DataFrame,
                              df_calificaciones: pd.DataFrame,
                              df_materias: pd.DataFrame) -> Dict:
    """Genera el reporte maestro de Control Escolar."""
    df_calif = df_calificaciones.copy()
    df_calif['promedio'] = df_calif[['parcial_1', 'parcial_2', 'final']].mean(axis=1)
    promedios_est = df_calif.groupby('boleta')['promedio'].mean()
    
    tasa_aprob = (promedios_est >= 6.0).mean() * 100
    
    return {
        "resumen_general": {
            "total_estudiantes": len(df_estudiantes),
            "promedio_global": promedios_est.mean(),
            "tasa_aprobacion": tasa_aprob
        },
        "por_semestre": estadisticas_por_semestre(df_estudiantes, df_calificaciones),
        "mejores_estudiantes": ranking_estudiantes(df_calificaciones, df_estudiantes, 5),
        "estudiantes_riesgo": identificar_estudiantes_riesgo(df_calificaciones, df_estudiantes),
        "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def exportar_kardex(boleta: str, kardex: Dict, formato: str = 'csv') -> str:
    """Guarda las calificaciones en un archivo físico."""
    if kardex['estudiante'] is None or kardex['materias'] is None:
        return ""
    
    fecha = datetime.now().strftime("%Y%m%d")
    nombre_archivo = f"kardex_{boleta}_{fecha}.{formato}"
    df_mat = kardex['materias']
    
    if formato == 'csv':
        df_mat.to_csv(nombre_archivo, index=False)
    elif formato == 'json':
        df_mat.to_json(nombre_archivo, orient='records')
        
    return nombre_archivo


# =====================================================================
# FUNCIONES DE VISUALIZACIÓN
# =====================================================================

def mostrar_kardex(kardex: Dict) -> None:
    if kardex['estudiante'] is None:
        print("❌ Estudiante no encontrado")
        return
    
    est = kardex['estudiante']
    print("=" * 70)
    print("                         KARDEX ACADÉMICO")
    print("=" * 70)
    print(f"\n📋 DATOS DEL ESTUDIANTE")
    print("-" * 40)
    print(f"Boleta: {est.get('boleta', 'N/A')}")
    print(f"Nombre: {est.get('nombre', 'N/A')}")
    print(f"Semestre: {est.get('semestre', 'N/A')}")
    print(f"Carrera: {est.get('carrera', 'N/A')}")
    print(f"Email: {est.get('email', 'N/A')}")
    
    print(f"\n📚 CALIFICACIONES")
    print("-" * 70)
    if kardex['materias'] is not None and not kardex['materias'].empty:
        print(kardex['materias'].to_string(index=False))
    else:
        print("Sin calificaciones registradas")
    
    print(f"\n📊 RESUMEN")
    print("-" * 40)
    print(f"Promedio General: {kardex.get('promedio_general', 0):.2f}")
    print(f"Créditos Cursados: {kardex.get('creditos_cursados', 0)}")
    print(f"Materias Aprobadas: {kardex.get('materias_aprobadas', 0)}")
    print(f"Materias Reprobadas: {kardex.get('materias_reprobadas', 0)}")
    print("=" * 70)

def mostrar_reporte(reporte: Dict) -> None:
    print("=" * 70)
    print("              REPORTE ACADÉMICO - CIENCIA DE DATOS")
    print(f"              Generado: {reporte['fecha_generacion']}")
    print("=" * 70)
    
    res = reporte.get('resumen_general', {})
    print(f"\n📊 RESUMEN GENERAL")
    print("-" * 40)
    print(f"Total de estudiantes: {res.get('total_estudiantes', 'N/A')}")
    print(f"Promedio global: {res.get('promedio_global', 0):.2f}")
    print(f"Tasa de aprobación: {res.get('tasa_aprobacion', 0):.1f}%")
    
    if reporte.get('por_semestre') is not None:
        print(f"\n📅 ESTADÍSTICAS POR SEMESTRE")
        print("-" * 40)
        print(reporte['por_semestre'].to_string())
    
    if reporte.get('mejores_estudiantes') is not None:
        print(f"\n🏆 TOP 5 ESTUDIANTES")
        print("-" * 40)
        print(reporte['mejores_estudiantes'].to_string(index=False))
    
    if reporte.get('estudiantes_riesgo') is not None and not reporte['estudiantes_riesgo'].empty:
        print(f"\n⚠️ ESTUDIANTES EN RIESGO ({len(reporte['estudiantes_riesgo'])})")
        print("-" * 40)
        print(reporte['estudiantes_riesgo'].to_string(index=False))
    else:
        print(f"\n✅ No hay estudiantes en riesgo académico")
    
    print("\n" + "=" * 70)


# =====================================================================
# EJECUCIÓN PRINCIPAL
# =====================================================================

if __name__ == "__main__":
    # Cargar todos los datos
    df_estudiantes, df_calificaciones, df_materias = cargar_datos()
    
    # Imprimir validación inicial
    print("\nVALIDACIÓN DE DATOS")
    print("=" * 50)
    validacion = validar_datos(df_calificaciones)
    print(validacion)
    
    # Probar Kardex de un estudiante específico
    print("\nKARDEX DE ESTUDIANTE")
    print("=" * 50)
    kardex_prueba = obtener_kardex('2021630001', df_estudiantes, df_calificaciones, df_materias)
    mostrar_kardex(kardex_prueba)
    
    # Exportar el Kardex para probar la funcionalidad
    exportar_kardex('2021630001', kardex_prueba, formato='csv')
    
    # Generar y mostrar el reporte maestro
    print("\nREPORTE ACADÉMICO COMPLETO")
    reporte_final = generar_reporte_academico(df_estudiantes, df_calificaciones, df_materias)
    mostrar_reporte(reporte_final)

    