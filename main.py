"""
RecuerdaTec - Aplicación de gestión de tareas y recordatorios.

Proyecto de Tópicos Avanzados de Programación.
Tecnologías: Python, POO, Tkinter, Pandas, Matplotlib, CSV.

Para ejecutar:
    python main.py
"""

import tkinter as tk
from interfaz import InterfazRecuerdaTec


def main():
    """
    Punto de entrada del programa.
    Crea la ventana principal y lanza la interfaz.
    """
    ventana = tk.Tk()
    app = InterfazRecuerdaTec(ventana)
    ventana.mainloop()


# Solo ejecutamos main si corremos este archivo directamente
if __name__ == "__main__":
    main()
