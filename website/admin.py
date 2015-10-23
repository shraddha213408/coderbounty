from django.contrib import admin
from website.models import Issue, Watcher, Service, UserProfile, Bounty, UserService, XP, Delta

class ServiceAdmin(admin.ModelAdmin):
     list_display=[] 
     for x in Service._meta.get_all_field_names(): 
         list_display.append(str(x))

class BountyAdmin(admin.ModelAdmin):
    list_display=[] 
    for x in Bounty._meta.get_all_field_names(): 
        list_display.append(str(x))

class WatcherAdmin(admin.ModelAdmin):
    list_display=[] 
    for x in Watcher._meta.get_all_field_names(): 
        list_display.append(str(x))
        
class  XPAdmin(admin.ModelAdmin):
    list_display=[] 
    for x in XP._meta.get_all_field_names(): 
        list_display.append(str(x))

class IssueAdmin(admin.ModelAdmin):
    readonly_fields = ("created","modified")
    
admin.site.register(Issue, IssueAdmin)
admin.site.register(UserService)

admin.site.register(Service, ServiceAdmin)
#admin.site.register(Watcher, WatcherAdmin)
admin.site.register(UserProfile)
admin.site.register(Bounty)
admin.site.register(XP)

# admin.site.register(Delta,
#     list_display = ('user', 'rank', 'price', 'date'),
# )

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

UserAdmin.list_display = ('email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)