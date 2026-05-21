# tests/test_app_router.py
def test_app_has_page_registry():
    """Test app.py defines PAGE_REGISTRY."""
    import sys
    import importlib.util

    spec = importlib.util.spec_from_file_location("app", "app.py")
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)

    assert hasattr(app_module, "PAGE_REGISTRY")
    assert isinstance(app_module.PAGE_REGISTRY, dict)
    assert len(app_module.PAGE_REGISTRY) >= 6
