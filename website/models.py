from django.db import models
from string import Template
from django.contrib.auth.models import User
from django.db.models import Sum, Min
from django.utils.timesince import timeuntil
from django.conf import settings
from django.db.models.signals import post_save
import datetime
import urllib
import hashlib
from string import Template
from django.db.models import signals
import random
import urllib2
from actstream import action

YEAR_CHOICES = [(str(yr), str(yr)) for yr in range(1950, 2020)]


class Service(models.Model):
    """
    A web service that allows users to enter issues on projects
    """
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    template = models.CharField(max_length=255)
    regex = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=(('json', 'json'), ('xml', 'xml'), ('http', 'http')))
    api_url = models.CharField(max_length=255, blank=True)
    link_template = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name


class Issue(models.Model):
    """
    An issue from a web service entered into Coder Bounty
    """
    OPEN_STATUS = 'open'
    IN_REVIEW_STATUS = 'in review'
    PAID_STATUS = 'paid'
    STATUS_CHOICES = (
        (OPEN_STATUS, 'open'),
        (IN_REVIEW_STATUS, 'in review'),
        (PAID_STATUS, 'paid'),
    )
    LANGUAGES = (
        ('Java', 'Java'),
        ('C', 'C'),
        ('C++', 'C++'),
        ('PHP', 'PHP'),
        ('VB', 'VB'),
        ('Python', 'Python'),
        ('C#', 'C#'),
        ('JavaScript', 'JavaScript'),
        ('Perl', 'Perl'),
        ('Ruby', 'Ruby'),
        ('HTML', 'HTML'),
    )

    service = models.ForeignKey(Service, related_name='+')
    number = models.IntegerField()
    project = models.CharField(max_length=255)
    user = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='images/projects', blank=True)
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=400)
    language = models.CharField(max_length=255, choices=LANGUAGES, blank=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default=OPEN_STATUS)
    winner = models.ForeignKey(User, related_name="+", null=True, blank=True)
    paid = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    closed_by = models.CharField(max_length=255, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    notified_user = models.BooleanField(default=False)
    views = models.IntegerField(default=1)

    def bounties(self):
        return Bounty.objects.filter(issue=self).order_by('-ends')

    def all_bounties(self):
        return Bounty.objects.filter(issue=self).order_by('-ends')

    def bounty(self):
        return int(self.bounties().aggregate(Sum('price'))['price__sum'] or 0)

    def time_remaining(self):
        if self.status == self.OPEN_STATUS:
            return timeuntil(self.bounties().aggregate(Min('ends'))['ends__min'], datetime.datetime.now()).split(',')[0]
        return timeuntil(self.modified + datetime.timedelta(days=3), datetime.datetime.now()).split(',')[0]

    def html_url(self):
        service = self.service
        template = Template(service.link_template)
        return "http://" + service.domain + template.substitute({'user': self.user, 'project': self.project, 'number': self.number})

    def api_url(self):
        service = self.service
        template = Template(service.template)
        return service.api_url + template.substitute({'user': self.user, 'project': self.project, 'number': self.number})

    def __unicode__(self):
        return "%s issue #%s" % (self.project, self.number)

    def get_absolute_url(self):
        return "/issue/%s" % self.id

    class Meta:
        ordering = ['-created']
        unique_together = ("service", "number", "project")
  

    # there was an issue when saving from admin   
    # def save(self, *args, **kwargs):
    #     #add issue status to activity feed
    #     super(Issue, self).save(*args, **kwargs)
    #     if self.status == Issue.IN_REVIEW_STATUS:
    #         action.send(self.user, verb="is in review now",  target=self.number)
    #     elif self.status == Issue.OPEN_STATUS:
    #         action.send(self.user, verb="opened issue", target=self)
    #     elif self.status == Issue.PAID_STATUS:
    #         action.send(self.user, verb="was paid", target=self.number)

    


class Bounty(models.Model):
    """
    A bounty made on an issue
    """
    user = models.ForeignKey(User)
    issue = models.ForeignKey(Issue)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    ends = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def time_remaining(self):
        if self.issue.status == Issue.OPEN_STATUS:
            return timeuntil(self.ends, datetime.datetime.now()).split(',')[0]
        return timeuntil(self.ends, self.created).split(',')[0]

    def get_twitter_message(self):
        msg = "Added $%s bounty for %s issue %s. http://coderbounty.com/#%s" % (self.price, self.issue.project, self.issue.number, self.issue.id)
        return msg
   
    def save(self, *args, **kwargs):

        if self.pk is None:
            target = self.issue.number
            action.send(self.user, verb='placed a $' + str(self.price) + ' bounty on ', target=self.issue)

        super(Bounty, self).save(*args, **kwargs)


class UserProfile(models.Model):
    CHOICE_PAYMANT_SERVICE = (
        ('wepay', u'WePay'),
    )
    
    user = models.OneToOneField(User, related_name="userprofile")
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_service = models.CharField(max_length=255, null=True, blank=True, choices=CHOICE_PAYMANT_SERVICE)
    payment_service_email = models.EmailField(max_length=255, null=True, blank=True, default='')

    def avatar(self, size=28):
        for account in self.user.socialaccount_set.all():
            if 'avatar_url' in account.extra_data:
                    return account.extra_data['avatar_url']
            elif 'picture' in account.extra_data:
                    return account.extra_data['picture']

        gravatar_url = "http://www.gravatar.com/avatar.php?"
        gravatar_url += urllib.urlencode({'gravatar_id': hashlib.md5(self.user.email.lower()).hexdigest(), 'default': 'retro', 'size': str(size)})
        return gravatar_url

    def avatar_large(self, size=200):
        return self.avatar(size=200)

    def save(self, *args, **kwargs):
        if self.pk is None:
            action.send(self.user, verb='signed up')
        super(UserProfile, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.user.email


def create_profile(sender, **kwargs):
    """
    """
    user = kwargs["instance"]
    if kwargs["created"]:
        profile = UserProfile(user=user)
        profile.save()

post_save.connect(create_profile, sender=User)


TWITTER_MAXLENGTH = getattr(settings, 'TWITTER_MAXLENGTH', 140)


def post_to_twitter(sender, instance, *args, **kwargs):
    """
    Post new saved objects to Twitter.
        models.signals.post_save.connect(post_to_twitter, sender=MyModel)
    """

    # avoid to post the same object twice
    if not kwargs.get('created'):
        return False

    # check if there's a twitter account configured
    import tweepy
    try:
        consumer_key = settings.TWITTER_CONSUMER_KEY
        consumer_secret = settings.TWITTER_CONSUMER_SECRET
        access_key = settings.TWITTER_ACCESS_KEY
        access_secret = settings.TWITTER_ACCESS_SECRET
    except AttributeError:
        print 'WARNING: Twitter account not configured.'
        return False

    # create the twitter message
    try:
        text = instance.get_twitter_message()
    except AttributeError:
        text = unicode(instance)

    mesg = u'%s' % (text)
    if len(mesg) > TWITTER_MAXLENGTH:
        size = len(mesg + '...') - TWITTER_MAXLENGTH
        mesg = u'%s...' % (text[:-size])

    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)
        api.update_status(mesg)
    except urllib2.HTTPError, ex:
        print 'ERROR:', str(ex)
        return False


def delete_issue(sender, instance, *args, **kwargs):
    if Issue.objects.filter(bounty=instance).exists():
        if not instance.issue.bounties().exists():
            instance.issue.delete()


# def alert_winner(instance, created, **kwargs):
#     email_subj = "Issue %s in review"
#     email_text = """----
#     You've resolved the issue! If all checks out in 3 days you'll receive the bounty.
#     Coder Bounty
#     ---"""
#     if not created and instance.winner:
#         if instance.status == instance.IN_REVIEW_STATUS:
#             instance.winner.email_user(email_subj % instance, email_text)

# signals.post_save.connect(alert_winner, sender=Issue)
#todo: fix this so it doesn't throw an error
#signals.post_save.connect(post_to_twitter, sender=Bounty)
signals.post_delete.connect(delete_issue, sender=Bounty)
