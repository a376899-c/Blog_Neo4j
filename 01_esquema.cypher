// Restricciones: UNIQUE + NOT NULL = como la PRIMARY KEY de Oracle
// Usuarios
CREATE CONSTRAINT usuario_id_uq IF NOT EXISTS FOR (u:Usuario) REQUIRE u.user_id IS UNIQUE;
CREATE CONSTRAINT usuario_id_nn IF NOT EXISTS FOR (u:Usuario) REQUIRE u.user_id IS NOT NULL;
CREATE CONSTRAINT usuario_email_uq IF NOT EXISTS FOR (u:Usuario) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT usuario_email_nn IF NOT EXISTS FOR (u:Usuario) REQUIRE u.email IS NOT NULL;
CREATE CONSTRAINT usuario_name_nn IF NOT EXISTS FOR (u:Usuario) REQUIRE u.name IS NOT NULL;
CREATE CONSTRAINT usuario_rol_nn IF NOT EXISTS FOR (u:Usuario) REQUIRE u.rol IS NOT NULL;

// Artículos
CREATE CONSTRAINT articulo_id_uq IF NOT EXISTS FOR (a:Articulo) REQUIRE a.article_id IS UNIQUE;
CREATE CONSTRAINT articulo_id_nn IF NOT EXISTS FOR (a:Articulo) REQUIRE a.article_id IS NOT NULL;
CREATE CONSTRAINT articulo_title_nn IF NOT EXISTS FOR (a:Articulo) REQUIRE a.title IS NOT NULL;
CREATE CONSTRAINT articulo_date_nn IF NOT EXISTS FOR (a:Articulo) REQUIRE a.date IS NOT NULL;

// Comentarios
CREATE CONSTRAINT comentario_id_uq IF NOT EXISTS FOR (c:Comentario) REQUIRE c.comment_id IS UNIQUE;
CREATE CONSTRAINT comentario_id_nn IF NOT EXISTS FOR (c:Comentario) REQUIRE c.comment_id IS NOT NULL;
CREATE CONSTRAINT comentario_text_nn IF NOT EXISTS FOR (c:Comentario) REQUIRE c.text IS NOT NULL;
CREATE CONSTRAINT comentario_date_nn IF NOT EXISTS FOR (c:Comentario) REQUIRE c.date IS NOT NULL;

// Tags
CREATE CONSTRAINT tag_id_uq IF NOT EXISTS FOR (t:Tag) REQUIRE t.tag_id IS UNIQUE;
CREATE CONSTRAINT tag_name_uq IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT tag_name_nn IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS NOT NULL;

// Categorías
CREATE CONSTRAINT categoria_id_uq IF NOT EXISTS FOR (c:Categoria) REQUIRE c.category_id IS UNIQUE;
CREATE CONSTRAINT categoria_name_uq IF NOT EXISTS FOR (c:Categoria) REQUIRE c.name IS UNIQUE;
CREATE CONSTRAINT categoria_name_nn IF NOT EXISTS FOR (c:Categoria) REQUIRE c.name IS NOT NULL;
