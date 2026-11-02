try:
    from importlib.metadata import version

    __version__ = version("logpilot-cli")
except Exception:
    __version__ = "unknown"
