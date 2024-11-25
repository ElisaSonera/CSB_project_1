from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Choice, Question
from django.views.decorators.csrf import csrf_exempt #FLAW 2 (2/2)




class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        FLAW 1: Broken access control (1/2)

        Originally this function returned the last five published questions 
        (not including those set to be published in the future).

        To implement broken access control, this function now returns
        all the questions, whether published or not.

        """
    #FLAW 1 fix: Uncomment the line after this and remove the line after it
        #return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
        return Question.objects.all().order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        FLAW 1: Broken access control (2/2)

        Originally this function excluded any questions 
        that weren't published yet.

        To implement broken access control, this function now
        let's user access unpublished questions too.

        """

    #FLAW 1 fix: Uncomment the line after this and remove the line under it.
        #return Question.objects.filter(pub_date__lte=timezone.now())        
        return Question.objects.all()



class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


""" 
        FLAW 2: CSRF

        CSRF is disabled for the voting function.
        Therefore, the voting system can be attacked with
        cross site request forgery.

"""
#FLAW 2 fix: Remove the exempt under this comment   (1/2)
# and the csrf exempt import on line 7              (2/2)
@csrf_exempt
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


##### LISÄYS: SIGN UP OMINAISUUS ####

from django.contrib.auth.forms import UserCreationForm    

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()   
            return HttpResponseRedirect(reverse('polls:index')) 
    else:
        form = UserCreationForm()
    return render(request, 'polls/signup.html', {'form': form})