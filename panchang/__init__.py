"""panchang -- offline Drik Panchang and Hindu festival calculator.

Pure standard library, no network, no external data files.  Astronomy is
computed from the Meeus algorithms; calendar and festival rules are data
structures evaluated at runtime.
"""

from __future__ import annotations

__version__ = "0.1.0"

from . import julian, sun, moon, ayanamsa, solver  # noqa: F401

__all__ = ["julian", "sun", "moon", "ayanamsa", "solver", "__version__"]
