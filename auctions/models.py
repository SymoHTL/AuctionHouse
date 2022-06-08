from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}"


class Brand(models.Model):
    brand = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.brand}"


class Model(models.Model):
    model = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.model}"


class Listing(models.Model):
    name = models.CharField(max_length=64)
    starting_bid = models.IntegerField()
    description = models.CharField(max_length=254)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='categoryId', null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='brandId', null=True, blank=True)
    model = models.ForeignKey(Model, on_delete=models.CASCADE, related_name='modelId', null=True, blank=True)

    url = models.CharField(max_length=254)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner', null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.starting_bid}€ {self.owner}"


class Watchlist(models.Model):
    user_watchlist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_watchlist')
    listing_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='listing_item')

    def __str__(self):
        return f"{self.user_watchlist} {self.listing_item}"


class Bid(models.Model):
    user_bid = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bid')
    item_bid = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='item_bid')
    bid = models.IntegerField()

    def __str__(self):
        return f"{self.user_bid} {self.item_bid.name} {self.bid}"


class Comment(models.Model):
    user_comment = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comment', null=True, blank=True)
    listing_comment = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='listing_comment', null=True,
                                        blank=True)
    comment = models.CharField(max_length=1024)
    date = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f"{self.user_comment} {self.listing_comment.name} {self.comment}"
