from django.shortcuts import render

# Create your views here.

def main_render(request, page='stebek', slug=''):
    return render(request, 'frontend.html', {'page': page})
