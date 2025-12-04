# gui.py
# Interfaz gráfica (Tkinter). Usa scanner_io y scanner_core.

import os
import threading
import time
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from scanner_io import generar_diccionario_desde_csv, cargar_diccionario, guardar_salida
from scanner_core import analizar_texto, ER_PALABRA_BASICA, ER_PUNTUACION, ER_DIGITO

class AnalizadorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Practica2 - Analizador Léxico")
        self.geometry("980x640")
        self.minsize(920, 560)

        # Rutas por defecto
        self.csv_ruta = os.path.abspath("diccionario_espanol.csv")
        self.diccionario_ruta = os.path.abspath("diccionario_espanol.txt")
        self.texto_ruta = os.path.abspath("texto_entrada.txt")

        # Estado
        self.diccionario = set()
        self.tokens = []

        # Construir UI
        self.create_widgets()
        self.log("Interfaz lista.")

    def create_widgets(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(side="top", fill="x", padx=8, pady=6)

        mid_frame = ttk.Frame(self)
        mid_frame.pack(side="top", fill="both", expand=True, padx=8, pady=6)

        left_frame = ttk.Frame(mid_frame, width=420)
        left_frame.pack(side="left", fill="y", padx=(0,8), pady=2)

        right_frame = ttk.Frame(mid_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(side="bottom", fill="x", padx=8, pady=6)

        # Top controls
        ttk.Label(top_frame, text="CSV diccionario:").pack(side="left")
        self.csv_entry = ttk.Entry(top_frame, width=50)
        self.csv_entry.insert(0, self.csv_ruta)
        self.csv_entry.pack(side="left", padx=6)
        ttk.Button(top_frame, text="Seleccionar CSV", command=self.seleccionar_csv).pack(side="left", padx=2)
        ttk.Button(top_frame, text="Generar diccionario", command=self.thread_generar_diccionario).pack(side="left", padx=6)

        ttk.Separator(top_frame, orient="vertical").pack(side="left", fill="y", padx=8)
        ttk.Button(top_frame, text="Cargar diccionario (.txt)", command=self.seleccionar_diccionario_y_cargar).pack(side="left", padx=6)
        ttk.Button(top_frame, text="Seleccionar texto entrada", command=self.seleccionar_texto).pack(side="left", padx=6)

        # Left: estado y controles
        left_inner = ttk.LabelFrame(left_frame, text="Estado y controles")
        left_inner.pack(side="top", fill="both", expand=True)

        self.estado_dicc_lbl = ttk.Label(left_inner, text=f"Diccionario: {os.path.basename(self.diccionario_ruta)} (no cargado)")
        self.estado_dicc_lbl.pack(anchor="w", padx=6, pady=(6,2))

        btn_frame = ttk.Frame(left_inner)
        btn_frame.pack(fill="x", padx=6, pady=6)
        ttk.Button(btn_frame, text="Analizar texto (usar dicc cargado)", command=self.thread_analizar).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Guardar tokens (tokens_salida.txt)", command=self.guardar_tokens_dialog).pack(side="left", padx=4)

        # counts
        self.counts_text = tk.Text(left_inner, height=6, width=44, state="disabled", wrap="word")
        self.counts_text.pack(padx=6, pady=(6,8))

        # regex display
        regex_frame = ttk.LabelFrame(left_frame, text="Expresiones Regulares (usadas)")
        regex_frame.pack(fill="x", pady=6)
        reg_text = (
            f"ER_PALABRA_BASICA: {ER_PALABRA_BASICA}\n"
            f"ER_PUNTUACION:     {ER_PUNTUACION}\n"
            f"ER_DIGITO:         {ER_DIGITO}\n\n"
            "Tokenizador: letras Unicode | dígitos (decimales opc.) | signos [.,;:¿?¡!] | fallback"
        )
        ttk.Label(regex_frame, text=reg_text, justify="left").pack(anchor="w", padx=6, pady=6)

        # Right: tokens table
        right_inner = ttk.LabelFrame(right_frame, text="Tokens detectados")
        right_inner.pack(fill="both", expand=True)

        cols = ("Tipo", "Lexema")
        self.tree = ttk.Treeview(right_inner, columns=cols, show="headings")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Lexema", text="Lexema")
        self.tree.column("Tipo", width=180, anchor="w")
        self.tree.column("Lexema", width=420, anchor="w")
        vsb = ttk.Scrollbar(right_inner, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(right_inner, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.tree.pack(side="top", fill="both", expand=True, padx=6, pady=(6,0))
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")

        details_frame = ttk.Frame(right_inner)
        details_frame.pack(fill="x", padx=6, pady=6)
        ttk.Button(details_frame, text="Seleccionar fila y ver detalle", command=self.mostrar_detalle_token).pack(side="left", padx=4)
        ttk.Button(details_frame, text="Exportar tabla CSV", command=self.exportar_tokens_csv).pack(side="left", padx=4)

        # Bottom: log
        log_frame = ttk.LabelFrame(bottom_frame, text="Registro de acciones (log)")
        log_frame.pack(fill="both", expand=True)
        self.log_widget = tk.Text(log_frame, height=8, state="disabled", wrap="word")
        self.log_widget.pack(fill="both", expand=True, padx=6, pady=6)

    # Utilities
    def log(self, texto):
        now = time.strftime("%H:%M:%S")
        self.log_widget.configure(state="normal")
        self.log_widget.insert("end", f"[{now}] {texto}\n")
        self.log_widget.see("end")
        self.log_widget.configure(state="disabled")

    def seleccionar_csv(self):
        ruta = filedialog.askopenfilename(title="Selecciona CSV (columna 'Alfabético')",
                                          filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if ruta:
            self.csv_entry.delete(0, "end")
            self.csv_entry.insert(0, ruta)
            self.csv_ruta = ruta
            self.log(f"CSV seleccionado: {ruta}")

    def seleccionar_diccionario_y_cargar(self):
        ruta = filedialog.askopenfilename(title="Seleccionar diccionario (.txt) para cargar",
                                          filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if ruta:
            self.diccionario_ruta = ruta
            self.log(f"Cargando diccionario desde: {ruta}")
            try:
                self.diccionario = cargar_diccionario(ruta)
                self.estado_dicc_lbl.config(text=f"Diccionario: {os.path.basename(ruta)} ({len(self.diccionario)} palabras)")
                self.log(f"Diccionario cargado: {len(self.diccionario)} palabras.")
                self.actualizar_counts()
            except Exception as e:
                messagebox.showerror("Error al cargar diccionario", str(e))
                self.log(f"Error cargando diccionario: {e}")

    def seleccionar_texto(self):
        ruta = filedialog.askopenfilename(title="Seleccionar texto entrada",
                                          filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if ruta:
            self.texto_ruta = ruta
            self.log(f"Archivo de texto seleccionado: {ruta}")

    def mostrar_detalle_token(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sin selección", "Selecciona primero una fila en la tabla de tokens.")
            return
        item = self.tree.item(sel[0])
        tipo, lex = item["values"]
        messagebox.showinfo("Detalle token", f"Tipo: {tipo}\nLexema: {lex}")

    def exportar_tokens_csv(self):
        if not self.tokens:
            messagebox.showwarning("Sin tokens", "No hay tokens para exportar. Ejecuta un análisis primero.")
            return
        ruta = filedialog.asksaveasfilename(title="Guardar CSV tokens", defaultextension=".csv",
                                           filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not ruta:
            return
        try:
            with open(ruta, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Tipo", "Lexema"])
                for t, l in self.tokens:
                    writer.writerow([t, l])
            self.log(f"Tokens exportados a CSV: {ruta}")
            messagebox.showinfo("Exportado", f"Tokens exportados a: {ruta}")
        except Exception as e:
            self.log(f"Error exportando tokens: {e}")
            messagebox.showerror("Error", str(e))

    def guardar_tokens_dialog(self):
        if not self.tokens:
            if messagebox.askyesno("Guardar salida", "No hay tokens en memoria. ¿Deseas ejecutar análisis usando el archivo de texto seleccionado?"):
                self.thread_analizar()
            else:
                return
        ruta_default = os.path.join(os.getcwd(), "tokens_salida.txt")
        ruta = filedialog.asksaveasfilename(title="Guardar tokens salida", defaultextension=".txt",
                                           initialfile=ruta_default,
                                           filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not ruta:
            return
        try:
            guardar_salida(self.tokens, ruta)
            self.log(f"Tokens guardados en: {ruta}")
            messagebox.showinfo("Guardado", f"Tokens guardados en: {ruta}")
        except Exception as e:
            self.log(f"Error al guardar tokens: {e}")
            messagebox.showerror("Error al guardar", str(e))

    # Threaded operations
    def thread_generar_diccionario(self):
        thread = threading.Thread(target=self.generar_diccionario)
        thread.daemon = True
        thread.start()

    def generar_diccionario(self):
        csv_path = self.csv_entry.get().strip() or self.csv_ruta
        if not csv_path or not os.path.exists(csv_path):
            self.log("No hay CSV válido seleccionado para generar diccionario.")
            messagebox.showwarning("CSV faltante", "Selecciona un archivo CSV válido (que tenga la columna 'Alfabético').")
            return
        try:
            self.log(f"Iniciando generación de diccionario desde CSV: {csv_path}")
            salida_txt = os.path.join(os.getcwd(), "diccionario_espanol.txt")
            generar_diccionario_desde_csv(csv_path, salida_txt)
            self.log(f"Diccionario generado en: {salida_txt}")
            # autoload
            self.diccionario_ruta = salida_txt
            self.diccionario = cargar_diccionario(salida_txt)
            self.estado_dicc_lbl.config(text=f"Diccionario: {os.path.basename(salida_txt)} ({len(self.diccionario)} palabras)")
            self.log(f"Diccionario autoload: {len(self.diccionario)} palabras.")
            self.actualizar_counts()
        except Exception as e:
            self.log(f"Error al generar diccionario: {e}")
            messagebox.showerror("Error", str(e))

    def thread_analizar(self):
        thread = threading.Thread(target=self.analizar)
        thread.daemon = True
        thread.start()

    def analizar(self):
        # Cargar diccionario si no está
        if not self.diccionario:
            resp = messagebox.askyesno("Diccionario no cargado", "No hay diccionario cargado. ¿Deseas intentar cargar el archivo predeterminado diccionario_espanol.txt?")
            if resp:
                ruta_def = os.path.join(os.getcwd(), "diccionario_espanol.txt")
                if os.path.exists(ruta_def):
                    try:
                        self.diccionario = cargar_diccionario(ruta_def)
                        self.estado_dicc_lbl.config(text=f"Diccionario: {os.path.basename(ruta_def)} ({len(self.diccionario)} palabras)")
                        self.log(f"Diccionario cargado: {len(self.diccionario)} palabras.")
                    except Exception as e:
                        self.log(f"Error cargando diccionario por defecto: {e}")
                        messagebox.showerror("Error al cargar diccionario", str(e))
                        return
                else:
                    messagebox.showwarning("Diccionario faltante", "No se encontró diccionario_espanol.txt. Genera uno desde CSV primero.")
                    return
            else:
                return

        if not os.path.exists(self.texto_ruta):
            messagebox.showwarning("Texto faltante", f"No se encontró el archivo de texto: {self.texto_ruta}")
            return

        self.log(f"Iniciando análisis del texto: {self.texto_ruta}")
        try:
            with open(self.texto_ruta, "r", encoding="utf-8") as f:
                texto = f.read()
        except Exception as e:
            self.log(f"Error leyendo texto: {e}")
            messagebox.showerror("Error", str(e))
            return

        try:
            resultado = analizar_texto(texto, self.diccionario)
            self.tokens = resultado
            self.log(f"Análisis completado. Tokens detectados: {len(self.tokens)}")
            self.actualizar_tabla_tokens()
            self.actualizar_counts()
        except Exception as e:
            self.log(f"Error en análisis: {e}")
            messagebox.showerror("Error en análisis", str(e))

    # UI updates
    def actualizar_tabla_tokens(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for tipo, lex in self.tokens:
            self.tree.insert("", "end", values=(tipo, lex))

    def actualizar_counts(self):
        counts = {"PALABRA_VALIDA_ESPANOL": 0, "PUNTUACION": 0, "DIGITO": 0, "ERROR_ORTOGRAFICO": 0}
        for tipo, _ in self.tokens:
            counts[tipo] = counts.get(tipo, 0) + 1
        texto = (
            f"Palabras válidas: {counts['PALABRA_VALIDA_ESPANOL']}\n"
            f"Puntuación:        {counts['PUNTUACION']}\n"
            f"Dígitos:           {counts['DIGITO']}\n"
            f"Errores ort.:      {counts['ERROR_ORTOGRAFICO']}\n"
            f"Diccionario cargado: {len(self.diccionario)} palabras\n"
        )
        self.counts_text.configure(state="normal")
        self.counts_text.delete("1.0", "end")
        self.counts_text.insert("1.0", texto)
        self.counts_text.configure(state="disabled")
