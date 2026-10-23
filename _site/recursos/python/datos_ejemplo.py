"""Datos sintéticos para el sitio de ejemplo.

Todo lo que sale de aquí es simulado y se dice así en cada página que lo usa: sirve para
mostrar cómo se ven los materiales con la marca, no describe pacientes ni participantes.
"""
import numpy as np
import pandas as pd
from scipy import signal

# ---------------------------------------------------------------------------- Imágenes
_ELIPSES_SHEPP_LOGAN = [  # (intensidad, a, b, x0, y0, ángulo en grados) — versión modificada (Toft)
    (1.0, .69, .92, 0, 0, 0), (-.8, .6624, .874, 0, -.0184, 0),
    (-.2, .11, .31, .22, 0, -18), (-.2, .16, .41, -.22, 0, 18),
    (.1, .21, .25, 0, .35, 0), (.1, .046, .046, 0, .1, 0), (.1, .046, .046, 0, -.1, 0),
    (.1, .046, .023, -.08, -.605, 0), (.1, .023, .023, 0, -.606, 0), (.1, .023, .046, .06, -.605, 0),
]


def shepp_logan(n=256):
    """Fantoma de Shepp-Logan modificado, n x n, valores entre 0 y 1."""
    y, x = np.mgrid[1:-1:n * 1j, -1:1:n * 1j]
    img = np.zeros((n, n))
    for v, a, b, x0, y0, ang in _ELIPSES_SHEPP_LOGAN:
        t = np.radians(ang)
        xr = (x - x0) * np.cos(t) + (y - y0) * np.sin(t)
        yr = -(x - x0) * np.sin(t) + (y - y0) * np.cos(t)
        img[(xr / a) ** 2 + (yr / b) ** 2 <= 1] += v
    return np.clip(img, 0, 1)


def fantoma_uh(n=256, ruido=6.0, semilla=0):
    """El fantoma en unidades Hounsfield aproximadas: aire -1000, LCR ~5, cerebro ~35, hueso ~1000."""
    v = shepp_logan(n)
    y, x = np.mgrid[1:-1:n * 1j, -1:1:n * 1j]
    cabeza = (x / .69) ** 2 + (y / .92) ** 2 <= 1   # elipse exterior: los ventrículos (0) son LCR, no aire
    uh = np.where(cabeza, np.interp(v, [0, .2, .3, 1.0], [5, 35, 60, 1000]), -1000.0)
    uh = uh + np.random.default_rng(semilla).normal(0, ruido, uh.shape)
    return uh


def ventana(uh, ancho, nivel):
    """Ventana y nivel: lleva [nivel - ancho/2, nivel + ancho/2] a [0, 1] y recorta el resto."""
    return np.clip((uh - (nivel - ancho / 2)) / ancho, 0, 1)


# ---------------------------------------------------------------------------- Señales
def ecg_sintetico(fs=500, duracion=10.0, fc=72, semilla=0):
    """ECG sintético (mV) como suma de gaussianas por latido (P, Q, R, S, T).

    Devuelve t, limpio y contaminado (deriva de línea base + interferencia de red de 60 Hz +
    ruido de banda ancha): tres componentes no deseadas con estructuras distintas.
    """
    rng = np.random.default_rng(semilla)
    t = np.arange(0, duracion, 1 / fs)
    ondas = [(.15, -.20, .025), (-.10, -.035, .010), (1.10, 0, .012), (-.25, .035, .012), (.30, .25, .045)]
    limpio = np.zeros_like(t)
    r = 0.35
    while r < duracion:
        for amp, centro, ancho in ondas:
            limpio += amp * np.exp(-((t - r - centro) ** 2) / (2 * ancho ** 2))
        r += 60 / fc * (1 + rng.normal(0, .03))
    deriva = .35 * np.sin(2 * np.pi * .25 * t + .6) + .15 * np.sin(2 * np.pi * .11 * t)
    red = .06 * np.sin(2 * np.pi * 60 * t)
    ruido = rng.normal(0, .015, t.size)
    return t, limpio, limpio + deriva + red + ruido


def semg_sintetico(fs=2000, duracion=6.0, semilla=1):
    """sEMG sintético (mV): ruido de banda 20-450 Hz modulado por tres contracciones.

    Añade interferencia de red (60 Hz y armónicos) y un artefacto de movimiento lento.
    Devuelve t, señal cruda y la activación que la generó (para comparar).
    """
    rng = np.random.default_rng(semilla)
    t = np.arange(0, duracion, 1 / fs)
    activacion = np.zeros_like(t)
    for inicio, fin, nivel in [(.6, 1.8, .55), (2.6, 3.6, 1.0), (4.4, 5.4, .35)]:
        subida = 1 / (1 + np.exp(-(t - inicio) / .05)); bajada = 1 / (1 + np.exp((t - fin) / .05))
        activacion += nivel * subida * bajada
    # Espectro parecido al de un sEMG de superficie: máximo entre 60 y 120 Hz y cola hasta ~400 Hz.
    sos = signal.butter(2, [40, 160], btype="band", fs=fs, output="sos")
    portadora = signal.sosfilt(sos, rng.normal(0, 1, t.size))
    portadora /= portadora.std()
    emg = .4 * (activacion + .03) * portadora
    red = .05 * np.sin(2 * np.pi * 60 * t) + .015 * np.sin(2 * np.pi * 180 * t + .4)
    movimiento = .25 * np.exp(-((t - 2.55) ** 2) / (2 * .08 ** 2)) + .12 * np.sin(2 * np.pi * .7 * t)
    return t, emg + red + movimiento, activacion


# ---------------------------------------------------------------------------- Marcha
PARAMETROS_MARCHA = [  # 13 familias de «Gait Cycle Parameters» (Vicon), unidad, media, DE entre sujetos
    ("Cadencia", "pasos/min", 104, 9), ("Velocidad de marcha", "m/s", 1.10, .18),
    ("Tiempo de zancada", "s", 1.16, .10), ("Tiempo de paso", "s", .58, .05),
    ("Despegue del pie opuesto", "%", 11.5, 1.8), ("Contacto del pie opuesto", "%", 50.2, 1.2),
    ("Despegue del pie", "%", 61.8, 2.0), ("Apoyo simple", "s", .41, .04),
    ("Apoyo doble", "s", .28, .05), ("Longitud de zancada", "m", 1.22, .14),
    ("Longitud de paso", "m", .61, .07), ("Ancho de paso", "m", .11, .03), ("Índice de cojera", "", 1.02, .04),
]
# Diferencia simulada (en DE) de quienes tienen riesgo frente a quienes no; 0 = sin efecto.
_EFECTO = {"Velocidad de marcha": -.95, "Longitud de zancada": -.85, "Longitud de paso": -.7,
           "Apoyo doble": .8, "Cadencia": -.45, "Ancho de paso": .35}
# Variabilidad entre ensayos (en DE entre sujetos): define cuán repetible es cada parámetro.
_RUIDO_ENSAYO = {"Índice de cojera": 1.1, "Despegue del pie opuesto": .85, "Contacto del pie opuesto": .7,
                 "Ancho de paso": .55, "Apoyo doble": .45}


def marcha_sintetica(semilla=7):
    """44 participantes simulados, 5 marchas cada uno, 13 parámetros.

    Desenlace binario como el derivado del SPPB: 16 con riesgo, 26 sin riesgo y 2 sin
    clasificación (quedan fuera: 42 analizables). Devuelve (largo, participantes).
    """
    rng = np.random.default_rng(semilla)
    ids = [f"P{i:02d}" for i in range(1, 45)]
    riesgo = np.array([1] * 16 + [0] * 26 + [-1] * 2)
    rng.shuffle(riesgo)
    filas = []
    latente = rng.normal(0, 1, 44)  # capacidad física común: los parámetros se correlacionan
    for nombre, unidad, media, de in PARAMETROS_MARCHA:
        efecto = _EFECTO.get(nombre, 0.0)
        propio = rng.normal(0, 1, 44)
        carga = .55 if nombre in _EFECTO else .25
        z = carga * latente + np.sqrt(1 - carga ** 2) * propio + efecto * (riesgo == 1) - efecto * 16 / 42
        ruido = _RUIDO_ENSAYO.get(nombre, .3)
        for i, pid in enumerate(ids):
            for e in range(1, 6):
                filas.append((pid, e, nombre, unidad, media + de * (z[i] + rng.normal(0, ruido))))
    largo = pd.DataFrame(filas, columns=["participante", "ensayo", "parametro", "unidad", "valor"])
    etiqueta = np.where(riesgo == 1, "riesgo", np.where(riesgo == 0, "sin riesgo", "sin clasificar"))
    participantes = pd.DataFrame({"participante": ids, "sppb": etiqueta})
    return largo, participantes
