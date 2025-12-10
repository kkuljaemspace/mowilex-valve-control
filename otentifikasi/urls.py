from django.urls import path, include
from . import views

urlpatterns = [
    path('profile', views.profile, name="profile"),
    path('edit-profile', views.edit_profile, name="edit_profile"),
    path('app-identity', views.app_identity, name="app-identity"),
    path('app-identity/edit', views.edit_app_identity, name="edit_app_identity"),
    path('change-password', views.change_password, name='change_password'),
    path('login', views.login, name="login"),
    path('logout', views.logout, name='logout'),

    path('user-management', views.user_management, name='user_management'),
    path('user-management/add', views.add_user_management, name='add_user_management'),
    path('user-management/edit/<int:user_id>/', views.edit_user_management, name='edit_user_management'),
    path('user-management/delete/<int:user_id>/', views.delete_user_management, name='delete_user_management'),

    # Groups
    path('groups/', views.group, name='group'),
    path('groups/add/', views.add_group, name='add_group'),
    path('groups/edit/<int:pk>/', views.edit_group, name='edit_group'),
    path('groups/delete/<int:pk>/', views.delete_group, name='delete_group'),
    # Menus
    path('menus/', views.menu, name='menu'),
    path('menus/add/', views.add_menu, name='add_menu'),
    path('menus/edit/<int:pk>/', views.edit_menu, name='edit_menu'),
    path('menus/delete/<int:pk>/', views.delete_menu, name='delete_menu'),
    # Submenus
    path('submenus/', views.submenu, name='submenu'),
    path('submenus/add/', views.add_submenu, name='add_submenu'),
    path('submenus/edit/<int:pk>/', views.edit_submenu, name='edit_submenu'),
    path('submenus/delete/<int:pk>/', views.delete_submenu, name='delete_submenu'),
]

handler403 = 'otentifikasi.views.permission_denied_view'

