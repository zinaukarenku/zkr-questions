from django.db import models

from nariai.models import Politician

# Create your models here.

#Seimo projekto modelis
#didžioji dalis šios informacijos surenkama per robotus
#Redaktoriams palikta nice_title, category, hidden, passed, correct, description
class Project(models.Model):
    id = models.AutoField(primary_key=True)
    initiators = models.ManyToManyField(Politician, related_name = "projects") #Nariai, inicijavę projektą
    code = models.CharField(max_length = 40, null = True, verbose_name = 'Projekto nr.') #projekto kodas, pvz XIIIP-100
    metacode = models.CharField(max_length = 40, null = True)
    title = models.TextField(null = True, verbose_name = 'Oficialus pavadinimas') #iš seimo
    nice_title = models.TextField(null = True, verbose_name = 'Gražus pavadinimas') #mūsų sugalvotas pavadinimas
    category = models.CharField( #Kategorija, roughly pagal ministeriją/komitetą
        max_length = 3,
        choices = (
            ('apl', 'Aplinka'),
            ('enr', 'Energetika'),
            ('fin', 'Finansai'),
            ('kap', 'Krašto apsauga'),
            ('kul', 'Kultūra'),
            ('sad', 'Socialinė apsauga ir darbas'),
            ('sap', 'Sveikatos apsauga'),
            ('smo', 'Švietimas ir mokslas'),
            ('tei', 'Teisingumas'),
            ('luk', 'Ūkis'),
            ('ure', 'Užsienio reikalai'),
            ('vre', 'Vidaus reikalai'),
            ('zuk', 'Žemės ūkis'),
        ),
        null = True,
        blank = True,
        verbose_name = 'Kategorija'
    )
    href = models.TextField(verbose_name = 'Nuoroda', unique = True) #į dokumentą
    hidden = models.BooleanField(default = False, verbose_name = 'Slėpti') #kartais weird duomenys, tad projektą norim paslėpti
    passed = models.NullBooleanField(verbose_name = 'Priimtas')
    correct = models.BooleanField(default = False, verbose_name = 'Duomenys tvarkingi')
    description = models.TextField(null = True, verbose_name = 'Aprašymas')
    date_start = models.DateField(null = True) #kada pateiktas projektas, gaunama per e-seimas dokumentų įrašus
    date_end = models.DateField(null = True) #kada nubalsuota dėl projekto, gaunama iš dienotvarkės
    days = models.IntegerField(null = True) #delta tarp date_start ir date_end
    scanned = models.BooleanField(default = False) #ar nuskaityti duomenys
    
    #Balsai
    #Modelyje jie apskaičiuojami iš votes objektų; čia išsaugomi tik patogumui pateikiant ir ieškant.
    votes_u = models.PositiveIntegerField(null = True) #balsai už
    votes_p = models.PositiveIntegerField(null = True) #prieš
    votes_s = models.PositiveIntegerField(null = True) #susilaikę
    votes_delta = models.IntegerField(null = True) #delta tarp votes_u ir votes_p

    #padaro balsų ir dienų apskaičiavimus (surenka balsus ir suranda deltas)
    def calculate_votes(self):
        votes_tally = {}
        for votect in self.votes.values('vote').annotate(models.Count('vote')):
            votes_tally[votect['vote']] = votect['vote__count']
        self.votes_u = votes_tally.get('u', 0)
        self.votes_p = votes_tally.get('p', 0)
        self.votes_s = votes_tally.get('s', 0)
        self.votes_delta = self.votes_u - self.votes_p
        if(self.date_end):
            self.days = self.date_end - self.date_start
            self.days = self.days.days #kek
        self.set_metacode()
        self.save()

    #sugeneruoja balsus pagal frakciją
    #biški hackas nes tiesiog pasižiūri į narių partijas ir balsus sudeda pagal jas
    #bet tos partijos neatitinka frakcijų, tad tai reiktų perdirbt, gal įrašant frakciją prie balso
    def votes_fraction(self):
        vote_list = self.votes.values('voter__party', 'vote')
        vote_list = vote_list.annotate(count=models.Count('voter__party'))
        vote_dict = {}
        #prepare everything to build the return dict
        for elem in vote_list: 
            if elem['vote'] == '':
                elem['vote'] = 'n'
            vote_dict[elem['voter__party']] = {}
        #now to actually build it
        for elem in vote_list:
            vote_dict[elem['voter__party']][elem['vote']] = elem['count']
        return vote_dict

    def set_metacode(self):
        try:
            metacode = self.code[:self.code.index('(')]
        except ValueError:
            metacode = self.code
        self.metacode = metacode

    def __str__(self):
        return self.code + ": " + self.title

    class Meta:
        verbose_name = 'Projektas'
        verbose_name_plural = 'Projektai'


#Nuorodos modelis, naudojamas seimo darbotvarkės nuskaitymui
class Link(models.Model):
    href = models.CharField(max_length = 100, unique = True)
    level = models.CharField(
        max_length = 1,
        choices = (
            ('n', 'Pagrindinis'),
            ('s', 'Sesija'),
            ('p', 'Posėdis'),
            ('i', 'Įrašas'),
            ('b', 'Balsavimas'),
        )
    )
    extra = models.TextField(null = True) #papildomiems dalymas, numeriams, etc
    balsavimas_type = models.CharField(
        max_length = 1,
        null = True,
        choices = (
            ('b', 'Balsuota'),
            ('s', 'Bendras sutarimas'),
        )
    )
    balsavimas_result = models.CharField(
        max_length = 1,
        null = True,
        choices = (
            ('p', 'Pritarta'),
            ('a', 'Atmesta'),
        )
    )
    projects = models.ManyToManyField(Project, related_name = 'schedule_entries') #šitą turėtų turėt tik 'i' tipo linkai
    parent = models.ForeignKey("self", related_name='children', null = True, on_delete=models.CASCADE)
    date = models.DateField() 
    time = models.TimeField(null = True) #nebūtinai turim tą laiką (sesija, posėdis), tad saugom atskirai
    scanned = models.BooleanField(default=False)
    funny = models.NullBooleanField()

    def __str__(self):
        if self.extra:
            return '%s %s - %s' % (self.date, self.get_level_display(), self.extra)
        else:
            return '%s %s' % (self.date, self.get_level_display())


#Balso modelis
#Susietas su balsavimo tipo link
#Viskas surenkama darbotvarkės roboto
class Vote(models.Model):
    voter = models.ForeignKey(Politician, related_name = 'votes', on_delete=models.CASCADE)
    fraction = models.CharField(max_length = 100, null = True)
    parent = models.ForeignKey(Link, related_name = 'votes', on_delete=models.CASCADE)
    vote = models.CharField(
        max_length = 1,
        choices = (
            ('u', 'Už'),
            ('p', 'Prieš'),
            ('s', 'Susilaikė'),
            ('n', 'Nebalsavo'),
        ),
    )

    class Meta:
        unique_together = ('parent', 'voter')


