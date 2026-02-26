try:
    from importlib.metadata import version

    __version__ = version("logpilot")
except Exception:
    __version__ = "unknown"
