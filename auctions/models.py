from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass



class Categories(models.Model):
    category = models.CharField(max_length=24)

    def __str__(self):
        return self.category


class Listings(models.Model):
    Title = models.CharField(max_length=36 , blank=False)
    Description = models.CharField(max_length=512, blank=False)
    Current_price = models.IntegerField(blank=False) 
    Image = models.URLField(blank = True)
    ChosenCategory = models.ForeignKey(Categories, on_delete=models.PROTECT ,blank=True, null=True , related_name="items")
    created_by = models.ForeignKey(User,on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    watchlisted_in = models.ManyToManyField(User,blank=True, null=True,related_name="Witems")

    def __str__(self):
        return self.Title

class Comment(models.Model):
    comment = models.CharField(max_length=512)
    commented_in = models.ForeignKey(Listings,on_delete=models.CASCADE,related_name="comments")
    commented_by = models.ForeignKey(User,on_delete=models.CASCADE)


class Bids(models.Model):
    bids = models.IntegerField()
    bidded_in = models.ForeignKey(Listings,on_delete=models.CASCADE,related_name="bids")
    bidded_by = models.ForeignKey(User,on_delete=models.PROTECT)




   






