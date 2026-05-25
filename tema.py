"""
Módulo de temas visuales (claro y oscuro).
Paleta unificada en escala gris, azul y blanco.
"""


TEMA_CLARO = {
    'nombre': 'claro',
    'fondo': '#e8eef4',
    'panel': '#ffffff',
    'texto': '#2d3e50',
    'texto_secundario': '#6b7c93',
    'boton': '#4a6fa5',
    'boton_secundario': '#6b8cae',
    'boton_peligro': '#5a6b7d',
    'boton_texto': '#ffffff',
    'entrada_bg': '#ffffff',
    'entrada_fg': '#2d3e50',
    'resumen_bg': '#f4f7fb',
    'borde': '#c5d0dc',
    'grafica_fondo': '#e8eef4',
    'grafica_ejes': '#2d3e50',
    'grafica_colores': ['#4a6fa5', '#6b8cae', '#9bb3d1', '#b8c9e0'],
    'prioridad': {
        'Alta': '#9bb3d1',
        'Media': '#c5d4e3',
        'Baja': '#e8eef4'
    },
    'semana_hoy': '#c5d4e3',
    'semana_celda': '#ffffff'
}

TEMA_OSCURO = {
    'nombre': 'oscuro',
    'fondo': '#1e2a38',
    'panel': '#2a3a4d',
    'texto': '#e8eef4',
    'texto_secundario': '#9bb3d1',
    'boton': '#5a7eb5',
    'boton_secundario': '#4a6a8a',
    'boton_peligro': '#4a5568',
    'boton_texto': '#ffffff',
    'entrada_bg': '#354a5f',
    'entrada_fg': '#e8eef4',
    'resumen_bg': '#354a5f',
    'borde': '#4a6a8a',
    'grafica_fondo': '#1e2a38',
    'grafica_ejes': '#e8eef4',
    'grafica_colores': ['#5a7eb5', '#6b8cae', '#4a6a8a', '#9bb3d1'],
    'prioridad': {
        'Alta': '#4a6a8a',
        'Media': '#354a5f',
        'Baja': '#2a3a4d'
    },
    'semana_hoy': '#4a6a8a',
    'semana_celda': '#354a5f'
}


def obtener_tema(modo_oscuro=False):
    """Devuelve el diccionario de colores según el modo elegido."""
    if modo_oscuro:
        return TEMA_OSCURO.copy()
    return TEMA_CLARO.copy()
