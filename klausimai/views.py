import json

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse, HttpResponseServerError, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404

from .models import Area, Party, Question, Politician, Answer, Promise

# Create your views here.

#most of the work there is done in javascript
@ensure_csrf_cookie
def start(request):
    logos = []
    total_questions = Question.objects.filter(approval=True).count()
    answered_questions = Question.objects.filter(answer__isnull=False).distinct().count()
    total_answers = Answer.objects.all().count()
    answered_politicians = Politician.objects.filter(answer__isnull=False).distinct().count()
    total_politicians = Politician.objects.filter(status='is').count()
    for party in Party.objects.exclude(logo_name=None).exclude(active=False):
        newname = str(party.name).replace(' ','@')
        logos.append({"name": newname,"url": party.logo_name})
    return render(request, template_name='klausimai/start.html',context={"logos":logos,
                                              "total_questions": total_questions,
                                              "answered_questions": answered_questions,
                                              "total_answers": total_answers,
                                              "answered_politicians": answered_politicians,
                                              "total_politicians": total_politicians})

#returns data for the typeahead in start
def init(request):
    teritorijosAr = []
    partiesAr = []
    politiciansAr = []
    areas = Area.objects.exclude(map_name='Daugiamandatė')
    parties = Party.objects.all()
    politicians = Politician.objects.filter(status='is')
    for area in areas:
        teritorijosAr.append(area.proper_name)
    for party in parties:
        partiesAr.append(party.name)
    for politician in politicians:
        politiciansAr.append(politician.full_name)
    jsonResp = {
        'data': {
            'teritorijos': teritorijosAr,
            'partijos': partiesAr,
            'politikai': politiciansAr,
        }
    }
    return JsonResponse(jsonResp)

#returns politician list for an area (for typeahead selection in start)
def area(request):
    proper_name = request.POST['reqData']
    try:
        area = Area.objects.get(proper_name=proper_name)
    except Exception:
        return HttpResponseServerError()
    jsonResp = {
        'politicians': []
    }
    for politician in area.politician_set.filter(status='is').order_by('full_name'):
        jsonResp['politicians'].append({
            'name': politician.full_name,
            'party': politician.party.name,
            'area': proper_name,
            'id': politician.id,
            'registered': politician.is_registered,
        })
    return JsonResponse(jsonResp)

#returns politician list for a party (for typeahead selection in start)
def party(request):
    name = request.POST['reqData']
    try:
        party = Party.objects.get(name=name)
    except Exception:
        return HttpResponseServerError()
    jsonResp = {
        'politicians': []
    }
    for politician in party.politician_set.filter(status='is').order_by('full_name'):
        jsonResp['politicians'].append({
            'name': politician.full_name,
            'party': name,
            'area': politician.area.proper_name,
            'id': politician.id,
            'registered': politician.is_registered,
        })
    return JsonResponse(jsonResp)

#returns single politician if that was selected in typeahead
def politicianJson(request):
    name = request.POST['reqData']
    try:
        politician = Politician.objects.get(full_name=name)
    except Exception:
        return HttpResponseServerError()
    jsonResp = {
        'politicians': [{
            'name': politician.full_name,
            'party': politician.party.name,
            'area': politician.area.proper_name,
            'id': politician.id,
            'registered': politician.is_registered,
        }]
    }
    return JsonResponse(jsonResp)

#all *Add views are there to provide data for the show more button in question lists

#displays latest 10 approved questions
def latest(request):
    questions = Question.objects.order_by('-time').filter(approval=True)[:10]
    return render(request, 'klausimai/latest.html', 
            context={"questions": questions,
                     "description": "Čia parodyti naujausi patvirtini klausimai",
                     "load_type": "/latest/"})

def latestAdd(request, step):
    questions = Question.objects.order_by('-time').filter(approval=True)[int(step)*10:(int(step)+1)*10]
    return render(request, 'klausimai/latestAdd.html', context={"questions": questions})

#displays latest 10 unanswered questions
def latestUnans(request):
    questions = Question.objects.order_by('-time').filter(approval=True, answer__isnull=True)[:10]
    return render(request, 'klausimai/latest.html',
                  context={"questions": questions,
                           "description": "Naujausi neatsakyti klausimai",
                           "load_type": "/latest/",
                           "load_extra": "unanswered/"})

def latestUnansAdd(request, step):
    questions = Question.objects.order_by('-time').filter(approval=True, answer__isnull=True)[int(step)*10:(int(step)+1)*10]
    return render(request, 'klausimai/latestAdd.html', context={"questions": questions, "load_extra": "unanswered/"})

#displays latest 10 answered questions
def latestAns(request):
    questions = Question.objects.order_by('-time').filter(approval=True, answer__isnull=False).distinct()[:10]
    return render(request, 'klausimai/latest.html',
                  context={"questions": questions,
                           "description": "Naujausi atsakyti klausimai",
                           "load_type": "/latest/",
                           "load_extra": "answered/"})

def latestAnsAdd(request, step):
    questions = Question.objects.order_by('-time').filter(approval=True, answer__isnull=False).distinct()[int(step)*10:(int(step)+1)*10]
    return render(request, 'klausimai/latestAdd.html', context={"questions": questions})

#shows a question's answers and comments to those answers
def question(request, pk):
    question = Question.objects.get(pk=pk)
    context={"question": question}
    try:
        if request.user.expert:
            context["expert"] = request.user.expert.id
    except Exception:
        pass
    return render(request, 'klausimai/question.html',context=context)

#displays politician info as well as 10 latest questions they got
def politician(request, pk):
    politician = Politician.objects.get(pk=pk)
    questions = politician.question_set.order_by('-time').filter(approval=True)[:10]
    qs_total = politician.question_set.filter(approval=True).count()
    qs_answered = politician.question_set.filter(answer__politician=politician).count()
    context={"questions": questions,
             "pol_name": politician.full_name,
             "biography": politician.biography,
             "description": "Visi politikui užduoti klausimai",
             "pol_total": qs_total,
             "pol_answered": qs_answered,
             "load_type": "/politician/"+str(pk)+"/",
             "load_extra": "",
             "pol_id": pk,
             "promises": politician.promise_set.all()}
    return render(request, 'klausimai/latest.html',context=context)

def politicianAdd(request, pk, step):
    politician = Politician.objects.get(pk=pk)
    questions = politician.question_set.order_by('-time').filter(approval=True)[int(step)*10:(int(step)+1)*10]
    return render(request, 'klausimai/latestAdd.html', context={"questions": questions, "pol_id": pk})

#displays politician info as well as 10 latest unanswered questions they got
def politicianUnans(request, pk):
    politician = Politician.objects.get(pk=pk)
    questions = politician.question_set.order_by('-time').filter(approval=True).exclude(answer__politician=politician)[:10]
    qs_total = politician.question_set.filter(approval=True).count()
    qs_answered = politician.question_set.filter(answer__politician=politician).count()
    context={"questions": questions,
             "pol_name": politician.full_name,
             "biography": politician.biography,
             "description": "Klausimai, užduoti politikui, kurių jis neatsakė",
             "pol_total": qs_total,
             "pol_answered": qs_answered,
             "load_type": "/politician/"+str(pk)+"/",
             "load_extra": "unanswered/",
             "pol_id": pk,
             "promises": politician.promise_set.all()}
    return render(request, 'klausimai/latest.html',context=context)

def politicianUnansAdd(request, pk, step):
    politician = Politician.objects.get(pk=pk)
    questions = politician.question_set.order_by('-time').filter(approval=True).exclude(answer__politician=politician)[int(step)*10:(int(step)+1)*10]
    return render(request, 'klausimai/latestAdd.html', context={"questions": questions, "load_extra": "unanswered/", "pol_id": pk})

#displays politician info as well as 10 latest answered questions by them
def politicianAns(request, pk):
    politician = Politician.objects.get(pk=pk)
    questions = politician.question_set.order_by('-time').filter(approval=True).filter(answer__politician=politician).distinct()[:10]
    qs_total = politician.question_set.filter(approval=True).count()
    qs_answered = politician.question_set.filter(answer__politician=politician).count()
    context={"questions": questions,
             "pol_name": politician.full_name,
             "biography": politician.biography,
             "description": "Klausimai, užduoti politikui, kuriuos jis atsakė",
             "pol_total": qs_total,
             "pol_answered": qs_answered,
             "load_type": "/politician/"+str(pk)+"/",
             "load_extra": "answered/",
             "pol_id": pk,
             "promises": politician.promise_set.all()}
    return render(request, 'klausimai/latest.html',context=context)

def politicianAnsAdd(request, pk, step):
    politician = Politician.objects.get(pk=pk)
    questions = politician.question_set.order_by('-time').filter(approval=True).filter(answer__politician=politician).distinct()[int(step)*10:(int(step)+1)*10]
    return render(request, 'klausimai/latestAdd.html', context={"questions": questions, "pol_id": pk})

def promise(request, pk):
    prom = get_object_or_404(Promise, pk=pk)
    context = {
        'promise': prom,
        'updates': prom.update_set.order_by('-time_added')
    }
    return render(request, 'klausimai/promise.html', context=context)

#user page, redirects to appropriate page for user
@login_required
def userRedir(request):
    if request.user.is_staff:
        return redirect('klausimai:approval')
    if hasattr(request.user, 'politician'):
        return redirect('klausimai:answers')
    if hasattr(request.user, 'expert'):
        return redirect('klausimai:comments')
    return redirect('klausimai:start')

#moderator internal page, literally just questions with two buttons each
@login_required
def approval(request):
    if not request.user.is_staff:
        return redirect("/")
    context = {
        'questions': Question.objects.filter(approval=None),
        'moderated': request.user.moderated.all(),
    }
    return render(request, 'klausimai/approval.html', context=context)

#politician internal page, lets them set bio as well as answer questions
@login_required
def answers(request):
    try:
        politician = Politician.objects.get(user=request.user)
    except Exception:
        redirect('/')
    context = {
        "questions": Question.objects.filter(approval=True).filter(politicians=politician).exclude(answer__politician=politician),
        "pol_id": politician.id,
        "biography": politician.biography,
        "notif_status": politician.notifs_allow}
    return render(request, 'klausimai/answers.html', context=context)

#just tells experts where to find questions
@login_required
def comments(request):
    return render(request, 'klausimai/comments.html')

#unsubs politician from notification emails about questions they got
@login_required
def unsubReg(request):
    if hasattr(request.user, 'politician'):
        request.user.politician.notifs_allow = False
        request.user.politician.save()
        return redirect('klausimai:answers')
    else:
        return redirect('/')

#resubs politician to notificaion emails about questions they got
@login_required
def subReg(request):
    if hasattr(request.user, 'politician'):
        request.user.politician.notifs_allow = True
        request.user.politician.save()
        return redirect('klausimai:answers')
    else:
        return redirect('/')

#unsubscribes question from notification emails about questions
def unsubUnreg(request, pk):
    try:
        question = Question.objects.get(pk=pk)
    except Exception:
        return redirect('/')
    question.notifs_allow = False
    question.save()
    return redirect('/')
