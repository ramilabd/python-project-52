from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username")

    def clean_username(self):
        username = self.cleaned_data["username"]
        exists = (
            User.objects.filter(username__iexact=username)
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if exists:
            raise ValidationError(
                self.instance.unique_error_message(User, ["username"])
            )
        return username