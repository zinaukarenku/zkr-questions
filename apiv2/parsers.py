import json, csv, datetime, decimal, requests
from lxml import html

from django.db import IntegrityError

from nariai.models import Group, Politician, Membership, AttendanceRecord
from darbai.models import Project, Vote

#konfiguracijos dict'ų padalinimui

NARIAI_FIELD_SPLIT = (
    ('asm_id',),
    ('party', 'email', 'photo', 'bio', 'name'),
)

MEMBERSHIP_FIELD_SPLIT = (
    ('member', 'group', 'date_start'),
    ('date_end', 'role'),
)


#extra functions

#iš pavardė vardas padaro vardas pavardė
def reverse_name(name):
    parts = name.split(' ')
    first_name = ' '.join(parts[1:])
    last_name = parts[0]
    return '{} {}'.format(first_name, last_name)

#paima dict'ą ir padalija į masyvą su keliais dict'ais pagal keys
#naudinga su create_or_update ir panašiais metodais
def dict_split(initial, field_split):
    retlist = [{} for i in field_split]
    for field in initial:
        for index, split_list in enumerate(field_split):
            if field in split_list:
                retlist[index][field] = initial[field]
                break
    return retlist
        

#senojo lrs.lt puslapio parseriai, kai dar niekos robotukų neblokuodavo ir jokių mandrų js šūdų nebuvo ^^

#aktyvumas, efektyvumas, etc
def parse_activity_table():

    #gaunam puslapio html
    req = requests.get('http://www3.lrs.lt/pls/inter/w5_smn_akt_new.seim_nar_proj?p_kad_ses=&p_start=2016-11-13&p_end=&p_asm_id=&p_rus=&p_forma=')
    tree = html.fromstring(req.content)

    #kiekvienai eilutei su nariu puslapyje esančioje lentelėje
    for el in  tree.cssselect('table .basic > tr')[1:]:
        li = el.cssselect('td') #masyvukas su eilutės info
        try:
            pol = Politician.objects.get(name = reverse_name(li[0].text)) #politiko vardas
        except Politician.DoesNotExist: #nėra tokio duombazėj :O
            print(li[0].text, 'not found')
            continue
        pol.submitted_total = int(li[1].text_content()) 
        pol.activity = decimal.Decimal(li[2].text)
        if li[3].text != '\xa0': #'\xa0' yra mandras tarpas, ten padėtas jei nėra info
            pol.submitted_passed = int(li[3].text)
            pol.effectiveness = decimal.Decimal(li[4].text[2:-1])
        pol.save()

#lankomumas; 'yr' - metai, 'mo' - mėnuo, abu kaip sveikieji skaičiai
def parse_attendance(yr, mo):

    if mo < 10: #reikia url'ui :(
        mo = str('0' + str(mo))
    req = requests.get('http://www3.lrs.lt/pls/inter/w5_smn_akt_new.seim_nar_lank_det?p_met={}&p_men={}&p_var=0&p_rus=0'.format(yr, mo))
    main = html.fromstring(req.content).cssselect('table .basic > tr') #gaunam reikalingą html

    #kiekvienai eilutei su politiku 
    for row in main[2:-1]:
        try:
            pol = Politician.objects.get(name = reverse_name(row[0].text)) #gaunam politiką
        except Politician.DoesNotExist: #nėra tokio duombazėj :O
            print(row[0].text, 'not found')
            continue
        meetings_total = 0
        meetings_attended = int(row[-1].text_content()) #dalyvautų dienų skaičius
        for day in row[1:-1]: #kadangi staiga mėnesio viduryje galėjo atsirasti naujas seimo narys, turime meetings_total skaičiuoti kiekvienam inidividualiai
            if day.text_content() != '\xa0':
                meetings_total += 1

        #dabar išsaugom surinktus duomenis
        try:
            rec = AttendanceRecord.objects.get(year = yr, 
                                               month = mo, 
                                               politician = pol)
        except AttendanceRecord.DoesNotExist:
            rec = AttendanceRecord(year = yr, month = mo, politician = pol)
        rec.last_day = int(main[1][-1].text_content())
        rec.meetings_total = meetings_total
        rec.meetings_attended = meetings_attended
        rec.save()

#iš failo susirenka json'ą ir jį paverčia į narius duombazėj
def parse_nariai(f):
    rdr = json.load(f)
    for row in rdr: #kiekvienam nariui json'e
        row['bio'] = json.dumps(row['bio']) #bio paverčiam į objektą
        split_row = dict_split(row, NARIAI_FIELD_SPLIT) #padalina masyvą į vienanarį su asm_id ir į papildomą su basic info
        pol, created = Politician.objects.update_or_create(defaults=split_row[1], **split_row[0]) #suranda narį pagal asm_id ir jam priskiria naują basic info
        
        #sutvarkom apygardos info
        if row['area'] == 'Pagal sąrašą': 
            pol.area = 'Daugiamandatė'
        else:
            pol.area = ' '.join(row['area'].split(' ')[:-1])
        pol.save() 

        #tvarkomės su politiko pareigom
        for par in row['pareigos']:
            memobj = {} #sutrumpinta iš membership object - info iš jo bus išsaugota kaip membership
            memobj['member'] = pol
            group = par.get('group', '') #gauname atitinkamą grupę
            if group:
                group = Group.objects.get_or_create(name=par['group'])
                memobj['group'] = group[0]
                dates = par.get('dates', '') #susitvarkom su datom, kurios nebūtinai egzistuoja
                if dates:
                    dates = dates.split(' \u2013 ')
                if len(dates) >= 1:
                    if dates[0]:
                        memobj['date_start'] = datetime.datetime.strptime(dates[0], '%Y-%m-%d').date()
                if len(dates) == 2:
                    if dates[1]:
                        memobj['date_end'] = datetime.datetime.strptime(dates[1], '%Y-%m-%d').date()
                memobj['role'] = par['role']
                split_memobj = dict_split(memobj, MEMBERSHIP_FIELD_SPLIT) #padalijam memobj išsaugojimui, panašiai kaip su politiku pradžioje
                Membership.objects.update_or_create(defaults=split_memobj[1], **split_memobj[0])

        #tvarkomės su politiko inicijuotais projektais
        for proj in row['projects']:
            proj, created = Project.objects.get_or_create(href=proj)
            proj.initiators.add(pol)
            proj.save()

        pol.set_name_normal() #išsaugom first_name ir last_name
        pol.save()

#paima csv failą ir duombazėj atsiranda projektai
def parse_projects(f):
    rdr = csv.DictReader(f)
    for row in rdr: #kiekvienai csv eilutei 

        #susitvarkom su projekto kodu
        if row['code'].rfind('(') > 0:
            row['code'] = row['code'][:row['code'].rfind('(')]

        proj, created = Project.objects.update_or_create(code=row['code']) #gaunam projektą
        proj.title = row['title']

        #sutvarkom datas (kurios nebūtinai abi egzistuoja)
        proj.date_start = datetime.datetime.strptime(row['date_start'], '%Y-%m-%d').date()
        if row['date_end']:
            proj.date_end = datetime.datetime.strptime(row['date_end'], '%Y-%m-%d').date()
        proj.save()

        #tvarkomės su balsais
        if row['balsai'] and not proj.votes.all(): #jei balsai dar neegzistuoja
            votes = json.loads(row['balsai']) 
            for vote in votes:
                pol, created = Politician.objects.get_or_create(asm_id=vote['asm_id']) #gaunam politiką
                v = Vote(voter = pol, vote = vote['vote'], project = proj) #sukuriam patį balsą
                v.save()

        proj.url = row['source_url']

        #jeigu nesąmonė su datom
        if proj.date_end and proj.date_start > proj.date_end:
            proj.hidden = True
        proj.calculate_votes()
