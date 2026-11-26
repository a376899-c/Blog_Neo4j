# App de escritorio del blog (Tkinter)
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator
from neo4j.exceptions import AuthError, ServiceUnavailable

import blog_db as db
import config
from conexion import cerrar, probar_conexion

# Colores y letra
MORADO = "#4c2a85"
MORADO_OSCURO = "#3a1f68"
MORADO_CLARO = "#ede7f6"
FONDO = "#f5f5f7"
BLANCO = "#ffffff"
TEXTO = "#1f2937"
GRIS = "#6b7280"
BORDE = "#dcdce3"
ROJO = "#dc2626"
VERDE = "#15803d"
AZUL_BOTON = "#2563eb"
LETRA = "Segoe UI"

# Color de cada rol (igual en toda la app)
COLOR_ROL = {"admin": "#eb6834", "usuario": "#2a78d6"}
FONDO_ROL = {"admin": "#fdeee7", "usuario": "#e8f1fc"}
NOMBRE_ROL = {"admin": "ADMINISTRADOR", "usuario": "USUARIO"}
ICONO_ROL = {"admin": "★", "usuario": "●"}

GRAFICOS = ["Comentarios por artículo", "Comentarios por usuario (color = rol)",
            "Artículos por categoría", "Artículos por tag"]


# ---------- Ayudas para crear la interfaz ----------
def boton(padre, texto, comando, color=MORADO):
    return tk.Button(padre, text=texto, command=comando, bg=color, fg=BLANCO, activebackground=MORADO_OSCURO,
                     activeforeground=BLANCO, relief="flat", font=(LETRA, 10, "bold"), padx=14, pady=6,
                     cursor="hand2", bd=0)


def etiqueta(padre, texto, tam=10, negrita=False, color=TEXTO, fondo=BLANCO):
    if negrita:
        letra = (LETRA, tam, "bold")
    else:
        letra = (LETRA, tam)
    return tk.Label(padre, text=texto, font=letra, fg=color, bg=fondo)


def entrada(padre, ancho=30, oculta=False):
    caja = tk.Entry(padre, width=ancho, font=(LETRA, 10), relief="solid", bd=1)
    if oculta:
        caja.config(show="•")
    return caja


# Etiqueta + caja de texto, una debajo de la otra
def campo(padre, texto, oculta=False):
    etiqueta(padre, texto).pack(anchor="w")
    caja = entrada(padre, 36, oculta)
    caja.pack(pady=(0, 6), ipady=3)
    return caja


def tarjeta(padre, titulo=""):
    marco = tk.Frame(padre, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1, padx=16, pady=12)
    if titulo != "":
        etiqueta(marco, titulo, 11, True, MORADO).pack(anchor="w", pady=(0, 8))
    return marco


# Tabla con barra de desplazamiento; columnas = [(clave, titulo, ancho), ...]
def tabla(padre, columnas, alto=10):
    marco = tk.Frame(padre, bg=BLANCO)
    claves = []
    mas_ancha = 0
    for col in columnas:
        claves.append(col[0])
        if col[2] > mas_ancha:
            mas_ancha = col[2]
    tree = ttk.Treeview(marco, columns=claves, show="headings", height=alto, selectmode="browse")
    for clave, titulo, ancho in columnas:
        tree.heading(clave, text=titulo)
        if ancho <= 90:
            alineacion = "center"
        else:
            alineacion = "w"
        tree.column(clave, width=ancho, minwidth=40, anchor=alineacion, stretch=(ancho == mas_ancha))
    barra = ttk.Scrollbar(marco, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=barra.set)
    tree.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    tree.tag_configure("admin", background=FONDO_ROL["admin"])
    tree.tag_configure("usuario", background=FONDO_ROL["usuario"])
    return marco, tree


# Llena una tabla; si se indica columna_rol, la fila se pinta del color de ese rol
def llenar(tree, filas, claves, clave_id, columna_rol=None):
    for item in tree.get_children():
        tree.delete(item)
    for fila in filas:
        valores = []
        for clave in claves:
            valor = fila[clave]
            if clave == "rol" or clave == "autor_rol":
                valor = NOMBRE_ROL[valor]
            valores.append(valor)
        color = []
        if columna_rol is not None:
            color = [fila[columna_rol]]
        tree.insert("", "end", iid=str(fila[clave_id]), values=valores, tags=color)


# Id de la fila elegida en una tabla (o None)
def seleccionado(tree):
    elegidos = tree.selection()
    if len(elegidos) == 0:
        return None
    return int(elegidos[0])


# Lista con el campo "name" de cada fila
def nombres_de(filas):
    nombres = []
    for fila in filas:
        nombres.append(fila["name"])
    return nombres


# Lista para marcar varios elementos con clic
def lista_multiple(padre, texto, valores):
    marco = tk.Frame(padre, bg=BLANCO)
    marco.pack(side="left", padx=(0, 10), anchor="n")
    etiqueta(marco, texto, 9).pack(anchor="w")
    lista = tk.Listbox(marco, selectmode="multiple", exportselection=False, height=6, width=22,
                       font=(LETRA, 10), relief="solid", bd=1, selectbackground="#c7b8e6", selectforeground=TEXTO)
    for valor in valores:
        lista.insert("end", valor)
    lista.pack()
    return lista


# Elementos marcados en una lista
def marcados(lista):
    elegidos = []
    for i in lista.curselection():
        elegidos.append(lista.get(i))
    return elegidos


# Marca en la lista los nombres indicados
def marcar(lista, nombres):
    lista.selection_clear(0, "end")
    for i in range(lista.size()):
        if lista.get(i) in nombres:
            lista.selection_set(i)


def estilos():
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("Treeview", font=(LETRA, 10), rowheight=26, background=BLANCO, fieldbackground=BLANCO,
                foreground=TEXTO, bordercolor=BORDE)
    s.configure("Treeview.Heading", font=(LETRA, 10, "bold"), background=MORADO_CLARO, foreground=MORADO,
                relief="flat")
    s.map("Treeview", background=[("selected", "#c7b8e6")], foreground=[("selected", TEXTO)])
    s.configure("TCombobox", padding=4)


# Ventana principal
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BLOG - Bases de Datos Avanzadas (Neo4j)")
        self.geometry("1320x780")
        self.minsize(1100, 680)
        self.state("zoomed")
        self.configure(bg=FONDO)
        estilos()
        self.usuario = None
        self.protocol("WM_DELETE_WINDOW", self.salir)
        self.mostrar_login()

    # Tkinter llama a esta función cuando un botón tiene un error: lo mostramos en una ventana
    def report_callback_exception(self, tipo, error, rastro):
        if isinstance(error, ValueError):
            messagebox.showerror("Aviso", str(error))
        elif isinstance(error, ServiceUnavailable) or isinstance(error, AuthError):
            cerrar()
            messagebox.showerror("Sin conexión con Neo4j", "No se pudo conectar a la base de datos.\n"
                                 "Revisa que esté encendida (Start) en Neo4j Desktop.")
        else:
            messagebox.showerror("Error", str(error))

    def es_admin(self):
        return self.usuario is not None and self.usuario["rol"] == "admin"

    # Borra todo lo que hay dentro de un marco
    def limpiar(self, marco):
        for hijo in marco.winfo_children():
            hijo.destroy()

    def salir(self):
        cerrar()
        self.destroy()

    # ---------- Inicio de sesión ----------
    def mostrar_login(self):
        self.limpiar(self)
        self.usuario = None
        fondo = tk.Frame(self, bg=MORADO)
        fondo.pack(fill="both", expand=True)
        caja = tk.Frame(fondo, bg=BLANCO, padx=44, pady=30)
        caja.place(relx=0.5, rely=0.5, anchor="center")

        etiqueta(caja, "BLOG", 26, True, MORADO).pack()
        etiqueta(caja, "Python + Neo4j", 10, color=GRIS).pack(pady=(0, 16))

        zona = tk.Frame(caja, bg=BLANCO)
        zona.pack(fill="x")

        # Formulario para entrar
        self.caja_login = tk.Frame(zona, bg=BLANCO)
        etiqueta(self.caja_login, "Iniciar sesión", 13, True).pack(anchor="w", pady=(0, 8))
        self.e_correo = campo(self.caja_login, "Correo")
        self.e_pass = campo(self.caja_login, "Contraseña", oculta=True)
        boton(self.caja_login, "Entrar", self.entrar).pack(fill="x", pady=(6, 8))
        enlace = etiqueta(self.caja_login, "¿No tienes cuenta? Regístrate aquí", 9, color=AZUL_BOTON)
        enlace.config(cursor="hand2")
        enlace.pack()
        enlace.bind("<Button-1>", self.ir_registro)
        self.e_correo.bind("<Return>", self.ir_a_contrasena)
        self.e_pass.bind("<Return>", self.entrar)

        # Formulario para crear cuenta (siempre rol usuario)
        self.caja_registro = tk.Frame(zona, bg=BLANCO)
        etiqueta(self.caja_registro, "Crear cuenta", 13, True).pack(anchor="w", pady=(0, 8))
        self.r_nombre = campo(self.caja_registro, "Nombre")
        self.r_correo = campo(self.caja_registro, "Correo")
        self.r_pass = campo(self.caja_registro, "Contraseña", oculta=True)
        self.r_pass2 = campo(self.caja_registro, "Confirmar contraseña", oculta=True)
        nota = etiqueta(self.caja_registro, "Las cuentas nuevas son de tipo USUARIO (solo comentan).\n"
                                            "Un administrador puede cambiarte el rol.", 8, color=GRIS)
        nota.config(justify="left")
        nota.pack(anchor="w", pady=(0, 8))
        boton(self.caja_registro, "Crear cuenta", self.registrar).pack(fill="x", pady=(0, 8))
        regreso = etiqueta(self.caja_registro, "← Ya tengo cuenta", 9, color=AZUL_BOTON)
        regreso.config(cursor="hand2")
        regreso.pack()
        regreso.bind("<Button-1>", self.ir_login)

        # Estado de la conexión
        ttk.Separator(caja).pack(fill="x", pady=(16, 8))
        fila = tk.Frame(caja, bg=BLANCO)
        fila.pack(fill="x")
        self.lbl_conexion = etiqueta(fila, "", 9)
        self.lbl_conexion.pack(side="left")
        tk.Button(fila, text="Probar conexión", command=self.probar, font=(LETRA, 8), relief="flat",
                  bg=MORADO_CLARO, fg=MORADO, cursor="hand2").pack(side="right")

        self.ir_login()
        self.after(150, self.probar)

    def ir_login(self, evento=None):
        self.caja_registro.pack_forget()
        self.caja_login.pack(fill="x")
        self.e_correo.focus_set()

    def ir_registro(self, evento=None):
        self.caja_login.pack_forget()
        self.caja_registro.pack(fill="x")
        self.r_nombre.focus_set()

    def ir_a_contrasena(self, evento=None):
        self.e_pass.focus_set()

    # Prueba la conexión con Neo4j
    def probar(self):
        try:
            probar_conexion()
            self.lbl_conexion.config(text=f"● Conectado a Neo4j  (base: {config.DATABASE})", fg=VERDE)
        except Exception:
            self.lbl_conexion.config(text="● Sin conexión: enciende la base en Neo4j Desktop", fg=ROJO)

    # Inicia sesión
    def entrar(self, evento=None):
        usuario = db.usuario_login(self.e_correo.get(), self.e_pass.get())
        if usuario is None:
            messagebox.showerror("Iniciar sesión", "Correo o contraseña incorrectos.")
            return
        self.usuario = usuario
        self.mostrar_principal()

    # Crea una cuenta nueva (rol usuario)
    def registrar(self):
        nombre = self.r_nombre.get()
        correo = self.r_correo.get()
        password = self.r_pass.get()
        if password != self.r_pass2.get():
            raise ValueError("Las contraseñas no coinciden.")
        nuevo = db.usuario_insert(nombre, correo, password, "usuario")
        messagebox.showinfo("Cuenta creada", f"Cuenta creada correctamente.\nID: {nuevo}\nRol: USUARIO")
        self.usuario = db.usuario_login(correo, password)
        self.mostrar_principal()

    # ---------- Pantalla principal: menú lateral y encabezado con el rol ----------
    def mostrar_principal(self):
        self.limpiar(self)
        rol = self.usuario["rol"]

        lateral = tk.Frame(self, bg=MORADO, width=230)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        etiqueta(lateral, "BLOG", 22, True, BLANCO, MORADO).pack(pady=(22, 0))
        tk.Frame(lateral, bg="#6a4aa5", height=1).pack(fill="x", padx=18, pady=16)

        self.botones_menu = {}
        self.boton_menu(lateral, "⌂   Inicio", "inicio", self.vista_inicio)
        self.boton_menu(lateral, "☰   Blog: leer y comentar", "blog", self.vista_blog)
        self.boton_menu(lateral, "▥   Estadísticas", "estadisticas", self.vista_estadisticas)
        if self.es_admin():
            etiqueta(lateral, "ADMINISTRACIÓN", 8, True, "#b9a6dd", MORADO).pack(anchor="w", padx=22, pady=(14, 4))
            self.boton_menu(lateral, "✎   Administrar artículos", "articulos", self.vista_articulos)
            self.boton_menu(lateral, "☺   Usuarios", "usuarios", self.vista_usuarios)
            self.boton_menu(lateral, "#   Tags y categorías", "etiquetas", self.vista_etiquetas)

        tk.Button(lateral, text="←   Cerrar sesión", anchor="w", font=(LETRA, 10), bg=MORADO_OSCURO, fg=BLANCO,
                  bd=0, relief="flat", activebackground="#2a1650", activeforeground=BLANCO, padx=22, pady=10,
                  cursor="hand2", command=self.cerrar_sesion).pack(side="bottom", fill="x")
        etiqueta(lateral, "Python · Neo4j\nProyecto final", 8, color="#b9a6dd", fondo=MORADO).pack(side="bottom",
                                                                                                    pady=10)

        derecha = tk.Frame(self, bg=FONDO)
        derecha.pack(side="left", fill="both", expand=True)

        # Encabezado: quién está en el sistema y con qué rol
        encabezado = tk.Frame(derecha, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1, padx=24, pady=10)
        encabezado.pack(fill="x")
        izq = tk.Frame(encabezado, bg=BLANCO)
        izq.pack(side="left")
        etiqueta(izq, "Sesión iniciada como", 8, color=GRIS).pack(anchor="w")
        etiqueta(izq, self.usuario["name"], 13, True).pack(anchor="w")
        etiqueta(izq, self.usuario["email"], 9, color=GRIS).pack(anchor="w")
        der = tk.Frame(encabezado, bg=BLANCO)
        der.pack(side="right")
        tk.Label(der, text=f" {ICONO_ROL[rol]}  {NOMBRE_ROL[rol]} ", font=(LETRA, 11, "bold"), bg=COLOR_ROL[rol],
                 fg=BLANCO, padx=10, pady=4).pack(anchor="e")
        if rol == "admin":
            permisos = "Puede crear, modificar y eliminar todo"
        else:
            permisos = "Puede leer los artículos y comentar"
        etiqueta(der, permisos, 9, color=GRIS).pack(anchor="e", pady=(4, 0))

        self.contenido = tk.Frame(derecha, bg=FONDO, padx=24, pady=16)
        self.contenido.pack(fill="both", expand=True)
        self.vista_inicio()

    def boton_menu(self, padre, texto, clave, comando):
        b = tk.Button(padre, text=texto, anchor="w", font=(LETRA, 10), bg=MORADO, fg=BLANCO, bd=0, relief="flat",
                      activebackground=MORADO_OSCURO, activeforeground=BLANCO, padx=22, pady=9, cursor="hand2",
                      command=comando)
        b.pack(fill="x")
        self.botones_menu[clave] = b

    # Marca la opción del menú y limpia la parte derecha
    def preparar_vista(self, clave):
        for nombre in self.botones_menu:
            if nombre == clave:
                self.botones_menu[nombre].config(bg=MORADO_OSCURO)
            else:
                self.botones_menu[nombre].config(bg=MORADO)
        self.limpiar(self.contenido)

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar sesión", f"¿Cerrar la sesión de {self.usuario['name']}?"):
            self.mostrar_login()

    def titulo(self, texto, subtitulo):
        etiqueta(self.contenido, texto, 18, True, fondo=FONDO).pack(anchor="w")
        etiqueta(self.contenido, subtitulo, 10, color=GRIS, fondo=FONDO).pack(anchor="w", pady=(0, 12))

    # ---------- Pantalla de inicio ----------
    def vista_inicio(self):
        self.preparar_vista("inicio")
        self.titulo(f"Bienvenido, {self.usuario['name']}",
                    "Sistema de gestión de un blog con Python y una base de datos de grafos Neo4j.")
        r = db.resumen()
        fila = tk.Frame(self.contenido, bg=FONDO)
        fila.pack(fill="x", pady=(0, 14))
        self.tarjeta_numero(fila, r["articulos"], "Artículos", "nodos :Articulo")
        self.tarjeta_numero(fila, r["comentarios"], "Comentarios", "nodos :Comentario")
        self.tarjeta_numero(fila, r["usuarios"], "Usuarios", f"{r['admins']} administradores")
        self.tarjeta_numero(fila, r["tags"], "Tags", "nodos :Tag")
        self.tarjeta_numero(fila, r["categorias"], "Categorías", "nodos :Categoria")

        aviso = tarjeta(self.contenido, "¿Qué puedo hacer?")
        aviso.pack(fill="x", pady=(0, 14))
        if self.es_admin():
            texto = ("Eres ADMINISTRADOR: puedes crear, editar y eliminar artículos, asignarles tags y categorías, "
                     "administrar usuarios (y cambiar su rol) y eliminar comentarios. También puedes comentar.")
        else:
            texto = ("Eres USUARIO: puedes leer todos los artículos y dejar comentarios. "
                     "Tu nombre y tu rol aparecerán junto a cada comentario que escribas.")
        explicacion = etiqueta(aviso, texto, 10)
        explicacion.config(wraplength=980, justify="left")
        explicacion.pack(anchor="w")

        quienes = tarjeta(self.contenido, "Usuarios del sistema (¿quién es administrador y quién usuario?)")
        quienes.pack(fill="both", expand=True)
        columnas = [("name", "Nombre", 220), ("rol", "Rol", 140), ("articulos", "Artículos", 80),
                    ("comentarios", "Comentarios", 90), ("ultimo_acceso", "Último acceso", 160)]
        marco, tree = tabla(quienes, columnas, 8)
        marco.pack(fill="both", expand=True)
        llenar(tree, db.usuario_all(), ["name", "rol", "articulos", "comentarios", "ultimo_acceso"], "user_id", "rol")

    def tarjeta_numero(self, padre, numero, texto, detalle):
        t = tarjeta(padre)
        t.pack(side="left", fill="x", expand=True, padx=(0, 10))
        etiqueta(t, str(numero), 22, True, MORADO).pack(anchor="w")
        etiqueta(t, texto, 10, True).pack(anchor="w")
        etiqueta(t, detalle, 8, color=GRIS).pack(anchor="w")

    # ---------- Blog: leer y comentar ----------
    def vista_blog(self):
        self.preparar_vista("blog")
        self.titulo("Blog", "Elige un artículo para leerlo y comentarlo. Los comentarios muestran quién los "
                            "escribió y su rol.")
        filtros = tk.Frame(self.contenido, bg=FONDO)
        filtros.pack(fill="x", pady=(0, 10))
        etiqueta(filtros, "Tag:", fondo=FONDO).pack(side="left")
        self.cb_tag = ttk.Combobox(filtros, state="readonly", width=18, values=["(todos)"] + nombres_de(db.tag_all()))
        self.cb_tag.current(0)
        self.cb_tag.pack(side="left", padx=(4, 14))
        etiqueta(filtros, "Categoría:", fondo=FONDO).pack(side="left")
        self.cb_cat = ttk.Combobox(filtros, state="readonly", width=18,
                                   values=["(todas)"] + nombres_de(db.categoria_all()))
        self.cb_cat.current(0)
        self.cb_cat.pack(side="left", padx=(4, 14))
        etiqueta(filtros, "Ordenar:", fondo=FONDO).pack(side="left")
        self.cb_orden = ttk.Combobox(filtros, state="readonly", width=16,
                                     values=["Más recientes", "Más antiguos", "Título A-Z", "Título Z-A"])
        self.cb_orden.current(0)
        self.cb_orden.pack(side="left", padx=(4, 14))
        self.cb_tag.bind("<<ComboboxSelected>>", self.blog_cargar_lista)
        self.cb_cat.bind("<<ComboboxSelected>>", self.blog_cargar_lista)
        self.cb_orden.bind("<<ComboboxSelected>>", self.blog_cargar_lista)

        cuerpo = tk.Frame(self.contenido, bg=FONDO)
        cuerpo.pack(fill="both", expand=True)

        izquierda = tarjeta(cuerpo, "Artículos")
        izquierda.pack(side="left", fill="both", padx=(0, 12))
        columnas = [("title", "Título", 250), ("autor", "Autor", 130), ("comentarios", "Com.", 50)]
        marco, self.tree_blog = tabla(izquierda, columnas, 20)
        marco.pack(fill="both", expand=True)
        self.tree_blog.bind("<<TreeviewSelect>>", self.blog_mostrar)

        self.panel_articulo = tarjeta(cuerpo)
        self.panel_articulo.pack(side="left", fill="both", expand=True)
        self.blog_cargar_lista()

    def blog_cargar_lista(self, evento=None):
        orden = self.cb_orden.get()
        if orden == "Más recientes":
            campo_orden, tipo = "date", "DESC"
        elif orden == "Más antiguos":
            campo_orden, tipo = "date", "ASC"
        elif orden == "Título A-Z":
            campo_orden, tipo = "title", "ASC"
        else:
            campo_orden, tipo = "title", "DESC"
        tag = None
        if self.cb_tag.current() > 0:
            tag = self.cb_tag.get()
        categoria = None
        if self.cb_cat.current() > 0:
            categoria = self.cb_cat.get()

        filas = db.articulo_all(campo_orden, tipo, tag, categoria)
        llenar(self.tree_blog, filas, ["title", "autor", "comentarios"], "article_id")
        if len(filas) > 0:
            self.tree_blog.selection_set(str(filas[0]["article_id"]))
        else:
            self.limpiar(self.panel_articulo)
            etiqueta(self.panel_articulo, "No hay artículos con ese filtro.", 11, color=GRIS).pack(pady=40)

    # Muestra el artículo elegido con sus comentarios
    def blog_mostrar(self, evento=None):
        article_id = seleccionado(self.tree_blog)
        if article_id is None:
            return
        a = db.articulo_get(article_id)
        self.articulo_actual = article_id
        p = self.panel_articulo
        self.limpiar(p)

        titulo = etiqueta(p, a["title"], 16, True)
        titulo.config(wraplength=640, justify="left")
        titulo.pack(anchor="w")
        meta = tk.Frame(p, bg=BLANCO)
        meta.pack(anchor="w", pady=(2, 6))
        etiqueta(meta, f"Por {a['autor']}", 9, True, GRIS).pack(side="left")
        tk.Label(meta, text=f" {NOMBRE_ROL[a['autor_rol']]} ", font=(LETRA, 7, "bold"),
                 bg=COLOR_ROL[a["autor_rol"]], fg=BLANCO).pack(side="left", padx=6)
        etiqueta(meta, f"·  {a['date']}  ·  Artículo #{a['article_id']}", 9, color=GRIS).pack(side="left")

        tags = "—"
        if len(a["tags"]) > 0:
            tags = "#" + ", #".join(a["tags"])
        categorias = "—"
        if len(a["categorias"]) > 0:
            categorias = ", ".join(a["categorias"])
        etiqueta(p, f"Tags: {tags}     Categorías: {categorias}", 9, color=MORADO).pack(anchor="w", pady=(0, 6))

        texto = tk.Text(p, height=4, wrap="word", font=(LETRA, 11), relief="flat", bg="#fafafb", padx=10, pady=8)
        if a["text"] is not None:
            texto.insert("1.0", a["text"])
        texto.config(state="disabled")
        texto.pack(fill="x", pady=(0, 10))

        etiqueta(p, f"Comentarios ({a['comentarios']})", 11, True, MORADO).pack(anchor="w")
        columnas = [("autor", "Quién comentó", 150), ("rol", "Rol", 120), ("date", "Fecha", 120),
                    ("text", "Comentario", 360)]
        marco, self.tree_coment = tabla(p, columnas, 6)
        marco.pack(fill="both", expand=True, pady=(4, 6))
        llenar(self.tree_coment, db.comentario_all(article_id), ["autor", "rol", "date", "text"], "comment_id", "rol")

        # Leyenda de colores y botón para borrar (solo admin)
        leyenda = tk.Frame(p, bg=BLANCO)
        leyenda.pack(fill="x")
        for r in ["admin", "usuario"]:
            tk.Label(leyenda, text="   ", bg=FONDO_ROL[r], highlightbackground=COLOR_ROL[r],
                     highlightthickness=1).pack(side="left", padx=(0, 4))
            etiqueta(leyenda, f"{NOMBRE_ROL[r].capitalize()}   ", 8, color=GRIS).pack(side="left")
        if self.es_admin():
            boton(leyenda, "Eliminar comentario seleccionado", self.blog_borrar_comentario, ROJO).pack(side="right")

        # Escribir comentario (cualquier rol)
        nuevo = tk.Frame(p, bg=BLANCO)
        nuevo.pack(fill="x", pady=(10, 0))
        quien = tk.Frame(nuevo, bg=BLANCO)
        quien.pack(anchor="w")
        etiqueta(quien, f"Comentar como {self.usuario['name']}", 9, True).pack(side="left")
        rol = self.usuario["rol"]
        tk.Label(quien, text=f" {NOMBRE_ROL[rol]} ", font=(LETRA, 7, "bold"), bg=COLOR_ROL[rol],
                 fg=BLANCO).pack(side="left", padx=6)
        self.txt_comentario = tk.Text(nuevo, height=2, wrap="word", font=(LETRA, 10), relief="solid", bd=1)
        self.txt_comentario.pack(fill="x", pady=4)
        fila = tk.Frame(nuevo, bg=BLANCO)
        fila.pack(fill="x")
        etiqueta(fila, "URL (opcional):", 9).pack(side="left")
        self.e_url = entrada(fila, 40)
        self.e_url.pack(side="left", padx=6, ipady=2)
        boton(fila, "Publicar comentario", self.blog_comentar).pack(side="right")

    def blog_comentar(self):
        texto = self.txt_comentario.get("1.0", "end")
        nuevo = db.comentario_insert(self.articulo_actual, self.usuario["user_id"], texto, self.e_url.get())
        messagebox.showinfo("Comentario", f"Comentario publicado.\nID: {nuevo}")
        self.blog_refrescar()

    def blog_borrar_comentario(self):
        comment_id = seleccionado(self.tree_coment)
        if comment_id is None:
            raise ValueError("Selecciona un comentario de la tabla.")
        autor = self.tree_coment.item(str(comment_id), "values")[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar el comentario #{comment_id} de {autor}?"):
            db.comentario_delete(comment_id)
            self.blog_refrescar()

    # Vuelve a cargar la lista y deja elegido el mismo artículo
    def blog_refrescar(self):
        actual = self.articulo_actual
        self.blog_cargar_lista()
        if self.tree_blog.exists(str(actual)):
            self.tree_blog.selection_set(str(actual))
            self.tree_blog.see(str(actual))

    # ---------- Administrar artículos (solo admin) ----------
    def vista_articulos(self):
        self.preparar_vista("articulos")
        if not self.es_admin():
            raise ValueError("Solo un administrador puede modificar artículos.")
        self.titulo("Administrar artículos", "Crea, consulta, actualiza, elimina y ordena los artículos.")
        cuerpo = tk.Frame(self.contenido, bg=FONDO)
        cuerpo.pack(fill="both", expand=True)

        # Formulario
        form = tarjeta(cuerpo, "Datos del artículo")
        form.pack(side="left", fill="y", padx=(0, 12))
        self.lbl_id = etiqueta(form, "Artículo nuevo", 10, True, GRIS)
        self.lbl_id.pack(anchor="w", pady=(0, 6))
        etiqueta(form, "Título").pack(anchor="w")
        self.e_titulo = entrada(form, 46)
        self.e_titulo.pack(anchor="w", pady=(0, 6), ipady=3)
        etiqueta(form, "Texto").pack(anchor="w")
        self.txt_texto = tk.Text(form, width=46, height=6, wrap="word", font=(LETRA, 10), relief="solid", bd=1)
        self.txt_texto.pack(anchor="w", pady=(0, 6))
        listas = tk.Frame(form, bg=BLANCO)
        listas.pack(anchor="w", fill="x")
        self.lb_tags = lista_multiple(listas, "Tags (clic para marcar varios)", nombres_de(db.tag_all()))
        self.lb_cats = lista_multiple(listas, "Categorías", nombres_de(db.categoria_all()))
        botones = tk.Frame(form, bg=BLANCO)
        botones.pack(fill="x", pady=(10, 0))
        boton(botones, "Nuevo", self.art_nuevo, GRIS).pack(side="left", padx=(0, 6))
        boton(botones, "Guardar", self.art_guardar).pack(side="left", padx=(0, 6))
        boton(botones, "Eliminar", self.art_eliminar, ROJO).pack(side="left")
        etiqueta(form, "El autor de un artículo nuevo es el administrador que lo crea.", 8,
                 color=GRIS).pack(anchor="w", pady=(8, 0))

        # Tabla con orden
        derecha = tarjeta(cuerpo, "Artículos guardados")
        derecha.pack(side="left", fill="both", expand=True)
        orden = tk.Frame(derecha, bg=BLANCO)
        orden.pack(fill="x", pady=(0, 6))
        etiqueta(orden, "Ordenar por:").pack(side="left")
        self.cb_art_campo = ttk.Combobox(orden, state="readonly", width=10, values=["Fecha", "Título", "ID"])
        self.cb_art_campo.current(2)
        self.cb_art_campo.pack(side="left", padx=4)
        etiqueta(orden, "Tipo:").pack(side="left", padx=(8, 0))
        self.cb_art_tipo = ttk.Combobox(orden, state="readonly", width=12, values=["Ascendente", "Descendente"])
        self.cb_art_tipo.current(0)
        self.cb_art_tipo.pack(side="left", padx=4)
        boton(orden, "Ordenar", self.art_cargar).pack(side="left", padx=6)
        columnas = [("article_id", "ID", 45), ("title", "Título", 260), ("autor", "Autor", 140),
                    ("date", "Fecha", 130), ("comentarios", "Com.", 50)]
        marco, self.tree_art = tabla(derecha, columnas, 18)
        marco.pack(fill="both", expand=True)
        self.tree_art.bind("<<TreeviewSelect>>", self.art_seleccionar)
        self.art_nuevo()
        self.art_cargar()

    def art_cargar(self):
        campo_elegido = self.cb_art_campo.get()
        if campo_elegido == "Fecha":
            campo_orden = "date"
        elif campo_elegido == "Título":
            campo_orden = "title"
        else:
            campo_orden = "id"
        if self.cb_art_tipo.get() == "Ascendente":
            tipo = "ASC"
        else:
            tipo = "DESC"
        llenar(self.tree_art, db.articulo_all(campo_orden, tipo),
               ["article_id", "title", "autor", "date", "comentarios"], "article_id")

    # Deja el formulario vacío para un artículo nuevo
    def art_nuevo(self):
        self.art_id = None
        self.lbl_id.config(text="Artículo nuevo")
        self.e_titulo.delete(0, "end")
        self.txt_texto.delete("1.0", "end")
        marcar(self.lb_tags, [])
        marcar(self.lb_cats, [])
        for item in self.tree_art.selection():
            self.tree_art.selection_remove(item)
        self.e_titulo.focus_set()

    # Pasa el artículo elegido al formulario
    def art_seleccionar(self, evento=None):
        article_id = seleccionado(self.tree_art)
        if article_id is None:
            return
        a = db.articulo_get(article_id)
        self.art_id = article_id
        self.lbl_id.config(text=f"Editando artículo #{article_id}  (autor: {a['autor']})")
        self.e_titulo.delete(0, "end")
        self.e_titulo.insert(0, a["title"])
        self.txt_texto.delete("1.0", "end")
        if a["text"] is not None:
            self.txt_texto.insert("1.0", a["text"])
        marcar(self.lb_tags, a["tags"])
        marcar(self.lb_cats, a["categorias"])

    def art_guardar(self):
        titulo = self.e_titulo.get()
        texto = self.txt_texto.get("1.0", "end")
        tags = marcados(self.lb_tags)
        categorias = marcados(self.lb_cats)
        if self.art_id is None:
            nuevo = db.articulo_insert(self.usuario["user_id"], titulo, texto, tags, categorias)
            messagebox.showinfo("Artículo creado", f"Artículo creado correctamente.\nID: {nuevo}")
            self.art_cargar()
            self.tree_art.selection_set(str(nuevo))
        else:
            actual = self.art_id
            db.articulo_update(actual, titulo, texto, tags, categorias)
            messagebox.showinfo("Artículo actualizado", f"Artículo #{actual} actualizado.")
            self.art_cargar()
            self.tree_art.selection_set(str(actual))

    def art_eliminar(self):
        if self.art_id is None:
            raise ValueError("Selecciona en la tabla el artículo que quieres eliminar.")
        n = db.contar_comentarios(self.art_id)
        if messagebox.askyesno("Confirmar", f"¿Desea eliminar el artículo {self.art_id}?\n"
                                            f"También se borrarán sus {n} comentario(s)."):
            db.articulo_delete(self.art_id)
            messagebox.showinfo("Eliminado", "Artículo eliminado correctamente.")
            self.art_nuevo()
            self.art_cargar()

    # ---------- Usuarios (solo admin) ----------
    def vista_usuarios(self):
        self.preparar_vista("usuarios")
        if not self.es_admin():
            raise ValueError("Solo un administrador puede administrar usuarios.")
        self.titulo("Usuarios", "Crea usuarios y decide quién es ADMINISTRADOR y quién es USUARIO.")
        form = tarjeta(self.contenido, "Crear usuario")
        form.pack(fill="x", pady=(0, 12))
        fila = tk.Frame(form, bg=BLANCO)
        fila.pack(fill="x")
        etiqueta(fila, "Nombre:").pack(side="left")
        self.u_nombre = entrada(fila, 22)
        self.u_nombre.pack(side="left", padx=(4, 12), ipady=3)
        etiqueta(fila, "Correo:").pack(side="left")
        self.u_correo = entrada(fila, 26)
        self.u_correo.pack(side="left", padx=(4, 12), ipady=3)
        etiqueta(fila, "Contraseña:").pack(side="left")
        self.u_pass = entrada(fila, 14, oculta=True)
        self.u_pass.pack(side="left", padx=(4, 12), ipady=3)
        etiqueta(fila, "Rol:").pack(side="left")
        self.cb_rol = ttk.Combobox(fila, state="readonly", width=14, values=["USUARIO", "ADMINISTRADOR"])
        self.cb_rol.current(0)
        self.cb_rol.pack(side="left", padx=(4, 12))
        boton(fila, "Crear usuario", self.usr_crear).pack(side="left")

        lista = tarjeta(self.contenido, "Usuarios registrados")
        lista.pack(fill="both", expand=True)
        columnas = [("user_id", "ID", 45), ("name", "Nombre", 180), ("email", "Correo", 210), ("rol", "Rol", 130),
                    ("articulos", "Artículos", 75), ("comentarios", "Coment.", 70),
                    ("fecha_registro", "Registro", 130), ("ultimo_acceso", "Último acceso", 130)]
        marco, self.tree_usr = tabla(lista, columnas, 14)
        marco.pack(fill="both", expand=True)
        botones = tk.Frame(lista, bg=BLANCO)
        botones.pack(fill="x", pady=(8, 0))
        boton(botones, "★ Hacer administrador", self.usr_hacer_admin, COLOR_ROL["admin"]).pack(side="left")
        boton(botones, "● Hacer usuario", self.usr_hacer_usuario, COLOR_ROL["usuario"]).pack(side="left", padx=6)
        boton(botones, "Eliminar usuario", self.usr_eliminar, ROJO).pack(side="right")
        self.usr_cargar()

    def usr_cargar(self):
        columnas = ["user_id", "name", "email", "rol", "articulos", "comentarios", "fecha_registro", "ultimo_acceso"]
        llenar(self.tree_usr, db.usuario_all(), columnas, "user_id", "rol")

    def usr_crear(self):
        if self.cb_rol.get() == "ADMINISTRADOR":
            rol = "admin"
        else:
            rol = "usuario"
        nuevo = db.usuario_insert(self.u_nombre.get(), self.u_correo.get(), self.u_pass.get(), rol)
        messagebox.showinfo("Usuario creado", f"Usuario creado correctamente.\nID: {nuevo}\nRol: {NOMBRE_ROL[rol]}")
        self.u_nombre.delete(0, "end")
        self.u_correo.delete(0, "end")
        self.u_pass.delete(0, "end")
        self.usr_cargar()

    # Usuario elegido en la tabla (no puede ser uno mismo)
    def usuario_elegido(self):
        user_id = seleccionado(self.tree_usr)
        if user_id is None:
            raise ValueError("Selecciona un usuario de la tabla.")
        if user_id == self.usuario["user_id"]:
            raise ValueError("No puedes cambiar ni eliminar tu propia cuenta mientras la usas.")
        return user_id

    def usr_hacer_admin(self):
        self.usr_cambiar_rol("admin")

    def usr_hacer_usuario(self):
        self.usr_cambiar_rol("usuario")

    def usr_cambiar_rol(self, rol):
        user_id = self.usuario_elegido()
        db.usuario_cambiar_rol(user_id, rol)
        self.usr_cargar()
        self.tree_usr.selection_set(str(user_id))

    def usr_eliminar(self):
        user_id = self.usuario_elegido()
        nombre = self.tree_usr.item(str(user_id), "values")[1]
        if messagebox.askyesno("Confirmar", f"¿Eliminar al usuario {nombre}?\nTambién se borrarán sus comentarios."):
            db.usuario_delete(user_id)
            self.usr_cargar()

    # ---------- Tags y categorías (solo admin) ----------
    def vista_etiquetas(self):
        self.preparar_vista("etiquetas")
        if not self.es_admin():
            raise ValueError("Solo un administrador puede modificar tags y categorías.")
        self.titulo("Tags y categorías", "Organiza los artículos. Se asignan a cada artículo en "
                                         "'Administrar artículos'.")
        cuerpo = tk.Frame(self.contenido, bg=FONDO)
        cuerpo.pack(fill="both", expand=True)

        panel_tags = tarjeta(cuerpo, "Tags")
        panel_tags.pack(side="left", fill="both", expand=True, padx=(0, 12))
        self.tag_nombre, self.tag_url, self.tree_tags = self.panel_etiqueta(panel_tags, self.tag_crear,
                                                                            self.tag_eliminar)
        panel_cats = tarjeta(cuerpo, "Categorías")
        panel_cats.pack(side="left", fill="both", expand=True)
        self.cat_nombre, self.cat_url, self.tree_cats = self.panel_etiqueta(panel_cats, self.categoria_crear,
                                                                            self.categoria_eliminar)
        self.tags_cargar()
        self.categorias_cargar()

    # Formulario (nombre, url, Crear) + tabla + botón Eliminar
    def panel_etiqueta(self, panel, crear, eliminar):
        fila = tk.Frame(panel, bg=BLANCO)
        fila.pack(fill="x", pady=(0, 8))
        etiqueta(fila, "Nombre:").pack(side="left")
        e_nombre = entrada(fila, 16)
        e_nombre.pack(side="left", padx=4, ipady=3)
        etiqueta(fila, "URL:").pack(side="left")
        e_url = entrada(fila, 18)
        e_url.pack(side="left", padx=4, ipady=3)
        boton(fila, "Crear", crear).pack(side="left", padx=4)
        columnas = [("id", "ID", 45), ("name", "Nombre", 170), ("url", "URL", 170), ("articulos", "Artículos", 75)]
        marco, tree = tabla(panel, columnas, 16)
        marco.pack(fill="both", expand=True)
        boton(panel, "Eliminar seleccionado", eliminar, ROJO).pack(anchor="e", pady=(8, 0))
        return e_nombre, e_url, tree

    def tags_cargar(self):
        llenar(self.tree_tags, db.tag_all(), ["id", "name", "url", "articulos"], "id")

    def categorias_cargar(self):
        llenar(self.tree_cats, db.categoria_all(), ["id", "name", "url", "articulos"], "id")

    def tag_crear(self):
        nuevo = db.tag_insert(self.tag_nombre.get(), self.tag_url.get())
        messagebox.showinfo("Creado", f"Tag creado correctamente.\nID: {nuevo}")
        self.tag_nombre.delete(0, "end")
        self.tag_url.delete(0, "end")
        self.tags_cargar()

    def categoria_crear(self):
        nuevo = db.categoria_insert(self.cat_nombre.get(), self.cat_url.get())
        messagebox.showinfo("Creado", f"Categoría creada correctamente.\nID: {nuevo}")
        self.cat_nombre.delete(0, "end")
        self.cat_url.delete(0, "end")
        self.categorias_cargar()

    def tag_eliminar(self):
        tag_id = seleccionado(self.tree_tags)
        if tag_id is None:
            raise ValueError("Selecciona un tag de la tabla.")
        valores = self.tree_tags.item(str(tag_id), "values")
        if messagebox.askyesno("Confirmar", f"¿Eliminar el tag '{valores[1]}'?\n"
                                            f"Se quitará de {valores[3]} artículo(s); los artículos NO se borran."):
            db.tag_delete(tag_id)
            self.tags_cargar()

    def categoria_eliminar(self):
        category_id = seleccionado(self.tree_cats)
        if category_id is None:
            raise ValueError("Selecciona una categoría de la tabla.")
        valores = self.tree_cats.item(str(category_id), "values")
        if messagebox.askyesno("Confirmar", f"¿Eliminar la categoría '{valores[1]}'?\n"
                                            f"Se quitará de {valores[3]} artículo(s); los artículos NO se borran."):
            db.categoria_delete(category_id)
            self.categorias_cargar()

    # ---------- Estadísticas con gráficos ----------
    def vista_estadisticas(self):
        self.preparar_vista("estadisticas")
        self.titulo("Estadísticas", "Gráficos calculados en vivo con consultas Cypher (COUNT) sobre el grafo.")
        fila = tk.Frame(self.contenido, bg=FONDO)
        fila.pack(fill="x", pady=(0, 10))
        etiqueta(fila, "Gráfico:", fondo=FONDO).pack(side="left")
        self.cb_grafico = ttk.Combobox(fila, state="readonly", width=38, values=GRAFICOS)
        self.cb_grafico.current(0)
        self.cb_grafico.pack(side="left", padx=6)
        self.cb_grafico.bind("<<ComboboxSelected>>", self.dibujar)
        boton(fila, "Actualizar", self.dibujar).pack(side="left", padx=6)

        panel = tarjeta(self.contenido)
        panel.pack(fill="both", expand=True)
        self.figura = Figure(figsize=(9, 5), dpi=100, facecolor="#fcfcfb", layout="constrained")
        self.lienzo = FigureCanvasTkAgg(self.figura, master=panel)
        self.lienzo.get_tk_widget().pack(fill="both", expand=True)
        self.dibujar()

    # Dibuja el gráfico elegido
    def dibujar(self, evento=None):
        eleccion = self.cb_grafico.get()
        if eleccion == GRAFICOS[0]:
            datos = db.stats_comentarios_por_articulo()
            eje = "Número de comentarios"
        elif eleccion == GRAFICOS[1]:
            datos = db.stats_comentarios_por_usuario()
            eje = "Número de comentarios"
        elif eleccion == GRAFICOS[2]:
            datos = db.stats_articulos_por_categoria()
            eje = "Número de artículos"
        else:
            datos = db.stats_articulos_por_tag()
            eje = "Número de artículos"

        nombres = []
        valores = []
        colores = []
        for d in datos:
            nombres.append(d["nombre"])
            valores.append(d["total"])
            if "rol" in d:
                colores.append(COLOR_ROL[d["rol"]])
            else:
                colores.append(COLOR_ROL["usuario"])

        self.figura.clear()
        ax = self.figura.add_subplot(111)
        ax.set_facecolor("#fcfcfb")
        barras = ax.barh(nombres, valores, height=0.5, color=colores, edgecolor="#fcfcfb", linewidth=2)
        ax.invert_yaxis()
        for i in range(len(barras)):
            barra = barras[i]
            ax.text(barra.get_width() + 0.05, barra.get_y() + barra.get_height() / 2, str(valores[i]),
                    va="center", fontsize=9, color="#52514e")
        if eleccion == GRAFICOS[1]:
            leyenda = [Patch(color=COLOR_ROL["admin"], label="Administrador"),
                       Patch(color=COLOR_ROL["usuario"], label="Usuario")]
            ax.legend(handles=leyenda, loc="lower right", frameon=False, fontsize=9)

        maximo = 1
        for v in valores:
            if v > maximo:
                maximo = v
        ax.set_xlim(0, maximo * 1.15)
        ax.set_title(eleccion, loc="left", fontsize=13, fontweight="bold", color="#0b0b0b", pad=12)
        ax.set_xlabel(eje, color="#52514e")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(axis="x", color="#e5e5e2", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_color("#c9c9c4")
        ax.tick_params(colors="#52514e", labelsize=9, length=0)
        self.lienzo.draw()


# Arranca la app
if __name__ == "__main__":
    App().mainloop()
