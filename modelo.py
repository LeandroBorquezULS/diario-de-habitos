import json
from datetime import datetime

ARCHIVO = "registros.json"  # mantenemos formato json para compatibilidad


class Registro:
    def __init__(self, fecha, usuario, animo, habitos_basicos, habitos_estado, nota):
        """
        fecha: string con formato "YYYY-MM-DD HH:MM" (usamos datetime.now().strftime)
        usuario: nombre del usuario
        animo: int 1-5
        habitos_basicos: dict {"Agua": bool, "Ejercicio": bool, "Estudio": bool}
        habitos_estado: dict {...}  # los checkboxes de '¿Qué influye en tu estado?'
        nota: string (recortada a 200 chars)
        """
        self.fecha = fecha
        self.usuario = usuario
        self.animo = animo
        self.habitos_basicos = habitos_basicos
        self.habitos_estado = habitos_estado
        self.nota = (nota or "")[:200]

    def a_dict(self):
        return {
            "fecha": self.fecha,
            "usuario": self.usuario,
            "animo": self.animo,
            "habitos_basicos": self.habitos_basicos,
            "habitos_estado": self.habitos_estado,
            "nota": self.nota
        }


class Modelo:
    def __init__(self):
        self.datos = self.cargar()

    def cargar(self):
        try:
            with open(ARCHIVO, "r", encoding="utf-8") as f:
                data = json.load(f)
                # garantizar compatibilidad: si en registros antiguos la clave era "habitos" convertirla
                for d in data:
                    if "habitos" in d and "habitos_basicos" not in d:
                        # suponer que "habitos" es una mezcla: lo colocamos en habitos_estado
                        d["habitos_estado"] = d.pop("habitos")
                    # si faltan keys, asegurarlas
                    d.setdefault("habitos_basicos", {"Agua": False, "Ejercicio": False, "Estudio": False})
                    d.setdefault("habitos_estado", {})
                    d.setdefault("nota", "")
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def guardar(self):
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(self.datos, f, ensure_ascii=False, indent=2)

    def existe_fecha(self, fecha_str, usuario):
        """
        Verifica si ya existe un registro para la misma fecha (mismo día) y usuario.
        fecha_str debe ser 'YYYY-MM-DD' o cadena de fecha completa; aquí usamos solo la parte YYYY-MM-DD.
        """
        fecha_dia = fecha_str[:10]
        return any(d.get("usuario") == usuario and d.get("fecha", "")[:10] == fecha_dia for d in self.datos)

    def obtener_registro_por_dia(self, fecha_str, usuario):
        """Devuelve el registro (dict) del día si existe, sino None."""
        fecha_dia = fecha_str[:10]
        for d in self.datos:
            if d.get("usuario") == usuario and d.get("fecha", "")[:10] == fecha_dia:
                return d
        return None

    def agregar(self, registro: Registro):
        """
        Si hay ya un registro del mismo dia y usuario, lo reemplaza.
        Si no, lo agrega al final.
        """
        fecha_dia = registro.fecha[:10]
        for i, d in enumerate(self.datos):
            if d.get("usuario") == registro.usuario and d.get("fecha", "")[:10] == fecha_dia:
                self.datos[i] = registro.a_dict()
                self.guardar()
                return
        # si no lo encontró, agregar nuevo
        self.datos.append(registro.a_dict())
        self.guardar()

    def obtener_todos(self):
        # ordenar por fecha descendente (si el formato es YYYY-MM-DD HH:MM funciona lexicográficamente)
        return sorted(self.datos, key=lambda x: x.get("fecha", ""), reverse=True)

    def ultimos(self, n=7):
        return self.obtener_todos()[:n]
