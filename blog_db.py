# Operaciones del blog (CRUD) en Neo4j
import hashlib
from datetime import datetime

from conexion import consultar, ejecutar

ROLES = ["admin", "usuario"]


# Cifra la contraseña con SHA-256
def cifrar(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# Fecha de Neo4j a texto
def fecha_texto(valor):
    if valor is None:
        return ""
    return valor.to_native().strftime("%d/%m/%Y %H:%M")


# Fecha y hora actual
def ahora():
    return datetime.now().replace(microsecond=0)


# Quita espacios de un texto
def limpio(texto):
    if texto is None:
        return ""
    return texto.strip()


# Siguiente id: el mayor + 1 (como NVL(MAX(id), 0) + 1 en Oracle)
def siguiente_id(query):
    mayor = consultar(query)[0]["mayor"]
    if mayor is None:
        return 1
    return mayor + 1


# ---------- USUARIOS ----------
# ¿Ya existe el correo?
def existe_email(email):
    filas = consultar("MATCH (u:Usuario) WHERE toLower(u.email) = toLower($email) RETURN count(u) AS total",
                      email=limpio(email))
    return filas[0]["total"]


# Crea un usuario
def usuario_insert(name, email, password, rol="usuario"):
    name = limpio(name)
    email = limpio(email).lower()
    if name == "" or email == "" or password == "":
        raise ValueError("Nombre, correo y contraseña son obligatorios.")
    if "@" not in email or "." not in email:
        raise ValueError("El correo no es válido.")
    if len(password) < 4:
        raise ValueError("La contraseña debe tener al menos 4 caracteres.")
    if rol not in ROLES:
        raise ValueError("Rol inválido: debe ser 'admin' o 'usuario'.")
    if existe_email(email) > 0:
        raise ValueError(f"El correo {email} ya está registrado.")
    nuevo = siguiente_id("MATCH (u:Usuario) RETURN max(u.user_id) AS mayor")
    ejecutar("""
        CREATE (u:Usuario {user_id: $id, name: $name, email: $email, password: $password,
                           rol: $rol, fecha_registro: $fecha})""",
             id=nuevo, name=name, email=email, password=cifrar(password), rol=rol, fecha=ahora())
    return nuevo


# Inicia sesión
def usuario_login(email, password):
    filas = consultar("""
        MATCH (u:Usuario {email: $email, password: $password})
        SET u.ultimo_acceso = $fecha
        RETURN u.user_id AS user_id, u.name AS name, u.email AS email, u.rol AS rol""",
        email=limpio(email).lower(), password=cifrar(password), fecha=ahora())
    if len(filas) == 0:
        return None
    return filas[0]


# Lista de usuarios con su actividad
def usuario_all():
    filas = consultar("""
        MATCH (u:Usuario)
        OPTIONAL MATCH (u)-[:ESCRIBIO]->(a:Articulo)
        WITH u, count(a) AS articulos
        OPTIONAL MATCH (u)-[:COMENTO]->(c:Comentario)
        RETURN u.user_id AS user_id, u.name AS name, u.email AS email, u.rol AS rol,
               articulos, count(c) AS comentarios,
               u.ultimo_acceso AS ultimo_acceso, u.fecha_registro AS fecha_registro
        ORDER BY user_id""")
    for f in filas:
        if f["ultimo_acceso"] is None:
            f["ultimo_acceso"] = "Nunca"
        else:
            f["ultimo_acceso"] = fecha_texto(f["ultimo_acceso"])
        f["fecha_registro"] = fecha_texto(f["fecha_registro"])
    return filas


# Cambia el rol (admin / usuario)
def usuario_cambiar_rol(user_id, rol):
    if rol not in ROLES:
        raise ValueError("Rol inválido.")
    contadores = ejecutar("MATCH (u:Usuario {user_id: $id}) SET u.rol = $rol", id=user_id, rol=rol)
    if contadores.properties_set == 0:
        raise ValueError(f"El usuario {user_id} no existe.")


# Borra un usuario (solo si no tiene artículos)
def usuario_delete(user_id):
    filas = consultar("""
        MATCH (u:Usuario {user_id: $id})-[:ESCRIBIO]->(a:Articulo)
        RETURN count(a) AS articulos""", id=user_id)
    articulos = filas[0]["articulos"]
    if articulos > 0:
        raise ValueError(f"No se puede eliminar: el usuario tiene {articulos} artículo(s).\n"
                         "Primero elimina sus artículos (es como la llave foránea de Oracle).")
    contadores = ejecutar("""
        MATCH (u:Usuario {user_id: $id})
        OPTIONAL MATCH (u)-[:COMENTO]->(c:Comentario)
        DETACH DELETE c, u""", id=user_id)
    if contadores.nodes_deleted == 0:
        raise ValueError(f"El usuario {user_id} no existe.")


# ---------- ARTÍCULOS ----------
# Reemplaza los tags de un artículo
def asignar_tags(article_id, tags):
    ejecutar("MATCH (a:Articulo {article_id: $id})-[r:TIENE_TAG]->() DELETE r", id=article_id)
    for nombre in tags:
        ejecutar("""
            MATCH (a:Articulo {article_id: $id}), (t:Tag {name: $nombre})
            MERGE (a)-[:TIENE_TAG]->(t)""", id=article_id, nombre=nombre)


# Reemplaza las categorías de un artículo
def asignar_categorias(article_id, categorias):
    ejecutar("MATCH (a:Articulo {article_id: $id})-[r:EN_CATEGORIA]->() DELETE r", id=article_id)
    for nombre in categorias:
        ejecutar("""
            MATCH (a:Articulo {article_id: $id}), (c:Categoria {name: $nombre})
            MERGE (a)-[:EN_CATEGORIA]->(c)""", id=article_id, nombre=nombre)


# Crea un artículo con sus tags y categorías
def articulo_insert(user_id, title, text, tags=[], categorias=[]):
    title = limpio(title)
    text = limpio(text)
    if title == "":
        raise ValueError("El título es obligatorio.")
    nuevo = siguiente_id("MATCH (a:Articulo) RETURN max(a.article_id) AS mayor")
    filas = consultar("""
        MATCH (u:Usuario {user_id: $user_id})
        CREATE (u)-[:ESCRIBIO]->(a:Articulo {article_id: $id, title: $title, text: $text, date: $fecha})
        RETURN a.article_id AS article_id""",
        user_id=user_id, id=nuevo, title=title, text=text, fecha=ahora())
    if len(filas) == 0:
        raise ValueError(f"El usuario {user_id} no existe; no se creó el artículo.")
    asignar_tags(nuevo, tags)
    asignar_categorias(nuevo, categorias)
    return nuevo


# Actualiza un artículo
def articulo_update(article_id, title, text, tags=[], categorias=[]):
    title = limpio(title)
    text = limpio(text)
    if title == "":
        raise ValueError("El título es obligatorio.")
    filas = consultar("""
        MATCH (a:Articulo {article_id: $id})
        SET a.title = $title, a.text = $text
        RETURN a.article_id AS article_id""", id=article_id, title=title, text=text)
    if len(filas) == 0:
        raise ValueError(f"El artículo {article_id} no existe.")
    asignar_tags(article_id, tags)
    asignar_categorias(article_id, categorias)


# Borra un artículo con sus comentarios
def articulo_delete(article_id):
    contadores = ejecutar("""
        MATCH (a:Articulo {article_id: $id})
        OPTIONAL MATCH (c:Comentario)-[:PERTENECE_A]->(a)
        DETACH DELETE c, a""", id=article_id)
    if contadores.nodes_deleted == 0:
        raise ValueError(f"El artículo {article_id} no existe.")


# Un artículo completo (datos, autor, tags, categorías y número de comentarios)
def articulo_get(article_id):
    filas = consultar("""
        MATCH (u:Usuario)-[:ESCRIBIO]->(a:Articulo {article_id: $id})
        RETURN a.article_id AS article_id, a.title AS title, a.text AS text, a.date AS date,
               u.user_id AS autor_id, u.name AS autor, u.rol AS autor_rol""", id=article_id)
    if len(filas) == 0:
        raise ValueError(f"El artículo {article_id} no existe.")
    articulo = filas[0]
    articulo["date"] = fecha_texto(articulo["date"])

    articulo["tags"] = []
    for f in consultar("""
            MATCH (:Articulo {article_id: $id})-[:TIENE_TAG]->(t:Tag)
            RETURN t.name AS name ORDER BY name""", id=article_id):
        articulo["tags"].append(f["name"])

    articulo["categorias"] = []
    for f in consultar("""
            MATCH (:Articulo {article_id: $id})-[:EN_CATEGORIA]->(c:Categoria)
            RETURN c.name AS name ORDER BY name""", id=article_id):
        articulo["categorias"].append(f["name"])

    articulo["comentarios"] = contar_comentarios(article_id)
    return articulo


# Lista de artículos (orden y filtros, como article_all_ordenado y articles_by_tag)
def articulo_all(orden="date", tipo="DESC", tag=None, categoria=None):
    if orden == "title":
        columna = "toLower(title)"
    elif orden == "date":
        columna = "date"
    elif orden == "id":
        columna = "article_id"
    else:
        raise ValueError("Atributo de orden inválido.")
    if tipo != "ASC" and tipo != "DESC":
        raise ValueError("Tipo de orden inválido.")

    query = "MATCH (u:Usuario)-[:ESCRIBIO]->(a:Articulo)\n"
    if tag:
        query = query + "MATCH (a)-[:TIENE_TAG]->(:Tag {name: $tag})\n"
    if categoria:
        query = query + "MATCH (a)-[:EN_CATEGORIA]->(:Categoria {name: $categoria})\n"
    query = query + """OPTIONAL MATCH (c:Comentario)-[:PERTENECE_A]->(a)
        RETURN a.article_id AS article_id, a.title AS title, a.date AS date,
               u.name AS autor, u.rol AS autor_rol, count(c) AS comentarios
        ORDER BY """ + columna + " " + tipo

    filas = consultar(query, tag=tag, categoria=categoria)
    for f in filas:
        f["date"] = fecha_texto(f["date"])
    return filas


# ---------- COMENTARIOS ----------
# Agrega un comentario
def comentario_insert(article_id, user_id, text, url=""):
    text = limpio(text)
    url = limpio(url)
    if text == "":
        raise ValueError("Escribe un comentario.")
    if url == "":
        url = None
    nuevo = siguiente_id("MATCH (c:Comentario) RETURN max(c.comment_id) AS mayor")
    filas = consultar("""
        MATCH (u:Usuario {user_id: $user_id}), (a:Articulo {article_id: $article_id})
        CREATE (u)-[:COMENTO]->(c:Comentario {comment_id: $id, text: $text, url: $url, date: $fecha})-[:PERTENECE_A]->(a)
        RETURN c.comment_id AS comment_id""",
        user_id=user_id, article_id=article_id, id=nuevo, text=text, url=url, fecha=ahora())
    if len(filas) == 0:
        raise ValueError(f"El artículo {article_id} no existe.")
    return nuevo


# Comentarios de un artículo con autor y rol
def comentario_all(article_id):
    filas = consultar("""
        MATCH (u:Usuario)-[:COMENTO]->(c:Comentario)-[:PERTENECE_A]->(:Articulo {article_id: $id})
        RETURN c.comment_id AS comment_id, c.text AS text, c.url AS url, c.date AS date,
               u.user_id AS user_id, u.name AS autor, u.rol AS rol
        ORDER BY date""", id=article_id)
    for f in filas:
        f["date"] = fecha_texto(f["date"])
        if f["url"] is None:
            f["url"] = ""
    return filas


# Borra un comentario
def comentario_delete(comment_id):
    contadores = ejecutar("MATCH (c:Comentario {comment_id: $id}) DETACH DELETE c", id=comment_id)
    if contadores.nodes_deleted == 0:
        raise ValueError(f"El comentario {comment_id} no existe.")


# Cuántos comentarios tiene un artículo
def contar_comentarios(article_id):
    filas = consultar("""
        MATCH (c:Comentario)-[:PERTENECE_A]->(:Articulo {article_id: $id})
        RETURN count(c) AS total""", id=article_id)
    return filas[0]["total"]


# ---------- TAGS ----------
# Crea un tag
def tag_insert(name, url=""):
    name = limpio(name)
    url = limpio(url)
    if name == "":
        raise ValueError("El nombre es obligatorio.")
    repetidos = consultar("MATCH (t:Tag) WHERE toLower(t.name) = toLower($name) RETURN count(t) AS total",
                          name=name)[0]["total"]
    if repetidos > 0:
        raise ValueError(f"Ya existe el tag '{name}'.")
    if url == "":
        url = None
    nuevo = siguiente_id("MATCH (t:Tag) RETURN max(t.tag_id) AS mayor")
    ejecutar("CREATE (t:Tag {tag_id: $id, name: $name, url: $url})", id=nuevo, name=name, url=url)
    return nuevo


# Lista de tags con cuántos artículos los usan
def tag_all():
    filas = consultar("""
        MATCH (t:Tag)
        OPTIONAL MATCH (a:Articulo)-[:TIENE_TAG]->(t)
        RETURN t.tag_id AS id, t.name AS name, t.url AS url, count(a) AS articulos
        ORDER BY name""")
    for f in filas:
        if f["url"] is None:
            f["url"] = ""
    return filas


# Borra un tag (los artículos no se borran)
def tag_delete(tag_id):
    contadores = ejecutar("MATCH (t:Tag {tag_id: $id}) DETACH DELETE t", id=tag_id)
    if contadores.nodes_deleted == 0:
        raise ValueError(f"No existe el tag {tag_id}.")


# ---------- CATEGORÍAS ----------
# Crea una categoría
def categoria_insert(name, url=""):
    name = limpio(name)
    url = limpio(url)
    if name == "":
        raise ValueError("El nombre es obligatorio.")
    repetidas = consultar("MATCH (c:Categoria) WHERE toLower(c.name) = toLower($name) RETURN count(c) AS total",
                          name=name)[0]["total"]
    if repetidas > 0:
        raise ValueError(f"Ya existe la categoría '{name}'.")
    if url == "":
        url = None
    nuevo = siguiente_id("MATCH (c:Categoria) RETURN max(c.category_id) AS mayor")
    ejecutar("CREATE (c:Categoria {category_id: $id, name: $name, url: $url})", id=nuevo, name=name, url=url)
    return nuevo


# Lista de categorías con cuántos artículos tienen
def categoria_all():
    filas = consultar("""
        MATCH (c:Categoria)
        OPTIONAL MATCH (a:Articulo)-[:EN_CATEGORIA]->(c)
        RETURN c.category_id AS id, c.name AS name, c.url AS url, count(a) AS articulos
        ORDER BY name""")
    for f in filas:
        if f["url"] is None:
            f["url"] = ""
    return filas


# Borra una categoría (los artículos no se borran)
def categoria_delete(category_id):
    contadores = ejecutar("MATCH (c:Categoria {category_id: $id}) DETACH DELETE c", id=category_id)
    if contadores.nodes_deleted == 0:
        raise ValueError(f"No existe la categoría {category_id}.")


# ---------- ESTADÍSTICAS ----------
# Cuenta con una consulta que regresa "total"
def contar(query):
    return consultar(query)[0]["total"]


# Totales para la pantalla de inicio
def resumen():
    return {
        "articulos": contar("MATCH (a:Articulo) RETURN count(a) AS total"),
        "comentarios": contar("MATCH (c:Comentario) RETURN count(c) AS total"),
        "usuarios": contar("MATCH (u:Usuario) RETURN count(u) AS total"),
        "admins": contar("MATCH (u:Usuario {rol: 'admin'}) RETURN count(u) AS total"),
        "tags": contar("MATCH (t:Tag) RETURN count(t) AS total"),
        "categorias": contar("MATCH (c:Categoria) RETURN count(c) AS total"),
    }


# Datos para los gráficos
def stats_comentarios_por_articulo():
    return consultar("""
        MATCH (a:Articulo)
        OPTIONAL MATCH (c:Comentario)-[:PERTENECE_A]->(a)
        RETURN a.title AS nombre, count(c) AS total
        ORDER BY total DESC, nombre""")


def stats_comentarios_por_usuario():
    return consultar("""
        MATCH (u:Usuario)
        OPTIONAL MATCH (u)-[:COMENTO]->(c:Comentario)
        RETURN u.name AS nombre, u.rol AS rol, count(c) AS total
        ORDER BY total DESC, nombre""")


def stats_articulos_por_categoria():
    return consultar("""
        MATCH (c:Categoria)
        OPTIONAL MATCH (a:Articulo)-[:EN_CATEGORIA]->(c)
        RETURN c.name AS nombre, count(a) AS total
        ORDER BY total DESC, nombre""")


def stats_articulos_por_tag():
    return consultar("""
        MATCH (t:Tag)
        OPTIONAL MATCH (a:Articulo)-[:TIENE_TAG]->(t)
        RETURN t.name AS nombre, count(a) AS total
        ORDER BY total DESC, nombre""")
