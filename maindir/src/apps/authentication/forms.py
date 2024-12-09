# from django import forms
# from django.contrib.auth import get_user_model
# from django.contrib.auth.forms import UserCreationForm
# from django.utils.translation import gettext_lazy as _
#
# User = get_user_model()
#
#
# class PasswordForm(forms.Form):
#     password = forms.CharField(
#         label='',
#         required=True,
#         widget=forms.PasswordInput(attrs={
#             'class': 'login__input',
#             'placeholder': 'Введите пароль'
#         })
#     )
#
#     def clean_password(self):
#         password = self.cleaned_data.get('password')
#         # Проверка, что пароль состоит из 4 цифр
#         if len(password) != 4 or not password.isdigit():
#             raise forms.ValidationError('Пароль должен состоять из 4 цифр.')
#         return password
#
#
#
#
# class UpdateFirstNameForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['first_name']
#         widgets = {
#             'first_name': forms.TextInput(attrs={'class': 'login__input'}),
#         }
#         labels = {
#             'first_name': '',
#         }
