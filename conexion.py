# Conexión de Python con Neo4j
from neo4j import GraphDatabase

# Datos de conexión (config.py)
try:
    import config
except ImportError:
    raise SystemExit("Falta config.py: copia config_ejemplo.py como config.py y escribe tu contrasena de Neo4j.")

_driver = None


# Aquí se conecta a la base
def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(config.URI, auth=(config.USUARIO, config.PASSWORD))
    return _driver


# Revisa que Neo4j esté encendido
def probar_conexion():
    try:
        get_driver().verify_connectivity()
    except Exception:
        cerrar()
        raise


# Consulta de lectura (MATCH ... RETURN)
def consultar(query, **parametros):
    resultado = get_driver().execute_query(query, parametros, database_=config.DATABASE)
    filas = []
    for registro in resultado.records:
        filas.append(registro.data())
    return filas


# Consulta que modifica datos (CREATE, SET, DELETE)
def ejecutar(query, **parametros):
    resultado = get_driver().execute_query(query, parametros, database_=config.DATABASE)
    return resultado.summary.counters


# Cierra la conexión
def cerrar():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


# Prueba rápida: python conexion.py
if __name__ == "__main__":
    try:
        probar_conexion()
        print("Conectado OK a", config.URI, "| base de datos:", config.DATABASE)
        for fila in consultar("MATCH (n) RETURN labels(n)[0] AS etiqueta, count(n) AS total ORDER BY etiqueta"):
            print(f"  {fila['etiqueta']:<12} {fila['total']}")
    except Exception as e:
        print("Error de conexion:", e)
    finally:
        cerrar()
