from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import Max
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Watchlist, Bid, Comment, Category, Brand, Model


class BidForm(forms.Form):
    bid_form = forms.IntegerField(required=True, label='Create your bid')
    bid_form.widget.attrs.update({'class': 'form-control'})


class CommentForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(), label='Leave a comment')
    comment.widget.attrs.update({
        'class': 'form-control',
        'rows': '3'
    })


def index(request):
    all_listings = Listing.objects.all()
    # Get unique values from category query
    all_categories = Category.objects.all()
    all_brands = Brand.objects.all()
    all_models = Model.objects.all()
    return render(request, "auctions/index.html", {
        "all_categories": all_categories,
        "listings": all_listings,
        "all_brands": all_brands,
        "all_models": all_models})


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


@login_required
def create_listing(request):
    if request.method == "GET":
        all_categories = Category.objects.all()
        all_brands = Brand.objects.all()
        all_models = Model.objects.all()
        return render(request, "auctions/create_listing.html", {
            "all_categories": all_categories,
            "all_brands": all_brands,
            "all_models": all_models,
        })
    if request.method == "POST":
        name = request.POST["name"]
        categoryId = request.POST["categoryId"]
        brandId = request.POST["brandId"]
        modelId = request.POST["modelId"]
        starting_bid = request.POST["starting_bid"]
        description = request.POST["description"]
        url = request.POST["url"]
        owner = request.POST['owner']
        user_owner = User.objects.get(username=owner)
        try:
            listings_created = Listing(name=name, category_id=categoryId, brand_id=brandId, model_id=modelId,
                                       starting_bid=starting_bid, description=description, url=url, owner=user_owner)

            listings_created.save()
            return HttpResponseRedirect(reverse("index"))
        except IntegrityError:
            return render(request, "auctions/create_listing.html", {
                "message": "Listing not created."
            })

    return render(request, "auctions/create_listing.html")


@login_required
def purchase_history(request):
    if request.method == "GET":
        listings = []
        if len(Listing.objects.get(winner_id=request.user.id)) is 0:
            listings = Listing.objects.none()
        else:
            listings = Listing.objects.get(winner_id=request.user.id)
        return render(request, "auctions/purchase_history.html", {
            "listings": listings
        })


def active_listing(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id)
        current_user = request.user.id
        bid_count = Bid.objects.filter(item_bid=listing_id).count()
        if bid_count > 0:
            max_bid = Bid.objects.filter(item_bid=listing_id).aggregate(Max('bid'))
            max_bid = max_bid['bid__max']
        else:
            max_bid = listing.starting_bid
        if Watchlist.objects.filter(user_watchlist=current_user, listing_item=listing_id).exists():
            watchlist_state = False
        else:
            watchlist_state = True
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")
    # All comments
    # Get comments for this listing item
    comments = Comment.objects.filter(listing_comment=listing_id)
    # Make a Bid block
    if request.method == 'POST':
        form = BidForm(request.POST)
        current_user = request.user.id
        listing_id = request.POST["listing_id"]
        listing_item = Listing.objects.get(id=listing_id)
        user_bid = User.objects.get(id=current_user)
        if form.is_valid():
            current_bid = form.cleaned_data['bid_form']
            bid_count = Bid.objects.filter(item_bid=listing_id).count()
            if bid_count > 0:
                max_bid = Bid.objects.filter(item_bid=listing_id).aggregate(Max('bid'))
                max_bid = max_bid['bid__max']
            else:
                max_bid = listing_item.starting_bid
            if current_user is listing_item.owner.id:
                return render(request, "auctions/active_listing.html", {
                    "listing": listing_item,
                    'comments': comments,
                    'max_bid': max_bid,
                    'bid_count': bid_count,
                    'form': BidForm(),
                    'comment_form': CommentForm(),
                    "err_message": "You cannot bid on your own listing."
                })
            if current_bid > max_bid:
                bid = Bid(user_bid=user_bid, item_bid_id=listing_item.id, bid=current_bid)
                bid.save()
                return render(request, "auctions/active_listing.html", {
                    "listing": listing_item,
                    'comments': comments,
                    'max_bid': current_bid,
                    'bid_count': bid_count + 1,
                    'form': BidForm(),
                    'comment_form': CommentForm(),
                    "succ_message": f"You made a successful bid for {current_bid} € !"
                })
            else:
                return render(request, "auctions/active_listing.html", {
                    "listing": listing_item,
                    'comments': comments,
                    'max_bid': max_bid,
                    'bid_count': bid_count,
                    'form': BidForm(),
                    'comment_form': CommentForm(),
                    "err_message": "Bid can't be less than current max bid"
                })
        else:
            return HttpResponseBadRequest("Form is not valid")
    # End bid block
    return render(request, "auctions/active_listing.html", {
        "listing": listing,
        'comments': comments,
        'watchlist_state': watchlist_state,
        'bid_count': bid_count,
        'max_bid': max_bid,
        'form': BidForm(),
        'comment_form': CommentForm()
    })


@login_required
def watchlist(request):
    current_user = request.user.id
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        # Get User id and Listing id through their models
        watching_user = User.objects.get(id=current_user)
        listing_item = Listing.objects.get(id=listing_id)
        # Create watchlist
        watchlist = Watchlist(user_watchlist=watching_user, listing_item=listing_item)
        # Check if user already have that item in watchlist
        current_item = Watchlist.objects.filter(user_watchlist=current_user, listing_item=listing_item)
        if current_item.exists():
            current_item.delete()
        else:
            watchlist.save()
    current_watch_id = Watchlist.objects.filter(user_watchlist=current_user)
    current_watchlist = current_watch_id.all()
    return render(request, "auctions/watchlist.html", {
        "all_watchlists": current_watchlist
    })


@login_required
def close_bid(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        active_listing = Listing.objects.get(id=listing_id)
        active_listing.active = False
        bid_count = Bid.objects.filter(item_bid=listing_id).count()
        if bid_count > 0:
            max_bid = Bid.objects.filter(item_bid=listing_id).aggregate(Max('bid'))
            max_bid = max_bid['bid__max']
            bid_winner = Bid.objects.get(item_bid=listing_id, bid=max_bid)
            active_listing.winner = bid_winner.user_bid
        else:
            active_listing.winner = None
        active_listing.save()
        return HttpResponseRedirect(reverse('index'))


@login_required
def comment(request):
    current_user = request.user.id
    current_user = User.objects.get(id=current_user)
    comment_form = CommentForm(request.POST)
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing_item = Listing.objects.get(id=listing_id)
        if comment_form.is_valid():
            current_comment = comment_form.cleaned_data['comment']
            create_comment = Comment(user_comment=current_user, listing_comment=listing_item, comment=current_comment)
            create_comment.save()
            return HttpResponseRedirect(reverse('active_listing', args=(listing_id,)))
        else:
            raise forms.ValidationError(comment_form.errors)


def category(request, category):
    category = Category.objects.get(category=category)
    listing_category = Listing.objects.filter(category_id=category.id)
    return render(request, "auctions/category.html", {
        'category': category,
        'listing_category': listing_category
    })


def brand(request, brand):
    brand = Brand.objects.get(brand=brand)
    listing_brand = Listing.objects.filter(brand_id=brand.id)
    return render(request, "auctions/brand.html", {
        'brand': brand,
        'listing_brand': listing_brand
    })


def model(request, model):
    model = Model.objects.get(model=model)
    listing_model = Listing.objects.filter(model_id=model.id)
    return render(request, "auctions/model.html", {
        'model': model,
        'listing_model': listing_model
    })
