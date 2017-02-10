from __future__ import unicode_literals
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

from django.db import models

class Category(models.Model):
	
	name_max_length = 128

	name = models.CharField(max_length=name_max_length, unique=True)
	views = models.IntegerField(default = 0)
	likes = models.IntegerField(default = 0)
	slug = models.SlugField(unique=True)
	
	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Category, self).save(*args, **kwargs)
	
	class Meta:
		verbose_name_plural = 'Categories'
	
	def __str__(self): 
		return self.name
		
	def __unicode__(self): 
		return self.name
		
class Page(models.Model):

	title_max_length = 128
	
	category = models.ForeignKey(Category)
	title = models.CharField(max_length=title_max_length)
	url = models.URLField()
	views = models.IntegerField(default = 0)
	
	def __str__(self):
		return self.title
		
	def __unicode__(self): 
		return self.title
		
class UserProfile(models.Model):
	user = models.OneToOneField(User)
	
	website = models.URLField(blank=True)
	picture = models.ImageField(upload_to='profile_images', blank=True)
	
	def __str__(self): 
		return self.name
		
	def __unicode__(self): 
		return self.name
