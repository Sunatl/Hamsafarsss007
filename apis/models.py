from django.db import models

    
    
class Group(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(null=True)

    def __str__(self):
        return self.name
    
class Students(models.Model):
    f_name  = models.CharField(max_length=50)
    l_name =  models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    date = models.DateField(auto_now=True)
    phone = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    group = models.ManyToManyField(Group,related_name="group")
    is_active = models.BooleanField(null=True)
    
    def __str__(self):
        return f"{self.f_name} {self.l_name}"




class Attendance(models.Model):
    omadan = models.TimeField(auto_now=True,null=True)
    raftan = models.TimeField(auto_now=True,null=True)
    der_mekunam = models.TextField(null=True)
    nameoyam = models.TextField(null=True)
    student = models.ForeignKey(Students, on_delete=models.CASCADE,related_name="student",null=True)
    
    def __str__(self):
        return self.student.f_name
