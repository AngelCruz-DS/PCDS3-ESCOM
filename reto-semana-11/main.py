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