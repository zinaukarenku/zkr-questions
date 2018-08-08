from django.core import mail
from django.core.files import File
from .models import Politician, Expert

def send_reg_mail():
    messages = []
    for pol in Politician.objects.filter(user=None):
        try:
            reg_tuple = pol.register()
            message = """
Sveiki,

Kviečiame jus prisijungti prie naujos „Žinau, ką renku“ platformos.

Platformoje Jums bet kas galės užduoti klausimus, Jūs į juos galėsite atsakyti, o mūsų ekspertų komanda Jūsų atsakymus galės komentuoti. Kiekvieną klausimą patikrins mūsų moderatoriai, tad Jums nereikės bijoti nekorektiškų ar įžulių klausimų.

Prisijungti galite čia:
https://klausimai.zinaukarenku.lt/registration/new/"""+reg_tuple[1]+"""/
Nustatę savo slaptažodį, spustelėkite "Prisijungimas", ten įvesktie savo el. pašto adresą ir savo kątik nustatytą slaptažodį. Prisijungę galėsite pamatyti savo neatsakytus klausimus ir nustatyti savo biografiją - ją matys visi, apsilankę Jūsų puslapyje. Ten taip pat bus rodomi visi Jūsų atsakyti ir neatsakyti klausimai, tad nepamirškite jų atsakinėti!

Dėkojame Jums už bendradarbiavimą.

Su pagarba,

„Žinau, ką renku“ komanda
"""
            messages.append(mail.EmailMessage('Prisijungimas prie „Žinau, ką renku“ platformos',message,'platforma@zinaukarenku.lt',[reg_tuple[0]],reply_to=['stanislovas@zinaukarenku.lt']))
        except Exception as e:
            print(pol.full_name, e)
    connection = mail.get_connection()
    connection.send_messages(messages)

def notify_politician(emails):
    messages = []
    for emailDict in emails:
        message = """
Sveiki,

Jums buvo užduota naujų klausimų!

Juos galite pažiūrėti čia:
https://klausimai.zinaukarenku.lt/answers/

Užėję galėsite tuos klausimus pamatyti ir atsakyti.

Su pagarba,

„Žinau, ką renku“ komanda
"""
        messages.append(mail.EmailMessage('Gavote klausimą „Žinau, ką renku“ platformoje',message,'platforma@zinaukarenku.lt',[emailDict['email']],reply_to=['stanislovas@zinaukarenku.lt']))
    connection = mail.get_connection()
    connection.send_messages(messages)
    

def notify_question(emails):
    messages = []
    for emailDict in emails:
        message = """
Sveiki,

Į Jūsų klausimą buvo atsakyta!

Atsakymus galite pažiūrėti čia:
https://klausimai.zinaukarenku.lt/question/"""+str(emailDict['id'])+"""/

Jei norite šių laiškų nebegauti, paspauskitę šią nuorodą:
https://klausimai.zinaukarenku.lt/unsubscribe/"""+str(emailDict['id'])+"""/

Su pagarba,

„Žinau, ką renku“ komanda
"""
        messages.append(mail.EmailMessage('Gavote atsakymą „Žinau, ką renku“ platformoje',message,'platforma@zinaukarenku.lt',[emailDict['email']],reply_to=['stanislovas@zinaukarenku.lt']))
    connection = mail.get_connection()
    connection.send_messages(messages)

def reset_pw_email(email, key):
    message = """
Sveiki,

Jūsų paskyrai „Žinau, ką renku“ platformoje buvo paprašyta slaptažodžio atnaujinimo nuoroda. Ji štai čia:

https://klausimai.zinaukarenku.lt/registration/new/"""+key+"""/

Jei nuorodos neprašėte, ją tiesiog galite ignoruoti.

Su pagarba,

„Žinau, ką renku“ komanda
"""
    emailmsg = mail.EmailMessage('„Žinau, ką renku“ slaptažodžio atsatymas',message,'platforma@zinaukarenku.lt',[email],reply_to=['stanislovas@zinaukarenku.lt'])
    emailmsg.send()

def gen_reg_link(key):
    return "https://klausimai.zinaukarenku.lt/registration/new/"+key+"/"

def set_logo(name,p):
    try:
        p.logo_name = name
        p.save()
    except Exception as e:
        print(p, e)

def send_exp_mail():
    messages = []
    for pol in Expert.objects.filter(user=None):
        try:
            reg_tuple = pol.register()
            message = """
Sveiki,

dėkojame, kad nusprendėte dirbti su „Žinau, ką renku“ ir pasiryžote komentuoti politikų atsakymus.

Slaptažodį platformoje galite nusistatyti štai čia:
https://klausimai.zinaukarenku.lt/registration/new/"""+reg_tuple[1]+"""/
Po to savo el. paštu ir nustatytu slaptažodžiu galėsite prisijungti tiesiog paspaudę „Prisijungti“.

Visada priimsime pasiūlymus, kaip platformą tobulinti ar tvarkyti. Geriausia šiuos pasiūlymus siųsti Stanislovui Kujaliui, iniciatyvos IT koordinatoriui, el. paštu stanislovas@zinaukarenku.lt . Šio laiško reply_to bet kuriuo atveju ten ir nustatytas.

Lauksime Jūsų komentarų!

Su pagarba,

„Žinau, ką renku“ komanda
"""
            messages.append(mail.EmailMessage('Prisijungimas prie „Žinau, ką renku“ platformos',message,'platforma@zinaukarenku.lt',[reg_tuple[0]],reply_to=['stanislovas@zinaukarenku.lt']))
        except Exception as e:
            print(pol.full_name, e)
    connection = mail.get_connection()
    connection.send_messages(messages)
