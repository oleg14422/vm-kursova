from django import forms
from markdownx.widgets import MarkdownxWidget


class ImageUploadForm(forms.Form):
    image = forms.ImageField()


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=16)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=16, required=True)
    last_name = forms.CharField(max_length=16, required=False, widget=forms.TextInput(attrs={'placeholder': 'Необов\'язково'}))
    password = forms.CharField(widget=forms.PasswordInput())


class ChangeUserDataForm(forms.Form):
    username = forms.CharField(max_length=16)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=16)
    last_name = forms.CharField(max_length=16, required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'maxlength': 120}), required=False)
    request_type = forms.CharField(widget=forms.HiddenInput())


class LoginForm(forms.Form):
    username = forms.CharField(max_length=16)
    password = forms.CharField(widget=forms.PasswordInput())


class CreatePostForm(forms.Form):
    title = forms.CharField(max_length=255)
    short_description = forms.CharField(widget=forms.Textarea(attrs={'maxlength': 127}))
    content = forms.CharField(widget=forms.Textarea())


class CreateCommentForm(forms.Form):
    comment_text = forms.CharField(widget=forms.Textarea)
    request_type = forms.CharField(widget=forms.HiddenInput)


class ChangePasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput())