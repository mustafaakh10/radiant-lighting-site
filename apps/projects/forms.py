from django import forms

from .models import Enquiry


class EnquiryForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot: bots fill it, people never see it

    class Meta:
        model = Enquiry
        fields = ["name", "phone", "email", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 4, "placeholder": "What are you lighting? Rooms, sizes, timeline…"}),
                   "phone": forms.TextInput(attrs={"inputmode": "tel", "autocomplete": "tel"}),
                   "name": forms.TextInput(attrs={"autocomplete": "name"}),
                   "email": forms.EmailInput(attrs={"autocomplete": "email"})}
