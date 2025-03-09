from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.timezone import now

class Lesson(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)  # Auto slug field
    body = models.TextField()
    created_at = models.DateTimeField(default=now)  # Auto date of creation
    thumbnail = models.ImageField(default='logo.png', blank=False)

    def __str__(self):
        return self.title

    def snippet(self):
        return self.body[:50] + '...'

    def save(self, *args, **kwargs):
        # Generate slug only if it doesn't exist
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)  # Call the original save method