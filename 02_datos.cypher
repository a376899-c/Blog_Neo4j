// Datos iniciales del blog
// Borra todo lo anterior
MATCH (n) DETACH DELETE n;

// Usuarios (contraseña cifrada con SHA-256)
CREATE (u:Usuario {user_id: 1, name: 'Ana Morales',     email: 'a376899@uach.mx', rol: 'admin',   password: '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', fecha_registro: localdatetime('2026-09-24T20:00:00')});
CREATE (u:Usuario {user_id: 2, name: 'Mauricio Ochoa',  email: 'a377194@uach.mx', rol: 'admin',   password: '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', fecha_registro: localdatetime('2026-09-24T20:05:00')});
CREATE (u:Usuario {user_id: 3, name: 'Gael R',          email: 'gael@blog.com',   rol: 'usuario', password: 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', fecha_registro: localdatetime('2026-09-24T20:50:00')});
CREATE (u:Usuario {user_id: 4, name: 'Jacqueline H',    email: 'jacqueline@blog.com', rol: 'usuario', password: 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', fecha_registro: localdatetime('2026-09-24T20:55:00')});
CREATE (u:Usuario {user_id: 5, name: 'Administrador',   email: 'admin@blog.com',  rol: 'admin',   password: '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', fecha_registro: localdatetime('2026-11-24T09:00:00')});
CREATE (u:Usuario {user_id: 6, name: 'Usuario Demo',    email: 'usuario@blog.com', rol: 'usuario', password: 'e606e38b0d8c19b24cf0ee3808183162ea7cd63ff7912dbb22b5e803286b4446', fecha_registro: localdatetime('2026-11-24T09:05:00')});

// Artículos
CREATE (a:Articulo {article_id: 1, title: 'Rutina para hiperpigmentación', date: localdatetime('2026-09-24T20:30:00'), text: 'Combina Thiamidol, niacinamida y ácidos. No se usan todos el mismo día para no irritar la piel.'});
CREATE (a:Articulo {article_id: 2, title: 'Niacinamida vs Glicólico', date: localdatetime('2026-09-24T20:33:00'), text: 'Niacinamida controla sebo y barrera. Glicólico exfolia. Juntos pueden irritar si no se alternan.'});
CREATE (a:Articulo {article_id: 3, title: 'Por qué el SPF 50+ es obligatorio', date: localdatetime('2026-09-24T20:36:00'), text: 'En clima con sol fuerte, sin SPF pierdes en una semana lo que logras en un mes de tratamiento.'});
CREATE (a:Articulo {article_id: 4, title: 'Señales de barrera dañada', date: localdatetime('2026-09-24T20:39:00'), text: 'Ardor, piel brillante y sensibilidad a todo. Es por exceso de ácidos. Hay que parar, no agregar más productos.'});
CREATE (a:Articulo {article_id: 5, title: 'Cómo recuperar la barrera', date: localdatetime('2026-09-24T20:41:00'), text: 'Pausa ácidos 1-2 semanas. Solo limpiador suave, humectante y SPF. Nada nuevo hasta mejorar.'});
CREATE (a:Articulo {article_id: 6, title: 'Salicílico vs Glicólico', date: localdatetime('2026-09-24T20:42:00'), text: 'Salicílico entra al poro y es para grasa y puntos negros. Glicólico es para textura y tono.'});
CREATE (a:Articulo {article_id: 7, title: 'Qué es Thiamidol', date: localdatetime('2026-09-24T20:44:00'), text: 'Inhibe la melanina con menos irritación que la hidroquinona. Por eso es más caro.'});
CREATE (a:Articulo {article_id: 8, title: 'Rutina de día vs noche', date: localdatetime('2026-09-24T20:46:00'), text: 'Día: proteger con antioxidante y SPF. Noche: reparar con ácidos o retinoides.'});

// Tags
CREATE (t:Tag {tag_id: 1, name: 'hiperpigmentacion'});
CREATE (t:Tag {tag_id: 2, name: 'rutina'});
CREATE (t:Tag {tag_id: 3, name: 'acidos'});
CREATE (t:Tag {tag_id: 4, name: 'ingredientes'});
CREATE (t:Tag {tag_id: 5, name: 'spf'});
CREATE (t:Tag {tag_id: 6, name: 'barrera'});

// Categorías
CREATE (c:Categoria {category_id: 1, name: 'Rutinas', url: 'www.desconocido.com'});
CREATE (c:Categoria {category_id: 2, name: 'Ingredientes'});
CREATE (c:Categoria {category_id: 3, name: 'Cuidado básico'});

// Quién escribió cada artículo
MATCH (u:Usuario {user_id: 2}), (a:Articulo {article_id: 1}) CREATE (u)-[:ESCRIBIO]->(a);
MATCH (u:Usuario {user_id: 2}), (a:Articulo {article_id: 2}) CREATE (u)-[:ESCRIBIO]->(a);
MATCH (u:Usuario {user_id: 1}), (a:Articulo {article_id: 3}) CREATE (u)-[:ESCRIBIO]->(a);
MATCH (u:Usuario {user_id: 1}), (a:Articulo {article_id: 4}) CREATE (u)-[:ESCRIBIO]->(a);
MATCH (u:Usuario {user_id: 1}), (a:Articulo {article_id: 5}) CREATE (u)-[:ESCRIBIO]->(a);
MATCH (u:Usuario {user_id: 2}), (a:Articulo {article_id: 6}) CREATE (u)-[:ESCRIBIO]->(a);
MATCH (u:Usuario {user_id: 1}), (a:Articulo {article_id: 7}) CREATE (u)-[:ESCRIBIO]->(a);
MATCH (u:Usuario {user_id: 2}), (a:Articulo {article_id: 8}) CREATE (u)-[:ESCRIBIO]->(a);

// Tags de cada artículo
MATCH (a:Articulo {article_id: 1}), (t:Tag {tag_id: 1}) CREATE (a)-[:TIENE_TAG]->(t);
MATCH (a:Articulo {article_id: 1}), (t:Tag {tag_id: 2}) CREATE (a)-[:TIENE_TAG]->(t);
MATCH (a:Articulo {article_id: 2}), (t:Tag {tag_id: 3}) CREATE (a)-[:TIENE_TAG]->(t);
MATCH (a:Articulo {article_id: 2}), (t:Tag {tag_id: 4}) CREATE (a)-[:TIENE_TAG]->(t);
MATCH (a:Articulo {article_id: 3}), (t:Tag {tag_id: 5}) CREATE (a)-[:TIENE_TAG]->(t);
MATCH (a:Articulo {article_id: 4}), (t:Tag {tag_id: 6}) CREATE (a)-[:TIENE_TAG]->(t);
MATCH (a:Articulo {article_id: 5}), (t:Tag {tag_id: 6}) CREATE (a)-[:TIENE_TAG]->(t);
MATCH (a:Articulo {article_id: 6}), (t:Tag {tag_id: 3}) CREATE (a)-[:TIENE_TAG]->(t);
MATCH (a:Articulo {article_id: 7}), (t:Tag {tag_id: 1}) CREATE (a)-[:TIENE_TAG]->(t);
MATCH (a:Articulo {article_id: 7}), (t:Tag {tag_id: 4}) CREATE (a)-[:TIENE_TAG]->(t);
MATCH (a:Articulo {article_id: 8}), (t:Tag {tag_id: 2}) CREATE (a)-[:TIENE_TAG]->(t);
MATCH (a:Articulo {article_id: 8}), (t:Tag {tag_id: 5}) CREATE (a)-[:TIENE_TAG]->(t);

// Categoría de cada artículo
MATCH (a:Articulo {article_id: 1}), (c:Categoria {category_id: 1}) CREATE (a)-[:EN_CATEGORIA]->(c);
MATCH (a:Articulo {article_id: 8}), (c:Categoria {category_id: 1}) CREATE (a)-[:EN_CATEGORIA]->(c);
MATCH (a:Articulo {article_id: 2}), (c:Categoria {category_id: 2}) CREATE (a)-[:EN_CATEGORIA]->(c);
MATCH (a:Articulo {article_id: 6}), (c:Categoria {category_id: 2}) CREATE (a)-[:EN_CATEGORIA]->(c);
MATCH (a:Articulo {article_id: 7}), (c:Categoria {category_id: 2}) CREATE (a)-[:EN_CATEGORIA]->(c);
MATCH (a:Articulo {article_id: 3}), (c:Categoria {category_id: 3}) CREATE (a)-[:EN_CATEGORIA]->(c);
MATCH (a:Articulo {article_id: 4}), (c:Categoria {category_id: 3}) CREATE (a)-[:EN_CATEGORIA]->(c);
MATCH (a:Articulo {article_id: 5}), (c:Categoria {category_id: 3}) CREATE (a)-[:EN_CATEGORIA]->(c);

// Comentarios: quién comentó y en qué artículo
MATCH (u:Usuario {user_id: 3}), (a:Articulo {article_id: 1})
CREATE (u)-[:COMENTO]->(:Comentario {comment_id: 1, text: 'Muy útil, yo uso Thiamidol en la noche.', date: localdatetime('2026-09-24T21:00:00')})-[:PERTENECE_A]->(a);
MATCH (u:Usuario {user_id: 3}), (a:Articulo {article_id: 2})
CREATE (u)-[:COMENTO]->(:Comentario {comment_id: 2, text: '¿Se pueden usar en días alternos?', date: localdatetime('2026-09-24T21:02:00')})-[:PERTENECE_A]->(a);
MATCH (u:Usuario {user_id: 4}), (a:Articulo {article_id: 1})
CREATE (u)-[:COMENTO]->(:Comentario {comment_id: 3, text: 'Me encantó la rutina, la voy a probar.', date: localdatetime('2026-09-24T21:05:00')})-[:PERTENECE_A]->(a);
MATCH (u:Usuario {user_id: 2}), (a:Articulo {article_id: 2})
CREATE (u)-[:COMENTO]->(:Comentario {comment_id: 4, text: 'Sí, Gael: alternarlos es la mejor opción.', date: localdatetime('2026-09-24T21:10:00')})-[:PERTENECE_A]->(a);
MATCH (u:Usuario {user_id: 6}), (a:Articulo {article_id: 3})
CREATE (u)-[:COMENTO]->(:Comentario {comment_id: 5, text: 'No sabía que el SPF era tan importante.', date: localdatetime('2026-11-24T09:10:00')})-[:PERTENECE_A]->(a);
MATCH (u:Usuario {user_id: 1}), (a:Articulo {article_id: 3})
CREATE (u)-[:COMENTO]->(:Comentario {comment_id: 6, text: 'Recuerden reaplicar cada 2 o 3 horas.', url: 'www.desconocido.com', date: localdatetime('2026-11-24T09:15:00')})-[:PERTENECE_A]->(a);
MATCH (u:Usuario {user_id: 4}), (a:Articulo {article_id: 5})
CREATE (u)-[:COMENTO]->(:Comentario {comment_id: 7, text: 'Esto me salvó la piel después de abusar de los ácidos.', date: localdatetime('2026-11-24T09:20:00')})-[:PERTENECE_A]->(a);
MATCH (u:Usuario {user_id: 3}), (a:Articulo {article_id: 6})
CREATE (u)-[:COMENTO]->(:Comentario {comment_id: 8, text: 'Excelente comparación.', date: localdatetime('2026-11-24T09:25:00')})-[:PERTENECE_A]->(a);
