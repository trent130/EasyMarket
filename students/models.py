from django.db import models

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # other fields...

    def __str__(self): 
        return self.first_name + ' ' + self.last_name
    
    class Meta:
        ordering = ['last_name']
        
class payment(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # other fields...

    def __str__(self): 
        return self.first_name + ' ' + self.last_name
    
    class Meta:
        ordering = ['last_name']
    