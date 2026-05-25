"""
Módulo del gestor de tareas.
Usa Pandas para manejar las tareas y un archivo CSV como almacenamiento.
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from tarea import Tarea


class GestorTareas:
    """Clase encargada de crear, leer, actualizar y eliminar tareas."""

    COLUMNAS = [
        'id', 'titulo', 'descripcion', 'fecha_inicio', 'fecha_fin',
        'hora_inicio', 'hora_fin', 'categoria', 'prioridad', 'estado',
        'recordatorio', 'repetir', 'fecha_completada'
    ]

    ORDEN_PRIORIDAD = {'Alta': 3, 'Media': 2, 'Baja': 1}

    def __init__(self, ruta_csv='datos/tareas.csv'):
        self.ruta_csv = ruta_csv
        self._crear_carpeta_si_no_existe()
        self.df = self._cargar_datos()

    def _crear_carpeta_si_no_existe(self):
        carpeta = os.path.dirname(self.ruta_csv)
        if carpeta and not os.path.exists(carpeta):
            os.makedirs(carpeta)

    def _migrar_columnas_antiguas(self, df):
        if 'fecha' in df.columns and 'fecha_inicio' not in df.columns:
            df['fecha_inicio'] = df['fecha']
        if 'fecha_fin' not in df.columns:
            df['fecha_fin'] = ''

        for col, val in {
            'hora_inicio': '', 'hora_fin': '', 'categoria': 'Personal',
            'repetir': 'Ninguna', 'fecha_completada': ''
        }.items():
            if col not in df.columns:
                df[col] = val

        if 'estado' not in df.columns:
            if 'completada' in df.columns:
                df['estado'] = df['completada'].apply(
                    lambda x: 'Completada' if bool(x) else 'Pendiente'
                )
            else:
                df['estado'] = 'Pendiente'

        return df

    def _cargar_datos(self):
        if os.path.exists(self.ruta_csv):
            df = pd.read_csv(self.ruta_csv)
            df = self._migrar_columnas_antiguas(df)
            for col in self.COLUMNAS:
                if col not in df.columns:
                    df[col] = ''
            df = df[self.COLUMNAS].copy()
            df.to_csv(self.ruta_csv, index=False)
            return df
        return pd.DataFrame(columns=self.COLUMNAS)

    def guardar(self):
        self.df.to_csv(self.ruta_csv, index=False)

    def _siguiente_id(self):
        if self.df.empty:
            return 1
        return int(self.df['id'].max()) + 1

    def agregar_tarea(self, titulo, descripcion, fecha_inicio, fecha_fin,
                      hora_inicio, hora_fin, categoria, prioridad,
                      recordatorio=True, repetir='Ninguna', estado='Pendiente'):
        nueva = Tarea(
            id_tarea=self._siguiente_id(),
            titulo=titulo, descripcion=descripcion,
            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
            hora_inicio=hora_inicio, hora_fin=hora_fin,
            categoria=categoria, prioridad=prioridad,
            estado=estado, recordatorio=recordatorio, repetir=repetir
        )
        self.df = pd.concat([self.df, pd.DataFrame([nueva.a_dict()])], ignore_index=True)
        self.guardar()
        return nueva

    def _filas_a_tareas(self, df):
        return [Tarea.desde_fila(fila) for _, fila in df.iterrows()]

    def obtener_todas(self, categoria_filtro=None, fecha_filtro=None, solo_pendientes=True):
        """Lista tareas; por defecto solo pendientes (lista principal)."""
        if self.df.empty:
            return []
        df = self.df.copy()
        if solo_pendientes:
            df = df[df['estado'] == 'Pendiente']
        tareas = self._filas_a_tareas(df)
        if categoria_filtro and categoria_filtro != 'Todas':
            tareas = [t for t in tareas if t.categoria == categoria_filtro]
        if fecha_filtro:
            tareas = [t for t in tareas if t.esta_activa_en_fecha(fecha_filtro)]
        return tareas

    def obtener_historial(self, tipo='Completada'):
        """
        Tareas del historial (completadas o fallidas).
        :param tipo: 'Completada', 'Fallida' o 'Todas'
        """
        if self.df.empty:
            return []
        if tipo == 'Todas':
            df = self.df[self.df['estado'].isin(['Completada', 'Fallida'])]
        else:
            df = self.df[self.df['estado'] == tipo]
        return self._filas_a_tareas(df)

    def obtener_por_id(self, id_tarea):
        fila = self.df[self.df['id'] == id_tarea]
        if fila.empty:
            return None
        return Tarea.desde_fila(fila.iloc[0])

    def obtener_por_fecha(self, fecha):
        """Solo tareas pendientes activas en esa fecha."""
        return [t for t in self.obtener_todas(solo_pendientes=True)
                if t.esta_activa_en_fecha(fecha)]

    def obtener_pendientes_con_recordatorio(self, fecha):
        tareas = self.obtener_por_fecha(fecha)
        return [t for t in tareas if t.recordatorio]

    def obtener_resumen_calendario(self):
        resumen = {}
        pendientes = self.obtener_todas(solo_pendientes=True)
        if not pendientes:
            return resumen

        for tarea in pendientes:
            try:
                inicio = pd.Timestamp(tarea.fecha_inicio)
                fin = pd.Timestamp(tarea.obtener_fecha_fin_efectiva())
                for dia in pd.date_range(inicio, fin, freq='D'):
                    fecha_str = dia.strftime('%Y-%m-%d')
                    if not tarea.esta_activa_en_fecha(fecha_str):
                        continue
                    if fecha_str not in resumen:
                        resumen[fecha_str] = {'cantidad': 0, 'prioridad': 'Baja'}
                    resumen[fecha_str]['cantidad'] += 1
                    resumen[fecha_str]['prioridad'] = self._prioridad_mayor(
                        resumen[fecha_str]['prioridad'], tarea.prioridad
                    )
            except Exception:
                continue
        return resumen

    def _prioridad_mayor(self, prioridad_a, prioridad_b):
        if self.ORDEN_PRIORIDAD.get(prioridad_a, 0) >= self.ORDEN_PRIORIDAD.get(prioridad_b, 0):
            return prioridad_a
        return prioridad_b

    def actualizar_tarea(self, id_tarea, titulo, descripcion, fecha_inicio,
                         fecha_fin, hora_inicio, hora_fin, categoria, prioridad,
                         estado, recordatorio, repetir):
        indice = self.df[self.df['id'] == id_tarea].index
        if len(indice) == 0:
            return False

        idx = indice[0]
        estado_anterior = str(self.df.at[idx, 'estado'])

        self.df.at[idx, 'titulo'] = titulo
        self.df.at[idx, 'descripcion'] = descripcion
        self.df.at[idx, 'fecha_inicio'] = fecha_inicio
        self.df.at[idx, 'fecha_fin'] = fecha_fin
        self.df.at[idx, 'hora_inicio'] = hora_inicio
        self.df.at[idx, 'hora_fin'] = hora_fin
        self.df.at[idx, 'categoria'] = categoria
        self.df.at[idx, 'prioridad'] = prioridad
        self.df.at[idx, 'estado'] = estado
        self.df.at[idx, 'recordatorio'] = recordatorio
        self.df.at[idx, 'repetir'] = repetir

        if estado in ('Completada', 'Fallida') and estado_anterior == 'Pendiente':
            self.df.at[idx, 'fecha_completada'] = datetime.now().strftime('%Y-%m-%d')
        elif estado == 'Pendiente':
            self.df.at[idx, 'fecha_completada'] = ''

        self.guardar()
        return True

    def cambiar_estado(self, id_tarea, nuevo_estado):
        """Cambia solo el estado (acciones rápidas desde la lista)."""
        if nuevo_estado not in Tarea.ESTADOS:
            return False
        tarea = self.obtener_por_id(id_tarea)
        if tarea is None:
            return False
        return self.actualizar_tarea(
            id_tarea, tarea.titulo, tarea.descripcion,
            tarea.fecha_inicio, tarea.fecha_fin,
            tarea.hora_inicio, tarea.hora_fin,
            tarea.categoria, tarea.prioridad,
            nuevo_estado, tarea.recordatorio, tarea.repetir
        )

    def alternar_recordatorio(self, id_tarea):
        tarea = self.obtener_por_id(id_tarea)
        if tarea is None:
            return False
        return self.actualizar_tarea(
            id_tarea, tarea.titulo, tarea.descripcion,
            tarea.fecha_inicio, tarea.fecha_fin,
            tarea.hora_inicio, tarea.hora_fin,
            tarea.categoria, tarea.prioridad,
            tarea.estado, not tarea.recordatorio, tarea.repetir
        )

    def eliminar_tarea(self, id_tarea):
        filas_antes = len(self.df)
        self.df = self.df[self.df['id'] != id_tarea]
        if len(self.df) < filas_antes:
            self.guardar()
            return True
        return False

    def obtener_estadisticas(self):
        total = len(self.df)
        if total == 0:
            return {
                'total': 0, 'pendientes': 0, 'completadas': 0, 'fallidas': 0,
                'alta': 0, 'media': 0, 'baja': 0,
                'con_recordatorio': 0
            }

        conteo_estado = self.df['estado'].value_counts()
        conteo_prioridad = self.df['prioridad'].value_counts()
        con_rec = int(self.df['recordatorio'].sum())

        return {
            'total': total,
            'pendientes': int(conteo_estado.get('Pendiente', 0)),
            'completadas': int(conteo_estado.get('Completada', 0)),
            'fallidas': int(conteo_estado.get('Fallida', 0)),
            'alta': int(conteo_prioridad.get('Alta', 0)),
            'media': int(conteo_prioridad.get('Media', 0)),
            'baja': int(conteo_prioridad.get('Baja', 0)),
            'con_recordatorio': con_rec
        }

    def obtener_avance_por_semana(self, semanas=8):
        if self.df.empty:
            return [], []

        df_comp = self.df[self.df['estado'] == 'Completada'].copy()
        if df_comp.empty:
            return [], []

        df_comp['fecha_completada'] = pd.to_datetime(df_comp['fecha_completada'], errors='coerce')
        df_comp = df_comp.dropna(subset=['fecha_completada'])
        if df_comp.empty:
            return [], []

        hoy = datetime.now()
        etiquetas, cantidades = [], []

        for i in range(semanas - 1, -1, -1):
            fin_semana = hoy - timedelta(days=i * 7)
            inicio_semana = fin_semana - timedelta(days=6)
            mask = (
                (df_comp['fecha_completada'] >= pd.Timestamp(inicio_semana.date())) &
                (df_comp['fecha_completada'] <= pd.Timestamp(fin_semana.date()))
            )
            etiquetas.append(fin_semana.strftime('%d/%m'))
            cantidades.append(int(mask.sum()))

        return etiquetas, cantidades

    def obtener_semana(self, fecha_referencia=None):
        if fecha_referencia is None:
            fecha_referencia = datetime.now()
        elif isinstance(fecha_referencia, str):
            fecha_referencia = datetime.strptime(fecha_referencia, '%Y-%m-%d')

        lunes = fecha_referencia - timedelta(days=fecha_referencia.weekday())
        nombres = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        dias = []
        for i in range(7):
            dia = lunes + timedelta(days=i)
            fecha_str = dia.strftime('%Y-%m-%d')
            dias.append({
                'fecha': fecha_str,
                'nombre_dia': nombres[i],
                'tareas': self.obtener_por_fecha(fecha_str)
            })
        return dias, lunes.strftime('%Y-%m-%d'), (lunes + timedelta(days=6)).strftime('%Y-%m-%d')
