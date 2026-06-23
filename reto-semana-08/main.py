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

