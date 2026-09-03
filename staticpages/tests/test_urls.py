import importlib


def test_api_url_modules_import_without_missing_view_actions():
    for module_name in (
        'staticpages.urls',
        'products.urls',
        'payment.urls',
    ):
        importlib.import_module(module_name)
