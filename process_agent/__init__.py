"""Process Identification Agent.

Prototype d'agent capable d'analyser les artefacts d'une équipe (notes de
réunion, documentation, tickets, comptes-rendus...) afin d'identifier les
processus réellement suivis par cette équipe.
"""

from .models import ProcessRecord

__all__ = ["ProcessRecord"]
