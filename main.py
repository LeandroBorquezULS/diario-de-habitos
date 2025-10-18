import tkinter as tk
from vista import Vista

def iniciar_app(nombre="Maximiliano"):
    root = tk.Tk()
    app = Vista(root, nombre)
    root.mainloop()

if __name__ == "__main__":
    iniciar_app("PEPE")
