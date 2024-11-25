# fuzzy_logic/forms.py
from django import forms

class FileUploadForm(forms.Form):
    file = forms.FileField(label="Загрузите текстовый файл")
