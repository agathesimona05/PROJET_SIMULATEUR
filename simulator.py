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

        # ── Méthodes spéciales ────────────────────────────────────────────────

    def __repr__(self) -> str:
        """Représentation technique, utile pour le débogage."""
        return (
            f"SimulationParams("
            f"initial={self.initial}, monthly={self.monthly}, "
            f"rate={self.rate}%, years={self.years}, "
            f"inflation={self.inflation}%, fees={self.fees}%)"
        )

    def __str__(self) -> str:
        """Représentation lisible pour l'utilisateur."""
        return (
            f"Simulation sur {self.years} ans — "
            f"capital initial {self.initial:,.0f} € — "
            f"versement {self.monthly:,.0f} €/mois — "
            f"taux net réel {self.net_rate:.2f} %/an"
        )

    # ── Propriétés calculées ──────────────────────────────────────────────

    @property
    def net_rate(self) -> float:
        """Taux net réel = taux brut − frais − inflation."""
        return self.rate - self.fees - self.inflation

    @property
    def monthly_rate(self) -> float:
        """Taux mensuel net = (taux − frais) / 12."""
        return (self.rate - self.fees) / 100 / 12