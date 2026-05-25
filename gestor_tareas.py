"""
Módulo del gestor de tareas.
Usa Pandas para manejar las tareas y un archivo CSV como almacenamiento.
"""

import os
import pandas as pd
from datetime import datetime, timedelta
from tarea import Tarea


class GestorTareas:
    """
    Clase encargada de crear, leer, actualizar y eliminar tareas.
    Todas las operaciones se hacen sobre un DataFrame de Pandas.
    """

    COLUMNAS = [
        'id', 'titulo', 'descripcion', 'fecha_inicio', 'fecha_fin',
        'hora_inicio', 'hora_fin', 'categoria', 'prioridad',
        'completada', 'recordatorio', 'repetir', 'fecha_completada'
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
        """Agrega columnas nuevas si el CSV es de una versión anterior."""
        if 'fecha' in df.columns and 'fecha_inicio' not in df.columns:
            df['fecha_inicio'] = df['fecha']
        if 'fecha_fin' not in df.columns:
            df['fecha_fin'] = ''

        columnas_nuevas = {
            'hora_inicio': '',
            'hora_fin': '',
            'categoria': 'Personal',
            'repetir': 'Ninguna',
            'fecha_completada': ''
        }
        for col, valor_defecto in columnas_nuevas.items():
            if col not in df.columns:
                df[col] = valor_defecto
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
                      recordatorio=True, repetir='Ninguna'):
        nueva = Tarea(
            id_tarea=self._siguiente_id(),
            titulo=titulo,
            descripcion=descripcion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            categoria=categoria,
            prioridad=prioridad,
            completada=False,
            recordatorio=recordatorio,
            repetir=repetir
        )
        self.df = pd.concat(
            [self.df, pd.DataFrame([nueva.a_dict()])],
            ignore_index=True
        )
        self.guardar()
        return nueva

    def obtener_todas(self, categoria_filtro=None, fecha_filtro=None):
        """
        Devuelve tareas aplicando filtros opcionales.
        :param categoria_filtro: 'Todas' o nombre de categoría
        :param fecha_filtro: fecha 'YYYY-MM-DD' para ver solo tareas activas ese día
        """
        if self.df.empty:
            return []
        tareas = [Tarea.desde_fila(fila) for _, fila in self.df.iterrows()]
        if categoria_filtro and categoria_filtro != 'Todas':
            tareas = [t for t in tareas if t.categoria == categoria_filtro]
        if fecha_filtro:
            tareas = [t for t in tareas if t.esta_activa_en_fecha(fecha_filtro)]
        return tareas

    def obtener_por_id(self, id_tarea):
        fila = self.df[self.df['id'] == id_tarea]
        if fila.empty:
            return None
        return Tarea.desde_fila(fila.iloc[0])

    def obtener_por_fecha(self, fecha):
        tareas = self.obtener_todas()
        return [t for t in tareas if t.esta_activa_en_fecha(fecha)]

    def obtener_pendientes_con_recordatorio(self, fecha):
        tareas = self.obtener_por_fecha(fecha)
        return [t for t in tareas if not t.completada and t.recordatorio]

    def obtener_resumen_calendario(self):
        resumen = {}
        if self.df.empty:
            return resumen

        # Revisamos un rango amplio para incluir tareas repetitivas
        fechas_inicio = pd.to_datetime(self.df['fecha_inicio'], errors='coerce')
        min_fecha = fechas_inicio.min()
        if pd.isna(min_fecha):
            return resumen

        inicio = min_fecha
        fin = inicio + pd.Timedelta(days=365)

        for dia in pd.date_range(inicio, fin, freq='D'):
            fecha_str = dia.strftime('%Y-%m-%d')
            tareas_dia = self.obtener_por_fecha(fecha_str)
            if not tareas_dia:
                continue
            prioridad = 'Baja'
            for t in tareas_dia:
                prioridad = self._prioridad_mayor(prioridad, t.prioridad)
            resumen[fecha_str] = {
                'cantidad': len(tareas_dia),
                'prioridad': prioridad
            }
        return resumen

    def _prioridad_mayor(self, prioridad_a, prioridad_b):
        if self.ORDEN_PRIORIDAD.get(prioridad_a, 0) >= self.ORDEN_PRIORIDAD.get(prioridad_b, 0):
            return prioridad_a
        return prioridad_b

    def actualizar_tarea(self, id_tarea, titulo, descripcion, fecha_inicio,
                         fecha_fin, hora_inicio, hora_fin, categoria, prioridad,
                         completada, recordatorio, repetir):
        indice = self.df[self.df['id'] == id_tarea].index
        if len(indice) == 0:
            return False

        idx = indice[0]
        estaba_completada = bool(self.df.at[idx, 'completada'])

        self.df.at[idx, 'titulo'] = titulo
        self.df.at[idx, 'descripcion'] = descripcion
        self.df.at[idx, 'fecha_inicio'] = fecha_inicio
        self.df.at[idx, 'fecha_fin'] = fecha_fin
        self.df.at[idx, 'hora_inicio'] = hora_inicio
        self.df.at[idx, 'hora_fin'] = hora_fin
        self.df.at[idx, 'categoria'] = categoria
        self.df.at[idx, 'prioridad'] = prioridad
        self.df.at[idx, 'completada'] = completada
        self.df.at[idx, 'recordatorio'] = recordatorio
        self.df.at[idx, 'repetir'] = repetir

        # Guardamos fecha de completado para la gráfica de avance
        if completada and not estaba_completada:
            self.df.at[idx, 'fecha_completada'] = datetime.now().strftime('%Y-%m-%d')
        elif not completada:
            self.df.at[idx, 'fecha_completada'] = ''

        self.guardar()
        return True

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
                'total': 0, 'completadas': 0, 'pendientes': 0,
                'alta': 0, 'media': 0, 'baja': 0
            }

        completadas = int(self.df['completada'].sum())
        pendientes = total - completadas
        conteo_prioridad = self.df['prioridad'].value_counts()
        return {
            'total': total,
            'completadas': completadas,
            'pendientes': pendientes,
            'alta': int(conteo_prioridad.get('Alta', 0)),
            'media': int(conteo_prioridad.get('Media', 0)),
            'baja': int(conteo_prioridad.get('Baja', 0))
        }

    def obtener_avance_por_semana(self, semanas=8):
        """
        Cuenta tareas completadas por semana para la gráfica de avance.
        Usa la columna fecha_completada.

        :return: lista de (etiqueta_semana, cantidad)
        """
        if self.df.empty:
            return [], []

        df_comp = self.df[self.df['completada'] == True].copy()
        if df_comp.empty:
            return [], []

        df_comp['fecha_completada'] = pd.to_datetime(
            df_comp['fecha_completada'], errors='coerce'
        )
        df_comp = df_comp.dropna(subset=['fecha_completada'])
        if df_comp.empty:
            return [], []

        hoy = datetime.now()
        etiquetas = []
        cantidades = []

        for i in range(semanas - 1, -1, -1):
            fin_semana = hoy - timedelta(days=i * 7)
            inicio_semana = fin_semana - timedelta(days=6)
            mask = (
                (df_comp['fecha_completada'] >= pd.Timestamp(inicio_semana.date())) &
                (df_comp['fecha_completada'] <= pd.Timestamp(fin_semana.date()))
            )
            cantidad = int(mask.sum())
            etiqueta = fin_semana.strftime('%d/%m')
            etiquetas.append(etiqueta)
            cantidades.append(cantidad)

        return etiquetas, cantidades

    def obtener_semana(self, fecha_referencia=None):
        """
        Devuelve las 7 fechas de la semana (lunes a domingo)
        y las tareas de cada día.

        :param fecha_referencia: cualquier día de la semana a mostrar
        :return: lista de dict {'fecha', 'nombre_dia', 'tareas'}
        """
        if fecha_referencia is None:
            fecha_referencia = datetime.now()
        elif isinstance(fecha_referencia, str):
            fecha_referencia = datetime.strptime(fecha_referencia, '%Y-%m-%d')

        # Lunes = 0 en weekday()
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
