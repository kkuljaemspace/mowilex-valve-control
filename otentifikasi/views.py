from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import auth, Group
from django.contrib import messages
from django.urls import reverse

from .forms import EditUserForm, EditIdentityForm, AddUserForm, AdminEditUserForm, GroupForm, MenuForm, SubmenuForm
from .models import AppIdentity, Profile, Menu, Submenu
from .decorators import group_required, submenu_access_required


# user management
def is_admin(user):
    return user.is_superuser


# Identity
@login_required
@user_passes_test(is_admin)
def app_identity(request):
    identity = get_object_or_404(AppIdentity, id=1)
    form1 = EditIdentityForm(instance=identity)
    return render(request, 'otentifikasi/app_identity.html', {'form1': form1})


@login_required
@user_passes_test(is_admin)
def edit_app_identity(request):
    identity = get_object_or_404(AppIdentity, id=1)
    if request.method == 'POST':
        form1 = EditIdentityForm(request.POST, request.FILES, instance=identity)
        if form1.is_valid():
            form1.save()
            messages.success(request, 'App Identity berhasil diperbarui.')
            return redirect('/app-identity')
    return redirect('/app-identity')


# user profile
@login_required
def profile(request):
    form1 = EditUserForm(instance=request.user)
    return render(request, 'otentifikasi/profile.html', {'form1': form1})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form1 = EditUserForm(request.POST, request.FILES, instance=request.user)
        if form1.is_valid():
            form1.save()
            messages.success(request, 'Profil berhasil diperbarui.')
            return redirect('profile')
    return redirect('profile')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Agar sesi tidak keluar setelah ubah password
            messages.success(request, 'Password berhasil diubah.')
            return redirect('profile')
    return redirect('profile')


# entering the app
def login(request):
    user = request.user
    if user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('/')
            else:
                messages.info(request, 'Credentials Invalid')
                return redirect('login')
        else:
            return render(request, 'otentifikasi/login.html')


def logout(request):
    auth.logout(request)
    return redirect('login')


@login_required
def user_management(request):
    # Mendapatkan parameter sort dan order dari URL
    sort = request.GET.get('sort', 'username')  # default sort by 'username'
    order = request.GET.get('order', 'asc')

    # Validasi kolom yang bisa di-sort
    valid_sort_fields = ['username', 'first_name', 'last_name', 'email', 'last_login']
    if sort not in valid_sort_fields:
        sort = 'username'

    # Menentukan urutan pengurutan
    if order == 'desc':
        sort_order = '-' + sort
    else:
        sort_order = sort

    # Mengambil daftar users dari database
    users = Profile.objects.all().order_by(sort_order)

    # Implementasi pagination (opsional)
    paginator = Paginator(users, 10)  # 10 users per halaman
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Menentukan urutan berikutnya untuk toggling
    if order == 'asc':
        next_order = 'desc'
    else:
        next_order = 'asc'

    context = {
        'users': page_obj,
        'current_sort': sort,
        'current_order': order,
        'next_order': next_order,
    }

    return render(request, 'otentifikasi/user_management.html', context)


@login_required
@user_passes_test(is_admin)
def add_user_management(request):
    if request.method == 'POST':
        adduserformpost = AddUserForm(request.POST)
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Cek apakah password cocok
        if password1 and password2 and password1 == password2:
            if adduserformpost.is_valid():
                user = adduserformpost.save()  # Simpan form dan ambil user yang disimpan
                messages.success(request, f"User {user.username} has been added.")
                return redirect(reverse('user_management'))  # Gunakan reverse untuk nama URL
            else:
                # Tampilkan pesan kesalahan form
                messages.warning(request, f"Invalid data: {adduserformpost.errors}")
        else:
            messages.info(request, "Passwords do not match.")

        return redirect(reverse('add_user_management'))  # Redirect kembali ke halaman form

    # Jika bukan POST, tampilkan form kosong
    adduserform = AddUserForm()
    context = {
        'adduserform': adduserform,
    }
    return render(request, 'otentifikasi/add_user_management.html', context)


@login_required
@user_passes_test(is_admin)
def edit_user_management(request, user_id):
    user = get_object_or_404(Profile, id=user_id)  # Ambil user berdasarkan ID

    if request.method == 'POST':
        edituserform = AdminEditUserForm(request.POST, request.FILES, instance=user)

        if edituserform.is_valid():
            edituserform.save()
            messages.success(request, f"User {user.username} has been updated.")
            return redirect(reverse('user_management'))
        else:
            messages.warning(request, f"Invalid data: {edituserform.errors}")

        return redirect(reverse('edit_user_management', args=[user_id]))

    else:
        edituserform = AdminEditUserForm(instance=user)
        context = {
            'edituserform': edituserform,
            'user': user,
        }
        return render(request, 'otentifikasi/edit_user_management.html', context)


@login_required
@user_passes_test(is_admin)
def delete_user_management(request, user_id):
    user = get_object_or_404(Profile, id=user_id)

    if request.method == 'POST':
        user.delete()
        messages.success(request, f"User {user.username} has been deleted.")
        return redirect(reverse('user_management'))

    context = {
        'user': user,
    }
    return render(request, 'otentifikasi/delete_user_management.html', context)


@login_required
@user_passes_test(is_admin)
def add_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group')
    else:
        form = GroupForm()
    return render(request, 'otentifikasi/user_access/add_group.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def add_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group')
    else:
        form = GroupForm()
    return render(request, 'otentifikasi/user_access/add_group.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def group(request):
    groups = Group.objects.all()
    return render(request, 'otentifikasi/user_access/group.html', {'groups': groups})


@login_required
@user_passes_test(is_admin)
def edit_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group')
    else:
        form = GroupForm(instance=group)
    return render(request, 'otentifikasi/user_access/edit_group.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def delete_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('group')
    return render(request, 'otentifikasi/user_access/delete_group.html', {'group': group})


# --------------------------------HANYA ADMIN
# 2. Halaman membuat Menu
@login_required
@user_passes_test(is_admin)
def menu(request):
    search_query = request.GET.get('q', '')
    if search_query:
        menus = Menu.objects.filter(name__icontains=search_query)
    else:
        menus = Menu.objects.all()
    return render(request, 'otentifikasi/user_access/menu.html', {'menus': menus, 'search_query': search_query})


@login_required
@user_passes_test(is_admin)
def add_menu(request):
    if request.method == 'POST':
        form = MenuForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('menu')
    else:
        form = MenuForm()
    return render(request, 'otentifikasi/user_access/add_menu.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def edit_menu(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
            return redirect('menu')
    else:
        form = MenuForm(instance=menu)
    return render(request, 'otentifikasi/user_access/edit_menu.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def delete_menu(request, pk):
    menu = get_object_or_404(Menu, pk=pk)
    if request.method == 'POST':
        menu.delete()
        return redirect('menu')
    return render(request, 'otentifikasi/user_access/delete_menu.html', {'menu': menu})


# 3. Halaman membuat submenu dan akses berdasarkan groups
@login_required
@user_passes_test(is_admin)
def submenu(request):
    search_query = request.GET.get('q', '')
    if request.user.is_superuser:
        submenus = Submenu.objects.all()
    else:
        user_groups = request.user.groups.all()
        submenus = Submenu.objects.filter(groups__in=user_groups).distinct()
    if search_query:
        submenus = submenus.filter(name__icontains=search_query)
    return render(request, 'otentifikasi/user_access/submenu.html',
                  {'submenus': submenus, 'search_query': search_query})


@login_required
@user_passes_test(is_admin)
def add_submenu(request):
    if request.method == 'POST':
        form = SubmenuForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('submenu')
    else:
        form = SubmenuForm()
    return render(request, 'otentifikasi/user_access/add_submenu.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def edit_submenu(request, pk):
    submenu = get_object_or_404(Submenu, pk=pk)
    if request.method == 'POST':
        form = SubmenuForm(request.POST, instance=submenu)
        if form.is_valid():
            form.save()
            return redirect('submenu')
    else:
        form = SubmenuForm(instance=submenu)
    return render(request, 'otentifikasi/user_access/edit_submenu.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def delete_submenu(request, pk):
    submenu = get_object_or_404(Submenu, pk=pk)
    if request.method == 'POST':
        submenu.delete()
        return redirect('submenu')
    return render(request, 'otentifikasi/user_access/delete_submenu.html', {'submenu': submenu})


def permission_denied_view(request, exception):
    return render(request, '403.html', status=403)
