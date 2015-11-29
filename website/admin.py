from django.contrib import admin
from website.models import Issue, Service, UserProfile, Bounty, Solution, Taker, Comment
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class ServiceAdmin(admin.ModelAdmin):
     list_display=[] 
     for x in Service._meta.get_all_field_names(): 
         list_display.append(str(x))

class BountyAdmin(admin.ModelAdmin):
    list_display = ('issue','price','user','created','ends','checkout_id')

class UserProfileAdmin(admin.ModelAdmin):
    list_display=('user','balance','payment_service', 'payment_service_email')

class IssueAdmin(admin.ModelAdmin):
    list_display=[]
    for x in Issue._meta.get_all_field_names():
        if x not in "service_id,winner_id,taker,solution,comment":
            list_display.append(str(x))
    readonly_fields = ("created","modified")
    list_display_links = ("title",)

class TakerAdmin(admin.ModelAdmin):
    list_display=('user','issue','created')


class CommentAdmin(admin.ModelAdmin):
    pass

admin.site.unregister(User)

UserAdmin.list_display = ('id','username','email', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff')
    
admin.site.register(Issue, IssueAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Bounty, BountyAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Solution)
admin.site.register(Taker, TakerAdmin)
admin.site.register(Comment, CommentAdmin)
