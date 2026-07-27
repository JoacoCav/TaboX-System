import os
import subprocess
import sys
import webbrowser
import customtkinter as ctk
from PIL import Image

# --- IMPORTACIÓN DIRECTA DE SCRCPY ---
import scrcpy  # Importamos scrcpy.py que está en el mismo directorio

# --- Configuración Visual ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

VERSION_ACTUAL = "1.1"
URL_GITHUB = "https://github.com/JoacoCav/"


def obtener_ruta_recurso(nombre_relativo):
    """Obtiene la ruta absoluta del archivo (funciona en desarrollo y con PyInstaller)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, nombre_relativo)
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directorio_base, nombre_relativo)


# ==========================================
# --- FUNCIÓN CORREGIDA PARA ABRIR SCRCPY --
# ==========================================
def abrir_scrcpy_modulo():
    """Destruye el launcher y arranca el módulo SCRCPY importado directamente."""
    app.destroy()  # Cierra la ventana principal de manera limpia
    scrcpy.iniciar_scrcpy()  # Inicia el módulo de SCRCPY sin usar subprocess


def cargar_icono(nombre_archivo, tamano=(30, 30)):
    ruta = obtener_ruta_recurso(os.path.join("icons", nombre_archivo))
    if os.path.exists(ruta):
        img_pil = Image.open(ruta)
        return ctk.CTkImage(
            light_image=img_pil, dark_image=img_pil, size=tamano
        )
    return None


def agregar_hover_animado(boton, incremento=6):
    ancho_original = boton.cget("width")
    alto_original = boton.cget("height")

    def al_entrar(e):
        boton.configure(
            width=ancho_original + incremento,
            height=alto_original + (incremento // 2),
        )

    def al_salir(e):
        boton.configure(width=ancho_original, height=alto_original)

    boton.bind("<Enter>", al_entrar)
    boton.bind("<Leave>", al_salir)


# Ventana principal
app = ctk.CTk()
app.title(f"TaboX System - Main Launcher (v{VERSION_ACTUAL})")
app.geometry("1000x600")
app.resizable(True, True)

# Forzar ventana al frente al iniciar
app.deiconify()
app.lift()
app.focus_force()
app.attributes("-topmost", True)
app.after(100, lambda: app.attributes("-topmost", False))

# ==========================================
# --- PANTALLA DE INICIO (SPLASH SCREEN) ---
# ==========================================
frame_splash = ctk.CTkFrame(app, fg_color="#121212")
frame_splash.pack(fill="both", expand=True)
app.after(0, lambda: app.wm_state("zoomed"))

# Imagen Splash
ruta_splash = obtener_ruta_recurso("icons/TaboX-System-NB.png")
if not os.path.exists(ruta_splash):
    ruta_splash = obtener_ruta_recurso("icons/TaboX-System.png")

if os.path.exists(ruta_splash):
    img_splash_pil = Image.open(ruta_splash)
    img_splash_ctk = ctk.CTkImage(
        light_image=img_splash_pil, dark_image=img_splash_pil, size=(650, 250)
    )
    label_splash_img = ctk.CTkLabel(frame_splash, image=img_splash_ctk, text="")
    label_splash_img.pack(pady=(60, 10))
else:
    label_splash_img = ctk.CTkLabel(
        frame_splash,
        text="TaboX System",
        font=ctk.CTkFont(size=28, weight="bold"),
    )
    label_splash_img.pack(pady=(100, 10))

label_estado_loading = ctk.CTkLabel(
    frame_splash, text="", font=ctk.CTkFont(size=15, weight="normal")
)
label_estado_loading.pack(pady=5)

progress_bar = ctk.CTkProgressBar(
    frame_splash, width=320, mode="indeterminate", progress_color="#00E5FF"
)

# Créditos
frame_creditos = ctk.CTkFrame(frame_splash, fg_color="transparent")
frame_creditos.pack(side="bottom", pady=20)

img_github_ctk = cargar_icono("github.webp", tamano=(25, 25))
img_android_ctk = cargar_icono("android1.webp", tamano=(25, 16))

lbl_creditos = ctk.CTkLabel(
    frame_creditos,
    text=" Created with Android, made by Joaquin Cavallo",
    image=img_android_ctk,
    compound="left",
    font=ctk.CTkFont(size=12, weight="normal"),
    text_color="#888888",
)
lbl_creditos.pack(pady=(0, 5))

btn_github_splash = ctk.CTkButton(
    frame_creditos,
    text=" Perfil de GitHub",
    image=img_github_ctk,
    compound="left",
    command=lambda: webbrowser.open(URL_GITHUB),
    width=150,
    height=28,
    fg_color="#24292e",
    hover_color="#333333",
    font=ctk.CTkFont(size=11, weight="normal"),
)
btn_github_splash.pack()
agregar_hover_animado(btn_github_splash, incremento=6)


def iniciar_animacion_cargando():
    label_estado_loading.configure(text="Cargando Módulos del Sistema...")
    progress_bar.pack(pady=10)
    progress_bar.start()
    app.after(2500, transicion_al_menu_seleccion)


def transicion_al_menu_seleccion():
    progress_bar.stop()
    frame_splash.destroy()
    construir_menu_seleccion_software()


app.after(1000, iniciar_animacion_cargando)


# ========================================================
# --- MENÚ DE SELECCIÓN DE SOFTWARE / LAUNCHER ---
# ========================================================
def construir_menu_seleccion_software():
    frame_menu = ctk.CTkFrame(app, fg_color="#121212")
    frame_menu.pack(fill="both", expand=True)

    # Encabezado
    if os.path.exists(ruta_splash):
        img_menu_pil = Image.open(ruta_splash)
        img_menu_ctk = ctk.CTkImage(
            light_image=img_menu_pil, dark_image=img_menu_pil, size=(450, 170)
        )
        lbl_top = ctk.CTkLabel(frame_menu, image=img_menu_ctk, text="")
        lbl_top.pack(pady=(30, 10))

    lbl_subtitulo = ctk.CTkLabel(
        frame_menu,
        text="Selecciona el software o módulo a ejecutar:",
        font=ctk.CTkFont(size=15, weight="normal"),
        text_color="#AAAAAA",
    )
    lbl_subtitulo.pack(pady=(0, 25))

    # Grid de Tarjetas
    frame_cards = ctk.CTkFrame(frame_menu, fg_color="transparent")
    frame_cards.pack(pady=10)

    # --- TARJETA 1: SISTEMA SCRCPY ---
    card1 = ctk.CTkFrame(
        frame_cards,
        fg_color="#1E1E1E",
        corner_radius=12,
        width=260,
        height=180,
    )
    card1.pack_propagate(False)
    card1.grid(row=0, column=0, padx=15, pady=10)

    lbl_c1_title = ctk.CTkLabel(
        card1,
        text="SCRCPY",
        font=ctk.CTkFont(size=16, weight="bold"),
        image=img_android_ctk,
        compound="left",
    )
    lbl_c1_title.pack(pady=(20, 5))

    lbl_c1_desc = ctk.CTkLabel(
        card1,
        text="Abre el panel de control para\ntransmitir y gestionar Android.",
        font=ctk.CTkFont(size=11),
        text_color="#888888",
    )
    lbl_c1_desc.pack(pady=5)

    btn_lanzar_scrcpy = ctk.CTkButton(
        card1,
        text="Abrir SCRCPY",
        fg_color="#00E5FF",
        text_color="#000000",
        hover_color="#00B4D8",
        font=ctk.CTkFont(weight="bold"),
        command=abrir_scrcpy_modulo,  # Llama a abrir_scrcpy_modulo
    )
    btn_lanzar_scrcpy.pack(side="bottom", pady=15)
    agregar_hover_animado(btn_lanzar_scrcpy)

    # --- TARJETA 2: EdeX-UI ---
    card2 = ctk.CTkFrame(
        frame_cards,
        fg_color="#1E1E1E",
        corner_radius=12,
        width=260,
        height=180,
    )
    card2.pack_propagate(False)
    card2.grid(row=0, column=1, padx=15, pady=10)

    lbl_c2_title = ctk.CTkLabel(
        card2, text="EdeX-UI", font=ctk.CTkFont(size=16, weight="bold")
    )
    lbl_c2_title.pack(pady=(20, 5))

    lbl_c2_desc = ctk.CTkLabel(
        card2,
        text="Consola Interactiva\nindependiente de Python.",
        font=ctk.CTkFont(size=11),
        text_color="#888888",
    )
    lbl_c2_desc.pack(pady=5)

    btn_lanzar_m2 = ctk.CTkButton(
        card2,
        text="Abrir EdeX-UI",
        fg_color="#00E5FF",
        text_color="#000000",
        hover_color="#00B4D8",
        font=ctk.CTkFont(weight="bold"),
    )
    btn_lanzar_m2.pack(side="bottom", pady=15)
    agregar_hover_animado(btn_lanzar_m2)

    # --- TARJETA 3: PANEL ADMIN ---
    card3 = ctk.CTkFrame(
        frame_cards,
        fg_color="#1E1E1E",
        corner_radius=12,
        width=260,
        height=180,
    )
    card3.pack_propagate(False)
    card3.grid(row=0, column=2, padx=15, pady=10)

    lbl_c3_title = ctk.CTkLabel(
        card3,
        text="Panel Admin",
        font=ctk.CTkFont(size=16, weight="bold"),
        compound="left",
    )
    lbl_c3_title.pack(pady=(20, 5))

    lbl_c3_desc = ctk.CTkLabel(
        card3,
        text="Abre el panel de control administrativo\npara modificar el sistema.",
        font=ctk.CTkFont(size=11),
        text_color="#888888",
    )
    lbl_c3_desc.pack(pady=5)

    btn_lanzar_admin = ctk.CTkButton(
        card3,
        text="Abrir Admin",
        fg_color="#00E5FF",
        text_color="#000000",
        hover_color="#00B4D8",
        font=ctk.CTkFont(weight="bold"),
    )
    btn_lanzar_admin.pack(side="bottom", pady=15)
    agregar_hover_animado(btn_lanzar_admin)

    # --- TARJETA 4: INFO Y FAQ ---
    card4 = ctk.CTkFrame(
        frame_cards,
        fg_color="#1E1E1E",
        corner_radius=12,
        width=260,
        height=180,
    )
    card4.pack_propagate(False)
    card4.grid(row=1, column=1, padx=15, pady=10)

    lbl_c4_title = ctk.CTkLabel(
        card4,
        text="Info y FAQ",
        font=ctk.CTkFont(size=16, weight="bold"),
        compound="left",
    )
    lbl_c4_title.pack(pady=(20, 5))

    lbl_c4_desc = ctk.CTkLabel(
        card4,
        text="Información sobre TaboX System y FAQ\nEnlaces a redes y repositorios.",
        font=ctk.CTkFont(size=11),
        text_color="#888888",
    )
    lbl_c4_desc.pack(pady=5)

    btn_lanzar_info = ctk.CTkButton(
        card4,
        text="Abrir Info y FAQ",
        fg_color="#00E5FF",
        text_color="#000000",
        hover_color="#00B4D8",
        font=ctk.CTkFont(weight="bold"),
    )
    btn_lanzar_info.pack(side="bottom", pady=15)
    agregar_hover_animado(btn_lanzar_info)

    # --- TARJETA 5: REPORTES ---
    card5 = ctk.CTkFrame(
        frame_cards,
        fg_color="#1E1E1E",
        corner_radius=12,
        width=260,
        height=180,
    )
    card5.pack_propagate(False)
    card5.grid(row=1, column=0, padx=15, pady=10)

    lbl_c5_title = ctk.CTkLabel(
        card5,
        text="Reportes",
        font=ctk.CTkFont(size=16, weight="bold"),
        compound="left",
    )
    lbl_c5_title.pack(pady=(20, 5))

    lbl_c5_desc = ctk.CTkLabel(
        card5,
        text="Informes, Reporte de Bugs y\nEnlaces a redes y repositorios\nde ayuda.",
        font=ctk.CTkFont(size=11),
        text_color="#888888",
    )
    lbl_c5_desc.pack(pady=5)

    btn_lanzar_reportes = ctk.CTkButton(
        card5,
        text="Abrir Reportes",
        fg_color="#00E5FF",
        text_color="#000000",
        hover_color="#00B4D8",
        font=ctk.CTkFont(weight="bold"),
    )
    btn_lanzar_reportes.pack(side="bottom", pady=15)
    agregar_hover_animado(btn_lanzar_reportes)

    # --- TARJETA 6: GITHUB ---
    card6 = ctk.CTkFrame(
        frame_cards,
        fg_color="#1E1E1E",
        corner_radius=12,
        width=260,
        height=180,
    )
    card6.pack_propagate(False)
    card6.grid(row=1, column=2, padx=15, pady=10)

    lbl_c6_title = ctk.CTkLabel(
        card6,
        text="GitHub",
        font=ctk.CTkFont(size=16, weight="bold"),
        image=img_github_ctk,
        compound="left",
    )
    lbl_c6_title.pack(pady=(20, 5))

    lbl_c6_desc = ctk.CTkLabel(
        card6,
        text="Repositorio Principal con\nArchivos, releases y otras\ndependencias.",
        font=ctk.CTkFont(size=11),
        text_color="#888888",
    )
    lbl_c6_desc.pack(pady=5)

    btn_lanzar_github = ctk.CTkButton(
        card6,
        text="Abrir GitHub",
        fg_color="#00E5FF",
        text_color="#000000",
        hover_color="#00B4D8",
        font=ctk.CTkFont(weight="bold"),
        command=lambda: webbrowser.open(
            "https://github.com/JoacoCav/TaboX-System"
        ),
    )
    btn_lanzar_github.pack(side="bottom", pady=15)
    agregar_hover_animado(btn_lanzar_github)

    # Salir
    btn_salir = ctk.CTkButton(
        frame_menu,
        text="Salir",
        fg_color="#D32F2F",
        hover_color="#9A0007",
        width=140,
        command=app.quit,
    )
    btn_salir.pack(side="bottom", pady=30)


app.mainloop()
