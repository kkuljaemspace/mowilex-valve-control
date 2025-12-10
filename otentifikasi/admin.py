from django.contrib import admin
from django.contrib.auth.models import User
from import_export.admin import ImportExportModelAdmin

from otentifikasi.models import AppIdentity, Submenu, Menu, Profile

# Register your models here.
admin.site.register(AppIdentity)


class SubmenuAdmin(ImportExportModelAdmin):
    list_display = ('menu', 'name', 'icon', 'url')
    list_filter = ('menu', 'groups')
    search_fields = ('menu__name', 'name')


admin.site.register(Submenu, SubmenuAdmin)


class MenuAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'icon')
    search_fields = ('name', 'icon')


admin.site.register(Menu, MenuAdmin)


class ProfileAdmin(ImportExportModelAdmin):
    list_display = ('username', 'first_name', 'last_name')
    search_fields = ('username', 'first_name', 'last_name')


admin.site.register(Profile, ProfileAdmin)
