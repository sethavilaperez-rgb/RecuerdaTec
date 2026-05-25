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
    ESTADOS = ['Pendiente', 'Completada', 'Fallida']

    def __init__(self, id_tarea, titulo, descripcion, fecha_inicio, prioridad,
                 fecha_fin='', hora_inicio='', hora_fin='', categoria='Personal',
                 estado='Pendiente', recordatorio=True, repetir='Ninguna',
                 fecha_completada=''):
        self.id_tarea = id_tarea
        self.titulo = titulo
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin if fecha_fin else ''
        self.hora_inicio = hora_inicio if hora_inicio else ''
        self.hora_fin = hora_fin if hora_fin else ''
        self.categoria = categoria if categoria else 'Personal'
        self.prioridad = prioridad
        self.estado = estado if estado in self.ESTADOS else 'Pendiente'
        self.recordatorio = recordatorio
        self.repetir = repetir if repetir else 'Ninguna'
        self.fecha_completada = fecha_completada if fecha_completada else ''

    @property
    def completada(self):
        """Compatibilidad con código que usaba el booleano completada."""
        return self.estado == 'Completada'

    @property
    def es_pendiente(self):
        return self.estado == 'Pendiente'

    def marcar_completada(self):
        self.estado = 'Completada'
        self.fecha_completada = datetime.now().strftime('%Y-%m-%d')

    def marcar_pendiente(self):
        self.estado = 'Pendiente'
        self.fecha_completada = ''

    def marcar_fallida(self):
        self.estado = 'Fallida'
        self.fecha_completada = datetime.now().strftime('%Y-%m-%d')

    def obtener_fecha_fin_efectiva(self):
        if self.fecha_fin and str(self.fecha_fin).strip():
            return str(self.fecha_fin)
        if self.repetir != 'Ninguna':
            return '2099-12-31'
        return self.fecha_inicio

    def esta_activa_en_fecha(self, fecha):
        if not self.es_pendiente:
            return False
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
        if self.hora_inicio and self.hora_fin:
            return f"{self.hora_inicio} - {self.hora_fin}"
        if self.hora_inicio:
            return f"desde {self.hora_inicio}"
        if self.hora_fin:
            return f"hasta {self.hora_fin}"
        return ''

    def a_dict(self):
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
            'estado': self.estado,
            'recordatorio': self.recordatorio,
            'repetir': self.repetir,
            'fecha_completada': self.fecha_completada
        }

    @staticmethod
    def desde_fila(fila):
        if 'fecha_inicio' in fila.index:
            fecha_inicio = str(fila['fecha_inicio'])
        else:
            fecha_inicio = str(fila.get('fecha', ''))

        fecha_fin = ''
        if 'fecha_fin' in fila.index and pd_no_es_vacio(fila['fecha_fin']):
            fecha_fin = str(fila['fecha_fin'])

        # Migrar columna antigua completada -> estado
        if 'estado' in fila.index and pd_no_es_vacio(fila['estado']):
            estado = str(fila['estado'])
        elif bool(fila.get('completada', False)):
            estado = 'Completada'
        else:
            estado = 'Pendiente'

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
            estado=estado,
            recordatorio=bool(fila['recordatorio']),
            repetir=str(fila.get('repetir', 'Ninguna') or 'Ninguna'),
            fecha_completada=str(fila.get('fecha_completada', '') or '')
        )

    def __str__(self):
        extra = f" [{self.categoria}]" if self.categoria else ''
        rep = f" (rep. {self.repetir})" if self.repetir != 'Ninguna' else ''
        return f"[{self.id_tarea}] {self.titulo}{extra}{rep} ({self.estado})"


def pd_no_es_vacio(valor):
    if valor is None:
        return False
    texto = str(valor).strip()
    return texto != '' and texto.lower() != 'nan'


def validar_hora(hora, nombre_campo, obligatoria=False):
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
