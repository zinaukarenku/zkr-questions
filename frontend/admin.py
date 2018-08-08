import tempfile

from django.conf.urls import url
from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group as Authgroup
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import redirect, render

from apiv2 import parsers
from darbai.models import Project, Link
from nariai.models import Politician, Membership, Group
from staticinfo.models import Page

from .forms import FileUploadForm

# Register your models here.

#mūsų admin page klasė
class MainAdmin(admin.AdminSite):
    site_header = 'Platformos valdymas'
    site_title = 'Platformos valdymas'

    #nustatom savo get_urls dėl papildomų views
    #hackas berods paimtas iš oficialių django docs
    def get_urls(self):
        urls = super(MainAdmin, self).get_urls()
        my_urls = [
            url(r'^c/$', self.actions_view),
            url(r'^c/calculate/$', self.calculate_view),
            url(r'^c/projects/$', self.project_upload),
            url(r'^c/politicians/$', self.politician_upload),
        ]
        return urls + my_urls

    #paprastas sąrašiukas linkų į papildomus admin pages
    def actions_view(self, request):
        if not request.user.is_staff:
            return HttpResponse(status = 403)
        request.current_app = self.name
        return render(
            request,
            'custom_admin/main.html',
            self.each_context(request)
        )

    #Paleidžia apskaičiavimo metodus projektų ir politikų objektuose
    def calculate_view(self, request):
        if not request.user.is_staff:
            return HttpResponse(status = 403)
        request.current_app = self.name
        try:
            for politician in Politician.objects.all():
                politician.calculate_attendance()
            for project in Project.objects.all():
                project.calculate_votes()
        except Exception as e:
            messages.add_message(request, messages.ERROR, e)
        else: 
            messages.add_message(request, messages.SUCCESS, 'Statistika perskaičiuota')
        return redirect('/admin/c/')

    #leidžia įkelti projektų duomenis CSV formatu
    #CSV failus sugeneruoja mūsų robotai
    #Šita funkcija iš esmės visą failą persirašo kaip temp failą atmintyje ir
    #paleidžia projektų parserį iš apiv2
    #kada nors pereisim prie JSON ir šitam (kaip politikams)
    def project_upload(self, request):
        if not request.user.is_staff:
            return HttpResponse(status=403)
        request.current_app = self.name
        if request.method == 'POST':
            form = FileUploadForm(request.POST)
            if not form.is_valid:
                messages.add_message(request, messages.ERROR, form.errors)
                return redirect('/admin/c/')
            form = FileUploadForm(request.POST)
            f = tempfile.SpooledTemporaryFile(mode='rw')
            f.write(request.FILES['upfile'].read().decode('utf-8-sig'))
            f.seek(0)
            parsers.parse_projects(f)
            messages.add_message(request, messages.SUCCESS, 'Projektai nuskaityti')
            return redirect('/admin/c/')
        else:
            form = FileUploadForm()
            context = dict(
                self.each_context(request), 
                form = form
            )
            return render(request, 'custom_admin/form.html', context)

    #leidžia įkelti politikų duomenis JSON formatu
    #JSON failus sugeneruoja narių robotas
    #Šita funkcija iš esmės visą failą persirašo kaip temp failą atmintyje ir
    #paleidžia politikų parserį iš apiv2
    def politician_upload(self, request):
        if not request.user.is_staff:
            return HttpResponse(status=403)
        request.current_app = self.name
        if request.method == 'POST':
            form = FileUploadForm(request.POST)
            if not form.is_valid:
                messages.add_message(request, messages.ERROR, form.errors)
                return redirect('/admin/c/')
            f = tempfile.SpooledTemporaryFile(mode='rw')
            f.write(request.FILES['upfile'].read().decode('utf-8-sig'))
            f.seek(0)
            parsers.parse_nariai(f)
            messages.add_message(request, messages.SUCCESS, 'Nariai nuskaityti')
            return redirect('/admin/c/')
        else:
            form = FileUploadForm()
            context = dict(
                self.each_context(request),
                form = form
            )
            return render(request, 'custom_admin/form.html', context)

main_admin = MainAdmin(name='main_admin') #sukuriame admin page pagal viršuje esančią klasę

#Naudojama narysčių (memberships, žr. nariai/models.py) sąrašui prie politiko puslapio admin page
class MembershipInline(admin.TabularInline):
    model = Membership


main_admin.register(User)
main_admin.register(Authgroup)
main_admin.register(Group)
main_admin.register(Link)

#projekto puslapis admin page
#leidžia redaguot reikalingus dalykus ir pažiūrėt neredaguojamus
@admin.register(Project, site=main_admin)
class ProjectAdmin(admin.ModelAdmin):
    readonly_fields = ('code', 'title', 'href',)
    fieldsets = (
        ('Nekeičiami duomenys', {
            'fields': ('code', 'title', 'href',),
        }),
        ('Nustatomi duomenys', {
            'fields':  ('nice_title', 'description', 'category'),
        }),
    )


#politiko puslapis admin page
@admin.register(Politician, site=main_admin)
class PoliticianAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'party', 'area')
    readonly_fields = ('name', 'area', 'party', 'asm_id')
    inlines = (MembershipInline,)
    fieldsets = (
        (None, {
            'fields': ('description','active'),
        }),
        ('Nekeičiami duomenys', {
            'description': 'Šiems duomenims pakeisti reikia mandrybių',
            'fields': readonly_fields,
        }),
    )


@admin.register(Page, site=main_admin)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title',)
