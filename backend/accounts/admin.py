from django.contrib import admin
from .models import User, Business, Membership, Role

admin.site.register(User)
admin.site.register(Business)
admin.site.register(Role)
admin.site.register(Membership)