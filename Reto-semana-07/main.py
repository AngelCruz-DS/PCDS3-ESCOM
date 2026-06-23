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

