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

# ── Validation (méthode privée) ───────────────────────────────────────

    @staticmethod
    def _validate(
        initial: float,
        monthly: float,
        rate: float,
        years: int,
        inflation: float,
        fees: float,
    ) -> None:
        """Valide tous les paramètres, lève ValidationError si besoin."""
        if initial < 0:
            raise ValidationError("Le capital initial ne peut pas être négatif.")
        if monthly < 0:
            raise ValidationError("Le versement mensuel ne peut pas être négatif.")
        if initial == 0 and monthly == 0:
            raise ValidationError(
                "Entrez au moins un capital initial ou un versement mensuel."
            )
        if rate < 0:
            raise ValidationError("Le taux de rendement ne peut pas être négatif.")
        if not (1 <= years <= 100):
            raise ValidationError("La durée doit être comprise entre 1 et 100 ans.")
        if not (0 <= inflation <= 30):
            raise ValidationError("L'inflation doit être comprise entre 0 et 30 %.")
        if not (0 <= fees < rate):
            raise ValidationError(
                "Les frais doivent être ≥ 0 et strictement inférieurs au taux."
            )

# ── Méthodes spéciales ────────────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"SimulationResult("
            f"{len(self)} ans, "
            f"final={self.final_capital:,.0f} €, "
            f"réel={self.final_real:,.0f} €)"
        )

    def __str__(self) -> str:
        return (
            f"Capital final  : {self.final_capital:>14,.2f} €\n"
            f"Capital réel   : {self.final_real:>14,.2f} €\n"
            f"Total investi  : {self.total_invested:>14,.2f} €\n"
            f"Intérêts       : {self.total_interest:>14,.2f} €\n"
            f"Plus-value     : {self.gain_pct:>13.1f} %"
        )

    def __len__(self) -> int:
        """Nombre d'années simulées (sans compter l'année 0)."""
        return len(self.capitals) - 1

    # ── Propriétés calculées ──────────────────────────────────────────────

    @property
    def final_capital(self) -> float:
        """Capital brut à la fin de la simulation."""
        return self.capitals[-1]

    @property
    def final_real(self) -> float:
        """Capital réel final, corrigé de l'inflation cumulée."""
        return self.reals[-1]

    @property
    def total_invested(self) -> float:
        """Montant total versé sur toute la durée."""
        return self.investeds[-1]

    @property
    def total_interest(self) -> float:
        """Intérêts générés = capital final − total investi."""
        return self.final_capital - self.total_invested

    @property
    def gain_pct(self) -> float:
        """Plus-value totale en % par rapport au capital investi."""
        if self.total_invested == 0:
            return 0.0
        return (self.final_capital / self.total_invested - 1) * 100