from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import *
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Max,Min

from .models import User

class LForm(forms.Form):
     Title = forms.CharField(label="TITLE",max_length=36)
     description = forms.CharField(widget=forms.Textarea , max_length=512)
     starting = forms.IntegerField(label="Opening Bid")
     image = forms.URLField(label="Image",required=False) 

def index(request):
    return render(request, "auctions/index.html" ,{
        "Listings": Listings.objects.all()
    })

@login_required(login_url="/login")
def create(request):
    if request.method == "POST":     
        form = LForm(request.POST)
        flag = 0
        if form.is_valid():
            title = form.cleaned_data["Title"]
            description = form.cleaned_data["description"]
            starting = form.cleaned_data["starting"]
            image_link = form.cleaned_data["image"]
            category = Categories.objects.get(pk=int(request.POST["category"]))
            flag = 1
        if flag == 1:
            item = Listings(Title=title,Description=description,Current_price=starting,Image=image_link,ChosenCategory=category,created_by=User.objects.get(username=request.user.username))
            item.save()
            newbid = Bids(bids=starting,bidded_in=item,bidded_by=User.objects.get(username=request.user.username)) 
            newbid.save()
        return HttpResponseRedirect("/create")
        
    
    return render(request, "auctions/create.html" ,{
        "form":LForm,
        "categories":Categories.objects.all()
    })


def show(request,id):
    print(Listings.objects.count())
    if(Listings.objects.count() == 0):
        return HttpResponse("Sorry , Item doesn't exist")
    if(id<Listings.objects.all().aggregate(Min("id"))['id__min'] or id>Listings.objects.all().aggregate(Max("id"))['id__max']):
        return HttpResponse("Sorry , Item doesn't exist")
    item = Listings.objects.get(pk=id)
    if item.bids.count()==0:                       #this is for listings created in admin interface
        newbid = Bids(bids=item.Current_price,bidded_in=item,bidded_by=User.objects.get(username=request.user.username)) 
        newbid.save()
    item.Current_price=item.bids.all().aggregate(Max("bids"))['bids__max']
    item.save()
    iswatchlist = False
    if request.user in User.objects.all():
         if item in request.user.Witems.all():
            iswatchlist=True
         else:
            iswatchlist=False
   
    if request.method == "POST":
        if 'Closebutton' in request.POST:
            item.is_active = False
            item.save()
            return HttpResponseRedirect("")
        if 'watchlistbutton' in request.POST:
            if item in request.user.Witems.all():
                item.watchlisted_in.remove(request.user)
            else:
                item.watchlisted_in.add(request.user)
            
            return HttpResponseRedirect(f"/{item.id}")
        if 'commentsubmit' in request.POST:
            postedcomment = request.POST["comment"]
            newcomment = Comment(comment=postedcomment,commented_in=item,commented_by=User.objects.get(username=request.user.username))
            newcomment.save()
            return render(request,"auctions/show.html" , {
                    "item":item,
                    "current_bidder":item.bids.all().get(bids=item.Current_price).bidded_by.username,
                    "CSuccess":True,
                    "iswatchlist":iswatchlist
                })
        elif 'bidsubmit' in request.POST:
            placedbid = int(request.POST["bid"])
            if(placedbid>item.bids.all().aggregate(Max("bids"))['bids__max']):
                newbid = Bids(bids=placedbid,bidded_in=item,bidded_by=User.objects.get(username=request.user.username)) 
                newbid.save()
                item.Current_price=item.bids.all().aggregate(Max("bids"))['bids__max']
                item.save()
                return render(request,"auctions/show.html" , {
                    "item":item,
                    "current_bidder":item.bids.all().get(bids=item.Current_price).bidded_by.username,
                    "Success":True,
                    "iswatchlist":iswatchlist
                })
            else:
                return render(request,"auctions/show.html" , {
                    "item":item,
                    "current_bidder":item.bids.all().get(bids=item.Current_price).bidded_by.username,
                    "Error":True,
                    "iswatchlist":iswatchlist
                })  
            
    print(iswatchlist)
    return render(request,"auctions/show.html" , {
        "item":item,
        "current_bidder":item.bids.all().get(bids=item.Current_price).bidded_by.username,
        "iswatchlist":iswatchlist
    })

def category(request):
    return render(request , "auctions/category.html" , {
        "Categories" : Categories.objects.all()
    })

def showcategory(request,categoryname):
    return render(request , "auctions/showcategory.html",{
        "items":Categories.objects.get(category=categoryname).items.all()
    })

@login_required(login_url="/login")
def watchlist(request):
    current_user = request.user
    return render(request , "auctions/watchlist.html" , {
        "witems": current_user.Witems.all()
    })




def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
