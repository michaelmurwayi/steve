from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone

from django.db.models import F

from .models import Choice, Question

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte = timezone.now()).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    # def get_queryset(self):
    #     """
    #     Excludes any questions that aren't published yet.
    #     """
    #     return Question.objects.filter(pub_date__lte = timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})
#
# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/results.html', {'question': question})

from time import sleep

def vote(request, question_id):
    print Question, dir(Question), '\n\n\n\n'
    question = get_object_or_404(Question, pk=question_id)
    print request.POST.getlist('choice[]')

    try:
        if not len(request.POST.getlist('choice[]')):
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': "You didn't select a choice.",
            })
        else:
            print question.choice_set.filter(pk__in=request.POST.getlist('choice[]'))
            question.choice_set.filter(pk__in=request.POST.getlist('choice[]')).update(votes=F('votes')+1)
            # sleep(3)
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
    except:
        pass
