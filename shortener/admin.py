from django.contrib import admin
# Register your models here.
from .models import KirrURL

class KirrURLAdmin(admin.ModelAdmin):
   list_display = ('user', 'url')
#    def get_user(self,obj):
#        return obj.user

#    get_user.admin_order_field  = 'user' 

admin.site.register(KirrURL, KirrURLAdmin)
# admin.site.register(extended)
