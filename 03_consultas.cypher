// Consultas que usa la app (para probar en Neo4j Browser)
// VER TODO EL GRAFO
MATCH (n) RETURN n;

// 1. USUARIOS
// Login: buscar usuario por correo y contrasena cifrada (SHA-256 de 'admin123')
MATCH (u:Usuario {email: 'admin@blog.com', password: '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'})
RETURN u.user_id, u.name, u.rol;

// Equivalente a fn_existe_email
MATCH (u:Usuario) WHERE toLower(u.email) = toLower('A376899@uach.mx') RETURN count(u) AS existe;

// Usuarios con su rol, articulos escritos y comentarios hechos
MATCH (u:Usuario)
OPTIONAL MATCH (u)-[:ESCRIBIO]->(a:Articulo)
WITH u, count(a) AS articulos
OPTIONAL MATCH (u)-[:COMENTO]->(c:Comentario)
RETURN u.user_id AS ID, u.name AS Nombre, u.rol AS Rol, articulos AS Articulos, count(c) AS Comentarios
ORDER BY ID;

// Crear usuario (id = MAX + 1, como NVL(MAX(user_id),0)+1 en Oracle)
OPTIONAL MATCH (x:Usuario)
WITH coalesce(max(x.user_id), 0) + 1 AS nuevo
CREATE (u:Usuario {user_id: nuevo, name: 'Prueba', email: 'prueba@blog.com', rol: 'usuario',
                   password: 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446',
                   fecha_registro: localdatetime()})
RETURN u;

// Cambiar rol (solo admin)
MATCH (u:Usuario {email: 'prueba@blog.com'}) SET u.rol = 'admin' RETURN u.name, u.rol;

// Borrar usuario y sus comentarios
MATCH (u:Usuario {email: 'prueba@blog.com'})
OPTIONAL MATCH (u)-[:COMENTO]->(c:Comentario)
DETACH DELETE c, u;

// 2. ARTICULOS
// Articulos con autor, rol del autor y numero de comentarios, ordenados por fecha (article_all_ordenado)
MATCH (u:Usuario)-[:ESCRIBIO]->(a:Articulo)
OPTIONAL MATCH (c:Comentario)-[:PERTENECE_A]->(a)
RETURN a.article_id AS ID, a.title AS Titulo, u.name AS Autor, u.rol AS Rol, a.date AS Fecha, count(c) AS Comentarios
ORDER BY Fecha DESC;

// Un articulo con sus tags y categorias (COLLECT junta los valores en una lista, como una coleccion)
MATCH (u:Usuario)-[:ESCRIBIO]->(a:Articulo {article_id: 1})
OPTIONAL MATCH (a)-[:TIENE_TAG]->(t:Tag)
WITH u, a, collect(t.name) AS tags
OPTIONAL MATCH (a)-[:EN_CATEGORIA]->(c:Categoria)
RETURN a.title, u.name AS autor, tags, collect(c.name) AS categorias;

// Articulos que tienen un tag (articles_by_tag)
MATCH (a:Articulo)-[:TIENE_TAG]->(:Tag {name: 'rutina'})
RETURN a.article_id, a.title, a.date ORDER BY a.date DESC;

// Crear articulo escrito por el usuario 2 y asociarle un tag y una categoria
MATCH (u:Usuario {user_id: 2})
OPTIONAL MATCH (x:Articulo)
WITH u, coalesce(max(x.article_id), 0) + 1 AS nuevo
CREATE (u)-[:ESCRIBIO]->(a:Articulo {article_id: nuevo, title: 'Artículo de prueba', text: 'Texto', date: localdatetime()})
WITH a
MATCH (t:Tag {name: 'spf'}), (c:Categoria {name: 'Rutinas'})
MERGE (a)-[:TIENE_TAG]->(t)
MERGE (a)-[:EN_CATEGORIA]->(c)
RETURN a;

// Actualizar articulo
MATCH (a:Articulo {title: 'Artículo de prueba'}) SET a.title = 'Artículo editado', a.text = 'Nuevo texto' RETURN a;

// Borrar articulo con sus comentarios y relaciones (en Oracle eran 4 DELETE)
MATCH (a:Articulo {title: 'Artículo editado'})
OPTIONAL MATCH (c:Comentario)-[:PERTENECE_A]->(a)
DETACH DELETE c, a;

// 3. COMENTARIOS
// Comentarios de un articulo con QUIEN comento y su ROL (comment_all)
MATCH (u:Usuario)-[:COMENTO]->(c:Comentario)-[:PERTENECE_A]->(:Articulo {article_id: 1})
RETURN c.comment_id AS ID, u.name AS QuienComento, u.rol AS Rol, c.text AS Comentario, c.date AS Fecha
ORDER BY Fecha;

// Comentar: el usuario 3 comenta el articulo 1
MATCH (u:Usuario {user_id: 3}), (a:Articulo {article_id: 1})
OPTIONAL MATCH (x:Comentario)
WITH u, a, coalesce(max(x.comment_id), 0) + 1 AS nuevo
CREATE (u)-[:COMENTO]->(c:Comentario {comment_id: nuevo, text: 'Comentario desde Neo4j Browser', date: localdatetime()})-[:PERTENECE_A]->(a)
RETURN c;

// fn_contar_comentarios
MATCH (c:Comentario)-[:PERTENECE_A]->(:Articulo {article_id: 1}) RETURN count(c) AS total;

// 4. ESTADISTICAS (las del grafico)
// Comentarios por articulo
MATCH (a:Articulo) OPTIONAL MATCH (c:Comentario)-[:PERTENECE_A]->(a)
RETURN a.title AS Articulo, count(c) AS Comentarios ORDER BY Comentarios DESC;

// Comentarios por usuario y rol
MATCH (u:Usuario) OPTIONAL MATCH (u)-[:COMENTO]->(c:Comentario)
RETURN u.name AS Usuario, u.rol AS Rol, count(c) AS Comentarios ORDER BY Comentarios DESC;

// Comentarios hechos por administradores vs usuarios
MATCH (u:Usuario)-[:COMENTO]->(c:Comentario)
RETURN u.rol AS Rol, count(c) AS Comentarios;

// Articulos por categoria y por tag
MATCH (c:Categoria) OPTIONAL MATCH (a:Articulo)-[:EN_CATEGORIA]->(c) RETURN c.name, count(a) AS Articulos ORDER BY Articulos DESC;
MATCH (t:Tag) OPTIONAL MATCH (a:Articulo)-[:TIENE_TAG]->(t) RETURN t.name, count(a) AS Articulos ORDER BY Articulos DESC;

// 5. CONSULTAS DE GRAFO (lo que es dificil en SQL)
// Articulos relacionados: comparten al menos un tag con el articulo 1
MATCH (a:Articulo {article_id: 1})-[:TIENE_TAG]->(t:Tag)<-[:TIENE_TAG]-(otro:Articulo)
RETURN otro.title AS Relacionado, collect(t.name) AS TagsEnComun ORDER BY size(TagsEnComun) DESC;

// Usuarios que comentaron articulos escritos por Ana Morales
MATCH (autor:Usuario {name: 'Ana Morales'})-[:ESCRIBIO]->(a:Articulo)<-[:PERTENECE_A]-(:Comentario)<-[:COMENTO]-(u:Usuario)
RETURN DISTINCT u.name AS Usuario, u.rol AS Rol;
