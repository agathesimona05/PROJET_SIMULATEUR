from __future__ import annotations

import math
import random

# ─────────────────────────────────────────────────────────────────────────────
# EXCEPTIONS PERSONNALISÉES
# ─────────────────────────────────────────────────────────────────────────────

class ValidationError(ValueError):
    """Levée quand les paramètres fournis sont invalides."""
    pass


# ─────────────────────────────────────────────────────────────────────────────
# CLASSE : SimulationParams
# ─────────────────────────────────────────────────────────────────────────────
lass SimulationParams:
    """
    Paramètres d'une simulation d'épargne.

    Valide les données à l'initialisation et expose une représentation
    claire pour le débogage.

    Attributes:
        initial   : Capital de départ en €.
        monthly   : Versement mensuel en €.
        rate      : Taux de rendement annuel brut en %.
        years     : Durée de l'investissement en années.
        inflation : Taux d'inflation annuel en %.
        fees      : Frais de gestion annuels en %.

    Example:
        >>> p = SimulationParams(5000, 200, 7.0, 20, 2.0, 0.5)
        >>> p.net_rate
        6.5
    """

    def __init__(
        self,
        initial: float,
        monthly: float,
        rate: float,
        years: int,
        inflation: float,
        fees: float,
    ) -> None:
        # On valide avant d'assigner — si ça plante, l'objet n'est pas créé
        self._validate(initial, monthly, rate, years, inflation, fees)

        self.initial = float(initial)
        self.monthly = float(monthly)
        self.rate = float(rate)
        self.years = int(years)
        self.inflation = float(inflation)
        self.fees = float(fees)