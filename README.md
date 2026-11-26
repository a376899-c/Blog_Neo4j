# Blog en Neo4j — Proyecto Final

**Bases de Datos Avanzadas · 7CC2 · Facultad de Ingeniería, UACH**

Integrantes:
- Ana Ruvi Morales Chavez — 376899
- Mauricio Adrian Ochoa Carrillo — 377194

Docente: Jose Saul Delira Miramontes

Aplicación de escritorio en **Python (Tkinter)** que administra un **blog** guardado en una base de datos de grafos **Neo4j**.
Es el mismo blog del Proyecto de la 1a. Evaluación (Oracle + PL/SQL), ahora modelado con **nodos y relaciones**.

---

## Funcionalidades

| | Administrador ★ | Usuario ● |
|---|:---:|:---:|
| Iniciar sesión / registrarse | ✅ | ✅ |
| Leer artículos, filtrar por tag/categoría y ordenar | ✅ | ✅ |
| Comentar artículos | ✅ | ✅ |
| Ver estadísticas (gráficos) | ✅ | ✅ |
| Crear, editar y eliminar artículos (con tags y categorías) | ✅ | ❌ |
| Eliminar comentarios | ✅ | ❌ |
| Crear usuarios, cambiar su rol, eliminarlos | ✅ | ❌ |
| Crear y eliminar tags y categorías | ✅ | ❌ |

- Arriba siempre se ve **quién inició sesión** y su **rol** (etiqueta naranja = administrador, azul = usuario).
- Cada comentario muestra **quién lo escribió** y si es **administrador o usuario**.
- La pantalla de inicio lista los usuarios del sistema con su rol y su último acceso.
- Estadísticas con gráficos de barras (matplotlib): comentarios por artículo, comentarios por usuario (color = rol), artículos por categoría y por tag.
- Las contraseñas se guardan cifradas con SHA-256.

## Modelo de grafo

```
(:Usuario)-[:ESCRIBIO]->(:Articulo)              Usuario 1-a-N Articulo
(:Usuario)-[:COMENTO]->(:Comentario)             Usuario 1-a-N Comentario
(:Comentario)-[:PERTENECE_A]->(:Articulo)        Articulo 1-a-N Comentario
(:Articulo)-[:TIENE_TAG]->(:Tag)                 Articulo N-a-N Tag
(:Articulo)-[:EN_CATEGORIA]->(:Categoria)        Articulo N-a-N Categoria
```

| Nodo | Propiedades |
|---|---|
| `Usuario` | user_id, name, email, password (SHA-256), rol (`admin`/`usuario`), fecha_registro, ultimo_acceso |
| `Articulo` | article_id, title, date, text |
| `Comentario` | comment_id, text, url, date |
| `Tag` | tag_id, name, url |
| `Categoria` | category_id, name, url |

### De Oracle (relacional) a Neo4j (grafo)

| Oracle (1a. evaluación) | Neo4j (este proyecto) |
|---|---|
| Tabla `users`, `articles`, ... | Etiqueta (label) `:Usuario`, `:Articulo`, ... |
| Fila | Nodo |
| Columna | Propiedad |
| `PRIMARY KEY` | Constraint `IS UNIQUE` + `IS NOT NULL` |
| `UNIQUE INDEX (LOWER(email))` | Constraint `IS UNIQUE` en `email` (se guarda en minúsculas) |
| `FOREIGN KEY articles.user_id` | Relación `(:Usuario)-[:ESCRIBIO]->(:Articulo)` |
| Tablas puente `article_tags`, `article_categories` | Relaciones `TIENE_TAG`, `EN_CATEGORIA` |
| `comments.name` (texto libre) | Relación `(:Usuario)-[:COMENTO]->` (se sabe quién y con qué rol) |
| `NVL(MAX(id),0)+1` | `coalesce(max(x.id),0)+1` |
| `DELETE` en 4 tablas para borrar un artículo | `DETACH DELETE` |
| `raise_application_error` | `ValueError("mensaje")` en Python |
| `SQL%ROWCOUNT` | Contadores del resultado (`nodes_deleted`, `properties_set`) |
| Variables bind `:id` | Parámetros `$id` |
| `COMMIT` / `ROLLBACK` | Transacción del driver (`session.execute_write`) |

## Estructura

```
Blog_Neo4j/
├── app.py                  # aplicación con ventanas (Tkinter)
├── blog_db.py              # CRUD del blog en Cypher (usuarios, artículos, comentarios, tags, categorías, estadísticas)
├── conexion.py             # conexión a Neo4j con el driver oficial
├── config_ejemplo.py       # plantilla de config.py (URI, usuario, contraseña, base)
├── cargar_datos.py         # crea la base "blog" y carga esquema + datos
├── prueba_crud.py          # prueba del CRUD en consola
├── abrir_app.bat           # abre la app con doble clic
├── requirements.txt
├── cypher/
│   ├── 01_esquema.cypher   # constraints UNIQUE / NOT NULL
│   ├── 02_datos.cypher     # datos iniciales (nodos y relaciones)
│   └── 03_consultas.cypher # consultas que usa la app, para Neo4j Browser
├── docs/
│   └── Reporte_Proyecto_Blog_Neo4j.pdf  # reporte: código documentado y capturas de la ejecución
└── capturas/               # capturas de pantalla de la aplicación funcionando
```

## Documentación

El reporte del proyecto (modelo de la base, archivos Cypher, código documentado y capturas de la ejecución)
está en [`docs/Reporte_Proyecto_Blog_Neo4j.pdf`](docs/Reporte_Proyecto_Blog_Neo4j.pdf).

## Instalación y uso

1. Instalar **Python 3.10+** y **Neo4j Desktop**.
2. Instalar las librerías:
   ```
   pip install -r requirements.txt
   ```
3. En Neo4j Desktop crear una instancia (versión 2025/2026), ponerle contraseña y darle **Start**.
4. Copiar `config_ejemplo.py` como **`config.py`** y escribir la contraseña de la instancia.
5. Crear la base `blog` y cargar los datos (solo la primera vez, o para reiniciar los datos):
   ```
   python cargar_datos.py
   ```
6. Abrir la aplicación:
   ```
   python app.py
   ```
   (o doble clic en `abrir_app.bat`)

> Si usan Neo4j **Community** (que no permite crear bases nuevas), pongan `DATABASE = "neo4j"` en `config.py`.

### Cuentas de prueba

| Correo | Contraseña | Rol |
|---|---|---|
| admin@blog.com | admin123 | Administrador |
| a376899@uach.mx | admin123 | Administrador |
| a377194@uach.mx | admin123 | Administrador |
| usuario@blog.com | user123 | Usuario |
| gael@blog.com | user123 | Usuario |
| jacqueline@blog.com | user123 | Usuario |

También se puede crear una cuenta nueva desde la pantalla de inicio de sesión (se crea como **Usuario**; un administrador la puede convertir en administrador).

### Ver el grafo en Neo4j Browser

En Neo4j Desktop → *Connect* → *Query*, elegir la base `blog` y ejecutar:

```cypher
MATCH (n) RETURN n;
```
