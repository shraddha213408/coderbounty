from django import forms
from .models import Issue,Bounty

class IssueCreateForm(forms.ModelForm):

    class Meta:
        model = Issue
        fields = ('title','language','content')

class BountyCreateForm(forms.ModelForm):

    class Meta:
        model = Bounty
        fields = ('price',)
