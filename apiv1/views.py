import json

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from klausimai.models import Party, Area, Politician, Expert, Question, Answer
#from django.contrib.auth.models import User

# Create your views here.

def stats(request):
    total_questions = Question.objects.filter(approval=True).count()
    total_answers = Answer.objects.all().count()
    answered_questions = Question.objects.filter(answer__isnull=False).distinct().count()
    total_politicians = Politician.objects.all().count()
    registered_politicians = Politician.objects.filter(is_registered=True).count()
    jsonResp = {
        'info_type': 'stats',
        'total_answers': total_answers,
        'total_questions': total_questions,
        'answered_questions': answered_questions,
        'total_politicians': total_politicians,
        'registered_politicians': registered_politicians,
        'party_stats': []
    }
    for party in Party.objects.all():
        jsonResp['party_stats'].append({
            'party_name': party.name,
            'total_questions': Question.objects.filter(approval=True, politicians__party=party).count(),
            'total_answers': Answer.objects.filter(politician__party=party).count(),
            'total_questions_distinct':  Question.objects.filter(approval=True, politicians__party=party).distinct().count(),
            'answered_questions': Question.objects.filter(answer__politician__party=party).distinct().count(),
            'total_politicians': party.politician_set.all().count(),
            'registered_politicians': party.politician_set.filter(is_registered=True).count(),
        })
    return JsonResponse(jsonResp)

def latest(request):
    total_questions = Question.objects.filter(approval=True).count()
    answered_questions = Question.objects.filter(answer__isnull=False).distinct().count()
    total_answers = Answer.objects.all().count()
    answers = Answer.objects.exclude(politician__party__active=False).order_by('-time')[:5]
    jsonResp = {
        'info_type': 'latestAnswers',
        'total_questions': total_questions,
        'answered_questions': answered_questions,
        'total_answers': total_answers,
        'questions': []
    }
    for answer in answers:
        jsonResp['questions'].append({
            'question_text': answer.question.question_text,
            'question_id': answer.question.id,
            'answer_text': answer.answer_text,
            'politician_id': answer.politician.id,
            'politician_name': answer.politician.full_name,
            'politician_party': answer.politician.party.name,
            'politician_area': answer.politician.area.proper_name,
        })
    return JsonResponse(jsonResp)

def question_dump(request):
    questions = Question.objects.filter(approval=True)
    jsonResp = {
        'info_type': 'questionDump',
        'total_questions': len(questions),
        'questions': [],
    }
    for question in questions:
        jsonResp['questions'].append({
            'question_id': question.id,
            'question_text': question.question_text,
            'answers': question.answer_set.count(),
            'asked_pols': question.politicians.count(),
        })
    return JsonResponse(jsonResp)

def politicianInfo(request, pk):
    politician = get_object_or_404(Politician, pk=pk)
    jsonResp = {
        'info_type': 'politicianInfo',
        'id': pk,
        'full_name': politician.full_name,
        'email': politician.email,
        'biography': politician.biography,
        'party': politician.party.name,
        'party_id': politician.party.id,
        'area': politician.area,
        'area_id': politician.area.id,
        'questions': [],
        'answers': [],
    }
    for question in politician.question_set.all():
        jsonResp['questions'].append({
            'id': question.id,
            'question_text': question.question_text
        })
    for answer in politician.answer_set.all():
        jsonResp['answers'].append({
            'id': answer.id,
            'question_id': answer.question.id,
            'answer_text': answer.answer_text,
        })
    return JsonResponse(jsonResp)

def expertInfo(request, pk):
    expert = get_object_or_404(Expert, pk=pk)
    jsonResp = {
        'info_type': 'expertInfo',
        'full_name': expert.full_name,
        'id': pk,
        'email': expert.email,
        'biography': expert.biography,
        'organisation': expert.organisation,
        'comments': [],
    }
    for comment in expert.comment_set.all():
        jsonResp['comments'].append({
            'question_id': comment.answer.question.id,
            'question_text': comment.answer.question.question_text,
            'answer_id': comment.answer.id,
            'answer_text': comment.answer.answer_text,
            'id': comment.id,
            'comment_text': comment.comment_text,
        })
    return JsonResponse(jsonResp)

def partyList(request):
    jsonResp = {
        'info_type': 'partyList',
        'parties': []
    }
    parties = Party.objects.all()
    for party in parties:
        jsonResp['parties'].append({
                'id': party.id,
                'name': party.name,
                'website': party.website
            })
    return JsonResponse(jsonResp)

def partyInfo(request, pk):
    party = get_object_or_404(Party, pk=pk)
    jsonResp =  {
        'info_type': 'partyinfo',
        'id': pk,
        'name': party.name,
        'website': party.website,
        'politicianCount': party.politician_set.all().count(),
        'politicianList': []
    }
    for politician in party.politician_set.all():
        jsonResp['politicianList'].append({
            'id': politician.id,
            'full_name': politician.full_name
        })
    return JsonResponse(jsonResp)

def areaList(request):
    areas = Area.objects.all()
    jsonResp = {
        'info_type': 'areaList',
        'areas': []
    }
    for area in areas:
        jsonResp['areas'].append({
            'id':area.id,
            'proper_name': area.proper_name,
            'area_type': area.area_type.area_type
        })
    return JsonResponse(jsonResp)

def areaInfo(request, pk):
    area = get_object_or_404(Area, pk=pk)
    jsonResp = {
        'info_type': 'areaInfo',
        'proper_name': area.proper_name,
        'area_type': area.area_type.area_type
    }
    return JsonResponse(jsonResp)

def questionInfo(request, pk):
    question = get_object_or_404(Question, pk=pk)
    jsonResp = {
        'info_type': 'questionInfo',
        'id': pk,
        'question': question.question_text,
        'time': question.time,
        'email': question.email,
        'answers': []
    }
    for answer in question.answer_set.all():
        jsonResp['answers'].append({
            'id': answer.id,
            'time': answer.time,
            'politician_id': answer.politician.id,
            'politician_name': answer.politician.full_name,
            'politician_party': answer.politician.party.name,
            'politician_area': answer.politician.area.proper_name,
            'answer_text': answer.answer_text,
            'comment_count': answer.comment_set.count(),
        })
    return JsonResponse(jsonResp)

def answerInfo(request, pk):
    answer = get_object_or_404(Answer, pk=pk)
    jsonResp = {
        'id': answer.id,
        'question_id': answer.question.id,
        'time': answer.time,
        'politician_id': answer.politician.id,
        'answer_text': answer.answer_text,
        'comments': [],
    }
    for comment in answer.comment_set.all():
        jsonResp['comments'].append({
            'id': comment.id,
            'time': comment.time,
            'expert_id': comment.expert.id,
            'expert_name': comment.expert.full_name,
            'comment_text': comment.comment_text,
        })
    return JsonResponse(jsonResp)

def askQuestion(request):
    try:
        jsonReq = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return JsonResponse({'info_type': 'error', 'error': 'not json request'})
    try:
        req_email = jsonReq['email']
        req_question = jsonReq['question_text']
        req_politicians = jsonReq['politicians']
    except KeyError:
        return JsonResponse({'info_type': 'error', 'error': 'correct entry not provided'})
    newQuestion = Question(
        email=req_email,
        question_text=req_question
    )
    newQuestion.save()
    if 'all' in req_politicians:
        for pol in Politician.objects.filter(status='is'):
            newQuestion.politicians.add(pol)
        newQuestion.save()
        return JsonResponse({'info_type': 'questionAddSuccess','id': newQuestion.id})
    else:
        for politician_id in req_politicians:
            try:
                politician = Politician.objects.get(pk=politician_id)
                newQuestion.politicians.add(politician)
                politician.save()
            except Exception:
                pass
        newQuestion.save()
        return JsonResponse({'info_type': 'questionAddSuccess','id': newQuestion.id})

def partyId(request):
    try:
        jsonReq = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return JsonResponse({'info_type': 'error', 'error': 'not json request'})
    try:
        req_party = jsonReq['party']
    except KeyError:
        return JsonResponse({'info_type': 'error', 'error': 'correct entry not provided'})
    try:
        party = Party.objects.get(name=req_party)
    except Exception:
        return JsonResponse({'info_type': 'error', 'error': 'party does not exist'})
    return JsonResponse({'info_type': 'party_id', 'id': party.id})

def politicianId(request):
    try:
        jsonReq = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return JsonResponse({'info_type': 'error', 'error': 'not json request'})
    try:
        req_politician = jsonReq['politician']
    except KeyError:
        return JsonResponse({'info_type': 'error', 'error': 'correct entry not provided'})
    try:
        politician = Politician.objects.get(full_name=req_politician)
    except Exception:
        return JsonResponse({'info_type': 'error', 'error': 'party does not exist'})
    return JsonResponse({'info_type': 'politician_id', 'id': politician.id})

def areaId(request):
    try:                       
        jsonReq = json.loads(request.body.decode("utf-8"))
    except ValueError:                                      
        return JsonResponse({'info_type': 'error', 'error': 'not json request'})
    try:  
        req_area = jsonReq['area']              
    except KeyError:
        return JsonResponse({'info_type': 'error', 'error': 'correct entry not provided'})
    try:  
        area = Area.objects.get(proper_name=req_politician)
    except Exception:                              
        return JsonResponse({'info_type': 'error', 'error': 'party does not exist'})
    return JsonResponse({'info_type': 'area_id', 'id': area.id})
