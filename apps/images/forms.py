from django import forms


class BookmarkForm(forms.Form):
    url = forms.URLField(
        widget=forms.URLInput(attrs={"placeholder": "https://example.com/image.jpg"})
    )
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "Give it a title"}),
    )
    description = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Optional description"}),
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "design, photography, nature"}),
        help_text="Comma-separated tags",
    )

    def clean_tags(self) -> list[str]:
        raw = self.cleaned_data.get("tags", "")
        return [t.strip().lower() for t in raw.split(",") if t.strip()]


class UploadForm(forms.Form):
    image = forms.ImageField()
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "Give it a title"}),
    )
    description = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Optional description"}),
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "design, photography, nature"}),
    )

    def clean_tags(self) -> list[str]:
        raw = self.cleaned_data.get("tags", "")
        return [t.strip().lower() for t in raw.split(",") if t.strip()]


class CollectionForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Collection name"}),
    )
    description = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "What's this collection about?"}),
    )
    is_private = forms.BooleanField(required=False, label="Private collection")
