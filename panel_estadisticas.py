"""
Panel de estadísticas embebido en la ventana principal.
"""

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tema import TEMA_CLARO


class PanelEstadisticas:
    """Muestra gráficas y resumen numérico dentro de un Frame."""

    def __init__(self, padre, gestor, callback_tema=None):
        self.gestor = gestor
        self.callback_tema = callback_tema

        self.marco = tk.LabelFrame(
            padre, text="Estadisticas de productividad",
            font=("Segoe UI", 10, "bold"), padx=10, pady=8
        )
        self.marco.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.lbl_resumen = tk.Label(self.marco, text="", font=("Segoe UI", 10), justify=tk.LEFT)
        self.lbl_resumen.pack(anchor="w", pady=6)

        self.marco_graficas = tk.Frame(self.marco)
        self.marco_graficas.pack(fill=tk.BOTH, expand=True)

        self.canvas_widget = None
        self.figura = None
        self.actualizar()

    def _obtener_tema(self):
        if self.callback_tema:
            return self.callback_tema()
        return TEMA_CLARO.copy()

    def actualizar(self):
        tema = self._obtener_tema()
        self.aplicar_tema(tema)

        stats = self.gestor.obtener_estadisticas()
        texto = (
            f"Total registradas: {stats['total']}   |   "
            f"Pendientes: {stats['pendientes']}   |   "
            f"Completadas: {stats['completadas']}   |   "
            f"Fallidas: {stats['fallidas']}   |   "
            f"Con recordatorio: {stats['con_recordatorio']}"
        )
        self.lbl_resumen.config(text=texto)

        for w in self.marco_graficas.winfo_children():
            w.destroy()
        if self.figura:
            plt.close(self.figura)
            self.figura = None
        self.canvas_widget = None

        if stats['total'] == 0:
            tk.Label(
                self.marco_graficas,
                text="Agrega tareas para ver las graficas.",
                font=("Segoe UI", 11), bg=tema['panel'], fg=tema['texto']
            ).pack(expand=True)
            return

        cols = tema.get('grafica_colores', ['#4a6fa5', '#6b8cae', '#9bb3d1'])
        self.figura, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10, 3.2))
        self.figura.patch.set_facecolor(tema['grafica_fondo'])

        ax1.bar(
            ['Pend.', 'Compl.', 'Fall.'],
            [stats['pendientes'], stats['completadas'], stats['fallidas']],
            color=[cols[0], cols[1], cols[2]]
        )
        ax1.set_title('Por estado', color=tema['grafica_ejes'], fontsize=10)
        ax1.tick_params(colors=tema['grafica_ejes'])

        valores_prio = [stats['alta'], stats['media'], stats['baja']]
        etiquetas_prio = ['Alta', 'Media', 'Baja']
        filtradas, vals, colores = [], [], []
        for i, v in enumerate(valores_prio):
            if v > 0:
                filtradas.append(etiquetas_prio[i])
                vals.append(v)
                colores.append(tema['prioridad'][etiquetas_prio[i]])
        if vals:
            ax2.pie(vals, labels=filtradas, colors=colores, autopct='%1.0f%%', startangle=90)
        ax2.set_title('Por prioridad', color=tema['grafica_ejes'], fontsize=10)

        etiquetas, cantidades = self.gestor.obtener_avance_por_semana()
        if etiquetas and sum(cantidades) > 0:
            ax3.plot(etiquetas, cantidades, marker='o', color=cols[0], linewidth=2)
            ax3.fill_between(range(len(cantidades)), cantidades, alpha=0.2, color=cols[1])
            ax3.set_title('Completadas por semana', color=tema['grafica_ejes'], fontsize=10)
            ax3.tick_params(colors=tema['grafica_ejes'], labelsize=7)
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
        else:
            ax3.text(0.5, 0.5, 'Sin avance aun', ha='center', color=tema['grafica_ejes'])
        ax3.grid(True, alpha=0.3, color=tema.get('borde', '#c5d0dc'))

        plt.tight_layout()
        self.canvas_widget = FigureCanvasTkAgg(self.figura, master=self.marco_graficas)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def aplicar_tema(self, tema):
        self.marco.configure(bg=tema['panel'], fg=tema['texto'])
        self.lbl_resumen.configure(bg=tema['panel'], fg=tema['texto'])
        self.marco_graficas.configure(bg=tema['panel'])
