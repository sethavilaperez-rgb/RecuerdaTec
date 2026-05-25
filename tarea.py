"""
Módulo de la clase Tarea.
Representa una tarea o recordatorio con sus datos principales.
"""

from datetime import datetime


class Tarea:
    """
    Clase que modela una tarea individual.
    Cada objeto guarda la información que se muestra en la interfaz.
    """

    CATEGORIAS = ['Escuela', 'Trabajo', 'Personal', 'Otro']
    TIPOS_REPETICION = ['Ninguna', 'Diaria', 'Semanal', 'Mensual']

    def __init__(self, id_tarea, titulo, descripcion, fecha_inicio, prioridad,
                 fecha_fin='', hora_inicio='', hora_fin='', categoria='Personal',
                 completada=False, recordatorio=True, repetir='Ninguna',
                 fecha_completada=''):
        """
        Inicializa una tarea con todos sus atributos.
        """
        self.id_tarea = id_tarea
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin if fecha_fin else ''
        self.hora_inicio = hora_inicio if hora_inicio else ''
        self.hora_fin = hora_fin if hora_fin else ''
        self.categoria = categoria if categoria else 'Personal'
        self.prioridad = prioridad
        self.completada = completada
        self.recordatorio = recordatorio
        self.repetir = repetir if repetir else 'Ninguna'
        self.fecha_completada = fecha_completada if fecha_completada else ''

    def marcar_completada(self):
        """Cambia el estado de la tarea a completada y guarda la fecha."""
        self.completada = True
        self.fecha_completada = datetime.now().strftime('%Y-%m-%d')

    def marcar_pendiente(self):
        """Cambia el estado de la tarea a pendiente."""
        self.completada = False
        self.fecha_completada = ''

    def obtener_fecha_fin_efectiva(self):
        """
        Si no hay fecha de término, usamos la de inicio.
        Para tareas repetitivas sin fin, usamos un límite lejano.
        """
        if self.fecha_fin and str(self.fecha_fin).strip():
            return str(self.fecha_fin)
        if self.repetir != 'Ninguna':
            return '2099-12-31'
        return self.fecha_inicio

    def esta_activa_en_fecha(self, fecha):
        """
        Indica si la tarea debe mostrarse en una fecha del calendario.
        Soporta rangos y tareas repetitivas.
        """
        if fecha < self.fecha_inicio:
            return False

        fin = self.obtener_fecha_fin_efectiva()
        if fecha > fin:
            return False

        if self.repetir == 'Ninguna':
            return True

        try:
            f = datetime.strptime(fecha, '%Y-%m-%d')
            inicio = datetime.strptime(self.fecha_inicio, '%Y-%m-%d')
        except ValueError:
            return False

        if self.repetir == 'Diaria':
            return True

        if self.repetir == 'Semanal':
            return f.weekday() == inicio.weekday()

        if self.repetir == 'Mensual':
            return f.day == inicio.day

        return True

    def obtener_horario_texto(self):
        """Texto corto con el horario de la tarea."""
        if self.hora_inicio and self.hora_fin:
            return f"{self.hora_inicio} - {self.hora_fin}"
        if self.hora_inicio:
            return f"desde {self.hora_inicio}"
        if self.hora_fin:
            return f"hasta {self.hora_fin}"
        return ''

    def a_dict(self):
        """Convierte la tarea a un diccionario para Pandas."""
        return {
            'id': self.id_tarea,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin,
            'hora_inicio': self.hora_inicio,
            'hora_fin': self.hora_fin,
            'categoria': self.categoria,
            'prioridad': self.prioridad,
            'completada': self.completada,
            'recordatorio': self.recordatorio,
            'repetir': self.repetir,
            'fecha_completada': self.fecha_completada
        }

    @staticmethod
    def desde_fila(fila):
        """Crea un objeto Tarea a partir de una fila del DataFrame."""
        if 'fecha_inicio' in fila.index:
            fecha_inicio = str(fila['fecha_inicio'])
        else:
            fecha_inicio = str(fila.get('fecha', ''))

        fecha_fin = ''
        if 'fecha_fin' in fila.index and pd_no_es_vacio(fila['fecha_fin']):
            fecha_fin = str(fila['fecha_fin'])

        return Tarea(
            id_tarea=int(fila['id']),
            titulo=str(fila['titulo']),
            descripcion=str(fila['descripcion']),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            hora_inicio=str(fila.get('hora_inicio', '') or ''),
            hora_fin=str(fila.get('hora_fin', '') or ''),
            categoria=str(fila.get('categoria', 'Personal') or 'Personal'),
            prioridad=str(fila['prioridad']),
            completada=bool(fila['completada']),
            recordatorio=bool(fila['recordatorio']),
            repetir=str(fila.get('repetir', 'Ninguna') or 'Ninguna'),
            fecha_completada=str(fila.get('fecha_completada', '') or '')
        )

    def __str__(self):
        estado = "Completada" if self.completada else "Pendiente"
        extra = f" [{self.categoria}]" if self.categoria else ''
        rep = f" ↻{self.repetir}" if self.repetir != 'Ninguna' else ''
        return f"[{self.id_tarea}] {self.titulo}{extra}{rep} ({estado})"


def pd_no_es_vacio(valor):
    """Revisa si un valor de Pandas no está vacío (evita NaN)."""
    if valor is None:
        return False
    texto = str(valor).strip()
    return texto != '' and texto.lower() != 'nan'


def validar_hora(hora, nombre_campo, obligatoria=False):
    """
    Valida formato de hora HH:MM (24 horas).
    :return: hora validada, None si hay error, '' si opcional vacía
    """
    hora = hora.strip()
    if not hora:
        if obligatoria:
            return None
        return ''
    try:
        datetime.strptime(hora, '%H:%M')
        return hora
    except ValueError:
        return None
