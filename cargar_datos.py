# Crea la base 'blog' y carga el esquema y los datos
import sys
from pathlib import Path

import config
from conexion import cerrar, consultar, get_driver, probar_conexion

CARPETA = Path(__file__).parent / "cypher"


# Separa un archivo .cypher en sentencias
def leer_sentencias(archivo):
    lineas = [l for l in archivo.read_text(encoding="utf-8").splitlines() if not l.strip().startswith("//")]
    return [s.strip() for s in "\n".join(lineas).split(";") if s.strip()]


# Crea la base de datos blog
def crear_base():
    try:
        get_driver().execute_query(f"CREATE DATABASE {config.DATABASE} IF NOT EXISTS WAIT", database_="system")
        print(f"Base de datos '{config.DATABASE}' lista.")
    except Exception as e:
        print(f"No se pudo crear la base '{config.DATABASE}' ({e.__class__.__name__}).")
        print("Si usas Neo4j Community, cambia DATABASE = \"neo4j\" en config.py y vuelve a ejecutar.")
        raise SystemExit(1) from e


# Ejecuta un archivo .cypher
def ejecutar_archivo(nombre):
    archivo = CARPETA / nombre
    sentencias = leer_sentencias(archivo)
    errores = 0
    for s in sentencias:
        try:
            get_driver().execute_query(s, database_=config.DATABASE)
        except Exception as e:
            errores += 1
            print(f"  ERROR en: {s.splitlines()[0][:70]}...\n         {e}")
    print(f"{nombre}: {len(sentencias) - errores} de {len(sentencias)} sentencias OK")
    return errores


# Carga todo: python cargar_datos.py
if __name__ == "__main__":
    try:
        probar_conexion()
    except Exception as e:
        print("No me pude conectar a Neo4j:", e)
        print("Revisa que la base este encendida (Start) en Neo4j Desktop y la contrasena en config.py.")
        sys.exit(1)
    try:
        crear_base()
        total_errores = ejecutar_archivo("01_esquema.cypher") + ejecutar_archivo("02_datos.cypher")
        print("\nNodos en la base:")
        for f in consultar("MATCH (n) RETURN labels(n)[0] AS etiqueta, count(n) AS total ORDER BY etiqueta"):
            print(f"  {f['etiqueta']:<12} {f['total']}")
        print("Relaciones:")
        for f in consultar("MATCH ()-[r]->() RETURN type(r) AS tipo, count(r) AS total ORDER BY tipo"):
            print(f"  {f['tipo']:<13} {f['total']}")
        print("\nListo." if total_errores == 0 else f"\nTerminado con {total_errores} error(es).")
    finally:
        cerrar()
