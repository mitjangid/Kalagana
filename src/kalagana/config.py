"""Optional configuration from environment variables (and a local ``.env``).

Kalagana needs no configuration to run -- every setting has a sensible default.
This module exists so deployments (a container, a service manager, a developer
shell) can override a few things without editing code.

It is deliberately dependency-free: a tiny ``.env`` parser reads ``KEY=VALUE``
lines from a file and fills only variables that are not already set in the
environment. No third-party package (such as ``python-dotenv``) is required.

Recognised variables (see ``.env.example`` for the full annotated list)
------------------------------------------------------------------------
``KALAGANA_HOST``            server bind address              (default 127.0.0.1)
``KALAGANA_PORT``            server port                      (default 8765)
``KALAGANA_CITY``            default city when none is given  (default delhi)
``KALAGANA_LAT`` / ``KALAGANA_LON``   default coordinates
``KALAGANA_TZ``              default IANA timezone            (default Asia/Kolkata)
``KALAGANA_AYANAMSA``        default ayanamsa                 (default lahiri)
``KALAGANA_TRADITION``       default tradition                (default north)
``KALAGANA_MONTH_SYSTEM``    purnimanta | amanta              (default purnimanta)
``KALAGANA_INCLUDE_MONTHLY`` include monthly observances      (default true)
``KALAGANA_INCLUDE_ISLAMIC`` include Islamic (Hijri) festivals (default true)
``KALAGANA_INCLUDE_FIXED``   include fixed-date national/observance days (default true)
``KALAGANA_FIND_YEARS``      look-ahead for find, in years    (default 3)
``KALAGANA_LANG``            preferred name language          (default en)
``KALAGANA_LOG_REQUESTS``    server request logging           (default true)
``KALAGANA_ENV_FILE``        path to a .env file to load      (default .env)
``KALAGANA_STRICT``          raise on invalid values          (default false)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

__all__ = [
    "Settings",
    "load_settings",
    "load_env_file",
    "DEFAULTS",
    "ENV_PREFIX",
]

ENV_PREFIX = "KALAGANA_"

DEFAULTS: Dict[str, str] = {
    "HOST": "127.0.0.1",
    "PORT": "8765",
    "CITY": "delhi",
    "LAT": "",
    "LON": "",
    "TZ": "Asia/Kolkata",
    "AYANAMSA": "lahiri",
    "TRADITION": "north",
    "MONTH_SYSTEM": "purnimanta",
    "INCLUDE_MONTHLY": "true",
    "INCLUDE_ISLAMIC": "true",
    "INCLUDE_FIXED": "true",
    "FIND_YEARS": "3",
    "LANG": "en",
    "LOG_REQUESTS": "true",
    "ENV_FILE": ".env",
    "STRICT": "false",
}

_TRUE = {"1", "true", "yes", "on", "y", "t"}
_FALSE = {"0", "false", "no", "off", "n", "f", ""}


class ConfigError(ValueError):
    """Raised for an invalid configuration value when strict mode is on."""


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def load_env_file(path: Optional[str] = None, *, override: bool = False) -> Dict[str, str]:
    """Load ``KEY=VALUE`` pairs from a ``.env`` file into ``os.environ``.

    Blank lines and lines beginning with ``#`` are ignored, an optional
    ``export`` prefix is stripped, and surrounding quotes are removed.  By
    default existing environment variables are **not** overwritten.  Returns the
    mapping that was read (which may be empty if the file does not exist).
    """
    env_path = Path(path or os.environ.get(ENV_PREFIX + "ENV_FILE", DEFAULTS["ENV_FILE"]))
    if not env_path.is_file():
        return {}
    loaded: Dict[str, str] = {}
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue
        value = _strip_quotes(value.strip())
        loaded[key] = value
        if override or key not in os.environ:
            os.environ[key] = value
    return loaded


def _get(env: Dict[str, str], name: str, default: str) -> str:
    return env.get(ENV_PREFIX + name, default)


def _get_int(env: Dict[str, str], name: str, default: int, strict: bool) -> int:
    raw = _get(env, name, str(default))
    try:
        return int(raw)
    except ValueError:
        if strict:
            raise ConfigError(f"{ENV_PREFIX}{name}={raw!r} is not an integer") from None
        return default


def _get_bool(env: Dict[str, str], name: str, default: bool, strict: bool) -> bool:
    raw = _get(env, name, "true" if default else "false").strip().lower()
    if raw in _TRUE:
        return True
    if raw in _FALSE:
        return False
    if strict:
        raise ConfigError(f"{ENV_PREFIX}{name}={raw!r} is not a boolean")
    return default


def _get_float(env: Dict[str, str], name: str, strict: bool) -> Optional[float]:
    raw = _get(env, name, "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        if strict:
            raise ConfigError(f"{ENV_PREFIX}{name}={raw!r} is not a number") from None
        return None


@dataclass(frozen=True)
class Settings:
    """Resolved configuration for the server and CLI defaults."""

    host: str = DEFAULTS["HOST"]
    port: int = int(DEFAULTS["PORT"])
    city: str = DEFAULTS["CITY"]
    lat: Optional[float] = None
    lon: Optional[float] = None
    tz: str = DEFAULTS["TZ"]
    ayanamsa: str = DEFAULTS["AYANAMSA"]
    tradition: str = DEFAULTS["TRADITION"]
    month_system: str = DEFAULTS["MONTH_SYSTEM"]
    include_monthly: bool = True
    include_islamic: bool = True
    include_fixed: bool = True
    find_years: int = 3
    lang: str = DEFAULTS["LANG"]
    log_requests: bool = True
    strict: bool = False

    def has_default_location(self) -> bool:
        """True when a fallback location (coordinates, or a city) is configured."""
        return (self.lat is not None and self.lon is not None) or bool(self.city)


def load_settings(
    env: Optional[Dict[str, str]] = None,
    *,
    env_file: Optional[str] = None,
    use_env_file: bool = True,
) -> Settings:
    """Build :class:`Settings` from the environment, optionally loading a ``.env``.

    Pass ``env`` to supply an explicit mapping (handy in tests).  The file is
    only read when ``use_env_file`` is true and ``env`` is not supplied.
    """
    if env is None:
        if use_env_file:
            load_env_file(env_file)
        env = dict(os.environ)

    strict = _get_bool(env, "STRICT", False, False)
    return Settings(
        host=_get(env, "HOST", DEFAULTS["HOST"]),
        port=_get_int(env, "PORT", int(DEFAULTS["PORT"]), strict),
        city=_get(env, "CITY", DEFAULTS["CITY"]),
        lat=_get_float(env, "LAT", strict),
        lon=_get_float(env, "LON", strict),
        tz=_get(env, "TZ", DEFAULTS["TZ"]),
        ayanamsa=_get(env, "AYANAMSA", DEFAULTS["AYANAMSA"]),
        tradition=_get(env, "TRADITION", DEFAULTS["TRADITION"]),
        month_system=_get(env, "MONTH_SYSTEM", DEFAULTS["MONTH_SYSTEM"]),
        include_monthly=_get_bool(env, "INCLUDE_MONTHLY", True, strict),
        include_islamic=_get_bool(env, "INCLUDE_ISLAMIC", True, strict),
        include_fixed=_get_bool(env, "INCLUDE_FIXED", True, strict),
        find_years=_get_int(env, "FIND_YEARS", 3, strict),
        lang=_get(env, "LANG", DEFAULTS["LANG"]),
        log_requests=_get_bool(env, "LOG_REQUESTS", True, strict),
        strict=strict,
    )
