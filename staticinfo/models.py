import markdown

from django.db import models

# Create your models here.

class Page(models.Model):
    title = models.TextField()
    content = models.TextField()
    slug = models.SlugField(unique=True)
    hidden = models.BooleanField(default=False)
    
    def as_html(self):
        return markdown.markdown(self.content)
