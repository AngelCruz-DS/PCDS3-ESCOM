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