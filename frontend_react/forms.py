from django import forms

#naudojama admin page projektų ir politikų failų įkėlimui
class FileUploadForm(forms.Form):
    upfile = forms.FileField()


