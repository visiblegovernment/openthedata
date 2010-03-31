from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.db.models import Q
from main.models import DataCategory,Department,DepartmentDataCategory
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, RequestContext

def index( request ):
    categories = DataCategory.objects.filter(type=DataCategory.STANDARD).annotate()
    departments = Department.objects.all()

    matrix = {}
    for department in departments:
        matrix[department.name] = {} 
        for category in categories:   
            matrix[department.name][category.id] = None
            
    departmentcategories = DepartmentDataCategory.objects.filter(category__type=DataCategory.STANDARD)
    for cross in departmentcategories:
        matrix[cross.dept.name][cross.category.id] = cross
        
    return render_to_response("main/standard_matrix/index.html",
                {'categories': categories,
                 'matrix': matrix,
                 'departments':  departments },
                context_instance=RequestContext(request))
