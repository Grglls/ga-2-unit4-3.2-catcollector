from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView

from .models import Cat, Toy
from .forms import FeedingForm

# Create your views here.
def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def cats_index(request):
    cats = Cat.objects.all()
    return render(request, 'cats/index.html', { 'cats': cats })


def cats_detail(request, cat_id):
    cat = Cat.objects.get(id=cat_id)
    # Toy id's the cat does have:
    id_list = cat.toys.all().values_list('id')
    # Toy id's the cat doesn't have:
    toys_cat_doesnt_have = Toy.objects.exclude(id__in=id_list)
    feeding_form = FeedingForm()
    return render(request, 'cats/detail.html', {
        'cat': cat,
        'feeding_form': feeding_form,
        'toys': toys_cat_doesnt_have
    })


def add_feeding(request, cat_id):
    # Create a ModelForm instance using the data from the request:
    form = FeedingForm(request.POST)
    # Validate the form:
    if form.is_valid():
        # Don't save the form to the db until it has the cat_id assigned:
        new_feeding = form.save(commit=False)
        new_feeding.cat_id = cat_id
        new_feeding.save()
    return redirect('detail', cat_id=cat_id)


class CatCreate(CreateView):
    model = Cat
    fields = ['name', 'breed', 'description', 'age']


class CatUpdate(UpdateView):
    model = Cat
    fields = ['breed', 'description', 'age']


class CatDelete(DeleteView):
    model = Cat
    success_url = '/cats'


class ToyIndex(ListView):
    model = Toy


class ToyDetail(DetailView):
    model = Toy


class ToyCreate(CreateView):
    model = Toy
    fields = '__all__'


class ToyUpdate(UpdateView):
    model = Toy
    fields = ['name', 'colour']


class ToyDelete(DeleteView):
    model = Toy
    success_url = '/toys'


def assoc_toy(request, cat_id, toy_id):
    # Note that you can pass a toy's id instead of the whole toy object:
    Cat.objects.get(id=cat_id).toys.add(toy_id)
    return redirect('detail', cat_id=cat_id)