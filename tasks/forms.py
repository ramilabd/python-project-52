from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("name", "description", "status", "executor", "labels")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["executor"].label_from_instance = (
            lambda user: user.get_full_name() or user.username
        )
        self.fields["status"].empty_label = "---------"
        self.fields["executor"].empty_label = "---------"
        for name in ("description", "status", "executor", "labels"):
            self.fields[name].widget.attrs["class"] = "w-full"