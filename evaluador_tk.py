"""
Evaluador de proyectos - Interfaz Tkinter
- Guarda/lee en evaluaciones.json
- Exporta resultados a CSV
- Notas 0-5
- Múltiples evaluaciones (espacios)
Autor: Generado para Hilan (adaptable)
"""

import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import json
import os
import csv

ARCHIVO = "evaluaciones.json"

def cargar_evaluaciones():
    if os.path.exists(ARCHIVO):
        try:
            with open(ARCHIVO, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def guardar_evaluaciones(evals):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(evals, f, indent=4, ensure_ascii=False)

# ---------- Lógica de evaluación ----------
def crear_evaluacion(evals, key, datos, criterios):
    evals[key] = {"datos": datos, "criterios": criterios, "resultados": None}
    guardar_evaluaciones(evals)

def calcular_resultados(datos, criterios, notas_dict):
    resultados = []
    nota_final = 0.0
    for crit, peso in criterios.items():
        nota = float(notas_dict.get(crit, 0))
        ponderado = nota * (peso / 100.0)
        resultados.append([crit, nota, peso, round(ponderado, 2)])
        nota_final += ponderado
    return {"datos": datos, "criterios": resultados, "nota_final": round(nota_final, 2)}

def exportar_csv(nombre_eval, resultados):
    if resultados is None:
        return False, "No hay resultados para exportar."
    filename = filedialog.asksaveasfilename(defaultextension=".csv",
                                            initialfile=f"{nombre_eval}.csv",
                                            filetypes=[("CSV files","*.csv"),("All files","*.*")])
    if not filename:
        return False, "Exportación cancelada."
    try:
        with open(filename, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Evaluación", nombre_eval])
            writer.writerow(["Nombre", resultados["datos"]["nombre"]])
            writer.writerow(["Rol", resultados["datos"]["rol"]])
            writer.writerow([])
            writer.writerow(["Criterio", "Nota (0-5)", "Peso (%)", "Aporte"])
            for row in resultados["criterios"]:
                writer.writerow(row)
            writer.writerow([])
            writer.writerow(["Nota final", resultados["nota_final"]])
        return True, f"Exportado a {filename}"
    except Exception as e:
        return False, str(e)

# ---------- GUI ----------
class EvaluadorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Evaluación - Tkinter")
        self.geometry("820x480")
        self.resizable(False, False)

        # Datos
        self.evaluaciones = cargar_evaluaciones()

        # UI: Listbox de evaluaciones
        left_frame = tk.Frame(self, padx=8, pady=8)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(left_frame, text="Evaluaciones / Espacios").pack()
        self.eval_listbox = tk.Listbox(left_frame, width=30, height=20)
        self.eval_listbox.pack(pady=4)
        self.eval_listbox.bind("<<ListboxSelect>>", self.on_select_eval)

        btn_frame = tk.Frame(left_frame)
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Crear nueva", command=self.ui_crear).grid(row=0, column=0, padx=3)
        tk.Button(btn_frame, text="Eliminar", command=self.ui_eliminar).grid(row=0, column=1, padx=3)
        tk.Button(btn_frame, text="Exportar CSV", command=self.ui_exportar).grid(row=1, column=0, columnspan=2, pady=4)

        # Right: detalles y acciones
        right_frame = tk.Frame(self, padx=8, pady=8)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Info persona
        info_frame = tk.LabelFrame(right_frame, text="Datos (Nombre / Rol)", padx=8, pady=8)
        info_frame.pack(fill=tk.X, pady=4)
        self.lbl_nombre = tk.Label(info_frame, text="Nombre: -")
        self.lbl_nombre.pack(anchor="w")
        self.lbl_rol = tk.Label(info_frame, text="Rol: -")
        self.lbl_rol.pack(anchor="w")
        tk.Button(info_frame, text="Editar datos", command=self.ui_editar_datos).pack(anchor="e", pady=4)

        # Criterios
        crit_frame = tk.LabelFrame(right_frame, text="Criterios (Nombre : Peso %)", padx=8, pady=8)
        crit_frame.pack(fill=tk.BOTH, expand=True, pady=4)
        self.crit_listbox = tk.Listbox(crit_frame, height=8)
        self.crit_listbox.pack(fill=tk.BOTH, expand=True, pady=2)
        crit_btns = tk.Frame(crit_frame)
        crit_btns.pack(pady=4)
        tk.Button(crit_btns, text="Añadir criterio", command=self.ui_add_criterio).grid(row=0, column=0, padx=3)
        tk.Button(crit_btns, text="Eliminar criterio", command=self.ui_del_criterio).grid(row=0, column=1, padx=3)
        tk.Button(crit_btns, text="Validar pesos (100%)", command=self.ui_validar_pesos).grid(row=0, column=2, padx=3)

        # Calificar
        grade_frame = tk.LabelFrame(right_frame, text="Calificación", padx=8, pady=8)
        grade_frame.pack(fill=tk.X, pady=4)
        tk.Button(grade_frame, text="Calificar esta evaluación", command=self.ui_calificar).pack(side=tk.LEFT)
        tk.Button(grade_frame, text="Ver resultados", command=self.ui_ver_resultados).pack(side=tk.LEFT, padx=8)

        # Resultados list (detalle)
        res_frame = tk.LabelFrame(right_frame, text="Resultado (Detalle)", padx=8, pady=8)
        res_frame.pack(fill=tk.BOTH, expand=True, pady=4)
        self.res_text = tk.Text(res_frame, height=8, state="disabled")
        self.res_text.pack(fill=tk.BOTH, expand=True)

        self.refresh_eval_listbox()

    def refresh_eval_listbox(self):
        self.eval_listbox.delete(0, tk.END)
        for key in self.evaluaciones.keys():
            self.eval_listbox.insert(tk.END, key)

    def get_selected_eval(self):
        sel = self.eval_listbox.curselection()
        if not sel:
            return None
        return self.eval_listbox.get(sel[0])

    # ---------- UI actions ----------
    def on_select_eval(self, event=None):
        key = self.get_selected_eval()
        if not key:
            self.lbl_nombre.config(text="Nombre: -")
            self.lbl_rol.config(text="Rol: -")
            self.crit_listbox.delete(0, tk.END)
            self.res_text.config(state="normal")
            self.res_text.delete(1.0, tk.END)
            self.res_text.config(state="disabled")
            return
        data = self.evaluaciones[key]
        datos = data.get("datos", {})
        self.lbl_nombre.config(text=f"Nombre: {datos.get('nombre','-')}")
        self.lbl_rol.config(text=f"Rol: {datos.get('rol','-')}")
        self.crit_listbox.delete(0, tk.END)
        criterios = data.get("criterios", {})
        for crit, peso in criterios.items():
            self.crit_listbox.insert(tk.END, f"{crit} : {peso}%")
        # mostrar resultados si existen
        if data.get("resultados"):
            self.mostrar_resultados_text(key, data["resultados"])
        else:
            self.res_text.config(state="normal")
            self.res_text.delete(1.0, tk.END)
            self.res_text.insert(tk.END, "No hay resultados registrados aún.")
            self.res_text.config(state="disabled")

    def ui_crear(self):
        nombre_eval = simpledialog.askstring("Nueva evaluación", "Nombre para la evaluación (ej: Grupo A):", parent=self)
        if not nombre_eval:
            return
        if nombre_eval in self.evaluaciones:
            messagebox.showwarning("Aviso", "Ya existe una evaluación con ese nombre.")
            return
        # pedir datos
        nombre = simpledialog.askstring("Datos", "Nombre de la persona a evaluar:", parent=self)
        rol = simpledialog.askstring("Datos", "Rol en la gestión del proyecto:", parent=self)
        if not nombre:
            nombre = ""
        if not rol:
            rol = ""
        # crear criterios por UI repetida hasta que el usuario decida o llegue a 100%
        criterios = {}
        total = 0
        messagebox.showinfo("Criterios", "Ahora define criterios y pesos. Deben sumar 100% en total.")
        while total < 100:
            crit = simpledialog.askstring("Criterio", f"Ingrese nombre del criterio (total actual {total}%):", parent=self)
            if not crit:
                break
            try:
                peso = simpledialog.askinteger("Peso", f"Ingrese peso (%) para '{crit}':", parent=self, minvalue=0, maxvalue=100)
            except Exception:
                messagebox.showerror("Error", "Peso inválido.")
                continue
            if peso is None:
                break
            if total + peso > 100:
                messagebox.showwarning("Peso excede", f"Agregar {peso}% excede 100%. Total actual {total}%. Intente otro valor.")
                continue
            criterios[crit] = peso
            total += peso
            if total == 100:
                break
            cont = messagebox.askyesno("Continuar", "¿Desea añadir otro criterio?")
            if not cont:
                if total != 100:
                    messagebox.showwarning("Atención", f"El total de pesos es {total}%. Debe ser 100%. Continúe añadiendo o ajuste.")
                # allow loop to continue
        # requiere que total sea 100
        if sum(criterios.values()) != 100:
            messagebox.showerror("Error", "Los pesos no suman 100%. No se creó la evaluación.")
            return
        crear_evaluacion(self.evaluaciones, nombre_eval, {"nombre": nombre, "rol": rol}, criterios)
        self.refresh_eval_listbox()
        messagebox.showinfo("Ok", f"Evaluación '{nombre_eval}' creada.")
        # seleccionar creado
        idx = list(self.evaluaciones.keys()).index(nombre_eval)
        self.eval_listbox.selection_clear(0, tk.END)
        self.eval_listbox.selection_set(idx)
        self.on_select_eval()

    def ui_eliminar(self):
        key = self.get_selected_eval()
        if not key:
            messagebox.showwarning("Aviso", "Seleccione una evaluación.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar evaluación '{key}'? Esta acción no se puede deshacer."):
            del self.evaluaciones[key]
            guardar_evaluaciones(self.evaluaciones)
            self.refresh_eval_listbox()
            self.on_select_eval()

    def ui_editar_datos(self):
        key = self.get_selected_eval()
        if not key:
            messagebox.showwarning("Aviso", "Seleccione una evaluación.")
            return
        datos = self.evaluaciones[key].get("datos", {})
        nombre = simpledialog.askstring("Editar", "Nombre:", initialvalue=datos.get("nombre",""), parent=self)
        rol = simpledialog.askstring("Editar", "Rol:", initialvalue=datos.get("rol",""), parent=self)
        if nombre is not None and rol is not None:
            self.evaluaciones[key]["datos"] = {"nombre": nombre, "rol": rol}
            guardar_evaluaciones(self.evaluaciones)
            self.on_select_eval()

    def ui_add_criterio(self):
        key = self.get_selected_eval()
        if not key:
            messagebox.showwarning("Aviso", "Seleccione una evaluación primero.")
            return
        criterios = self.evaluaciones[key].get("criterios", {})
        total = sum(criterios.values())
        crit = simpledialog.askstring("Nuevo criterio", f"Nombre del criterio (total actual {total}%):", parent=self)
        if not crit:
            return
        peso = simpledialog.askinteger("Peso", f"Ingrese peso (%) para '{crit}':", parent=self, minvalue=0, maxvalue=100)
        if peso is None:
            return
        if total + peso > 100:
            messagebox.showwarning("Peso excede", f"Agregar {peso}% excede 100%. Total actual {total}%.")
            return
        criterios[crit] = peso
        self.evaluaciones[key]["criterios"] = criterios
        guardar_evaluaciones(self.evaluaciones)
        self.on_select_eval()

    def ui_del_criterio(self):
        key = self.get_selected_eval()
        if not key:
            messagebox.showwarning("Aviso", "Seleccione una evaluación primero.")
            return
        sel = self.crit_listbox.curselection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un criterio en la lista.")
            return
        texto = self.crit_listbox.get(sel[0])
        crit = texto.split(" : ")[0]
        if messagebox.askyesno("Confirmar", f"Eliminar criterio '{crit}'?"):
            criterios = self.evaluaciones[key]["criterios"]
            criterios.pop(crit, None)
            # si elimina, validar que suma siga siendo 100 si ya había resultados o si se quiere cerrar
            guardar_evaluaciones(self.evaluaciones)
            self.on_select_eval()

    def ui_validar_pesos(self):
        key = self.get_selected_eval()
        if not key:
            messagebox.showwarning("Aviso", "Seleccione una evaluación.")
            return
        criterios = self.evaluaciones[key].get("criterios", {})
        s = sum(criterios.values())
        if s == 100:
            messagebox.showinfo("OK", "Los pesos suman 100%.")
        else:
            messagebox.showwarning("No válido", f"Los pesos suman {s}%. Deben ser 100%.")

    def ui_calificar(self):
        key = self.get_selected_eval()
        if not key:
            messagebox.showwarning("Aviso", "Seleccione una evaluación.")
            return
        criterios = self.evaluaciones[key].get("criterios", {})
        if not criterios:
            messagebox.showwarning("Aviso", "La evaluación no tiene criterios definidos.")
            return
        if sum(criterios.values()) != 100:
            messagebox.showwarning("Peso inválido", "Los pesos deben sumar 100% antes de calificar.")
            return
        datos = self.evaluaciones[key].get("datos", {})
        notas = {}
        for crit in criterios.keys():
            while True:
                res = simpledialog.askstring("Calificación", f"Ingrese nota (0-5) para '{crit}':", parent=self)
                if res is None:
                    # cancel
                    if messagebox.askyesno("Cancelar", "¿Cancelar calificación? Se descartarán notas ingresadas."):
                        return
                    else:
                        continue
                try:
                    val = float(res)
                    if 0.0 <= val <= 5.0:
                        notas[crit] = val
                        break
                    else:
                        messagebox.showwarning("Rango inválido", "La nota debe estar entre 0 y 5.")
                except:
                    messagebox.showwarning("Valor inválido", "Ingrese un número válido.")
        resultados = calcular_resultados(datos, criterios, notas)
        self.evaluaciones[key]["resultados"] = resultados
        guardar_evaluaciones(self.evaluaciones)
        messagebox.showinfo("Ok", "Calificación registrada.")
        self.on_select_eval()

    def ui_ver_resultados(self):
        key = self.get_selected_eval()
        if not key:
            messagebox.showwarning("Aviso", "Seleccione una evaluación.")
            return
        resultados = self.evaluaciones[key].get("resultados")
        if not resultados:
            messagebox.showinfo("Sin resultados", "Aún no hay resultados para esta evaluación.")
            return
        self.mostrar_resultados_text(key, resultados)

    def mostrar_resultados_text(self, key, resultados):
        self.res_text.config(state="normal")
        self.res_text.delete(1.0, tk.END)
        d = resultados["datos"]
        self.res_text.insert(tk.END, f"Evaluación: {key}\n")
        self.res_text.insert(tk.END, f"Nombre: {d.get('nombre','-')}\n")
        self.res_text.insert(tk.END, f"Rol: {d.get('rol','-')}\n\n")
        self.res_text.insert(tk.END, "Criterios:\n")
        for crit, nota, peso, aporte in resultados["criterios"]:
            self.res_text.insert(tk.END, f" - {crit}: {nota}/5  (Peso {peso}% ) → Aporte: {aporte}\n")
        self.res_text.insert(tk.END, f"\nNota final: {resultados['nota_final']}/5\n")
        self.res_text.config(state="disabled")

    def ui_exportar(self):
        key = self.get_selected_eval()
        if not key:
            messagebox.showwarning("Aviso", "Seleccione una evaluación.")
            return
        resultados = self.evaluaciones[key].get("resultados")
        ok, msg = exportar_csv(key, resultados)
        if ok:
            messagebox.showinfo("Exportar", msg)
        else:
            messagebox.showerror("Exportar", msg)


if __name__ == "__main__":
    app = EvaluadorApp()
    app.mainloop()
