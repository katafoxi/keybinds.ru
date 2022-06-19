from django.db import models
from django.urls import reverse


class Program(models.Model):
    title= models.CharField(max_length=50)
    version= models.CharField(max_length=50)
    icon = models.ImageField(upload_to='icon')
    program_site = models.URLField(max_length=250)

    def __str__(self):
        return  self.title

    def get_absolute_url(self):
        return reverse('program', kwargs={'program_id':self.pk})

class ProgramCommand(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    command_name = models.CharField(max_length=250)
    command_description = models.CharField(max_length=250)
    command_help = models.URLField(max_length=250)
    icon = models.ImageField(upload_to='icon')

    def __str__(self):
        return  self.command_name






