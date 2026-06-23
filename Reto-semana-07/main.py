import re
from typing import Dict, List, Optional
from collections import Counter, defaultdict

# --- PARTE 1: PATRONES BASE ---

PATRON_HTTP = re.compile(r'''
    ^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+-\s+-\s+  # Extrae la IP
    \[(?P<timestamp>[^\]]+)\]\s+                 # Fecha entre corchetes
    "(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+HTTP/[0-9.]+"\s+  # Metodo y Ruta
    (?P<status>\d{3})\s+(?P<bytes>\d+|-)\s+      # Status y Bytes
    "(?P<referer>[^"]*)"\s+"(?P<user_agent>[^"]*)" # Referer y Navegador
''', re.VERBOSE)

PATRON_ERROR = re.compile(r'''
    ^\[(?P<timestamp>[^\]]+)\]\s+
    (?P<level>[A-Z]+)\s+
    (?P<module>\S+)\s+-\s+
    (?P<error_type>\w+):\s+
    (?P<message>.*)$
''', re.VERBOSE)

PATRON_AUTH = re.compile(r'''
    ^\[AUTH\]\s+(?P<timestamp>[\d-]+\s[\d:]+)\s+\|\s+
    user=(?P<user>[^|]+)\s+\|\s+
    action=(?P<action>[^|]+)\s+\|\s+
    status=(?P<status>[^|]+)\s+\|\s+
    ip=(?P<ip>[^|]+)\s+\|\s+
    (?:session=(?P<session>[^|]+)|attempts=(?P<attempts>\d+))
''', re.VERBOSE)

PATRON_DB = re.compile(r'''
    ^\[DB-(?P<timestamp>[^\]]+)\]\s+
    (?P<query_type>QUERY|SLOW_QUERY)\s+
    (?:executed\sin\s(?P<time_q>[\d.]+)[s]|.*\((?P<time_sq>[\d.]+)[s]\)):\s+
    (?P<query>.*)$
''', re.VERBOSE)

# --- PARTE 1.2: FUNCIONES DE PARSEO ---

def parse_http_log(linea: str) -> Optional[Dict]:
    match = PATRON_HTTP.match(linea)
    if match:
        d = match.groupdict()
        d['status'] = int(d['status'])
        d['bytes'] = 0 if d['bytes'] == '-' else int(d['bytes'])
        return d
    return None

def parse_error_log(linea: str) -> Optional[Dict]:
    match = PATRON_ERROR.match(linea)
    return match.groupdict() if match else None

def parse_auth_log(linea: str) -> Optional[Dict]:
    match = PATRON_AUTH.match(linea)
    if match:
        d = match.groupdict()
        d['user'] = d['user'].strip()
        d['action'] = d['action'].strip()
        d['status'] = d['status'].strip()
        d['ip'] = d['ip'].strip()
        d['extra'] = {'session': d['session']} if d['session'] else {'attempts': int(d['attempts'])}
        return d
    return None

def parse_db_log(linea: str) -> Optional[Dict]:
    match = PATRON_DB.match(linea)
    if match:
        d = match.groupdict()
        # Aqui vemos cual de los dos tiempos de ejecucion capturó
        tiempo = d['time_q'] if d['time_q'] else d['time_sq']
        return {
            "timestamp": d['timestamp'],
            "query_type": d['query_type'],
            "execution_time": float(tiempo),
            "query": d['query']
        }
    return None
# --- PARTE 2: ANALIZADOR DE SEGURIDAD (Fase 1) ---

def detectar_ataques_fuerza_bruta(logs_auth: List[Dict]) -> List[Dict]:
    """Detecta si una IP falló el login más de 3 veces."""
    intentos_fallidos = defaultdict(int)
    for log in logs_auth:
        if log['status'] == 'FAILED':
            # ¡Nuestro viejo amigo += haciendo su trabajo de acumular!
            intentos_fallidos[log['ip']] += log['extra'].get('attempts', 1)
    
    return [{"ip": ip, "intentos": count} for ip, count in intentos_fallidos.items() if count > 3]

def detectar_errores_criticos(logs_error: List[Dict]) -> List[Dict]:
    """Filtra los errores que son nivel ERROR o CRITICAL."""
    return [log for log in logs_error if log['level'] in ['ERROR', 'CRITICAL']]
# --- PARTE 2: ANALIZADOR DE SEGURIDAD (Fase 2) ---

PATRONES_SQL_INJECTION = [
    r"(?i)\bOR\b\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+",  # Busca el clásico OR 1=1
    r"(?i)\bUNION\b.*\bSELECT\b",                       # UNION SELECT
    r"--",                                              # Comentario SQL
    r"(?i)\bDROP\b\s+\bTABLE\b",                        # DROP TABLE
    r"(?i)\bDELETE\b\s+\bFROM\b.*\bWHERE\b\s+1\s*=\s*1",# DELETE WHERE 1=1
]

def detectar_sql_injection(logs_db: List[Dict]) -> List[Dict]:
    """Busca trampas de inyección SQL en las consultas."""
    sospechosos = []
    for log in logs_db:
        for patron in PATRONES_SQL_INJECTION:
            if re.search(patron, log['query']):
                sospechosos.append(log)
                break
    return sospechosos

def detectar_path_traversal(logs_http: List[Dict]) -> List[Dict]:
    """Busca intentos de navegar hacia atrás en las carpetas del servidor."""
    sospechosos = []
    patron = r'\.\./|\.\.\\|%2e%2e%2f'
    for log in logs_http:
        if re.search(patron, log['path'], re.IGNORECASE):
            sospechosos.append(log)
    return sospechosos
# --- PARTE 3: CLASIFICADOR Y GENERADOR DE REPORTES ---

def clasificar_linea(linea: str) -> str:
    """Decide qué tipo de log es leyendo el inicio de la línea."""
    if linea.startswith("[AUTH]"): return 'auth'
    if linea.startswith("[DB-"): return 'db'
    if re.match(r'^\d{1,3}\.', linea): return 'http'
    if re.match(r'^\[\d{4}-', linea): return 'error'
    return 'desconocido'

def generar_reporte(logs: str) -> Dict:
    """Toma todo el texto, lo procesa y genera el diccionario final."""
    lineas = [l for l in logs.split('\n') if l.strip()]
    
    parsed_http = []
    parsed_error = []
    parsed_auth = []
    parsed_db = []
    
    # 1. Separar y parsear cada línea
    for linea in lineas:
        tipo = clasificar_linea(linea)
        if tipo == 'http':
            p = parse_http_log(linea)
            if p: parsed_http.append(p)
        elif tipo == 'error':
            p = parse_error_log(linea)
            if p: parsed_error.append(p)
        elif tipo == 'auth':
            p = parse_auth_log(linea)
            if p: parsed_auth.append(p)
        elif tipo == 'db':
            p = parse_db_log(linea)
            if p: parsed_db.append(p)

    # 2. Calcular estadísticas de HTTP
    status_counts = Counter([log['status'] for log in parsed_http])
    status_format = {
        "2xx": sum(v for k, v in status_counts.items() if 200 <= k < 300),
        "3xx": sum(v for k, v in status_counts.items() if 300 <= k < 400),
        "4xx": sum(v for k, v in status_counts.items() if 400 <= k < 500),
        "5xx": sum(v for k, v in status_counts.items() if 500 <= k < 600)
    }
    rutas_counts = Counter([log['path'] for log in parsed_http])
    
    # 3. Calcular rendimiento DB
    tiempo_promedio = sum(log['execution_time'] for log in parsed_db) / len(parsed_db) if parsed_db else 0

    # 4. Ensamblar el diccionario final
    return {
        "resumen": {
            "total_lineas": len(lineas),
            "por_tipo": {"http": len(parsed_http), "error": len(parsed_error), "auth": len(parsed_auth), "db": len(parsed_db)}
        },
        "http": {
            "total_requests": len(parsed_http),
            "por_status": status_format,
            "top_rutas": rutas_counts.most_common()
        },
        "errores": {
            "total": len(parsed_error),
            "por_nivel": dict(Counter([log['level'] for log in parsed_error]))
        },
        "seguridad": {
            "alertas_fuerza_bruta": detectar_ataques_fuerza_bruta(parsed_auth),
            "alertas_sql_injection": detectar_sql_injection(parsed_db),
            "alertas_path_traversal": detectar_path_traversal(parsed_http)
        },
        "rendimiento": {
            "queries_lentos": [log for log in parsed_db if log['query_type'] == 'SLOW_QUERY'],
            "tiempo_promedio_queries": tiempo_promedio
        }
    }

def mostrar_reporte(reporte: Dict) -> None:
    """Imprime el reporte en la terminal de forma bonita y legible."""
    print("=" * 70)
    print("                    REPORTE DE ANÁLISIS DE LOGS")
    print("=" * 70)
    
    print("\n📊 RESUMEN GENERAL")
    print("-" * 40)
    print(f"Total de líneas procesadas: {reporte['resumen']['total_lineas']}")
    print("Por tipo:")
    for tipo, count in reporte['resumen']['por_tipo'].items():
        print(f"  • {tipo.upper()}: {count}")
    
    if 'http' in reporte:
        print("\n🌐 LOGS HTTP")
        print("-" * 40)
        print(f"Total requests: {reporte['http']['total_requests']}")
        print("Por código de estado:")
        for status, count in reporte['http']['por_status'].items():
            if count > 0: print(f"  • {status}: {count}")
        print("Top 5 rutas más solicitadas:")
        for ruta, count in reporte['http'].get('top_rutas', [])[:5]:
            print(f"  • {ruta}: {count} requests")
    
    if 'errores' in reporte:
        print("\n❌ ERRORES")
        print("-" * 40)
        print(f"Total errores: {reporte['errores']['total']}")
        print("Por nivel:")
        for nivel, count in reporte['errores']['por_nivel'].items():
            print(f"  • {nivel}: {count}")
    
    if 'seguridad' in reporte:
        print("\n🔒 ALERTAS DE SEGURIDAD")
        print("-" * 40)
        fb = reporte['seguridad'].get('alertas_fuerza_bruta', [])
        if fb:
            print(f"⚠️  Posibles ataques de fuerza bruta: {len(fb)}")
            for alerta in fb:
                print(f"     IP: {alerta['ip']} - {alerta['intentos']} intentos fallidos")
        
        sql = reporte['seguridad'].get('alertas_sql_injection', [])
        if sql:
            print(f"⚠️  Posibles SQL Injection: {len(sql)}")
            for alerta in sql[:3]:
                print(f"     Query: {alerta['query'][:60]}...")
        
        pt = reporte['seguridad'].get('alertas_path_traversal', [])
        if pt:
            print(f"⚠️  Posibles Path Traversal: {len(pt)}")
            for alerta in pt[:3]:
                print(f"     Ruta: {alerta['path']}")
    
    if 'rendimiento' in reporte:
        print("\n⏱️  RENDIMIENTO")
        print("-" * 40)
        print(f"Queries lentos detectados: {len(reporte['rendimiento'].get('queries_lentos', []))}")
        if 'tiempo_promedio_queries' in reporte['rendimiento']:
            print(f"Tiempo promedio de queries: {reporte['rendimiento']['tiempo_promedio_queries']:.3f}s")
    
    print("\n" + "=" * 70)
if __name__ == "__main__":
    LOGS_PRUEBA = """
192.168.1.100 - - [15/Mar/2024:10:23:45 -0600] "GET /api/users HTTP/1.1" 200 1234 "https://ejemplo.com" "Mozilla/5.0 (Windows NT 10.0)"
192.168.1.101 - - [15/Mar/2024:10:23:46 -0600] "POST /api/login HTTP/1.1" 200 89 "-" "curl/7.68.0"
192.168.1.102 - - [15/Mar/2024:10:23:47 -0600] "GET /admin/../../../etc/passwd HTTP/1.1" 403 0 "-" "sqlmap/1.0"
[2024-03-15 10:24:00] INFO app.startup - Application started successfully on port 8080
[2024-03-15 10:25:12] ERROR app.database - DatabaseConnectionError: Connection refused to host db.server.com:5432
[2024-03-15 10:25:15] WARNING app.cache - CacheWarning: Redis connection timeout, using fallback
[2024-03-15 10:26:00] ERROR app.auth - AuthenticationError: Invalid token for user admin@empresa.com
[AUTH] 2024-03-15 10:30:00 | user=admin@empresa.com | action=LOGIN | status=SUCCESS | ip=10.0.0.5 | session=abc123xyz
[AUTH] 2024-03-15 10:31:00 | user=hacker@mail.com | action=LOGIN | status=FAILED | ip=192.168.1.50 | attempts=1
[AUTH] 2024-03-15 10:31:30 | user=hacker@mail.com | action=LOGIN | status=FAILED | ip=192.168.1.50 | attempts=2
[AUTH] 2024-03-15 10:32:00 | user=hacker@mail.com | action=LOGIN | status=FAILED | ip=192.168.1.50 | attempts=3
[AUTH] 2024-03-15 10:32:30 | user=hacker@mail.com | action=LOGIN | status=FAILED | ip=192.168.1.50 | attempts=4
[AUTH] 2024-03-15 10:33:00 | user=otro@empresa.com | action=LOGOUT | status=SUCCESS | ip=10.0.0.10 | session=def456uvw
[DB-2024-03-15 10:35:22] QUERY executed in 0.045s: SELECT * FROM users WHERE email = 'admin@empresa.com'
[DB-2024-03-15 10:35:25] QUERY executed in 0.012s: SELECT id, name FROM products WHERE active = 1
[DB-2024-03-15 10:36:00] SLOW_QUERY (2.5s): SELECT * FROM orders o JOIN products p ON o.product_id = p.id JOIN users u ON o.user_id = u.id
[DB-2024-03-15 10:37:00] QUERY executed in 0.001s: SELECT * FROM users WHERE username = 'admin' OR 1=1--'
[DB-2024-03-15 10:38:00] QUERY executed in 0.002s: SELECT * FROM users UNION SELECT * FROM passwords
192.168.1.200 - - [15/Mar/2024:10:40:00 -0600] "GET /products?id=1 HTTP/1.1" 200 5678 "https://tienda.com" "Mozilla/5.0"
192.168.1.200 - - [15/Mar/2024:10:40:05 -0600] "GET /products?id=2 HTTP/1.1" 200 4321 "https://tienda.com" "Mozilla/5.0"
192.168.1.201 - - [15/Mar/2024:10:41:00 -0600] "GET /api/users HTTP/1.1" 401 123 "-" "PostmanRuntime/7.26.8"
192.168.1.201 - - [15/Mar/2024:10:41:05 -0600] "GET /api/users HTTP/1.1" 500 0 "-" "PostmanRuntime/7.26.8"
[2024-03-15 10:42:00] ERROR app.api - NullPointerException: Cannot read property 'id' of undefined
[DB-2024-03-15 10:45:00] SLOW_QUERY (5.2s): SELECT COUNT(*) FROM logs WHERE date > '2024-01-01'
    """.strip()
    
    reporte = generar_reporte(LOGS_PRUEBA)
    mostrar_reporte(reporte)