from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from datetime import datetime
from django.template import defaultfilters



def usr_img_destination(instance, filename):
	destination = 'user_images/%s/%s' % (instance.user.username, filename)
	return destination


def team_img_destination(instance, filename):
	destination = 'team_images/%s/%s' % (instance.name, filename)
	return destination


class UserProfile(models.Model):
	user = models.OneToOneField(User)
	image = models.ImageField(upload_to=usr_img_destination, default="default_images/default_user_img.png")
	birthday = models.DateField(blank=True, null=True)
	country = models.CharField(max_length=100, blank=True)
	city = models.CharField(max_length=100, blank=True)
	address = models.CharField(max_length=200, blank=True)
	about_me = models.TextField(max_length=1000, blank=True)
	posts = models.IntegerField(default=0)	

	def __unicode__(self):
		return unicode(self.user)

	def get_absolute_url(self):
		return reverse('user_overview', kwargs={'user_id':self.user.id})
		
	def increment_posts(self):
		self.posts += 1
		self.save()


class Category(models.Model):
	category = models.CharField(max_length=100)

	class Meta:
		verbose_name = 'Category'
		verbose_name_plural = 'Categories'

	def __unicode__(self):
		return unicode(self.category)

	def get_absolute_url(self):
		return reverse('search_subcategory', kwargs={'category_id':self.id})

class SubCategory(models.Model):
	category = models.ForeignKey(Category)
	subcategory = models.CharField(max_length=100)

	class Meta:
		verbose_name = 'Subcategory'
		verbose_name_plural = 'Subcategories'

	def __unicode__(self):
		return unicode(self.subcategory)

	def get_absolute_url(self):
		return reverse('search_teams_in_cat', kwargs={'category_id':self.category.id, 'subcategory':self.id})


class TeamProfile(models.Model):
	name = models.CharField(max_length=256)
	image = models.ImageField(upload_to=team_img_destination, default="default_images/default_team_img.jpg")
	category = models.ForeignKey(SubCategory)
	description = models.TextField(max_length=1000)
	country = models.CharField(max_length=60, blank=True)
	city = models.CharField(max_length=60, blank=True)
	address = models.CharField(max_length=200, blank=True)
	date_founded = models.DateTimeField(auto_now_add=True)

	Y = 'Y'
	N = 'N'
	RECRUITING_CHOICES = (
		(Y, 'Yes'),
		(N, 'No'),
	)
	recruiting = models.CharField(max_length=1, choices=RECRUITING_CHOICES, default=Y)
	
	def __unicode__(self):
		return unicode(self.name)

	class Meta:
		ordering = ['-date_founded']

	def get_absolute_url(self):
		return reverse('team_overview', kwargs={'team_id':self.id})


class Membership(models.Model):
	user = models.ForeignKey(User)
	team = models.ForeignKey(TeamProfile)
	joined_team = models.DateTimeField(auto_now_add=True)

	LDR = 'LDR'
	MOD = 'MOD'
	USR = 'USR'
	USER_TYPE_CHOICES = (
		(LDR, 'Leader'),
		(MOD, 'Moderator'),
		(USR, 'User'),
	)
	user_type = models.CharField(max_length=3, choices=USER_TYPE_CHOICES, default=USR)

	class Meta:
		ordering = ['user_type', '-joined_team']


A = 'A'
I = 'I'
INVITATION_CHOICES = (
	(A, 'Accepted'),
	(I, 'In progress')
)

class Invitation(models.Model):
	user = models.ForeignKey(User)
	team = models.ForeignKey(TeamProfile)
	date_sent = models.DateTimeField(auto_now_add=True)
	accepted = models.CharField(max_length=1, choices=INVITATION_CHOICES, default=I)

	class Meta:
		ordering = ['-date_sent']


class Friendship(models.Model):
	user = models.ForeignKey(User, related_name='f_user')
	friend = models.ForeignKey(User, related_name='f_friend')
	date_sent = models.DateTimeField(auto_now_add=True)
	accepted = models.CharField(max_length=1, choices=INVITATION_CHOICES, default=I)

	class Meta:
		ordering = ['-date_sent']


class Message(models.Model):
	sender = models.ForeignKey(User, related_name="m_sender")
	reciever = models.ForeignKey(User, related_name="m_reciever")
	title = models.CharField(max_length=256)
	content = models.TextField(max_length=1000)
	date_sent = models.DateTimeField(auto_now_add=True)

	Y='Y'
	N='N'
	READ_CHOICES=(
		(Y, 'Y'),
		(N, 'N'),
	)
	read = models.CharField(max_length=1, choices=READ_CHOICES, default=N)

	class Meta:
		ordering = ['-date_sent']

	def get_absolute_url(self):
		return reverse('message_read', kwargs={'message_id':self.id})

	def read_message(self):
		self.read = 'Y'
		self.save()


class Tasks(models.Model):
	creator = models.ForeignKey(User)
	team = models.ForeignKey(TeamProfile)
	task = models.CharField(max_length=100)
	description = models.TextField(max_length=1000)
	date_created = models.DateTimeField(auto_now_add=True)
	deadline = models.DateTimeField(blank=True, null=True)
	date_finished = models.DateTimeField(blank=True, null=True)

	H = 'H'
	N = 'N'
	L = 'L'
	PRIORITY_CHOICES = (
		(H, 'High'),
		(N, 'Normal'),
		(L, 'Low'),
	)
	priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default=N)

	class Meta:
		ordering = ['date_finished', '-date_created']

	def get_absolute_url(self):
		return reverse('team_subtasks', kwargs={'team_id':self.team.id, 'task_id':self.id})

	def finish_task(self):
		self.date_finished = datetime.now()
		self.save()


class SubTasks(models.Model):
	task = models.ForeignKey(Tasks)
	subtask = models.CharField(max_length=100)
	description = models.TextField(max_length=1000)
	date_created = models.DateTimeField(auto_now_add=True)
	deadline = models.DateTimeField(blank=True, null=True)
	date_finished = models.DateTimeField(blank=True, null=True)

	class Meta:
		ordering = ['date_finished', 'date_created']

	def subtask_list(self):
		if self.date_finished is None:
			return u"%s\n(%s - In progress)\n%s" % (self.subtask, self.date_created, self.description)
		else:
			finished = self.date_finished.strftime("%D %T")
			return u"%s\n(%s - %s)\n%s" % (self.subtask, self.date_created, self.finished, self.description)

	def finish_subtask(self):
		self.date_finished = datetime.now()
		self.save()


class Forum(models.Model):
	team = models.ForeignKey(TeamProfile)
	title = models.CharField(max_length=100)

	def __unicode__(self):
		return self.title

	def num_posts(self):
		return sum([t.num_posts() for t in self.threads.all()])

	def last_post(self):
		threads = self.threads.all()
		last = none
		for thread in threads:
			lastp = thread.last_post
			if lastp and (not last or lastp.date_created > last.date_created):
				last = lastp
		return last

	def get_absolute_url(self):
		return reverse('team_forum_threads', kwargs={'team_id':self.team.id, 'forum_id':self.id})


class Thread(models.Model):
	forum = models.ForeignKey(Forum, related_name='threads')
	creator = models.ForeignKey(User)
	title = models.CharField(max_length=100)
	date_created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-date_created']

	def __unicode__(self):
		return unicode("%s - %s" % (self.creator, self.title))

	def last_post(self): return first(self.posts.all())
	def num_posts(self): return self.posts.count()
	def num_replies(self): return self.posts.count() - 1

	def get_absolute_url(self):
		return reverse('team_forum_posts', kwargs={'team_id':self.forum.team.id, 'forum_id':self.forum.id, 'thread_id':self.id})


class Post(models.Model):
	thread = models.ForeignKey(Thread)
	creator = models.ForeignKey(User)
	date_created = models.DateTimeField(auto_now_add=True)
	title = models.CharField(max_length=60)
	content = models.TextField(max_length=1000)

	class Meta:
		ordering = ['date_created']

	def __unicode__(self):
		return unicode("%s - %s" % (self.creator, self.title))

	def last_post(self):
		return u"%s %s - %s\n%s" % (self.creator.first_name, self.creator.last_name, self.title, self.date_created)

	def profile_data(self):
		p = self.creator
		return p.userprofile.posts, p.userprofile.image

	def display_post(self):
		return u"%s %s - %s (%s)\n%s" % (self.creator.first_name, self.creator.last_name, self.title, self.date_created, self.content)

ONE = 1
TWO = 2
THREE = 3
FOUR = 4
FIVE = 5
SIX = 6
SEVEN = 7
EIGHT = 8
NINE = 9
TEN = 10
RATING_CHOICES = (
	(ONE, '1'),
	(TWO, '2'),
	(THREE, '3'),
	(FOUR, '4'),
	(FIVE, '5'),
	(SIX, '6'),
	(SEVEN, '7'),
	(EIGHT, '8'),
	(NINE, '9'),
	(TEN, '10'),
)

class UserReview(models.Model):
	user = models.ForeignKey(User, related_name='user_reviewed')
	reviewed_by = models.ForeignKey(User, related_name='reviewer')
	rating = models.IntegerField(choices=RATING_CHOICES, default=ONE)
	content = models.TextField(max_length=1000)
	date_created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['date_created']


class TeamReview(models.Model):
	team = models.ForeignKey(TeamProfile)
	reviewed_by = models.ForeignKey(User)
	rating = models.IntegerField(choices=RATING_CHOICES, default=ONE)
	content = models.TextField(max_length=1000)
	date_created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['date_created']


class UserStatus(models.Model):
	user = models.ForeignKey(User)
	content = models.TextField(max_length = 500)
	date_created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-date_created']


class TeamStatus(models.Model):
	team = models.ForeignKey(TeamProfile)
	content = models.TextField(max_length = 500)
	date_created = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-date_created']