from django import forms


class RegisterForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"})
    )
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={"placeholder": "username", "autocomplete": "username"}),
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••", "autocomplete": "new-password"}),
    )


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••", "autocomplete": "current-password"})
    )


class ProfileForm(forms.Form):
    full_name = forms.CharField(max_length=120, required=False, widget=forms.TextInput(attrs={"placeholder": "Full name"}))
    bio = forms.CharField(max_length=500, required=False, widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Tell people about yourself"}))
    website = forms.URLField(required=False, widget=forms.URLInput(attrs={"placeholder": "https://yoursite.com"}))
    location = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={"placeholder": "City, Country"}))
    privacy_level = forms.ChoiceField(
        choices=[("public", "Public"), ("followers", "Followers only"), ("private", "Private")]
    )


class AvatarForm(forms.Form):
    avatar = forms.ImageField()
