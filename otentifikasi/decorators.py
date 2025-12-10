# otentifikasi/decorators.py

import logging
from functools import wraps

from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from .models import Submenu

logger = logging.getLogger(__name__)

def submenu_access_required_branch(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Get the current URL
        current_url = request.path
        logger.debug(f"Accessing URL: {current_url}")

        # Extract the base URL for Submenu lookup
        base_url = current_url.rsplit('/', 2)[0] + '/'
        logger.debug(f"Base URL for Submenu lookup: {base_url}")

        # Retrieve the Submenu instance based on 'url' field or other criteria
        # Pastikan bahwa filter ini menggunakan field yang benar
        # Jika Submenu memiliki ForeignKey ke KategoriAlat, gunakan 'kategori_alat' untuk filtering
        submenu = Submenu.objects.filter(url__startswith=base_url).first()
        logger.debug(f"Retrieved Submenu: {submenu}")

        if not submenu:
            logger.warning(f"No Submenu found for URL starting with: {base_url}")
            raise PermissionDenied("Submenu tidak ditemukan.")

        # Retrieve associated groups
        allowed_groups = submenu.groups.all()
        logger.debug(f"Allowed Groups for Submenu '{submenu}': {allowed_groups}")

        # Check if user is superuser
        if request.user.is_superuser:
            logger.debug("User is superuser. Access granted.")
            return view_func(request, *args, **kwargs)

        # Retrieve user's groups
        user_groups = request.user.groups.all()
        logger.debug(f"User Groups: {user_groups}")

        # Check intersection
        if user_groups.intersection(allowed_groups).exists():
            logger.debug("User has required group access. Access granted.")
            return view_func(request, *args, **kwargs)
        else:
            logger.warning("User does not have required group access.")
            raise PermissionDenied("Anda tidak memiliki akses ke submenu ini.")

    return _wrapped_view

def submenu_access_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Mendapatkan URL yang diminta oleh user
        current_url = request.path

        # Mencari submenu yang URL-nya menjadi prefix dari current_url
        # Menggunakan filter dengan startswith
        submenu = Submenu.objects.filter(url__startswith=current_url.rsplit('/', 1)[0] + '/').first()

        # Jika tidak ada submenu yang ditemukan, tolak akses
        if not submenu:
            raise PermissionDenied("Submenu tidak ditemukan.")

        # Jika user adalah superuser, izinkan akses
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        # Mengecek apakah user ada di grup yang diizinkan untuk submenu ini
        user_groups = request.user.groups.all()
        allowed_groups = submenu.groups.all()

        if user_groups.intersection(allowed_groups).exists():
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied("Anda tidak memiliki akses ke submenu ini.")
    return _wrapped_view

def group_required(*group_names):
    """Membatasi akses pengguna ke grup tertentu."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) or u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups)
