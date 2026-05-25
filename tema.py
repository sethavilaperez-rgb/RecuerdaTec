"""
Módulo de temas visuales (claro y oscuro).
Centraliza los colores para aplicar modo oscuro fácilmente.
"""


TEMA_CLARO = {
    'nombre': 'claro',
    'fondo': '#f0f4f8',
    'panel': '#ffffff',
    'texto': '#2c3e50',
    'texto_secundario': '#7f8c8d',
    'boton': '#4a90d9',
    'boton_texto': '#ffffff',
    'entrada_bg': '#ffffff',
    'entrada_fg': '#2c3e50',
    'grafica_fondo': '#f0f4f8',
    'grafica_ejes': '#2c3e50',
    'prioridad': {
        'Alta': '#ffcccc',
        'Media': '#fff3cd',
        'Baja': '#cce5ff'
    },
    'semana_hoy': '#d4edda',
    'semana_celda': '#ffffff'
}

TEMA_OSCURO = {
    'nombre': 'oscuro',
    'fondo': '#1a1a2e',
    'panel': '#16213e',
    'texto': '#eaeaea',
    'texto_secundario': '#a0a0b0',
    'boton': '#4a90d9',
    'boton_texto': '#ffffff',
    'entrada_bg': '#0f3460',
    'entrada_fg': '#eaeaea',
    'grafica_fondo': '#1a1a2e',
    'grafica_ejes': '#eaeaea',
    'prioridad': {
        'Alta': '#5c2a2a',
        'Media': '#5c4a1a',
        'Baja': '#1a3a5c'
    },
    'semana_hoy': '#1a4d3a',
    'semana_celda': '#0f3460'
}


def obtener_tema(modo_oscuro=False):
    """
    Devuelve el diccionario de colores según el modo elegido.

    :param modo_oscuro: True para tema oscuro, False para claro
    """
    if modo_oscuro:
        return TEMA_OSCURO.copy()
    return TEMA_CLARO.copy()
