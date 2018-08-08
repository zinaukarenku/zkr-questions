from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

import random, string

from zkr_registration.models import Registree

# Create your models here.

class Party(models.Model):
    #partijos ir visuomeniniai rinkimų komitetai
    name = models.CharField(max_length=100)
    website = models.CharField(max_length=40, null=True)
    logo_name = models.CharField(max_length=40, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)

class AreaType(models.Model):
    #savivaldybė ar vienmandatė?
    area_type = models.CharField(max_length=40)

class Area(models.Model):
    #savivaldybių ir vienmandačių informacija
    proper_name = models.CharField(max_length=100) #tikrasis pavadinimas
    map_name = models.CharField(max_length=40) #frontpage žemėlapio vardas
    area_type = models.ForeignKey(AreaType, on_delete=models.CASCADE) #savivaldybė ar vienmandatė?

    def __str__(self):
        return str(self.proper_name)

class Politician(models.Model):
    full_name = models.CharField(max_length=40)
    email = models.CharField(max_length=40, unique=True) #politiko el. paštas
    biography = models.TextField(null=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE) #politiko partija
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    notifs_allow = models.BooleanField(default=True)
    notifs_activate = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False)
    moderator = models.ForeignKey(User, null=True, related_name='moderated', on_delete=models.CASCADE)
    choices = (
        ('ka', 'Kandidatuoja'),
        ('ne', 'Neišrinktas'),
        ('is', 'Išrinktas'),
    )
    status = models.CharField(max_length=20,choices=choices,default='ka')

    def __str__(self):
        return str(self.full_name)

    def newKey(self):
        try:
            key = self.user.registree.key
            return key
        except Exception:
            key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(40))
            reg = Registree(user=self.user,key=key)
            reg.save()
            return key
    
    def register(self):
        try:
            self.user = User.objects.create_user(self.email, email=self.email)
            self.user.first_name = str(self.full_name)
            self.save()
            return (str(self.email), self.newKey())
        except Exception as e:
            print(self.full_name, e)

    def setne(self):
        self.status = 'ne'
        self.notifs_allow = False
        self.user.set_unusable_password()
        self.save()

    def setis(self):
        self.status = 'is'
        self.save()
    
    def setka(self):
        self.status = 'ka'
        self.save()

class Question(models.Model):
    time = models.DateTimeField(auto_now=True)
    time_added = models.DateTimeField(auto_now_add=True)
    question_text = models.CharField(max_length=500)
    email = models.CharField(max_length=40) #klaususiojo el. paštas
    approval = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    politicians = models.ManyToManyField(Politician) #kurių politikų paklausė
    notifs_allow = models.BooleanField(default=True)
    notifs_activate = models.BooleanField(default=False)

    def __str__(self):
        return str(self.question_text)

class Answer(models.Model):
    time = models.DateTimeField(auto_now=True)
    answer_text = models.TextField()
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE) #kuris politikas atsakė
    question = models.ForeignKey(Question, on_delete=models.CASCADE) #į kurį klausimą atsakė

    def __str__(self):
        return str(self.answer_text)

class Promise(models.Model):
    text = models.TextField()
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE)
    source = models.TextField()

    def __str__(self):
        return '({}) {}'.format(politician.full_name, text)

class Update(models.Model):
    time_added = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    promise = models.ForeignKey(Promise, on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(self.time_added, self.politician)

class Expert(models.Model):
    full_name = models.CharField(max_length=40)
    email = models.CharField(max_length=40, unique=True)
    biography = models.TextField(null=True)
    organisation = models.CharField(max_length=100)
    user = models.OneToOneField(User,null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(full_name)

    def newKey(self):
        try:
            key = self.user.registree.key
        except Exception:
            key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(40))
            reg = Registree(user=self.user,key=key)
            reg.save()
        return key

    def register(self):
        try:
            self.user = User.objects.create_user(self.email, email=self.email)
            self.user.first_name = str(self.full_name)
            self.save()
            return (str(self.email), self.newKey())
        except Exception as e:
            print(self.full_name, e)

class Comment(models.Model):
    time = models.DateTimeField(auto_now=True)
    comment_text = models.TextField()
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return str(comment_text)
