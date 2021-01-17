from django import forms
from .validators import validate_url, validate_http

class SubmitUrlForm(forms.Form):
    url = forms.CharField(
        label='', 
        validators=[validate_url, validate_http],
        widget = forms.TextInput(
                attrs= {"placeholder": "Long URL",
                         "class": "form-control"    }            
        ) 
        )
    # def clean(self):
    #     cleaned_data = super(SubmitUrlForm, self).clean()
    #     url = cleaned_data['url']
    #     print(url)
    #     url_validator = URLValidator()
    #     try:
    #         url_validator(url)
    #     except:
    #         raise forms.ValidationError("Invalid URL! Try again")
    #     #return url

    def clean_url(self):
        url = self.cleaned_data['url']
        if "http" in url:
            return url
        else:
            return "http://" + url
