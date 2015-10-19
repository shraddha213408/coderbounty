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
    )

    service = models.ForeignKey(Service, related_name='+', null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
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
    notified_user = models.BooleanField(default=None)

    def bounties(self):
        if self.status == self.OPEN_STATUS:
            return Bounty.objects.filter(issue=self, ends__gt=datetime.datetime.now()).order_by('-ends')
        return Bounty.objects.filter(issue=self).order_by('-ends')

    def all_bounties(self):
        return Bounty.objects.filter(issue=self).order_by('-ends')

    def bounty(self):
        return int(self.bounties().aggregate(Sum('price'))['price__sum'] or 0)

    def time_remaining(self):
        if self.status == self.OPEN_STATUS:
            return timeuntil(self.bounties().aggregate(Min('ends'))['ends__min'], datetime.datetime.now()).split(',')[0]
        return timeuntil(self.modified + datetime.timedelta(days=3), datetime.datetime.now()).split(',')[0]

    def watchers(self):
        return Watcher.objects.filter(issue=self)

    def html_url(self):
        service = self.service
        template = Template(service.link_template)
        return "http://" + service.domain + template.substitute({'user': self.user, 'project': self.project, 'number': self.number})

    def api_url(self):
        service = self.service
        template = Template(service.template)
        return service.api_url + template.substitute({'user': self.user, 'project': self.project, 'number': self.number})

    def __unicode__(self):
        return "%s - %s" % (self.number, self.project)

    class Meta:
        unique_together = ("service", "number", "project")


class Bounty(models.Model):
    """
    A bounty made on an issue
    """
    user = models.ForeignKey(User, null=True, blank=True)
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


class Watcher(models.Model):
    user = models.ForeignKey(User)
    issue = models.ForeignKey(Issue)
    bounty = models.BooleanField(default=None)
    status = models.BooleanField(default=None)


class UserService(models.Model):
    user = models.ForeignKey(User)
    service = models.ForeignKey(Service, related_name='+')
    username = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return self.username

    class Meta:
        unique_together = ("user", "service")


class XP(models.Model):
    user = models.ForeignKey(User)
    points = models.IntegerField()
    what_for = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=(('coder', 'coder'), ('owner', 'owner')), null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

#class Badge(models.Model):
#    icon = models.ImageField(upload_to='static/images/badges', blank=True)
#    name = models.CharField(max_length=255)
#    message = models.CharField(max_length=255)
#    how_to = models.CharField(max_length=255)

#class UserBadge(models.Model):
#    user = models.ForeignKey(User)
#    badge = models.ForeignKey(Badge)
#    created = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_service = models.CharField(max_length=255, null=True, blank=True)
    payment_service_email = models.CharField(max_length=255, null=True, blank=True, default='')
    coins = models.IntegerField(default=0)

    @property
    def gravatar(self, size=28):
        gravatar_url = "http://www.gravatar.com/avatar.php?"
        gravatar_url += urllib.urlencode({'gravatar_id': hashlib.md5(self.user.email.lower()).hexdigest(), 'default': 'retro', 'size': str(size)})
        return gravatar_url

    def xp(self):
        return XP.objects.filter(user=self.user).aggregate(Sum('points'))['points__sum']

    def gravatar_large(self, size=200):
        return self.gravatar(size=200)

    def gravatar_winner(self, size=23):
        return self.gravatar(size=23)

    def github_username(self):
        service = Service.objects.get(name="Github")
        return UserService.objects.get(user=self.user, service=service)

    def google_code_username(self):
        service = Service.objects.get(name="Google Code")
        return UserService.objects.get(user=self.user, service=service)

    def bitbucket_username(self):
        service = Service.objects.get(name="Bitbucket")
        return UserService.objects.get(user=self.user, service=service)


    def save(self, *args, **kwargs):
        from actstream import action
        #if new user signs up add it to the activity feed
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


class DeltaManager(models.Manager):
    def get_random_user(self):
        ''' generate a random user to send out the delta '''
        rank_min = self.get_query_set().aggregate(Min('rank'))['rank__min']
        delta = random.choice(self.get_query_set().filter(rank=rank_min))
        delta.rank += 1
        delta.price = 5
        delta.date = datetime.datetime.now()
        delta.save()
        return delta.user

    def cleanup(self):
        ''' clean up the delta not used over 24hours '''
        day_before = datetime.datetime.now() - datetime.timedelta(seconds=86400 - 5)
        for delta in self.get_query_set().filter(price__gt=0).filter(date__lt=day_before):
            delta.price = 0
            delta.save()


class Delta(models.Model):
    user = models.ForeignKey(User, unique=True)
    rank = models.IntegerField(default=0)
    date = models.DateTimeField(default=datetime.datetime.now)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    objects = DeltaManager()


def on_new_user(instance, created, **kwargs):
    if created:
        Delta.objects.get_or_create(user=instance)


TWITTER_MAXLENGTH = getattr(settings, 'TWITTER_MAXLENGTH', 140)


def post_to_twitter(sender, instance, *args, **kwargs):
    """
    Post new saved objects to Twitter.

    Example:
        from django.db import models

        class MyModel(models.Model):
            text = models.CharField(max_length=255)
            link = models.CharField(max_length=255)

            def __unicode__(self):
                return u'%s' % self.text

            def get_absolute_url(self):
                return self.link

            # the following method is optional
            def get_twitter_message(self):
                return u'my-custom-twitter-message: %s - %s' \
                        % (self.text, self.link)

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


def alert_winner(instance, created, **kwargs):
    email_subj = "Issue %s in review"
    email_text = """----
    You've resolved the issue! If all checks out in 3 days you'll receive the bounty.
    Coder Bounty
    ---"""
    if not created and instance.winner:
        if instance.status == instance.IN_REVIEW_STATUS:
            instance.winner.email_user(email_subj % instance, email_text)

signals.post_save.connect(on_new_user, sender=User)
signals.post_save.connect(alert_winner, sender=Issue)
#todo: fix this so it doesn't throw an error
#signals.post_save.connect(post_to_twitter, sender=Bounty)
signals.post_delete.connect(delete_issue, sender=Bounty)


# class CoinManager(models.Manager):
#     def add_coin_for_user(self, user, request=None):
#         try:
#             cookie_coins = int(request.COOKIES.get('coins', 0))
#         except:
#             cookie_coins = 0

#         day_of_year = int(datetime.datetime.strftime(datetime.datetime.now(), "%j"))
#         obj, created = self.get_query_set().get_or_create(user=user)
#         if obj.day_of_year != day_of_year:
#             # update UserProfile set coins +1
#             try:
#                 user_profile = user.get_profile()
#                 if user_profile.coins == 0 and cookie_coins > 0:
#                     user_profile.coins = cookie_coins
#                 user_profile.coins += 1
#                 user_profile.save()
#             except UserProfile.DoesNotExist:
#                 return False
#             else:
#                 # save the newest day of year
#                 obj.day_of_year = day_of_year
#                 obj.save()
#                 return True
#         return False


# class Coin(models.Model):
#     user = models.OneToOneField(User)
#     day_of_year = models.PositiveIntegerField(default=0)
#     #objects = CoinManager()
