"""Config + active-project resolution for the seo-geo-report-engine framework.

Merge order (lowest to highest priority):
    config/framework.yml  <  projects/<name>/client.yml  <  env  <  CLI args

Usage:
    from lib.config import load
    cfg = load(project="demo")   # or None to auto-resolve
    cfg.project           -> "demo" | None
    cfg.get("brand.accent")
    cfg.client            -> dict from client.yml
    cfg.project_dir       -> Path to projects/<name>
"""
from __future__ import annotations

import os
from pathlib import Path

from . import yaml_min


def root() -> Path:
    # tools/lib/config.py -> framework root
    return Path(__file__).resolve().parents[2]


def load_yaml(path) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    data = yaml_min.safe_load(p.read_text(encoding="utf-8"))
    return data or {}


def load_env(path) -> dict:
    """Parse a .env file into a dict and populate os.environ (without clobbering)."""
    p = Path(path)
    out = {}
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        out[k] = v
        os.environ.setdefault(k, v)
    return out


def active_profile() -> str:
    """Which secrets profile is active: MKT_PROFILE env > config/active-profile file > 'personal'."""
    p = os.environ.get("MKT_PROFILE")
    if p and p.strip():
        return p.strip()
    f = root() / "config" / "active-profile"
    if f.exists():
        v = f.read_text(encoding="utf-8").strip()
        if v:
            return v
    return "personal"


def load_secrets() -> str:
    """Load the active profile's secrets over the shared base. Returns the profile name.

    Layout: config/secrets.env holds keys shared by every profile (Ahrefs, OpenRouter, ...);
    config/secrets.<profile>.env holds per-profile keys (e.g. DataForSEO for personal vs business).
    The profile file loads FIRST so its values win (load_env uses setdefault), then the shared base.
    """
    r = root()
    prof = active_profile()
    load_env(r / "config" / f"secrets.{prof}.env")
    load_env(r / "config" / "secrets.env")
    return prof


def deep_merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def resolve_project(name=None, projects_dir="projects"):
    if name:
        return name
    if os.environ.get("MKT_PROJECT"):
        return os.environ["MKT_PROJECT"]
    try:
        rel = Path.cwd().resolve().relative_to(root() / projects_dir)
        return rel.parts[0]
    except Exception:
        return None


class Config:
    def __init__(self, framework, client, project, projects_dir, profile=None):
        self.framework = framework or {}
        self.client = client or {}
        self.project = project
        self.profile = profile
        self._projects_dir = projects_dir
        # brand: framework defaults overridden by client.brand
        self._merged = deep_merge(self.framework, {"client": self.client})

    @property
    def root(self) -> Path:
        return root()

    @property
    def project_dir(self):
        return (root() / self._projects_dir / self.project) if self.project else None

    def brand(self) -> dict:
        return deep_merge(self.framework.get("brand", {}), self.client.get("brand", {}))

    def get(self, dotted, default=None):
        """Look up 'a.b.c' in client first, then framework defaults."""
        for source in (self.client, self.framework):
            cur = source
            ok = True
            for part in dotted.split("."):
                if isinstance(cur, dict) and part in cur:
                    cur = cur[part]
                else:
                    ok = False
                    break
            if ok:
                return cur
        return default

    def as_dict(self):
        return {
            "project": self.project,
            "profile": self.profile,
            "project_dir": str(self.project_dir) if self.project_dir else None,
            "framework": self.framework,
            "client": self.client,
        }


def load(project=None) -> Config:
    r = root()
    framework = load_yaml(r / "config" / "framework.yml")
    prof = load_secrets()
    pdir = framework.get("projects_dir", "projects")
    proj = resolve_project(project, pdir)
    client = {}
    if proj:
        client = load_yaml(r / pdir / proj / "client.yml")
    return Config(framework, client, proj, pdir, profile=prof)
