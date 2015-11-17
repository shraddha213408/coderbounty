from django import forms
from .models import Issue,Bounty,UserProfile
from django.contrib.auth.models import User

class IssueCreateForm(forms.ModelForm):

    class Meta:
        model = Issue
        fields = ('title','language','content')

class BountyCreateForm(forms.ModelForm):

    class Meta:
        model = Bounty
        fields = ('price',)


class UserProfileForm(forms.ModelForm):
    user = forms.IntegerField(label="", widget=forms.HiddenInput(), required=False)
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(required=False, label="Last Name")
    email = forms.EmailField(label="Email", max_length=255)
    
    class Meta:
        model = UserProfile
        exclude = ('balance',)

    def clean(self):
        cleaned_data=super(UserProfileForm, self).clean()
        user_id = cleaned_data.get("user")
        user = User.objects.get(id=user_id)
        user.first_name = cleaned_data.get("first_name")
        user.last_name = cleaned_data.get("last_name")
        user.email = cleaned_data.get("email")
        user.save()

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
    	user = kwargs['instance'].user
        
        if user.pk:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email