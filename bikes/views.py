from django.shortcuts import render
from django.http import HttpResponse
from django.template import Template, Context

from .models import *

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def html_escape(text):
    """Produce entities within text."""
    return "".join(html_escape_table.get(c,c) for c in text)

# Create your views here.

def index(request):
    s = bike.objects.filter(station=1)
    print s
    return render(request, 'bikes/index.html', context = {'bikes':s})

# class IndexView(generic.ListView):
#     template_name = 'polls/index.html'
#     context_object_name = 'latest_question_list'
#
#     def get_queryset(self):
#         """Return the last five published questions."""
#         return Question.objects.filter(pub_date__lte = timezone.now()).order_by('-pub_date')[:5]
