from django.db import models
from django.contrib.auth.models import User

from klausimai.models import Politician as OldPol

# Create your models here.

#narių grupės modelis
#visas frakcijas, laikinąsias grupes, komisijas etc generalizuojam kaip grupes
class Group(models.Model):
    name = models.CharField(max_length = 255, unique = True)
    frac_name = models.CharField(max_length = 40, null = True, blank = True)
    description = models.TextField(null = True, blank = True)
    grouptype = models.CharField(
        max_length = 2,
        choices = (
            ('fr', 'Frakcija'),
            ('pg', 'Parlamentinė grupė'),
            ('ks', 'Komisija'),
            ('km', 'Komitetas'),
            ('pa', 'Pakomitetis'),
            ('dg', 'Delegacija'),
        ),
        null = True,
    )

    def __str__(self):
        return self.name

#politiko modelis
#didžiąją dalį informacijos šiems objektams surenka mūsų robotai
#išskyrus active, user, oldpol, description
class Politician(models.Model):
    name = models.CharField(max_length = 100, null = True) #vardas ir pavardė
    first_name = models.CharField(max_length = 50, null = True) #vardas
    last_name = models.CharField(max_length = 50, null = True) #pavardė
    area = models.TextField(null = True) #apygarda
    party = models.TextField(null = True) #partija; nebūtinai sutampa su frakcija
    groups = models.ManyToManyField(Group, through='Membership') #grupės

    meetings_total = models.PositiveIntegerField(null = True) #kiek plenarinių posėdžių galėjo dalyvauti
    meetings_attended = models.PositiveIntegerField(null = True) #kiek dalyvavo
    attendance = models.DecimalField(null = True, decimal_places = 2, max_digits = 4) #santykis tarp meetings_attended ir meetings_total

    submitted_total= models.PositiveIntegerField(null = True) #kiek pateikė projektų
    activity = models.DecimalField(null=True,decimal_places=2,max_digits=4) #santykis tarp nario pateiktų projektų ir visų pateiktų projektų
    submitted_passed = models.PositiveIntegerField(null = True) #priimtų projektų skaičius
    effectiveness = models.DecimalField(null = True, decimal_places = 2, max_digits = 4) #santykis tarp submitted_passed ir submitted_total
    
    active = models.BooleanField(default = True, verbose_name = 'Dabartinis narys') #ar narys dabar seime

    email = models.CharField(max_length = 100, null = True) #el. paštas
    
    #bio
    description = models.TextField(null = True, verbose_name = "Aprašymas") #savanorių parašyta bio
    photo = models.TextField(null = True) #nuotrauka iš lrs.lt
    bio = models.TextField(null = True) #visokie visokiausi duomenys surinkti iš robotų, pagal kuriuos nelabai mums rūpi po to ieškot
    asm_id = models.IntegerField(null = True) #ID skaičius naudojamas lrs.lt; padeda su parsinimu

    #nustato politiko name, first_name ir last_name pagal suteiktą string, kurioje vardas eina prieš pavardę
    #Pvz "Viktorija Čmilytė-Nielsen"
    def name_normal(self, name):
        parts = name.split(' ')
        self.first_name = ' '.join(parts[:-1])
        self.last_name = parts[-1]
        name = '{0} {1}'.format(self.first_name, self.last_name)
        self.name = name
        return name

    #nustato politiko name, first_name ir last_name pagal suteiktą string, kurioje vardas eina po pavardės
    #pvz "Čmilytė-Nielsen Viktorija"
    def name_reverse(self, name):
        parts = name.split(' ')
        self.first_name = ' '.join(parts[1:])
        self.last_name = parts[0]
        name = '{0} {1}'.format(self.first_name, self.last_name)
        self.name = name
        return name

    #iš jau išsaugoto name sudaro first_name ir last_name
    def set_name_normal(self):
        parts = self.name.split(' ')
        self.first_name = ' '.join(parts[:-1])
        self.last_name = parts[-1]

    #apskaičiuoja politiko lankomumą
    def calculate_attendance(self):
        att = self.attendancerecord_set
        self.meetings_total = att.aggregate(models.Sum('meetings_total'))['meetings_total__sum']
        self.meetings_attended = att.aggregate(models.Sum('meetings_attended'))['meetings_attended__sum']
        if self.meetings_attended and self.meetings_total:
            self.attendance = self.meetings_attended / self.meetings_total
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['last_name']


#Kadangi turime papildomų duomenų kiekvienai narystei, paprasto ManyToManyField neužtenka
#Jį papildome šiuo modeliu
class Membership(models.Model):
    role = models.TextField(null = True) #nario rolė grupėje
    member = models.ForeignKey(Politician, related_name = 'memberships', on_delete=models.CASCADE) #narys
    group = models.ForeignKey(Group, related_name = 'members', on_delete=models.CASCADE) #grupė
    date_start = models.DateField(null = True) #nuo kada grupėje
    date_end = models.DateField(null = True) #kada išėjo (arba pakeitė į kitą role ergo į kitą membership)

    def __str__(self):
        return '{0} - {1}'.format(self.member.name, self.group.name)

    class Meta:
        unique_together = ('member', 'group', 'date_start')


#dalyvavimo įrašas kiekvienam mėnesiui
#robotai surenkta duomenis pagal mėnesį, tad kiekvieno nario dalyvavimą ir išsaugom pagal mėnesius
#pagal šiuos po to suskaičiuojama narių attendance
class AttendanceRecord(models.Model):
    politician = models.ForeignKey(Politician, on_delete=models.CASCADE) #narys
    year = models.IntegerField() #metai
    month = models.IntegerField() #mėnuo
    meetings_total = models.IntegerField() #keliuose posėdžiuose galėjo būti
    meetings_attended = models.IntegerField() #keliuose buvo
    last_day = models.IntegerField() #paskutinė įrašyta diena; tai mums leidžia nuskaityti lankomumą mėnesio viduryje, ir jį atnaujinti nuskaičius vėliau

    class Meta:
        unique_together = ('politician', 'year', 'month')
