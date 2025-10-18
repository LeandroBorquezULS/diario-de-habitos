from datetime import datetime
from modelo import Modelo, Registro


class Controlador:
    def __init__(self, vista):
        self.vista = vista
        self.modelo = Modelo()

    def guardar_registro(self, usuario, animo, habitos_basicos, habitos_estado, nota):
        """
        Intenta guardar un registro para hoy.
        Si ya existe uno para el mismo usuario y día, pide confirmación a la vista para sobrescribir.
        """
        fecha_full = datetime.now().strftime("%Y-%m-%d %H:%M")
        fecha_dia = fecha_full[:10]

        if self.modelo.existe_fecha(fecha_dia, usuario):
            # obtener el registro actual para mostrarlo y preguntar
            actual = self.modelo.obtener_registro_por_dia(fecha_dia, usuario)
            # pedir confirmación vía vista (vista debe implementar confirmar_sobrescritura)
            confirmar = self.vista.confirmar_sobrescritura(actual)
            if not confirmar:
                # usuario canceló sobrescritura
                self.vista.mostrar_mensaje("No se sobrescribió el registro existente.")
                return

        reg = Registro(fecha_full, usuario, animo, habitos_basicos, habitos_estado, nota)
        self.modelo.agregar(reg)
        self.vista.mostrar_mensaje("Registro guardado correctamente.")

    def obtener_registros(self):
        return self.modelo.obtener_todos()

    def resumen_semanal(self):
        registros = self.modelo.ultimos(7)
        self.vista.mostrar_resumen(registros)
