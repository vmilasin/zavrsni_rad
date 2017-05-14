from django import forms
from . import models
from django.contrib.auth.models import User
from django.forms import extras


class UserSearchForm(forms.Form):
	username = forms.CharField()

class TeamSearchForm(forms.Form):
	team = forms.CharField()

class CategorySearchForm(forms.Form):
	category = forms.CharField()

class SubCategorySearchForm(forms.Form):
	subcategory = forms.CharField()


class LoginForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['username', 'password']
		help_texts = {
			'username':'',
			'password':''
		}
		labels = {
			'username':'',
			'password':''
		}
		widgets = {
			'username': forms.TextInput(attrs = {'placeholder': 'Username'}),
			'password': forms.PasswordInput(attrs = {'placeholder': 'Password'}),
		}

class UserRegistrationForm(forms.ModelForm):	
	class Meta:
		model = User
		fields = ['username', 'password', 'email', 'first_name', 'last_name']
		help_texts = {
			'username':'',
			'password':'',
			'email':'',
			'first_name':'',
			'last_name':''
		}


class UserManagementForm(forms.Form):
	first_name = forms.CharField(required=False, max_length=256)
	last_name = forms.CharField(required=False, max_length=256)
	birthday = forms.DateField(required=False, widget=extras.SelectDateWidget(years=range(1930,2015)))
	email = forms.EmailField(required=False)
	country = forms.CharField(required=False, max_length=100)
	city = forms.CharField(required=False, max_length=100)
	address = forms.CharField(required=False, max_length=200)
	image = forms.ImageField(required=False)
	about_me = forms.CharField(required=False, widget=forms.Textarea)


class NewCategoryForm(forms.ModelForm):
	class Meta:
		model = models.Category
		fields = ['category']

class NewSubcategoryForm(forms.ModelForm):
	class Meta:
		model = models.SubCategory
		fields = ['subcategory']


class TeamCreationForm(forms.ModelForm):
	class Meta:
		model = models.TeamProfile
		fields = ['name', 'category', 'description']

class TeamManagementForm(forms.ModelForm):
	class Meta:
		model = models.TeamProfile
		fields = ['name', 'recruiting', 'country', 'city', 'address', 'image', 'description']

class MembershipManagementForm(forms.ModelForm):
	class Meta:
		model = models.Membership
		fields = ['user_type']


class TaskForm(forms.ModelForm):
	class Meta:
		model = models.Tasks
		fields = ['task', 'description', 'priority']

class SubTaskForm(forms.ModelForm):
	class Meta:
		model = models.SubTasks
		fields = ['subtask', 'description']		


class ForumForm(forms.ModelForm):
	class Meta:
		model = models.Forum
		fields = ['title']

class ThreadForm(forms.ModelForm):
	class Meta:
		model = models.Thread
		fields = ['title']

class PostForm(forms.ModelForm):
	class Meta:
		model = models.Post
		fields = ['title', 'content']


class MessageForm(forms.ModelForm):
	class Meta:
		model = models.Message
		fields = ['title', 'content']


class UserReviewForm(forms.ModelForm):
	class Meta:
		model = models.UserReview
		fields = ['rating', 'content']

class TeamReviewForm(forms.ModelForm):
	class Meta:
		model= models.TeamReview
		fields = ['rating', 'content']


class UserStatusForm(forms.ModelForm):
	class Meta:
		model = models.UserStatus
		fields = ['content']
		labels = {
			'content' : 'Post a new status:'
		}

class TeamStatusForm(forms.ModelForm):
	class Meta:
		model = models.TeamStatus
		fields = ['content']
		labels = {
			'content' : 'Post a new status:'
		}