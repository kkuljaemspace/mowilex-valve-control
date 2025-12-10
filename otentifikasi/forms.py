from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group

from otentifikasi.models import Profile, AppIdentity, Menu, Submenu


class EditUserForm(forms.ModelForm):
    photo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Profile  # Ubah model menjadi Profile
        fields = ['first_name', 'last_name', 'email', 'photo']  # Tambahkan photo ke fields
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }

    def save(self, commit=True):
        profile = super(EditUserForm, self).save(commit=False)
        if self.cleaned_data['photo']:
            profile.photo = self.cleaned_data['photo']  # photo akan disimpan langsung di profile
        if commit:
            profile.save()  # Simpan instance Profile
        return profile


class EditIdentityForm(forms.ModelForm):
    logo = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = AppIdentity  # Ubah model menjadi Profile
        fields = ['nickname', 'fullname', 'logo']  # Tambahkan photo ke fields
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nickname'}),
            'fullname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fullname'}),
        }

    def save(self, commit=True):
        identity = super(EditIdentityForm, self).save(commit=False)
        if self.cleaned_data['logo']:
            identity.logo = self.cleaned_data['logo']  # photo akan disimpan langsung di profile
        if commit:
            identity.save()  # Simpan instance Profile
        return identity


class AddUserForm(UserCreationForm):
    # Field tambahan
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label='Profile Photo'
    )
    first_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
        label='First Name'
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        label='Last Name'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        label='Email'
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label='Groups'
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter your password'
            }
        )
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm your password'
            }
        )
    )

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'photo', 'groups', 'username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        if self.cleaned_data.get('photo'):
            user.photo = self.cleaned_data['photo']
        if commit:
            user.save()
            # Assign groups setelah user disimpan
            user.groups.set(self.cleaned_data['groups'])
            self.save_m2m()
        return user


class AdminEditUserForm(UserChangeForm):
    password = None  # Menghapus field password dari form edit

    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label='Profile Photo'
    )
    first_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
        label='First Name'
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        label='Last Name'
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        label='Email'
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label='Groups'
    )

    class Meta:
        model = Profile  # Pastikan ini sesuai dengan model user Anda
        fields = ['first_name', 'last_name', 'email', 'photo', 'groups', 'username']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        if self.cleaned_data.get('photo'):
            user.photo = self.cleaned_data['photo']
        if commit:
            user.save()
            user.groups.set(self.cleaned_data['groups'])
            self.save_m2m()
        return user


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['name', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'contoh: ri-home-line',
            }),
        }
        help_texts = {
            'icon': 'Masukkan class name Remix Icon (contoh: ri-home-line). Lihat https://remixicon.com/ untuk ikon yang tersedia.',
        }


class SubmenuForm(forms.ModelForm):
    class Meta:
        model = Submenu
        fields = ['menu', 'name', 'icon', 'url', 'groups']
        widgets = {
            'menu': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'contoh: ri-file-line',
            }),
            'url': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '/path/to/page/',
            }),
            'groups': forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            'icon': 'Masukkan class name Remix Icon (contoh: ri-file-line). Lihat https://remixicon.com/ untuk ikon yang tersedia.',
        }

    def __init__(self, *args, **kwargs):
        super(SubmenuForm, self).__init__(*args, **kwargs)
        # Mengatur field 'menu' agar tidak wajib jika diperlukan
        self.fields['menu'].required = False