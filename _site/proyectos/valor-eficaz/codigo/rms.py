"""Ejemplo de valor eficaz con datos sintéticos; solo biblioteca estándar."""

from math import sqrt


def valor_eficaz(senal):
    """Calcula el RMS de una secuencia no vacía de números reales."""
    if not senal:
        raise ValueError("La señal debe contener al menos una observación.")
    return sqrt(sum(valor ** 2 for valor in senal) / len(senal))


if __name__ == "__main__":
    senal = [0.2, -0.1, 0.4, -0.2]
    print(f"RMS: {valor_eficaz(senal):.3f}")
