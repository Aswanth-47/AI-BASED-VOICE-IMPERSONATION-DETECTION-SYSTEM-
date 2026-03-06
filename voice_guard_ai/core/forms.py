from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name', 'autocomplete': 'off'}))
    last_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'autocomplete': 'off'}))
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    password1 = forms.CharField(label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Create Password'}))
    password2 = forms.CharField(label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'autocomplete': 'off'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        if p1 and len(p1) < 8:
            raise forms.ValidationError("Password must be at least 8 characters.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username or Email', 'autocomplete': 'off'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class AudioUploadForm(forms.Form):
    audio_file = forms.FileField(
        label='Upload Audio File',
        help_text='Supported: MP3, WAV, OGG, FLAC, M4A (Max 50MB)',
        widget=forms.FileInput(attrs={'accept': 'audio/*', 'id': 'audioFileInput'})
    )

    ALLOWED_EXTENSIONS = ['mp3', 'wav', 'ogg', 'flac', 'm4a', 'aac', 'wma']
    MAX_SIZE_MB = 50

    def clean_audio_file(self):
        f = self.cleaned_data.get('audio_file')
        if f:
            ext = f.name.rsplit('.', 1)[-1].lower()
            if ext not in self.ALLOWED_EXTENSIONS:
                raise forms.ValidationError(
                    f"Unsupported format. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}")
            if f.size > self.MAX_SIZE_MB * 1024 * 1024:
                raise forms.ValidationError(f"File too large. Max size: {self.MAX_SIZE_MB}MB")
        return f
