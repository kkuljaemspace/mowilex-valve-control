from .models import AppIdentity

from .models import Menu, Submenu
from django.db.models import Q

def app_identity(request):
    try:
        identity = AppIdentity.objects.first()
    except AppIdentity.DoesNotExist:
        identity = None
    return {
        'app_identity': identity
    }

def menu_context(request):
    menu_list = []
    if request.user.is_authenticated:
        user_groups = request.user.groups.all()
        menus = Menu.objects.all().prefetch_related('submenus__groups')
        for menu in menus:
            submenus = menu.submenus.filter(
                Q(groups__in=user_groups) | Q(groups__isnull=True)
            ).distinct()
            if submenus.exists():
                menu_list.append({'menu': menu, 'submenus': submenus})
    else:
        # Untuk pengguna anonim, hanya tampilkan submenu tanpa pembatasan grup
        menus = Menu.objects.all().prefetch_related('submenus__groups')
        for menu in menus:
            submenus = menu.submenus.filter(groups__isnull=True)
            if submenus.exists():
                menu_list.append({'menu': menu, 'submenus': submenus})
    return {'menu_list': menu_list}
