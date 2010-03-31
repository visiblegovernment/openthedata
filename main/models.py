from django.db import models       
    
class Department(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255,null=True)
    abbrev = models.CharField(max_length=5)

    def __unicode__(self):
        return( self.name  )

class DataCategory(models.Model): 
    STANDARD = 0
    SPECIFIC = 1

    CategoryTypeChoices = [
        (STANDARD, 'Standard'),
        (SPECIFIC, 'Department Specific'), 
    ]
            
    type = models.IntegerField(choices=CategoryTypeChoices)    
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=60)
    desc = models.TextField()
    format = models.CharField(max_length=500)
    access = models.TextField()
    
    def __unicode__(self):
        return( self.code  )


class DepartmentDataCategory(models.Model):    
    dept = models.ForeignKey(Department)
    category = models.ForeignKey(DataCategory)
        
class DataSet(models.Model):
    desc = models.TextField()
    code = models.CharField(max_length=25,null=True, blank=True)    
    category = models.ForeignKey(DataCategory)
       
