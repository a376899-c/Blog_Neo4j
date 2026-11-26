# Prueba del CRUD en consola: python prueba_crud.py
import sys

import blog_db as db
from conexion import cerrar, probar_conexion


# Imprime la tabla de artículos
def print_rows(rows):
    print(f"{'ID':<4} {'TITULO':<36} {'AUTOR':<16} {'ROL':<8} {'COMENT':>6}")
    print("-" * 74)
    for r in rows:
        print(f"{r['article_id']:<4} {r['title'][:35]:<36} {r['autor'][:15]:<16} {r['autor_rol']:<8} {r['comentarios']:>6}")
    print()


if __name__ == "__main__":
    try:
        probar_conexion()
    except Exception as e:
        print("Error de conexión:", e)
        sys.exit(1)
    print("Conectado OK.\n")

    print("== Todos los artículos (orden por fecha DESC) ==")
    print_rows(db.articulo_all("date", "DESC"))

    print("== Consultar artículo 1 ==")
    a = db.articulo_get(1)
    print(f"{a['title']} | por {a['autor']} ({a['autor_rol']}) | tags={a['tags']} | categorias={a['categorias']}\n")

    print("== Insertar artículo (autor: usuario 1) ==")
    nuevo = db.articulo_insert(1, "Artículo de prueba", "Texto de prueba", tags=["spf"], categorias=["Rutinas"])
    print("Creado con ID:", nuevo)
    print_rows(db.articulo_all("id", "ASC"))

    print("== Actualizar artículo", nuevo, "==")
    db.articulo_update(nuevo, "Artículo de prueba (editado)", "Texto editado", tags=["spf", "rutina"], categorias=[])
    print(db.articulo_get(nuevo), "\n")

    print("== Comentar el artículo como usuario 3 ==")
    db.comentario_insert(nuevo, 3, "Comentario de prueba")
    for c in db.comentario_all(nuevo):
        print(f"  [{c['rol'].upper()}] {c['autor']}: {c['text']}  ({c['date']})")
    print("Total comentarios:", db.contar_comentarios(nuevo), "\n")

    print("== Eliminar artículo", nuevo, "(también borra su comentario) ==")
    db.articulo_delete(nuevo)
    print_rows(db.articulo_all("id", "ASC"))

    print("== Eliminar un artículo que NO existe (debe dar error) ==")
    try:
        db.articulo_delete(999)
    except ValueError as e:
        print("Error controlado:", e)

    cerrar()
    print("\nConexión cerrada.")
