"""Forms for the news application."""

from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
)

from .models import Article
from .models import CustomUser
from .models import Publisher
from .models import Newsletter


class RegisterForm(
    UserCreationForm
):
    """Register an application user."""

    email = forms.EmailField(
        required=True,
    )

    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        required=True,
        label="Account type",
    )

    publisher_name = forms.CharField(
        max_length=150,
        required=False,
        label="Publisher name",
        help_text=(
            "Required only when registering "
            "as a Publisher."
        ),
    )

    publisher_description = (
        forms.CharField(
            required=False,
            label="Publisher description",
            widget=forms.Textarea(
                attrs={
                    "rows": 4,
                }
            ),
        )
    )

    class Meta:
        model = CustomUser

        fields = [
            "username",
            "email",
            "role",
            "publisher_name",
            "publisher_description",
            "password1",
            "password2",
        ]

    def clean(self):
        """Validate Publisher registration."""

        cleaned_data = super().clean()

        role = cleaned_data.get(
            "role"
        )

        publisher_name = (
            cleaned_data.get(
                "publisher_name"
            )
        )

        if (
            role
            == CustomUser.PUBLISHER
            and not publisher_name
        ):
            self.add_error(
                "publisher_name",
                (
                    "A Publisher name is "
                    "required."
                ),
            )

        return cleaned_data

    def save(
        self,
        commit=True,
    ):
        """Create the user and Publisher profile."""

        user = super().save(
            commit=False
        )

        user.email = self.cleaned_data[
            "email"
        ]

        user.role = self.cleaned_data[
            "role"
        ]

        if commit:
            user.save()

            if (
                user.role
                == CustomUser.PUBLISHER
            ):
                Publisher.objects.create(
                    owner=user,
                    name=(
                        self.cleaned_data[
                            "publisher_name"
                        ]
                    ),
                    description=(
                        self.cleaned_data.get(
                            "publisher_description",
                            "",
                        )
                    ),
                )

        return user

    class Meta:
        model = CustomUser

        fields = [
            "username",
            "email",
            "role",
            "password1",
            "password2",
        ]

    def save(
        self,
        commit=True,
    ):
        user = super().save(
            commit=False
        )

        user.email = self.cleaned_data[
            "email"
        ]

        user.role = self.cleaned_data[
            "role"
        ]

        if commit:
            user.save()

        return user


class ArticleForm(forms.ModelForm):
    """Form used to create and edit articles."""

    class Meta:
        model = Article

        fields = [
            "title",
            "content",
            "publisher",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 10,
                }
            ),
        }

    def __init__(
        self,
        *args,
        user=None,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.user = user

        self.fields[
            "publisher"
        ].required = False

        self.fields[
            "publisher"
        ].help_text = (
            "Leave blank for an independent "
            "article."
        )

        if user is None:
            return

        is_editor = (
            user.is_superuser
            or user.role
            == CustomUser.EDITOR
            or user.groups.filter(
                name="Editor"
            ).exists()
        )

        if is_editor:
            self.fields[
                "publisher"
            ].queryset = (
                Publisher.objects.all()
            )

            self.fields[
                "publisher"
            ].disabled = True

        else:
            self.fields[
                "publisher"
            ].queryset = (
                Publisher.objects
                .filter(
                    journalists=user
                )
                .distinct()
            )

    def clean(self):
        """Set ownership before model validation."""

        cleaned_data = super().clean()

        publisher = cleaned_data.get(
            "publisher"
        )

        if (
            self.user
            and (
                self.user.role
                == CustomUser.JOURNALIST
                or self.user.groups.filter(
                    name="Journalist"
                ).exists()
            )
        ):
            if publisher:
                # Publisher article
                self.instance.author = None

            else:
                # Independent article
                self.instance.author = self.user

        return cleaned_data
class NewsletterForm(forms.ModelForm):
    """Form for creating and editing newsletters."""

    class Meta:
        model = Newsletter

        fields = [
            "title",
            "description",
            "articles",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                }
            ),
            "articles": forms.CheckboxSelectMultiple(),
        }

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        # Only published articles should normally
        # appear in a newsletter.
        self.fields[
            "articles"
        ].queryset = (
            Article.objects
            .filter(
                approved=True
            )
            .order_by(
                "-created_at"
            )
        )    

class PublisherEmployeeForm(
    forms.Form
):
    """Add an employee to a Publisher."""

    JOURNALIST = "JOURNALIST"
    EDITOR = "EDITOR"

    EMPLOYEE_CHOICES = [
        (
            JOURNALIST,
            "Journalist",
        ),
        (
            EDITOR,
            "Editor",
        ),
    ]

    employee_type = forms.ChoiceField(
        choices=EMPLOYEE_CHOICES,
    )

    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(),
        label="Registered user",
    )

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            **kwargs,
        )

        self.fields[
            "user"
        ].queryset = (
            CustomUser.objects
            .filter(
                role__in=[
                    CustomUser.JOURNALIST,
                    CustomUser.EDITOR,
                ]
            )
            .order_by(
                "username"
            )
        )

    def clean(self):
        """Check employee role."""

        cleaned_data = super().clean()

        employee_type = (
            cleaned_data.get(
                "employee_type"
            )
        )

        user = cleaned_data.get(
            "user"
        )

        if (
            employee_type
            and user
            and user.role
            != employee_type
        ):
            raise forms.ValidationError(
                (
                    "The selected user's role "
                    "does not match the "
                    "employee type."
                )
            )

        return cleaned_data

            