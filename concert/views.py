from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending
import requests as req


# Create your views here.

def signup(request):
    # verifying the reqeust is a POST
    if request.method == "POST":
        # getting the username and password 
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            # retrieving the first user object that matches the username
            user = User.objects.filter(username=username).first()
            # if a matching object was found
            if user:
                # returning the signup page withe the message that the user exists
                return render(request, "signup.html", {"form": SignUpForm, "message": "user already exists"})
            # user was not found so a new one can be created
            else:
                # creates a new user object with the username and password, saving the new object
                user = User.objects.create( username=username, password=make_password(password))
                # calling the login method with the request and user object
                login(request, user)
                # sending the user back to the mainpage
                return HttpResponseRedirect(reverse("index"))
        except User.DoesNotExist:
            return render(request, "signup.html", {"form": SignUpForm})
    # default return, sending user to the signup page and displaying the signup form
    return render(request, "signup.html", {"form": SignUpForm})
    


def index(request):
    return render(request, "index.html")


def songs(request):
    songs = {"songs":[
        {"id":1,
        "title":"duis faucibus accumsan odio curabitur convallis",
        "lyrics":"Morbi non lectus. Aliquam sit amet diam in magna bibendum imperdiet. Nullam orci pede, venenatis non, sodales sed, tincidunt eu, felis."}
    ]}
    return render(request, "songs.html", {"songs": songs["songs"]})
    


def photos(request):
    photos = [{
    "id": 1,
    "pic_url": "http://dummyimage.com/136x100.png/5fa2dd/ffffff",
    "event_country": "United States",
    "event_state": "District of Columbia",
    "event_city": "Washington",
    "event_date": "11/16/2022"
    }]
    return render(request, "photos.html", {"photos": photos})
    

def login_view(request):
    if request.method == "POST":
        # getting the username and password from the request
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.filter(username=username).first()
            # checks if a user was returned, if not user does not exist
            if not user:
                return render(request, "login.html", {"form": LoginForm})
            # user was found, checking if password is correct
            if user.check_password(password):
                login(request,user)
                return HttpResponseRedirect(reverse("index"))
        except User.DoesNotExist:
            return render(request, "login.html", {"form": LoginForm})
    # default return request, sending user back to login form
    return render(request, "login.html", {"form": LoginForm})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))

def concerts(request):
    print("concerts() function was called")
    # verifying user is signed in
    if request.user.is_authenticated:
        concert_list = []
        # getting all of the documents for the concerts
        concert_objects = Concert.objects.all()

        # looping through the concert objects
        for item in concert_objects:
            try:
                # getting the first user with the username passed in the request and
                # checking the value of the attending key:value
                status = item.attendee.filter(user=request.user).first().attending
            except Exception as e:
                status = "-"
                print("Exception thrown: " + str(e) + " status = " + str(status))
            # adding key:value pairs to the list of concert object
            concert_list.append({
                "concert": item,
                "status": status
            })
        # rendering the concerts html page with the concert key value being the list
        # of concerts from above
        return render(request, "concerts.html", {"concerts": concert_list})
    else:
        # default return redircting user to the login page
        return HttpResponseRedirect(reverse("login"))


def concert_detail(request, id):
    # verifying user in the request is authenticated
    if request.user.is_authenticated:
        # retrieving the document with a matching id value from the request
        obj = Concert.objects.get(pk=id)
        try:
            # gets the first matching attendee with a matching first name
            # and retrieving the attending value
            status = obj.attendee.filter(user=request.user).first().attending
        except:
            status = "-"
        # returning the concert_detail html page with key:value pairs filled in
        return render(request, "concert_detail.html", {"concert_details": obj, "status": status, "attending_choices": ConcertAttending.AttendingChoices.choices})
    else:
        # default response sending user to the login page
        return HttpResponseRedirect(reverse("login"))
    pass


def concert_attendee(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            concert_id = request.POST.get("concert_id")
            attendee_status = request.POST.get("attendee_choice")
            concert_attendee_object = ConcertAttending.objects.filter(
                concert_id=concert_id, user=request.user).first()
            if concert_attendee_object:
                concert_attendee_object.attending = attendee_status
                concert_attendee_object.save()
            else:
                ConcertAttending.objects.create(concert_id=concert_id,
                                                user=request.user,
                                                attending=attendee_status)

        return HttpResponseRedirect(reverse("concerts"))
    else:
        return HttpResponseRedirect(reverse("index"))
