import datetime
import json
import os
import subprocess
import sys
import threading
import urllib.request
import webbrowser
import customtkinter as ctk
from PIL import Image

# --- Configuración de Versión y Servidor ---
VERSION_ACTUAL = "1.1"
URL_VERSION_SERVIDOR = "https://raw.githubusercontent.com/JoacoCav/TaboX-System/refs/heads/main/SCRCPY/version.json"
URL_GITHUB = "https://github.com/JoacoCav/"

# Configuración visual
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def obtener_ruta_recurso(nombre_relativo):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, nombre_relativo)
    directorio_base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directorio_base, nombre_relativo)


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


def ejecutar_script_python(nombre_script):
    """Ejecuta un archivo .py externo utilizando el mismo intérprete de Python."""
    ruta_script = obtener_ruta_recurso(nombre_script)
    if os.path.exists(ruta_script):
        subprocess.Popen([sys.executable, ruta_script])
    else:
        print(f"[ERROR]: No se encontró el archivo: {ruta_script}")


def iniciar_scrcpy():
    global proceso_actual

    # Ventana principal
    app = ctk.CTk()
    app.title(f"TaboX System - SCRCPY (Beta v{VERSION_ACTUAL})")
    app.geometry("1000x600")
    app.resizable(True, True)

    # --- FORZAR VENTANA EN PRIMER PLANO AL INICIAR ---
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

    ruta_splash = obtener_ruta_recurso("icons/TaboX-System-NB.png")
    if not os.path.exists(ruta_splash):
        ruta_splash = obtener_ruta_recurso("icons/TaboX-System.png")

    if os.path.exists(ruta_splash):
        img_splash_pil = Image.open(ruta_splash)
        img_splash_ctk = ctk.CTkImage(
            light_image=img_splash_pil,
            dark_image=img_splash_pil,
            size=(650, 250),
        )
        label_splash_img = ctk.CTkLabel(
            frame_splash, image=img_splash_ctk, text=""
        )
        label_splash_img.pack(pady=(60, 10))
    else:
        label_splash_img = ctk.CTkLabel(
            frame_splash,
            text="TaboX System - SCRCPY",
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
        label_estado_loading.configure(
            text="Conectando con el Servidor..."
        )
        progress_bar.pack(pady=10)
        progress_bar.start()
        app.after(5000, transicion_al_menu)

    def transicion_al_menu():
        progress_bar.stop()
        frame_splash.destroy()
        construir_interfaz_principal()

    app.after(1000, iniciar_animacion_cargando)

    # ==========================================
    # --- INTERFAZ PRINCIPAL (MENU & TERMINAL) -
    # ==========================================

    def mostrar_bienvenida_dinamica():
        ahora = datetime.datetime.now()
        fecha_formateada = ahora.strftime("%d/%m/%Y - %H:%M:%S")

        mensaje = (
            f"==================================================\n"
            f"  Bienvenido/a a TaboX System -SCRCPY (v{VERSION_ACTUAL})\n"
            f"  Sesión iniciada: {fecha_formateada}\n"
            f"==================================================\n"
            f"> Consola lista. Selecciona una opción del panel.\n\n"
        )
        escribir_en_consola(mensaje)

    def construir_interfaz_principal():
        nonlocal texto_consola, entry_comando

        frame_izq = ctk.CTkFrame(app, width=350)
        frame_izq.pack(side="left", fill="y", padx=10, pady=10)

        label_titulo = ctk.CTkLabel(
            frame_izq,
            text="Panel de Control",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        label_titulo.pack(pady=(15, 10))

        frame_der = ctk.CTkFrame(app)
        frame_der.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        frame_cabecera_consola = ctk.CTkFrame(frame_der, fg_color="transparent")
        frame_cabecera_consola.pack(fill="x", padx=10, pady=(10, 5))

        label_consola = ctk.CTkLabel(
            frame_cabecera_consola,
            text="Terminal de Comandos:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        label_consola.pack(side="left")

        frame_estado_conexion = ctk.CTkFrame(
            frame_cabecera_consola, fg_color="transparent"
        )
        frame_estado_conexion.pack(side="right")

        label_circulo_verde = ctk.CTkLabel(
            frame_estado_conexion,
            text="●",
            text_color="#00E676",
            font=ctk.CTkFont(size=16),
        )
        label_circulo_verde.pack(side="left", padx=(0, 4))

        label_texto_conexion = ctk.CTkLabel(
            frame_estado_conexion,
            text="Conectado al servidor",
            text_color="#A0A0A0",
            font=ctk.CTkFont(size=11),
        )
        label_texto_conexion.pack(side="left")

        texto_consola = ctk.CTkTextbox(
            frame_der,
            width=320,
            fg_color="#1e1e1e",
            text_color="#ffffff",
            font=("Consolas", 11),
        )
        texto_consola.pack(padx=10, pady=(5, 0), fill="both", expand=True)

        def animar_punto_verde(visible=True):
            color = "#00E676" if visible else "#005522"
            label_circulo_verde.configure(text_color=color)
            app.after(800, lambda: animar_punto_verde(not visible))

        animar_punto_verde()
        mostrar_bienvenida_dinamica()

        frame_entrada = ctk.CTkFrame(frame_der, fg_color="transparent")
        frame_entrada.pack(fill="x", padx=10, pady=10)

        entry_comando = ctk.CTkEntry(
            frame_entrada,
            placeholder_text="Escribe aquí y presiona Enter...",
            font=("Consolas", 11),
        )
        entry_comando.pack(side="left", fill="x", expand=True, padx=(0, 5))
        entry_comando.bind("<Return>", enviar_comando_al_proceso)

        btn_enviar = ctk.CTkButton(
            frame_entrada,
            text="Enviar",
            width=70,
            command=enviar_comando_al_proceso,
        )
        btn_enviar.pack(side="right")

        frame_scroll_botones = ctk.CTkScrollableFrame(
            frame_izq, width=220, height=250, fg_color="transparent"
        )
        frame_scroll_botones.pack(pady=5, padx=5, fill="both", expand=True)

        icon_usb = cargar_icono("usb.logo.png")
        icon_wifi = cargar_icono("wifi.logo.png")
        icon_camera = cargar_icono("camera.logo.png")
        icon_restart = cargar_icono("salir.logo.png")
        icon_help = cargar_icono("help.logo.png")
        icon_tutorial = cargar_icono("help.logo.png")
        icon_update = cargar_icono("salir.logo.png")
        icon_exit = cargar_icono("salir.logo.png")

        btn_scrcpy = ctk.CTkButton(
            frame_scroll_botones,
            text=" SCRCPY - USB",
            image=icon_usb,
            compound="left",
            command=ejecutar_scrcpy_usb,
            height=35,
        )
        btn_scrcpy.pack(pady=6, padx=10, fill="x")

        btn_item2 = ctk.CTkButton(
            frame_scroll_botones,
            text=" SCRCPY - WiFi (Beta)",
            image=icon_wifi,
            compound="left",
            command=ejecutar_scrcpy_wifi,
            height=35,
        )
        btn_item2.pack(pady=6, padx=10, fill="x")

        btn_item3 = ctk.CTkButton(
            frame_scroll_botones,
            text=" Camara Frontal (MIC - WiFi)",
            image=icon_camera,
            compound="left",
            command=ejecutar_cameraf,
            height=35,
        )
        btn_item3.pack(pady=6, padx=10, fill="x")

        btn_item4 = ctk.CTkButton(
            frame_scroll_botones,
            text=" Camara Trasera (MIC - WiFi)",
            image=icon_camera,
            compound="left",
            command=ejecutar_camerab,
            height=35,
        )
        btn_item4.pack(pady=6, padx=10, fill="x")

        btn_item5 = ctk.CTkButton(
            frame_scroll_botones,
            text=" Reinicio (Debug)",
            image=icon_restart,
            compound="left",
            command=ejecutar_scrcpy_reinicio,
            height=35,
        )
        btn_item5.pack(pady=6, padx=10, fill="x")

        btn_item6 = ctk.CTkButton(
            frame_scroll_botones,
            text=" Ayuda - CMMDS",
            image=icon_help,
            compound="left",
            command=lambda: abrir_ventana_ayuda(app),
            height=35,
        )
        btn_item6.pack(pady=6, padx=10, fill="x")

        btn_item7 = ctk.CTkButton(
            frame_scroll_botones,
            text=" Tutorial (Android)",
            image=icon_tutorial,
            compound="left",
            command=lambda: abrir_ventana_tutorial(app),
            height=35,
        )
        btn_item7.pack(pady=6, padx=10, fill="x")

        btn_actualizar = ctk.CTkButton(
            frame_scroll_botones,
            text=" Buscar Actualización",
            image=icon_update,
            compound="left",
            command=lambda: comprobar_actualizacion_remota(
                app, escribir_en_consola
            ),
            height=35,
            fg_color="#1F6AA5",
            hover_color="#144870",
        )
        btn_actualizar.pack(pady=6, padx=10, fill="x")

        btn_salir = ctk.CTkButton(
            frame_izq,
            text=" Salir",
            image=icon_exit,
            compound="left",
            command=lambda: (ejecutar_script_python("main.py"), app.quit()),
            fg_color="#D32F2F",
            hover_color="#9A0007",
            height=35,
        )
        btn_salir.pack(side="bottom", pady=10, padx=15, fill="x")

        app.after(
            2000,
            lambda: comprobar_actualizacion_remota(app, escribir_en_consola),
        )

    # Variables de control
    texto_consola = None
    entry_comando = None

    def escribir_en_consola(texto, es_comando=False):
        if texto_consola is None:
            return
        texto_consola.configure(state="normal")
        if es_comando:
            texto_consola.insert("end", texto, "comando_usuario")
        else:
            texto_consola.insert("end", texto)
        texto_consola.see("end")
        texto_consola.configure(state="disabled")

    def enviar_comando_al_proceso(event=None):
        global proceso_actual
        if entry_comando is None:
            return
        comando = entry_comando.get()
        entry_comando.delete(0, "end")

        escribir_en_consola(f"> {comando}\n", es_comando=True)

        if proceso_actual and proceso_actual.poll() is None:
            try:
                proceso_actual.stdin.write(comando + "\n")
                proceso_actual.stdin.flush()
            except Exception as e:
                escribir_en_consola(f"[Error de entrada]: {e}\n")

    def ejecutar_proceso_interactivo(comando_o_lista, directorio_trabajo=None):
        def correr_proceso():
            global proceso_actual
            try:
                env = os.environ.copy()
                env["PYTHONUNBUFFERED"] = "1"

                proceso_actual = subprocess.Popen(
                    comando_o_lista,
                    cwd=directorio_trabajo,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=0,
                    env=env,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )

                while True:
                    char = proceso_actual.stdout.read(1)
                    if not char and proceso_actual.poll() is not None:
                        break
                    if char:
                        escribir_en_consola(char)

                proceso_actual.wait()
                escribir_en_consola("\n> Proceso finalizado.\n\n")
            except Exception as e:
                escribir_en_consola(f"\n[Error de ejecución]: {e}\n\n")

        hilo = threading.Thread(target=correr_proceso)
        hilo.daemon = True
        hilo.start()

    def ejecutar_scrcpy_usb():
        ruta_scrcpy = obtener_ruta_recurso(
            os.path.join("SCRCPY", "scrcpy-win64-V4.1", "USB.bat")
        )
        carpeta_scrcpy = os.path.dirname(ruta_scrcpy)
        if not os.path.exists(ruta_scrcpy):
            escribir_en_consola(
                f"[Error]: No se encontró scrcpy en {ruta_scrcpy}\n"
            )
            return
        escribir_en_consola("> Iniciando SCRCPY (USB)...\n")
        ejecutar_proceso_interactivo(
            ["cmd.exe", "/k", "USB.bat"], carpeta_scrcpy
        )

    def ejecutar_scrcpy_wifi():
        ruta_bat = obtener_ruta_recurso(
            os.path.join("SCRCPY", "scrcpy-win64-V4.1", "AutoADB.bat")
        )
        carpeta_scrcpy = os.path.dirname(ruta_bat)
        if not os.path.exists(ruta_bat):
            escribir_en_consola(
                f"[Error]: No se encontró el script en {ruta_bat}\n"
            )
            return
        escribir_en_consola("> Iniciando SCRCPY (WiFi)...\n")
        ejecutar_proceso_interactivo(
            ["cmd.exe", "/k", "AutoADB.bat"], carpeta_scrcpy
        )

    def ejecutar_cameraf():
        ruta_bat = obtener_ruta_recurso(
            os.path.join("SCRCPY", "scrcpy-win64-V4.1", "AutoCameraF.bat")
        )
        carpeta_scrcpy = os.path.dirname(ruta_bat)
        if not os.path.exists(ruta_bat):
            escribir_en_consola(
                f"[Error]: No se encontró el script en {ruta_bat}\n"
            )
            return
        escribir_en_consola("> Iniciando CAMARA FRONTAL...\n")
        ejecutar_proceso_interactivo(
            ["cmd.exe", "/k", "AutoCameraF.bat"], carpeta_scrcpy
        )

    def ejecutar_camerab():
        ruta_bat = obtener_ruta_recurso(
            os.path.join("SCRCPY", "scrcpy-win64-V4.1", "AutoCameraB.bat")
        )
        carpeta_scrcpy = os.path.dirname(ruta_bat)
        if not os.path.exists(ruta_bat):
            escribir_en_consola(
                f"[Error]: No se encontró el script en {ruta_bat}\n"
            )
            return
        escribir_en_consola("> Iniciando CAMARA TRASERA...\n")
        ejecutar_proceso_interactivo(
            ["cmd.exe", "/k", "AutoCameraB.bat"], carpeta_scrcpy
        )

    def ejecutar_scrcpy_reinicio():
        ruta_bat = obtener_ruta_recurso(
            os.path.join("SCRCPY", "scrcpy-win64-V4.1", "restart.bat")
        )
        carpeta_scrcpy = os.path.dirname(ruta_bat)
        if not os.path.exists(ruta_bat):
            escribir_en_consola(
                f"[Error]: No se encontró el script en {ruta_bat}\n"
            )
            return
        escribir_en_consola("> Iniciando SCRCPY REINICIO...\n")
        ejecutar_proceso_interactivo(
            ["cmd.exe", "/k", "restart.bat"], carpeta_scrcpy
        )

    app.mainloop()


# --- FUNCIONES AUXILIARES FUERA DE LA VENTANA PRINCIPAL ---

proceso_actual = None


def parse_version(v_str):
    try:
        return tuple(map(int, str(v_str).strip().split(".")))
    except ValueError:
        return (0,)


def comprobar_actualizacion_remota(app_parent, callback_consola=None):
    def revisar():
        if callback_consola:
            callback_consola("> Buscando actualizaciones en el servidor...\n")
        try:
            req = urllib.request.Request(
                URL_VERSION_SERVIDOR, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                version_servidor_raw = str(
                    data.get("version", VERSION_ACTUAL)
                ).strip()
                url_descarga = data.get("url_download", "").strip()
                notas = data.get("notas_cambios", "Sin notas disponibles.")

                v_servidor = parse_version(version_servidor_raw)
                v_actual = parse_version(VERSION_ACTUAL)

                if v_servidor > v_actual:
                    if callback_consola:
                        callback_consola(
                            f"\n[SISTEMA]: ¡Nueva versión {version_servidor_raw} disponible!\n"
                        )
                    notificar_actualizacion_gui(
                        app_parent, version_servidor_raw, url_descarga, notas
                    )
                else:
                    if callback_consola:
                        callback_consola(
                            f"> El sistema está actualizado (v{VERSION_ACTUAL}).\n\n"
                        )
        except Exception as e:
            if callback_consola:
                callback_consola(
                    f"[Error de conexión con el servidor]: {e}\n\n"
                )

    hilo = threading.Thread(target=revisar)
    hilo.daemon = True
    hilo.start()


def notificar_actualizacion_gui(
    app_parent, version_nueva, url_descarga, notas
):
    def aceptar_actualizacion():
        ventana_upd.destroy()
        descargar_e_instalar_actualizacion(app_parent, url_descarga)

    ventana_upd = ctk.CTkToplevel(app_parent)
    ventana_upd.title("Actualización disponible")
    ventana_upd.geometry("420x240")
    ventana_upd.resizable(False, False)
    ventana_upd.lift()
    ventana_upd.attributes("-topmost", True)

    lbl_info = ctk.CTkLabel(
        ventana_upd,
        text=f"¡Nueva versión {version_nueva} encontrada!",
        font=ctk.CTkFont(size=16, weight="bold"),
    )
    lbl_info.pack(pady=(20, 5))

    lbl_notas = ctk.CTkLabel(
        ventana_upd,
        text=f"Novedades:\n{notas}",
        font=ctk.CTkFont(size=12),
        wraplength=380,
    )
    lbl_notas.pack(pady=10)

    btn_descargar = ctk.CTkButton(
        ventana_upd,
        text="Descargar e Instalar",
        command=aceptar_actualizacion,
        fg_color="#00E5FF",
        text_color="#000000",
        hover_color="#00B4D8",
        font=ctk.CTkFont(weight="bold"),
    )
    btn_descargar.pack(pady=15)


def descargar_e_instalar_actualizacion(app_parent, url_descarga):
    def proceso_descarga():
        try:
            ruta_exe_actual = sys.executable
            directorio = os.path.dirname(ruta_exe_actual)
            ruta_nuevo_exe = os.path.join(directorio, "TaboX_System_New.exe")
            ruta_script_updater = os.path.join(
                directorio, "update_installer.bat"
            )

            urllib.request.urlretrieve(url_descarga, ruta_nuevo_exe)

            script_bat_contenido = f"""@echo off
timeout /t 2 /nobreak > nul
del "{ruta_exe_actual}"
move "{ruta_nuevo_exe}" "{ruta_exe_actual}"
start "" "{ruta_exe_actual}"
del "%~f0"
"""
            with open(ruta_script_updater, "w") as f:
                f.write(script_bat_contenido)

            subprocess.Popen(
                ["cmd.exe", "/c", ruta_script_updater],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            app_parent.quit()
        except Exception as e:
            print(f"Error en descarga: {e}")

    hilo = threading.Thread(target=proceso_descarga)
    hilo.daemon = True
    hilo.start()


def abrir_ventana_ayuda(app_parent):
    ventana_ayuda = ctk.CTkToplevel(app_parent)
    ventana_ayuda.title("Ayuda - Comandos SCRCPY")
    ventana_ayuda.geometry("550x615")
    ventana_ayuda.resizable(False, False)
    ventana_ayuda.lift()
    ventana_ayuda.attributes("-topmost", True)

    label_ayuda_titulo = ctk.CTkLabel(
        ventana_ayuda,
        text="Atajos y Comandos de SCRCPY",
        font=ctk.CTkFont(size=16, weight="bold"),
    )
    label_ayuda_titulo.pack(pady=(15, 10))

    caja_texto_ayuda = ctk.CTkTextbox(
        ventana_ayuda, width=550, height=500, font=("Consolas", 15)
    )
    caja_texto_ayuda.pack(padx=15, pady=5)

    contenido_ayuda = (
        "ATAJOS TECLADO SCRCPY:\n"
        "----------------------------------------------\n"
        "MOD + f           : Pantalla completa\n"
        "MOD + g           : Ajustar tamaño 1:1\n"
        "MOD + x / MOD + w : Redimensionar ventana\n"
        "MOD + h / inicio  : Botón Inicio (Home)\n"
        "MOD + b           : Botón Atrás (Back)\n"
        "MOD + s           : Aplicaciones recientes\n"
        "MOD + m           : Menú de opciones\n"
        "MOD + p           : Encender/Apagar pantalla\n"
        "MOD + o           : Apagar pantalla del celular\n"
        "MOD + Shift + o   : Encender pantalla del celular\n"
        "MOD + r           : Rotar pantalla\n"
        "MOD + n           : Abrir panel de notificaciones\n"
        "MOD + c           : Copiar portapapeles del dispositivo\n"
        "MOD + v           : Pegar portapapeles en el celular\n\n"
        "* Nota: 'MOD' equivale a la tecla Alt Izquierda por defecto.\n"
        "----------------------------------------------\n\n"
        "TaboX Systems - SCRCPY (Beta v1.1)\n\n"
        "¡Si tienes un problema, Recuerda informarlo en GitHub!\n"
        "--> https://github.com/JoacoCav/TaboX-System/issues <--\n"
        "----------------------------------------------\n"
    )

    caja_texto_ayuda.insert("1.0", contenido_ayuda)
    caja_texto_ayuda.configure(state="disabled")

    btn_cerrar = ctk.CTkButton(
        ventana_ayuda,
        text="Cerrar",
        command=ventana_ayuda.destroy,
        width=100,
    )
    btn_cerrar.pack(pady=10)


def abrir_ventana_tutorial(app_parent):
    ventana_tutorial = ctk.CTkToplevel(app_parent)
    ventana_tutorial.title("Tutorial - Android")
    ventana_tutorial.geometry("550x615")
    ventana_tutorial.resizable(False, False)
    ventana_tutorial.lift()
    ventana_tutorial.attributes("-topmost", True)

    label_tutorial_titulo = ctk.CTkLabel(
        ventana_tutorial,
        text="Atajos y Comandos de SCRCPY",
        font=ctk.CTkFont(size=16, weight="bold"),
    )
    label_tutorial_titulo.pack(pady=(15, 10))

    caja_texto_tutorial = ctk.CTkTextbox(
        ventana_tutorial, width=550, height=500, font=("Consolas", 15)
    )
    caja_texto_tutorial.pack(padx=15, pady=5)

    contenido_tutorial = (
        "Tutorial Para Android:\n"
        "----------------------------------------------\n"
        "SCRCPY USB\n"
        "1. Activar opciones de Desarrollador\n"
        "2. Habilitar depuración por USB\n"
        "3. Otorgar permisos necesarios\n"
        "4. Conectar dispositivo al PC (Para USB)\n\n"
        "----------------------------------------------\n"
        "SCRCPY WiFi\n\n"
        "1. Activar opciones de Desarrollador\n"
        "2. Conectar el PC y el Dispositivo al mismo WiFi\n"
        "3. Habilitar depuración por WiFi\n"
        "4. Copiar la dirección IP del Dispositivo\n"
        "5. Al Usar por Wifi poner la IP copiada\n"
        "6. El dispositivo debe estar encendido al conectar\n"
        "----------------------------------------------\n\n"
        "TaboX Systems - SCRCPY (Beta v1.1)\n\n"
        "¡Si tienes un problema, Recuerda informarlo en GitHub!\n"
        "--> https://github.com/JoacoCav/TaboX-System/issues <--\n"
        "----------------------------------------------\n"
    )

    caja_texto_tutorial.insert("1.0", contenido_tutorial)
    caja_texto_tutorial.configure(state="disabled")

    btn_cerrar = ctk.CTkButton(
        ventana_tutorial,
        text="Cerrar",
        command=ventana_tutorial.destroy,
        width=100,
    )
    btn_cerrar.pack(pady=10)


if __name__ == "__main__":
    iniciar_scrcpy()
