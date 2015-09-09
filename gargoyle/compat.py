try:
    from django.core.cache import caches
    get_cache = caches.__getitem__   # noqa
except ImportError:
    # Django < 1.7
    from django.core.cache import get_cache  # noqa
