from django.conf import settings #for importing SHORTCODE_MAX,MIN values from settings
import random
import string

#for activation email
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

SHORTCODE_MIN = getattr(settings, "SHORTCODE_MIN", 6) #the value of SHORTCODE_MIN from settings and if it not there then bydefault 6

def code_generator(size=SHORTCODE_MIN, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def  create_shortcode(instance, size=SHORTCODE_MIN):
    new_code = code_generator(size=size)
    Klass = instance.__class__
    qs_exits = Klass.objects.filter(shortcode=new_code).exists()
    if qs_exits:
        return create_shortcode(size=size) #to remove warning paste this before size (instance.__class__,)
    return new_code

#email activation
class AppTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_vaule(self,user, timestamp):
        return (text_type(user.is_active)+text_type(user.pk)+text_type(timestamp))

token_generator = AppTokenGenerator()