import numpy as np

np.random.seed(42)

estaciones = ['Coyoacán', 'Azcapotzalco', 'Xochimilco', 'Tlalpan', 'Miguel Hidalgo']
n_estaciones = len(estaciones)
n_dias = 7
n_horas = 24

# 1. Temperatura
temp_base = np.array([22, 24, 20, 19, 23])
hora_del_dia = np.arange(24)
variacion_diaria = 5 * np.sin((hora_del_dia - 6) * np.pi / 12)

temperatura = np.zeros((n_estaciones, n_dias, n_horas))
for i in range(n_estaciones):
    for d in range(n_dias):
        temperatura[i, d, :] = temp_base[i] + variacion_diaria + np.random.normal(0, 1.5, n_horas)

temperatura[1, 2, 10:14] = np.nan
temperatura[3, 5, 0:3] = np.nan

# 2. Humedad
humedad_base = np.array([55, 45, 70, 65, 50])
variacion_humedad = -15 * np.sin((hora_del_dia - 6) * np.pi / 12)

humedad = np.zeros((n_estaciones, n_dias, n_horas))
for i in range(n_estaciones):
    for d in range(n_dias):
        humedad[i, d, :] = humedad_base[i] + variacion_humedad + np.random.normal(0, 5, n_horas)

humedad = np.clip(humedad, 20, 95)
humedad[0, 4, 15:18] = np.nan

# 3. CO2
co2_base = np.array([380, 420, 360, 350, 410])
patron_trafico = np.zeros(24)
patron_trafico[7:10] = 30
patron_trafico[17:20] = 40
patron_trafico[12:14] = 15

co2 = np.zeros((n_estaciones, n_dias, n_horas))
for i in range(n_estaciones):
    for d in range(n_dias):
        co2[i, d, :] = co2_base[i] + patron_trafico + np.random.normal(0, 10, n_horas)

co2[:, 3, :] *= 1.15  # Día de contingencia
co2[2, 1, 5:8] = np.nan

temp_promedio_diario = np.nanmean(temperatura, axis=2)

n_dimensiones = temperatura.ndim
forma = temperatura.shape
total_elementos = temperatura.size
tipo_datos = temperatura.dtype
memoria_bytes = temperatura.nbytes

print("📊 PROPIEDADES DEL ARRAY TEMPERATURA")
print("─" * 40)
print(f"Dimensiones: {n_dimensiones}D")
print(f"Forma: {forma}")
print(f"  → {forma[0]} estaciones")
print(f"  → {forma[1]} días")
print(f"  → {forma[2]} horas por día")
print(f"Total de mediciones: {total_elementos:,}")
print(f"Tipo de datos: {tipo_datos}")
print(f"Memoria: {memoria_bytes:,} bytes ({memoria_bytes/1024:.2f} KB)")

# 1.2 Indexación
temp_coyoacan_d1_12h = temperatura[0, 0, 12]
temp_xochimilco_d3 = temperatura[2, 2, :]
temp_mh_7dias = temp_promedio_diario[4, :]
ultimo_co2 = co2[-1, -1, -1]

# 1.3 Slicing
temp_tardes = temperatura[:, :, 12:18]
humedad_subset = humedad[:3, -3:, :]
co2_mañanas_pares = co2[::2, :, 6:12]
temp_inverso = temperatura[:, ::-1, :]


# =====================================================================
# PARTE 2: ESTADÍSTICAS BÁSICAS
# =====================================================================

# 2.1 Estadísticas Globales (usando nan* para ignorar faltantes)
temp_promedio = np.nanmean(temperatura)
temp_maxima = np.nanmax(temperatura)
temp_minima = np.nanmin(temperatura)
temp_std = np.nanstd(temperatura)
temp_rango = temp_maxima - temp_minima

print("\n╔══════════════════════════════════════════════════════════════╗")
print("║            ESTADÍSTICAS GLOBALES DE TEMPERATURA              ║")
print("╠══════════════════════════════════════════════════════════════╣")
print(f"║  Promedio:      {temp_promedio:>6.2f} °C                               ║")
print(f"║  Máxima:        {temp_maxima:>6.2f} °C                               ║")
print(f"║  Mínima:        {temp_minima:>6.2f} °C                               ║")
print(f"║  Desv. Est.:    {temp_std:>6.2f} °C                               ║")
print(f"║  Rango:         {temp_rango:>6.2f} °C                               ║")
print("╚══════════════════════════════════════════════════════════════╝")

# 2.2 Estadísticas por Eje
# Promedio por estación (colapsamos días y horas: axis=(1,2))
temp_por_estacion = np.nanmean(temperatura, axis=(1,2))
# Humedad promedio por hora (colapsamos estaciones y días: axis=(0,1))
humedad_por_hora = np.nanmean(humedad, axis=(0,1))
# CO2 máximo por día (colapsamos estaciones y horas: axis=(0,2))
co2_max_por_dia = np.nanmax(co2, axis=(0,2))