from django.contrib import admin
from . models import Listing, Comment, User, Watchlist, Bid, Model, Brand, Category

admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Model)
admin.site.register(Listing)
admin.site.register(User)
admin.site.register(Watchlist)
admin.site.register(Bid)
admin.site.register(Comment)


