from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Topic, Entry
from .forms import TopicForm, EntryForm

from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
    """The home page for Learning Log"""
    return render(request, 'learnings_logs/index.html')

def check_topic_owner(request, topic):
    if topic.owner != request.user:
        raise Http404

@login_required
def topics(request):
    """Show all topics."""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learnings_logs/topics.html', context)

@login_required
def topic(request, topic_id):
    """Show a single topic and all its entries."""
    topic = Topic.objects.get(id=topic_id)
    # Make sure the topic belongs to the current user.
    check_topic_owner(request, topic)
    # if topic.owner != request.user:
    #     raise Http404

    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learnings_logs/topic.html', context)

@login_required
def new_topic(request):
    """Add a new topic."""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = TopicForm()
    else:
        # POST data submitted; process data/
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return HttpResponseRedirect(reverse('learnings_logs:topics'))

    context = {'form': form}
    return render(request, 'learnings_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Add a new entry for a particular topic."""
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        # No data dubmitted; create a blank form.
        form = EntryForm()
    else:
        # POST data sumbitted; process data.
        form = EntryForm(data=request.POST)
    
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            check_topic_owner(request, topic)
            new_entry.save()
            return HttpResponseRedirect(reverse('learnings_logs:topic', args=[topic_id]))
    context ={'topic': topic, 'form': form}
    return render(request, 'learnings_logs/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    check_topic_owner(request, topic)
    # if topic.owner != request.user:
    #     raise Http404

    if request.method != 'POST':
        #Initial request; pre-fil form with current entry.
        form = EntryForm(instance=entry)
    else:
        # POST data submitted; process data.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('learnings_logs:topic', args=[topic.id]))
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learnings_logs/edit_entry.html', context)
