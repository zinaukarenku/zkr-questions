from klausimai.models import Politician, Question
from klausimai.utils import notify_politician, notify_question
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

politicianEmails = []
questionEmails = []
politicians = Politician.objects.filter(notifs_allow=True, notifs_activate=True)
for politician in politicians:
    politician.notifs_activate = False
    politician.save()
    politicianEmails.append({'email': politician.email})
questions = Question.objects.filter(notifs_allow=True, notifs_activate=True)
for question in questions:
    question.notifs_activate = False
    question.save()
    questionEmails.append({'email': question.email, 'id': question.id})
notify_politician(politicianEmails)
notify_question(questionEmails)
