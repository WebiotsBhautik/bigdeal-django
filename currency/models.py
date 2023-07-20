import uuid
from django.db import models
from django.utils.text import slugify

# Create your models here.


class Currency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name=models.CharField(max_length=20)
    code=models.CharField(max_length=3)
    factor=models.DecimalField(max_digits=30,decimal_places=2, default=1.0)
    symbol=models.CharField(max_length=20)
    is_active=models.BooleanField(default=True,verbose_name='Status')
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(Currency, self).save(*args, **kwargs)

   