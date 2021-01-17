import json
import urllib.request
from django.core.mail import EmailMessage, send_mail# from django.conf import settings #for importing SHORTCODE_MAX,MIN values from settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.conf import settings
import threading
from .utils import token_generator

from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site

from .forms import SubmitUrlForm
from .models import KirrURL
# Create your views here.
# class EmailThreading(threading.Thread):
#     def __init__(self, email):
#         self.email = email
#         threading.Thread.__init__(self)

#     def run(self):
#         self. email.send(fail_silently=False)


class HomeView(View):
    def get(self, request, *args, **kwargs):
        the_form = SubmitUrlForm()
        context = {
            "title": "Kirr.co",
            "form": the_form
        }

        return render(request, "shortener/home.html", context)

    def post(self, request, *args, **kwargs):
        the_form = SubmitUrlForm(request.POST)
        context = {
            "title": "Kirr.co",
            "form": the_form
        }
        template =  "shortener/home.html"

        if the_form.is_valid():
            user = request.user
            new_url = the_form.cleaned_data['url']
            # print(new_url)
            obj,created = KirrURL.objects.get_or_create(url=new_url, user = user)

            context = {
                "object": obj,
                "created": created,
            }
            if created:
               template = "shortener/success.html"
            else:
               template =  "shortener/already-exists.html"

        return render(request, template, context )



def Kirr_redirect_view(request, shortcode=None, *args, **kwargs): #function based view
    #print(shortcode)
    # current_user = request.user
    obj = get_object_or_404(KirrURL, shortcode=shortcode)
    #obj_url = obj.url
    #try:
     #   obj = KirrURL.objects.get(shortcode=shortcode)
    #except:
     #   obj = KirrURL.objects.all().first()

    #obj_url = None
    #qs = KirrURL.objects.filter(shortcode__iexact=shortcode)
    #if qs.exists() and qs.count() == 1:
    #   obj = qs.first()
    #  obj_url = obj.url
    # print(obj.user_id)
    return HttpResponseRedirect(obj.url)

class URLRedirectView(View): #class based view
    def get(self, request, shortcode=None, *args, **kwargs):
        obj = get_object_or_404(KirrURL, shortcode=shortcode)
        return HttpResponseRedirect(obj.url)

def base(request):
    return render(request,'shortener/home.html')

def logout(request):
    auth.logout(request)
    return redirect('/')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username,password=password)

        if user is not None:
            ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req =  urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())
            ''' End reCAPTCHA validation '''

            if result['success']:
                auth.login(request,user)
                return redirect('/')
            else:
                messages.warning(request, 'Invalid reCAPTCHA. Please try again.')
                return redirect('login')
            # auth.login(request,user)
            # return redirect('/')
            # else:
            #     messages.warning(request,'Please activate your account first')
            #     return redirect('login')

        else:
            messages.warning(request,'Please activate your account first or Invalid Credentials')
            return redirect('login')


    else:
        return render(request,'login.html')


def register(request):

    if request.method == 'POST':
        # first_name = request.POST['first_name']
        # last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        # gender = request.POST['exampleRadios']
        # dateofbirth = request.POST['dob']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        # print(len(password1))

        if password1==password2:
            if User.objects.filter(username=username).exists():
                messages.warning(request,'USERNAME TAKEN')
                return redirect('register')

            elif User.objects.filter(email=email).exists():
                messages.warning(request,'EMAIL TAKEN')
                return redirect('register')

            elif len(email) == 0:
                messages.warning(request,'EMAIL MISSING')
                return redirect('register')

            # elif len(first_name) == 0:
            #     messages.warning(request,'FIRST NAME MISSING')
            #     return redirect('register')

            # elif len(last_name) == 0:
            #     messages.warning(request,'LAST NAME MISSING')
            #     return redirect('register')

            elif len(username) == 0:
                messages.warning(request,'USER NAME MISSING')
                return redirect('register')

            elif len(password1) == 0:
                messages.warning(request,'PASSWORD CANNOT BE EMPTY!!')
                return redirect('register')

            elif len(password1) < 6:
                messages.warning(request,'PASSWORD IS lESS THAN 6 CHARACTERS')
                return redirect('register')

            else:
                user = User.objects.create_user(username=username, password=password1, email=email)
                # newextended = extended(name=username, dateofbirth=dateofbirth, gender=gender, user=user)
                # newextended.save()
                # obj = KirrURL(user = user)
                # obj.save()
                user.is_active = False
                user.save()

                #email sending
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                domain = get_current_site(request).domain
                link = reverse('activate', kwargs={
                                'uidb64': uidb64, 'token': token_generator.make_token(user)})

                activate_url = 'http://' + domain + link
                email_body = 'Hi ' + user.username + \
                    ' Please use this link to verfiy your account\n' + activate_url

                email_subject = 'Activate your account Kirr.co'

                # email = EmailMessage(
                #     email_subject ,
                #     email_body ,
                #     'punchingguy69@gmail.com',
                #     [email],
                # )

                send_mail(email_subject ,
                    email_body ,
                    'punchingguy69@gmail.com',
                    [email],
                    fail_silently=False)
                # EmailThreading(email).start()
                messages.success(request,'USER CREATED')
                return redirect('login')

        else:
            messages.warning(request,'PASSWORD NOT MATCHING!!')
            return redirect('register')

        return redirect('/')

    else:
       return render(request,'register.html')


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                messages.info(request,'User already activated')
                return redirect('login')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()
            messages.info(request,'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')