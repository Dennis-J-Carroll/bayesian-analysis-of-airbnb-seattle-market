# tests/test_pages.py
def test_overview_page_structure():
    """Test overview page has required render function."""
    from dashboard.pages import overview

    assert hasattr(overview, "render")
    assert callable(overview.render)


def test_all_pages_have_render():
    """Test all pages export a render() function."""
    pages = [
        "overview",
        "neighborhood",
        "prediction",
        "market_intel",
        "business_strategy",
        "model_insights",
    ]

    for page_name in pages:
        module = __import__(f"dashboard.pages.{page_name}", fromlist=["render"])
        assert hasattr(module, "render")
        assert callable(module.render)
