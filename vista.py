import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from controlador import Controlador


class Vista:
    def __init__(self, root, nombre_usuario):
        self.root = root
        self.nombre_usuario = nombre_usuario

        # Ventana principal
        self.root.title("Control del Ánimo")
        self.root.geometry("800x800")
        self.root.configure(bg="#DAD6F8")
        self.root.minsize(500, 600)

        # Controlador
        self.controlador = Controlador(self)

        # Variables
        self.animo_var = tk.IntVar(value=3)
        self.habitos_basicos = {
            "Agua": tk.BooleanVar(),
            "Ejercicio": tk.BooleanVar(),
            "Estudio": tk.BooleanVar()
        }
        self.habitos = {
            "Salud": tk.BooleanVar(),
            "Ejercicio": tk.BooleanVar(),
            "Comida": tk.BooleanVar(),
            "Sueño": tk.BooleanVar(),
            "Pasatiempo": tk.BooleanVar(),
            "Estudio": tk.BooleanVar(),
            "Amigos": tk.BooleanVar(),
            "Familia": tk.BooleanVar(),
        }

        # Estilos
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TButton",
                        background="#9E8BDA",
                        foreground="#2B272E",
                        padding=10,
                        font=("Helvetica", 14, "bold"))

        style.configure("Custom.TCheckbutton",
                        background="#EDE7FF",
                        foreground="#1E1E2A",
                        font=("Helvetica", 14))

        # === Canvas + Scrollbar principal ===
        self.canvas = tk.Canvas(self.root, bg=self.root["bg"], highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Frame principal dentro del canvas
        self.main_frame = tk.Frame(self.canvas, bg="#EDE7FF")
        self._frame_window = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        # Actualizar scrollregion cuando cambie el contenido o el tamaño
        self.main_frame.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._resize_frame)

        self.crear_interfaz()

        # Forzar actualización inicial para evitar tener que hacer scroll
        self.root.update_idletasks()
        self._update_scroll_region()

    # ==== Scroll helpers ====
    def _update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self._frame_window, width=self.canvas.winfo_width())

    def _resize_frame(self, event):
        self.canvas.itemconfig(self._frame_window, width=event.width)
        self._update_scroll_region()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ==== Interfaz ====
    def crear_interfaz(self):
        # Bienvenida
        tk.Label(self.main_frame, text=f"Hola, {self.nombre_usuario} 👋",
                 font=("Helvetica", 22, "bold"), fg="#1E1E2A", bg="#EDE7FF").pack(pady=15)

        tk.Label(self.main_frame, text="¿Cómo te sientes hoy?",
                 font=("Helvetica", 18), fg="#1E1E2A", bg="#EDE7FF").pack(pady=10)

        # Imagen + slider
        self.img_label = tk.Label(self.main_frame, bg="#EDE7FF")
        self.img_label.pack(pady=10)
        self.actualizar_imagen()

        escala = tk.Scale(self.main_frame, from_=1, to=5, orient="horizontal",
                          variable=self.animo_var, bg="#EDE7FF",
                          highlightthickness=0, troughcolor="#D0C7F0",
                          fg="#1E1E2A", font=("Helvetica", 14))
        escala.pack(pady=10)
        self.animo_var.trace("w", lambda *a: self.actualizar_imagen())

        # Hábitos cumplidos
        tk.Label(self.main_frame, text="Hábitos cumplidos hoy:",
                 font=("Helvetica", 18, "bold"), fg="#1E1E2A", bg="#EDE7FF").pack(pady=(20, 10))

        marco_basicos = tk.Frame(self.main_frame, bg="#EDE7FF")
        marco_basicos.pack(pady=5)
        for i, (h, var) in enumerate(self.habitos_basicos.items()):
            ttk.Checkbutton(marco_basicos, text=h, variable=var, style="Custom.TCheckbutton").grid(row=0, column=i, padx=10, pady=5)

        # Factores
        tk.Label(self.main_frame, text="¿Qué influye en tu estado?",
                 font=("Helvetica", 18, "bold"), fg="#1E1E2A", bg="#EDE7FF").pack(pady=(25, 10))

        marco_habitos = tk.Frame(self.main_frame, bg="#EDE7FF")
        marco_habitos.pack(pady=5)
        for i, (h, var) in enumerate(self.habitos.items()):
            row = i // 4
            col = i % 4
            ttk.Checkbutton(marco_habitos, text=h, variable=var, style="Custom.TCheckbutton").grid(row=row, column=col, padx=10, pady=8)

        # Notas
        tk.Label(self.main_frame, text="Notas",
                 font=("Helvetica", 18, "bold"), fg="#1E1E2A", bg="#EDE7FF").pack(pady=(25, 5))

        self.texto_nota = tk.Text(self.main_frame, height=6, width=40, wrap="word",
                                  bg="#C4BCE4", fg="#1E1E2A", insertbackground="black",
                                  relief="flat", font=("Helvetica", 14))
        self.texto_nota.pack()
        self.contador = tk.Label(self.main_frame, text="0/200", fg="#555555",
                                 bg="#EDE7FF", font=("Helvetica", 12))
        self.contador.pack()
        self.texto_nota.bind("<KeyRelease>", self.actualizar_contador)

        # Botones
        ttk.Button(self.main_frame, text="Guardar registro", command=self.guardar).pack(pady=15)
        ttk.Button(self.main_frame, text="Ver registros", command=self.ver_registros).pack(pady=10)

    # ==== Métodos ====
    def actualizar_imagen(self):
        nivel = self.animo_var.get()
        try:
            img = Image.open(f"images/animo{nivel}.png").resize((120, 120))
            self.img = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.img, text="")
        except (FileNotFoundError, OSError, tk.TclError):
            self.img_label.config(text=f"[animo{nivel}.png]", image="")

    def actualizar_contador(self, event=None):
        texto = self.texto_nota.get("1.0", "end-1c")
        if len(texto) > 200:
            self.texto_nota.delete("1.0+200c", "end")
        self.contador.config(text=f"{len(texto)}/200")

    def guardar(self):
        registro_usuario = self.nombre_usuario
        registro_animo = self.animo_var.get()
        registro_habitos_basicos = {h: v.get() for h, v in self.habitos_basicos.items()}
        registro_habitos_estado = {h: v.get() for h, v in self.habitos.items()}
        registro_nota = self.texto_nota.get("1.0", "end-1c").strip()

        self.controlador.guardar_registro(
            registro_usuario,
            registro_animo,
            registro_habitos_basicos,
            registro_habitos_estado,
            registro_nota
        )

        self.animo_var.set(3)
        for var in self.habitos_basicos.values():
            var.set(False)
        for var in self.habitos.values():
            var.set(False)
        self.texto_nota.delete("1.0", "end")
        self.contador.config(text="0/200")

    def confirmar_sobrescritura(self, registro_actual):
        from tkinter import messagebox
        fecha = registro_actual.get("fecha", "")
        animo = registro_actual.get("animo", "")
        nota = registro_actual.get("nota", "")
        mensaje = (
            f"Ya existe un registro para hoy ({fecha}).\n\n"
            f"Ánimo actual: {animo}\n"
            f"Nota: {nota or 'Sin nota'}\n\n"
            "¿Deseas sobrescribir este registro?"
        )
        return messagebox.askyesno("Confirmar sobrescritura", mensaje)

    def mostrar_mensaje(self, mensaje):
        from tkinter import messagebox
        messagebox.showinfo("Información", mensaje)


    def ver_registros(self):
        data = self.controlador.obtener_registros()

        if not data:
            messagebox.showinfo("Registros", "No hay registros guardados aún.")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Registros guardados")
        vw, vh = 400, 400
        ventana.transient(self.root)
        ventana.resizable(True, True)
        ventana.update_idletasks()
        ventana.minsize(400, 300)

        try:
            rx = self.root.winfo_rootx()
            ry = self.root.winfo_rooty()
            rw = self.root.winfo_width()
            rh = self.root.winfo_height()
            x = rx + max((rw - vw) // 2, 0)
            y = ry + max((rh - vh) // 2, 0)
        except Exception:
            sw = ventana.winfo_screenwidth()
            sh = ventana.winfo_screenheight()
            x = max((sw - vw) // 2, 0)
            y = max((sh - vh) // 2, 0)

        ventana.geometry(f"{vw}x{vh}+{x}+{y}")
        ventana.configure(bg=self.root["bg"])

        canvas = tk.Canvas(ventana, bg=self.root["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#EDE7FF")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        mini_imgs = []

        for r in reversed(data):
            fila = tk.Frame(scroll_frame, bg="#EDE7FF")
            fila.pack(fill="x", pady=6, padx=6)

            nivel = r.get("animo", 3) or 3
            try:
                img = Image.open(f"images/animo{nivel}.png").resize((48, 48))
                photo = ImageTk.PhotoImage(img)
                mini_imgs.append(photo)
                lbl_img = tk.Label(fila, image=photo, bg="#EDE7FF")
            except (FileNotFoundError, OSError, tk.TclError):
                lbl_img = tk.Label(fila, text=f"[{nivel}]", width=6, bg="#EDE7FF", fg="#1E1E2A")
            lbl_img.pack(side="left", padx=(0, 12))

            contenido = tk.Frame(fila, bg="#EDE7FF")
            contenido.pack(side="left", fill="x", expand=True)

            tk.Label(contenido, text=f"{r.get('fecha', '')} - {r.get('usuario', '')}",
                     fg="#1E1E2A", bg="#EDE7FF", font=("Helvetica", 14, "bold")).pack(anchor="w")
            tk.Label(contenido, text=f"Ánimo: {r.get('animo', '')}",
                     fg="#1E1E2A", bg="#EDE7FF", font=("Helvetica", 13)).pack(anchor="w")

            basicos = [h for h, v in r.get('habitos_basicos', {}).items() if v]
            estado = [h for h, v in r.get('habitos_estado', {}).items() if v]
            tk.Label(contenido,
                     text=("Hábitos cumplidos: " + ", ".join(basicos)) if basicos else "Hábitos cumplidos: Ninguno",
                     fg="#1E1E2A", bg="#EDE7FF", font=("Helvetica", 13)).pack(anchor="w")
            tk.Label(contenido,
                     text=("Factores: " + ", ".join(estado)) if estado else "Factores: Ninguno",
                     fg="#1E1E2A", bg="#EDE7FF", font=("Helvetica", 13)).pack(anchor="w")
            if r.get("nota"):
                tk.Label(contenido, text=f"Nota: {r.get('nota')}",
                         fg="#555555", bg="#EDE7FF", wraplength=500,
                         font=("Helvetica", 13)).pack(anchor="w")
            ttk.Separator(scroll_frame, orient="horizontal").pack(fill="x", pady=8)

        # Mantener referencias a los PhotoImage para evitar que el recolector de basura
        # las elimine y usar setattr para evitar errores del comprobador de tipos
        setattr(ventana, "mini_imgs", mini_imgs)
