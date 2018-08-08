import json

from django.http import JsonResponse
from klausimai.models import Politician, Question, Answer, Comment, Promise, Update
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist

@login_required()
def approval(request):
    #is request in json?
    try:
        jsonReq = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return JsonResponse({'info_type': 'error', 'error': 'not json request'})
    #is the requesting user staff?
    if not request.user.is_staff:
        return JsonResponse({'info_type': 'error', 'error': 'not staff member'})
    #does the request have the correct info?
    try:
        question_id = jsonReq['question_id']
        approval = jsonReq['approval']
    except KeyError:
        return JsonResponse({'info_type': 'error', 'error': 'correct entry not provided'})
    #does the question exist?
    try:
        question = Question.objects.get(pk=question_id)
    except ObjectDoesNotExist:
        return JsonResponse({'info_type': 'error', 'error': 'question does not exist'})
    #let's approve it
    if approval == "approved":
        question.approval = request.user
        for politician in question.politicians.all():
            politician.notifs_activate = True
            politician.save()
        question.save()
    elif approval == "remove":
        question.delete()
    else:
        return JsonResponse({'info_type': 'error', 'error': 'invalid approval decision'})
    return JsonResponse({'info_type': 'ApprovalSuccess'})

@staff_member_required()
def newpromise(request):
    try:
        jsonReq = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return JsonResponse({'info_type': 'error', 'error': 'not json request'})
    if not request.user.is_staff:
        return JsonResponse({'info_type': 'error', 'error': 'not staff member'})
    try:
        promise_text = jsonReq['promise_text']
        politician_id = jsonReq['politician_id']
        source = jsonReq['source']
    except KeyError as e:
        return JsonResponse({'info_type': 'error', 'error': 'correct entry not provided'})
    try:
        politician = Politician.objects.get(pk=politician_id)
    except ObjectDoesNotExist:
        print(politician_id)
        return JsonResponse({'info_type': 'error', 'error': 'politician does not exist'})
    prom = Promise(text=promise_text,politician=politician,source=source)
    prom.save()
    return JsonResponse({'info_type': 'UpdateSuccess'})

@staff_member_required()
def update(request):
    try:
        jsonReq = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return JsonResponse({'info_type': 'error', 'error': 'not json request'})
    if not request.user.is_staff:
        return JsonResponse({'info_type': 'error', 'error': 'not staff member'})
    try:
        promise_id = jsonReq['promise_id']
        update_text = jsonReq['update_text']
    except KeyError as e:
        return JsonResponse({'info_type': 'error', 'error': 'correct entry not provided'})
    try:
        promise = Promise.objects.get(pk=promise_id)
    except ObjectDoesNotExist:
        return JsonResponse({'info_type': 'error', 'error': 'promise does not exist'})
    upd = Update(text=update_text,promise=promise)
    upd.save()
    return JsonResponse({'info_type': 'UpdateSuccess'})

@login_required()
def bio_change(request):
    #is request in json?
    try:
        jsonReq = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return JsonResponse({'info_type': 'error', 'error': 'not json request'})
    #is the requesting user a politician?
    try:
        politician = Politician.objects.get(user=request.user)
    except Exception:
        return JsonResponse({'info_type': 'error', 'error': 'user not politician'})
    #does the request actually have a bio included?
    try:
        bio = jsonReq['new_bio']
    except KeyError:
        return JsonResponse({'info_type': 'error', 'error': 'correct entry not provided'})
    #let's actually do it
    politician.biography = bio
    politician.save()
    return JsonResponse({'info_type': 'BioChangeSuccess'})

@login_required()
def answer(request):
    #is request json?
    try:
        jsonReq = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return JsonResponse({'info_type': 'error', 'error': 'not json request'})
    #is the requesting user a politician?
    try:
        politician = request.user.politician
    except RelatedObjectDoesNotExist:
        return JsonResponse({'info_type': 'error', 'error': 'user not politician'})
    #does the request have the correct things included?
    try:
        question_id = jsonReq['question_id']
        answer_text = jsonReq['answer_text']
    except KeyError:
        return JsonResponse({'info_type': 'error', 'error': 'correct entry not provided'})
    #does the question exist?
    try:
        question = Question.objects.get(pk=question_id)
    except ObjectDoesNotExist:
        return JsonResponse({'info_type': 'error', 'error': 'question does not exist'})
    #save answer
    answer = Answer(answer_text=answer_text,politician=politician,question=question)
    answer.save()
    question.notifs_activate = True
    question.save()
    return JsonResponse({'info_type': 'AnswerSuccess'})

@login_required()
def comment(request):
    #is request json?
    try:
        jsonReq = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return JsonResponse({'info_type': 'error', 'error': 'not json request'})
    #is the requesting user an expert?
    try:
        expert = request.user.expert
    except RelatedObjectDoesNotExist:
        return JsonResponse({'info_type': 'error', 'error': 'user not politician'})
    #does the request have the correct things included?
    try:
        answer_id = jsonReq['answer_id']
        comment_text = jsonReq['comment_text']
    except KeyError:
        return JsonResponse({'info_type': 'error', 'error': 'correct entry not provided'})
    #does the answer exist?
    try:
        answer = Answer.objects.get(pk=answer_id)
    except DoesNotExist:
        return JsonResponse({'info_type': 'error', 'error': 'question does not exist'})
    #save comment
    comment = Comment(comment_text=comment_text,expert=expert,answer=answer)
    comment.save()
    return JsonResponse({'info_type': 'CommentSuccess'})
