import requests, bs4, re
import datetime as dt

from django.db.utils import IntegrityError

from darbai.models import Link, Project

#nuo kada pradedam skaityti duomenis
ULTIMATE_START = dt.date(2016, 11, 13)
HOME_URL = 'http://www3.lrs.lt/pls/inter/w5_sale.kad_ses'

BALSAVIMAS_REGEX = re.compile('Įvyko balsavimas dėl [S a-ząčęėįšųūž]+ priėmimo;')

#tiesiog iškart randam svarbiausią sąrašą - eilutes duomenų lentelėje
def get_trs(link):
    req = requests.get(link.href)
    soup = bs4.BeautifulSoup(req.content, "html5lib")
    return soup, soup.body.find_all('table')[2].find_all('tr')

#perskaito sesijas nuo ULTIMATE_START į duombazę
def read_sesijos():

    #pirma, suraskim, nuo kada verta skaityti
    #randam naujausią sesiją ir skaitom tik nuo jos
    try:
        date_oldest = Link.objects.filter(level='s').order_by('-date')[0].date
    except IndexError:
        date_oldest = ULTIMATE_START

    #mums taip pat reikės HOME_URL link objekto
    HOME = Link.objects.get(href=HOME_URL)

    #sesijų sąrašas
    soup, trs = get_trs(HOME)
    #kiekvienai sesijų lentelės eilutei
    for tr in trs:
        tds = tr.find_all('td')
        try:
            date_string = tds[1].text.strip()
            date = dt.datetime.strptime(date_string, '%Y-%m-%d').date()
        except (IndexError, ValueError) as e: #jei neradom datos, metam
            continue
        else: 
            if date < date_oldest: #jei data per sena, metam
                continue

        #jei viskas tiko, išsaugom nuorodą vėlesniam skaitymui
        href = 'http://www3.lrs.lt/pls/inter/' + tds[0].a.attrs['href']
        defaults = {
            'extra': tds[0].text.strip(),
            'level': 's',
            'parent': HOME,
            'date': date,
        }
        link, created  = Link.objects.get_or_create(href=href, defaults=defaults)
        #sesija galbūt atsinaujino, tad darom taip
        #defaults suveiktų tik naujai sukurtam objektui, o mes norim kad ir senam
        link.scanned = False
        link.save()

#perskaitom duotos sesijos posėdžius
def read_given_sesija(sesija):

    #pirma gaukim, nuo kada mums reikia skaityt
    #susirandam naujausią duombazės posėdį šiai sesijai
    #ir skaitom tik už jį naujesnius (data didesnė)
    #jeigu nerandam, palyginimams naudosim ULTIMATE_START
    try:
        date_oldest = sesija.children.order_by('-date')[0].date
    except IndexError:
        date_oldest = ULTIMATE_START

    #Dabar pridėkime visus posėdžius
    #vėl gauname lentelę
    soup, trs = get_trs(sesija)

    #šiuo atveju tiek žaist su datom nereikės, jos garantuotos jei yra td
    for tr in trs:
        tds = tr.find_all('td')
        if not tds:
            continue
        date = dt.datetime.strptime(tds[0].text.strip(), '%Y-%m-%d').date()
        if date < date_oldest: #nekartokim jei jau saugojom
            continue
        
        #pagaliau, jei priklauso, išsaugom posėdį
        for a in tds[1].find_all('a'):
            href = 'http://www3.lrs.lt/pls/inter/' + a.attrs['href']
            defaults = {
                'extra': a.text.strip(),
                'level': 'p',
                'parent': sesija,
                'date': date,
            }
            link, created = Link.objects.get_or_create(href=href, defaults=defaults)
            link.scanned = False
            link.save()

    sesija.scanned = True
    sesija.save()

def read_given_posedis(posedis):

    #vėlgi, gaunam naujausią įrašą ir skaitom tik nesenesnius
    try:
        time_oldest = posedis.children.order_by('-time')[0].time
    except IndexError:
        time_oldest = dt.time(0,0)

    #gaunam reikalingą lentelę
    soup, trs = get_trs(posedis)

    #nuskaitom pačią lentelę
    for tr in trs:
        #pradedam nuo laiko
        tds = tr.find_all('td')
        try:
            time = dt.datetime.strptime(tds[0].text.strip(), '%H:%M').time()
        except (IndexError, ValueError) as e:
            continue
        if time < time_oldest:
            continue

        #Jei praėjo laiko check, įrašom
        href = 'http://www3.lrs.lt/pls/inter/' + tds[2].a.attrs['href']
        defaults = {
            'extra': "(%s) %s" % (tds[1].text.strip(), tds[2].text.strip()),
            'level': 'i',
            'parent': posedis,
            'date': posedis.date,
            'time': time,
        }
        link, created = Link.objects.get_or_create(href=href, defaults=defaults)
        link.scanned = False
        link.save()

    posedis.scanned = True
    posedis.save()


def read_given_entry(entry):

    #šįkart pradėsim ne nuo lentelės, o nuo atitinkamų projektų
    #info apie projektus surinksime vėliau, kol kas užteks nuorodos
    soup, trs = get_trs(entry)

    for dokhref in soup.find_all('a', text='dokumento\xa0tekstas'):
        project, created = Project.objects.get_or_create(href=dokhref.attrs['href'])
        entry.projects.add(project)

    #toliau paimsim balsavimus
    #išties mums svarbus tik pats paskutinis balsavimas, tik jei įvyko priėmimas
    if '[Priėmimas]' in entry.extra:
        tds = trs[-1].find_all('td')
        #įvyko normalus balsavimas, all is good (not necessarily)
        if BALSAVIMAS_REGEX.match(tds[1].text):
            href = 'http://www3.lrs.lt/pls/inter/' + tds[1].a.attrs['href']
            defaults = {
                'level': 'b',
                'parent': entry,
                'date': entry.date,
                'time': dt.datetime.strptime(tds[0].text,'%H:%M:%S').time(),
                'balsavimas_type': 'b', #dėl klausimo buvo balsuota
            }
            link, created = Link.objects.get_or_create(href=href, defaults=defaults)
            link.scanned = False
            link.save()
            entry.balsavimas_type = 'b'
        #kažkas buvo nutarta bendru sutarimu, pažiūrėsim ranka vėliau
        elif 'bendru' in tds[1].text:
            entry.balsavimas_type = 's'
        else: #gal kas pertraukos paprašė, shit happens, pažiūrėsim, pasijuoksim
            entry.funny = True

        for project in entry.projects.all():
            project.date_end = entry.date
            project.save()

    entry.scanned = True
    entry.save()

#padarom pertraukėlę nuo tų Link objektų
#šita funkcija paima Project objektą ir surenka jo duomenis iš jo href
def read_given_project(project):

    #svarbiausią lentelę gaunam kiek kitaip
    req = requests.get(project.href)
    soup = bs4.BeautifulSoup(req.content, 'lxml')
    try: 
        tds = soup.find(id='mainForm:j_id_34_1').tbody.find_all('tr')[0].find_all('td')
    except AttributeError:
        project.hidden = True
        project.save()
        return

    #mums tereikia tik tiek
    project.code = tds[4].text.strip()
    project.title = soup.find(id="mainForm:laTitle").text.strip()
    project.date_start = dt.datetime.strptime(tds[7].text.strip(),'%Y-%m-%d').date()

    project.scanned = True
    project.set_metacode()
    project.save()

