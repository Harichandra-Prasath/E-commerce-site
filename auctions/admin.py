from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Listings)
admin.site.register(Comment)
admin.site.register(Bids)
admin.site.register(Categories)
