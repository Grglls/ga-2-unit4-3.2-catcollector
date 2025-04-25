import uuid
import os
import boto3
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

from .models import Cat, Toy, Photo
from .forms import FeedingForm

# Create your views here.
def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def cats_index(request):
    cats = Cat.objects.filter(user=request.user)
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


def add_photo(request, cat_id):
    # photo-file will be the 'name' attribute on the input field, return None if not found:
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        # Need a unique 'key' for S3, needs image file extension too:
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        # Use try/except block incase there's an error:
        try:
            bucket = os.environ['S3_BUCKET']
            s3.upload_fileobj(photo_file, bucket, key)
            # Build the full URL for the photo:
            url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
            # Add the photo to the database:
            Photo.objects.create(url=url, cat_id=cat_id)
        except Exception as e:
            print('An error occurred uploading file to S3')
            print(e)
    return redirect('detail', cat_id=cat_id)


class CatCreate(CreateView):
    model = Cat
    fields = ['name', 'breed', 'description', 'age']

    # Override the inherited method called when a valid form is submitted:
    def form_valid(self, form):
        # Assign the logged in user (self.request.user) to the cat (form.instance):
        form.instance.user = self.request.user
        # Pass control back to the superclass CreateView's form_valid() method to do its job:
        return super().form_valid(form)


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


def unassoc_toy(request, cat_id, toy_id):
    # Note that you can pass a toy's id instead of the whole toy object:
    Cat.objects.get(id=cat_id).toys.remove(toy_id)
    return redirect('detail', cat_id=cat_id)


def signup(request):
    error_messaage = ''
    if request.method == 'POST':
        # Create a UserCreationForm instance using the data from the request:
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the form to the database:
            user = form.save()
            # Log the user in:
            login(request, user)
            return redirect('index')
        else:
            # If the form is not valid, set the error message:
            error_messaage = 'Invalid sign up - try again'
    # If the request method is GET, or the sign up fails, render signup.html with an empty form:
    form = UserCreationForm()
    context = {
        'form': form,
        'error_message': error_messaage
    }
    return render(request, 'registration/signup.html', context)