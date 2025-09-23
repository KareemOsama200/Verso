from django.conf import settings

def site_info(request):
    """Add site information to all templates"""
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Verso Store'),
        'SITE_DOMAIN': getattr(settings, 'SITE_DOMAIN', 'localhost:8000'),
        'MAPBOX_TOKEN': getattr(settings, 'MAPBOX_TOKEN', ''),
        'STRIPE_PUBLIC_KEY': getattr(settings, 'STRIPE_PUBLIC_KEY', ''),
    }