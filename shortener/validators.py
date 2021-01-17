from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

def validate_url(value):
    url_validator = URLValidator()
    reg_val = value
    if "http" in reg_val:
        new_val = reg_val
    else:
        new_val = "http://" + value
    try:
        url_validator(new_val)
    except:
        raise ValidationError("Invalid URL")
    return new_val

def validate_http(value):
    if not "https://" in value:
        if not "http://" in value:
            # raise ValidationError(" Invalid url!, try again with proper url")
             return value