from ._hillshade import hillshade, HillshadeSession

def __getattr__(name):
    if name in ("hillshade", "HillshadeSession"):
        try:
            from ._hillshade import hillshade, HillshadeSession  # type: ignore
        except Exception as e:
            raise ImportError(
                f"Failed to import coolproject._hillshade extension: {e}\n"
                "Try rebuilding the extension: `uv run maturin develop --reinstall`"
            ) from e
        globals()["hillshade"] = hillshade
        globals()["HillshadeSession"] = HillshadeSession
        return globals()[name]
    raise AttributeError(name)

__all__ = ["hillshade", "HillshadeSession", "__version__"]
