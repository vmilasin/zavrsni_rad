from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from . import forms
from . import models
import os
from django.conf import settings
from django.db.models import Q


def index(request):
	if request.method=='POST':
		login_form = forms.LoginForm(request.POST)
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				auth_login(request, user)
				return HttpResponseRedirect(reverse('user_overview', args=(user.id,)))
			else:
				return HttpResponseRedirect('/teambuilder/account_disabled/')
		else:
			return HttpResponseRedirect('/teambuilder/')
	else:
		login_form = forms.LoginForm()
	
	registration_form = forms.UserRegistrationForm()

	return render(request, 'index.html', {'login_form':login_form, 'registration_form':registration_form})


def registration(request):
	if request.method=='POST':
		registration_form = forms.UserRegistrationForm(request.POST)
		if registration_form.is_valid():
			try:
				user = User.objects.get(username=request.POST['username'])
				return HttpResponseRedirect('/teambuilder/registration_in_use/')
			except User.DoesNotExist:
				new_user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['password'], first_name=request.POST['first_name'], last_name=request.POST['last_name'])
				new_userprofile = User.objects.get(username=request.POST['username'])
				new_user_userprofile = models.UserProfile.objects.create(user=new_userprofile)
				os.mkdir(os.path.join(settings.BASE_DIR, 'lfg_app', 'static', 'images', 'user_images', request.POST['username']))
				return HttpResponseRedirect('/teambuilder/registration_success/')
	else:
		registration_form = forms.UserRegistrationForm()

	return render(request, 'registration.html', {'registration_form':registration_form})


def logout(request):
	auth_logout(request)
	return HttpResponseRedirect('/teambuilder/')

def login(request):
	login_form = forms.LoginForm()
	return render(request, 'login.html', {'login_form':login_form})

def registration_success(request):
	return render(request, 'registration_success.html',)

def registration_in_use(request):
	return render(request, 'registration_in_use.html')

def account_disabled(request):
	return render(request, 'account_disabled.html',)


@login_required
def start(request):
	logged_in_user = User.objects.get(id=request.user.id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	return render(request, 'start.html', {'logged_in_user':logged_in_user, 'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count})


@login_required
def user_management(request):
	logged_in_user = User.objects.get(id=request.user.id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	user = logged_in_user
	user_profile = models.UserProfile.objects.get(user=user)

	if request.method == 'POST':
		user_management_form = forms.UserManagementForm(request.POST, request.FILES)
		if user_management_form.is_valid():
			user.first_name = request.POST['first_name']
			user.last_name = request.POST['last_name']
			user.email = request.POST['email']
			user_profile.birthday = user_management_form.cleaned_data.get('birthday')
			user_profile.country = request.POST['country']
			user_profile.city = request.POST['city']
			user_profile.address = request.POST['address']
			user_profile.image = request.FILES.get('image', 'default_images/default_user_img.png')
			user_profile.about_me = request.POST['about_me']
			user.save()
			user_profile.save()
			return HttpResponseRedirect(reverse('user_about_me', args=(logged_in_user.id,)))
	else:
		user_management_form = forms.UserManagementForm(initial={'email':user.email, 'first_name':user.first_name, 'last_name':user.last_name, 'birthday':user.userprofile.birthday, 'country':user.userprofile.country, 'city':user.userprofile.city, 'address':user.userprofile.address, 'image':user.userprofile.image, 'about_me':user.userprofile.about_me})
	
	return render(request, 'user_management.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'user_management_form':user_management_form})


@login_required
def user_about_me(request, user_id):
	requested_user = User.objects.get(id=user_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	return render(request, 'user_about_me.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'requested_user':requested_user})


@login_required
def user_overview(request, user_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_user = User.objects.get(id=user_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	user_status_list = models.UserStatus.objects.filter(user=requested_user)

	try:	
		friendship_request_sent = models.Friendship.objects.get(Q(user=requested_user, friend=logged_in_user) | Q(user=logged_in_user, friend=requested_user))
	except models.Friendship.DoesNotExist:
		friendship_request_sent = None

	if 'friendship_request' in request.GET:
		friendship_request = models.Friendship.objects.create(user=requested_user, friend=logged_in_user)
		friendship_request.save()
		return HttpResponseRedirect(reverse('user_overview', args=(requested_user.id,)))
	else:
		friendship_request = False

	if request.method == 'POST':
		user_status_form = forms.UserStatusForm(request.POST)
		if user_status_form.is_valid():
			status = models.UserStatus.objects.create(user=logged_in_user, content=request.POST['content'])
			status.save()
		return HttpResponseRedirect(reverse('user_overview', args=(logged_in_user.id,)))
	else:
		user_status_form = forms.UserStatusForm()

	paginator = Paginator(user_status_list, 5)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)
		
	return render(request, 'user_overview.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'user_status_form':user_status_form, 'user_status_list':user_status_list, 'pages':pages, 'friendship_request_sent':friendship_request_sent, 'logged_in_user':logged_in_user, 'requested_user':requested_user, 'user_id':user_id})


@login_required
def del_user_status(request, status_id):
	logged_in_user = User.objects.get(id=request.user.id)
	status = models.UserStatus.objects.get(id=status_id)
	status.delete()
	return HttpResponseRedirect(reverse('user_overview', args=(logged_in_user.id,)))


@login_required
def user_friends(request, user_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_user = User.objects.get(id=user_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	friends_list = models.Friendship.objects.filter(Q(user=requested_user, accepted='Y') | Q(friend=requested_user, accepted='Y'))

	paginator = Paginator(friends_list, 10)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'user_friends.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'friends_list':friends_list, 'pages':pages, 'logged_in_user':logged_in_user, 'requested_user':requested_user, 'user_id':user_id})


@login_required
def user_requests(request):
	logged_in_user = User.objects.get(id=request.user.id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	user_requests_list = models.Friendship.objects.filter(user=logged_in_user, accepted='I')

	paginator = Paginator(user_requests_list, 10)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'user_requests.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'user_requests_list':user_requests_list, 'pages':pages, 'logged_in_user':logged_in_user})


@login_required
def friendship_processing(request, request_id, accepted):
	logged_in_user = User.objects.get(id=request.user.id)
	invitation = models.Friendship.objects.get(id=request_id)

	if accepted == '1':
		invitation.accepted = 'Y'
		invitation.save()
		return HttpResponseRedirect(reverse('user_requests'))
	if accepted == '0':
		invitation.delete()
		return HttpResponseRedirect(reverse('user_requests'))


@login_required
def unfriend(request, request_id):
	logged_in_user = User.objects.get(id=request.user.id)
	friend = models.Friendship.objects.get(id=request_id)
	friend.delete()
	return HttpResponseRedirect(reverse('user_friends', args=(logged_in_user.id,)))


@login_required
def user_teams(request, user_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_user = User.objects.get(id=user_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	teams_list = models.Membership.objects.filter(user=requested_user)

	paginator = Paginator(teams_list, 10)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'user_teams.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'teams_list':teams_list, 'pages':pages, 'logged_in_user':logged_in_user, 'requested_user':requested_user, 'user_id':user_id})


@login_required
def user_invitations(request):
	logged_in_user = User.objects.get(id=request.user.id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	user_invitations_list = models.Invitation.objects.filter(user=logged_in_user, accepted='I')

	paginator = Paginator(user_invitations_list, 20)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'user_invitations.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'user_invitations_list':user_invitations_list, 'pages':pages, 'logged_in_user':logged_in_user})


@login_required
def invitation_processing(request, request_id, accepted):
	logged_in_user = User.objects.get(id=request.user.id)
	invitation = models.Invitation.objects.get(id=request_id)

	if accepted == '1':
		invitation.accepted = 'Y'
		invitation.save()
		invitation_team = models.Membership.objects.create(user=logged_in_user, team=invitation.team)
		invitation_team.save()
		return HttpResponseRedirect(reverse('user_invitations'))
	if accepted == '0':
		invitation.delete()
		return HttpResponseRedirect(reverse('user_invitations'))


@login_required
def leave_team(request, membership_id):
	logged_in_user = User.objects.get(id=request.user.id)
	membership = models.Membership.objects.get(id=membership_id)
	membership.delete()
	return HttpResponseRedirect(reverse('user_teams', args=(logged_in_user.id,)))


@login_required
def user_reviews(request, user_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_user = User.objects.get(id=user_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	user_reviews_list = models.UserReview.objects.filter(user=requested_user)

	paginator = Paginator(user_reviews_list, 3)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'user_reviews.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'user_reviews_list':user_reviews_list, 'pages':pages, 'logged_in_user':logged_in_user, 'requested_user':requested_user})


@login_required
def review_user(request, user_reviewed):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_user_reviewed = User.objects.get(id=user_reviewed)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	if request.method == 'POST':
		review_user_form = forms.UserReviewForm(request.POST)
		if review_user_form.is_valid():
			review = models.UserReview.objects.create(user=requested_user_reviewed, reviewed_by=logged_in_user, rating=request.POST['rating'], content=request.POST['content'])
			review.save()
			return HttpResponseRedirect(reverse('user_reviews', args=(requested_user_reviewed.id,)))
	else:
		review_user_form = forms.UserReviewForm()

	return render(request, 'review_user.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'review_user_form':review_user_form, 'logged_in_user':logged_in_user, 'requested_user_reviewed':requested_user_reviewed})


@login_required
def review_team(request, team_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	if request.method == 'POST':
		review_team_form = forms.TeamReviewForm(request.POST)
		if review_team_form.is_valid():
			review = models.TeamReview.objects.create(team=requested_team, reviewed_by=logged_in_user, rating=request.POST['rating'], content=request.POST['content'])
			review.save()
			return HttpResponseRedirect(reverse('team_reviews', args=(requested_team.id,)))
	else:
		review_team_form = forms.TeamReviewForm()

	return render(request, 'review_team.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'review_team_form':review_team_form, 'logged_in_user':logged_in_user, 'requested_team':requested_team})


@login_required
def user_inbox(request):
	logged_in_user = User.objects.get(id=request.user.id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	user_inbox_list = models.Message.objects.filter(reciever=logged_in_user)

	paginator = Paginator(user_inbox_list, 10)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'user_inbox.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'user_inbox_list':user_inbox_list, 'pages':pages, 'logged_in_user':logged_in_user})


@login_required
def user_outbox(request):
	logged_in_user = User.objects.get(id=request.user.id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	user_outbox_list = models.Message.objects.filter(sender=logged_in_user)

	paginator = Paginator(user_outbox_list, 10)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'user_outbox.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'user_outbox_list':user_outbox_list, 'pages':pages, 'logged_in_user':logged_in_user})


@login_required
def message_compose(request, reciever_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_reciever = User.objects.get(id=reciever_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	if request.method == 'POST':
		message_compose_form = forms.MessageForm(request.POST)
		if message_compose_form.is_valid():
			message = models.Message.objects.create(sender=logged_in_user, reciever=requested_reciever, title=request.POST['title'], content=request.POST['content'])
			message.save()
			return HttpResponseRedirect(reverse('user_outbox'))
	else:
		message_compose_form = forms.MessageForm()

	return render(request, 'message_compose.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'message_compose_form':message_compose_form, 'logged_in_user':logged_in_user, 'requested_reciever':requested_reciever})


@login_required
def message_read(request, message_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_message = models.Message.objects.get(id=message_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	if requested_message.read == 'N':
		requested_message.read = 'Y'
		requested_message.save()

	return render(request, 'message_read.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'requested_message':requested_message})


@login_required
def search_category(request):
	logged_in_user = User.objects.get(id=request.user.id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	if request.method == 'POST':
		search_category_form = forms.CategorySearchForm(request.POST)
		if search_category_form.is_valid():
			category_list = models.Category.objects.filter(category__icontains=request.POST['category'])
	else:
		search_category_form = forms.CategorySearchForm()
		category_list = models.Category.objects.all()
		pages = None

	paginator = Paginator(category_list, 20)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'search_category.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'search_category_form':search_category_form, 'category_list':category_list, 'pages':pages, 'logged_in_user':logged_in_user})
	

@login_required
def search_subcategory(request, category_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_category = models.Category.objects.get(id=category_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	if request.method == 'POST':
		search_subcategory_form = forms.SubCategorySearchForm(request.POST)
		if search_subcategory_form.is_valid():
			subcategory_list = models.SubCategory.objects.filter(subcategory__icontains=request.POST['subcategory'])
	else:
		search_subcategory_form = forms.SubCategorySearchForm()
		subcategory_list = models.SubCategory.objects.filter(category=requested_category)
		pages = None

	paginator = Paginator(subcategory_list, 20)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'search_subcategory.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'search_subcategory_form':search_subcategory_form, 'subcategory_list':subcategory_list, 'pages':pages, 'logged_in_user':logged_in_user, 'requested_category':requested_category})


@login_required
def search_teams_in_cat(request, category_id, subcategory):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_category = models.Category.objects.get(id=category_id)
	requested_subcategory = models.SubCategory.objects.get(id=subcategory)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	if request.method == 'POST':
		search_teams_form = forms.TeamSearchForm(request.POST)
		if search_teams_form.is_valid():
			teams_list = models.TeamProfile.objects.filter(name__icontains=request.POST['team'])
	else:
		search_teams_form = forms.TeamSearchForm()	
		teams_list = models.TeamProfile.objects.filter(category=requested_subcategory)
		pages = None

	paginator = Paginator(teams_list, 5)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'search_teams_in_cat.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'search_teams_form':search_teams_form, 'teams_list':teams_list, 'pages':pages, 'logged_in_user':logged_in_user, 'requested_category':requested_category, 'requested_subcategory':requested_subcategory})


@login_required
def search_teams(request):
	logged_in_user = User.objects.get(id=request.user.id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	if request.method == 'POST':
		team_search_form = forms.TeamSearchForm(request.POST)
		if team_search_form.is_valid():
			teams_list = models.TeamProfile.objects.filter(name__icontains=request.POST['team'])

		paginator = Paginator(teams_list, 5)
		page = request.GET.get('page')
		try:
			pages = paginator.page(page)
		except PageNotAnInteger:
			pages = paginator.page(1)
		except EmptyPage:
			pages = paginator.page(paginator.num_pages)

	else:
		team_search_form = forms.TeamSearchForm()
		teams_list = None
		pages = None

	return render(request, 'search_teams.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'teams_list':teams_list, 'team_search_form':team_search_form, 'pages':pages, 'logged_in_user':logged_in_user})


@login_required
def search_users(request):
	logged_in_user = User.objects.get(id=request.user.id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	if request.method == 'POST':
		user_search_form = forms.UserSearchForm(request.POST)
		if user_search_form.is_valid():
			users_list = User.objects.filter(Q(username__icontains=request.POST['username']) | Q(first_name__icontains=request.POST['username']) | Q(last_name__icontains=request.POST['username']))

		paginator = Paginator(users_list, 10)
		page = request.GET.get('page')
		try:
			pages = paginator.page(page)
		except PageNotAnInteger:
			pages = paginator.page(1)
		except EmptyPage:
			pages = paginator.page(paginator.num_pages)
	
	else:
		user_search_form = forms.UserSearchForm()
		users_list = None
		pages = None

	return render(request, 'search_users.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'users_list':users_list, 'user_search_form':user_search_form, 'pages':pages, 'logged_in_user':logged_in_user})


@login_required
def team_creation(request):
	logged_in_user = User.objects.get(id=request.user.id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	if request.method == 'POST':
		team_creation_form = forms.TeamCreationForm(request.POST)
		if team_creation_form.is_valid():
			selected_category = models.SubCategory.objects.get(id=request.POST['category'])
			team = models.TeamProfile.objects.create(name=request.POST['name'], category=selected_category, description=request.POST['description'])
			team.save()
			new_team = models.TeamProfile.objects.get(name=request.POST['name'])
			leader = models.Membership.objects.create(user=logged_in_user, team=new_team, user_type='LDR')
			leader.save()
			os.mkdir(os.path.join(settings.BASE_DIR, 'lfg_app', 'static', 'images', 'team_images', request.POST['name']))
			new_team = models.TeamProfile.objects.get(name=request.POST['name'])
			return HttpResponseRedirect(reverse('team_creation_success', args=(new_team.id,)))
	else:
		team_creation_form = forms.TeamCreationForm()

	return render(request, 'team_creation.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'team_creation_form':team_creation_form, 'logged_in_user':logged_in_user})


@login_required
def team_creation_success(request, team_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	return render(request, 'team_creation_success.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'logged_in_user':logged_in_user, 'requested_team':requested_team})


@login_required
def team_management(request, team_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	if request.method == 'POST':
		team_management_form = forms.TeamManagementForm(request.POST, request.FILES)
		if team_management_form.is_valid():
			requested_team.name = request.POST['name']
			requested_team.recruiting = request.POST['recruiting']
			requested_team.country = request.POST['country']
			requested_team.city = request.POST['city']
			requested_team.address = request.POST['address']
			requested_team.image = request.FILES.get('image', 'default_images/default_team_img.jpg')
			requested_team.description = request.POST['description']
			requested_team.save()
			return HttpResponseRedirect(reverse('team_management', args=(requested_team.id,)))
	else:
		team_management_form = forms.TeamManagementForm(initial={'name':requested_team.name, 'category':requested_team.category, 'recruiting':requested_team.recruiting, 'country':requested_team.country, 'city':requested_team.city, 'address':requested_team.address, 'image':requested_team.image, 'description':requested_team.description})

	return render(request, 'team_management.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'team_management_form':team_management_form, 'requested_team':requested_team, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user})


@login_required
def team_about_us(request, team_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	return render(request, 'team_about_us.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'leader':leader, 'mods':mods, 'users':users, 'requested_team':requested_team, 'logged_in_user':logged_in_user})


@login_required
def team_overview(request, team_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	team_status_list = models.TeamStatus.objects.filter(team=requested_team)

	if request.method == 'POST':
		team_status_form = forms.TeamStatusForm(request.POST)
		if team_status_form.is_valid():
			status = models.TeamStatus.objects.create(team=requested_team, content=request.POST['content'])
			status.save()
			HttpResponseRedirect(reverse('team_overview', args=(requested_team.id,)))
	else:
		team_status_form = forms.TeamStatusForm()

	paginator = Paginator(team_status_list, 10)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'team_overview.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'leader':leader, 'mods':mods, 'users':users, 'team_status_form':team_status_form, 'team_status_list':team_status_list, 'pages':pages, 'logged_in_user':logged_in_user, 'requested_team':requested_team})


@login_required
def del_team_status(request, team_id, status_id):
	requested_team = models.TeamProfile.objects.get(id=team_id)
	status = models.TeamStatus.objects.get(id=status_id)
	status.delete()
	return HttpResponseRedirect(reverse('team_overview', args=(requested_team.id,)))


@login_required
def team_members(request, team_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	members_list = models.Membership.objects.filter(team=requested_team)

	paginator = Paginator(members_list, 30)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'team_members.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'members_list':members_list, 'pages':pages, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user, 'requested_team':requested_team})


@login_required
def team_membership_management(request, team_id, member_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	requested_member = User.objects.get(id=member_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	requested_membership = models.Membership.objects.get(user=requested_member)

	if request.method == 'POST':
		team_membership_management_form = forms.MembershipManagementForm(request.POST)
		if team_membership_management_form.is_valid():
			requested_membership.user_type = request.POST['user_type']
			if request.POST['user_type'] == 'LDR':
				old_leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
				old_leader.user_type = 'MOD'
				old_leader.save()
			requested_membership.save()
			return HttpResponseRedirect(reverse('team_members', args=(requested_team.id,)))
	else:
		team_membership_management_form = forms.MembershipManagementForm()

	return render(request, 'team_membership_management.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'team_membership_management_form':team_membership_management_form, 'requested_team':requested_team, 'requested_member':requested_member, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user})


@login_required
def kick_member(request, team_id, member_id):
	requested_team = models.TeamProfile.objects.get(id=team_id)
	requested_member = models.Membership.objects.get(id=member_id)

	requested_member.delete()
	return HttpResponseRedirect(reverse('team_members', args=(requested_team.id,)))


@login_required
def team_invitation(request, team_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	invitation_requested = models.Invitation.objects.filter(team=requested_team)

	if request.method == 'POST':
		user_search_form = forms.UserSearchForm(request.POST)
		if user_search_form.is_valid():
			users_list = User.objects.filter(Q(username__icontains=request.POST['username']) | Q(first_name__icontains=request.POST['username']) | Q(last_name__icontains=request.POST['username']))

		paginator = Paginator(users_list, 10)
		page = request.GET.get('page')
		try:
			pages = paginator.page(page)
		except PageNotAnInteger:
			pages = paginator.page(1)
		except EmptyPage:
			pages = paginator.page(paginator.num_pages)

	else:
		user_search_form = forms.UserSearchForm()
		users_list = None
		pages = None

	return render(request, 'team_invitation.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'invitation_requested':invitation_requested, 'user_search_form':user_search_form, 'users_list':users_list, 'pages':pages, 'requested_team':requested_team, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user})


@login_required
def team_invitation_creation(rquest, team_id, user_id):
	requested_team = models.TeamProfile.objects.get(id=team_id)
	requested_member = User.objects.get(id=user_id)
	invitation = models.Invitation.objects.create(user=requested_member, team=requested_team)
	invitation.save()
	return HttpResponseRedirect(reverse('team_invitation', args=(requested_team.id,)))


@login_required
def team_tasks(request, team_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	team_tasks_list = models.Tasks.objects.filter(team=requested_team)

	paginator = Paginator(team_tasks_list, 3)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'team_tasks.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'team_tasks_list':team_tasks_list, 'pages':pages, 'requested_team':requested_team, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user})


@login_required
def team_tasks_creation(request, team_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	if request.method == 'POST':
		task_creation_form = forms.TaskForm(request.POST)
		if task_creation_form.is_valid():
			new_task = models.Tasks.objects.create(creator=logged_in_user, team=requested_team, task=request.POST['task'], description=request.POST['description'], priority=request.POST['priority'])
			new_task.save()
		return HttpResponseRedirect(reverse('team_tasks', args=(requested_team.id,)))
	else:
		task_creation_form = forms.TaskForm()

	return render(request, 'team_tasks_creation.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'task_creation_form':task_creation_form, 'requested_team':requested_team, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user})


@login_required
def task_finish(request, team_id, task_id):
	requested_team = models.TeamProfile.objects.get(id=team_id)
	requested_task = models.Tasks.objects.get(id=task_id)
	
	requested_task.finish_task()
	return HttpResponseRedirect(reverse('team_tasks', args=(requested_team.id,)))


@login_required
def team_subtasks(request, team_id, task_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	requested_task = models.Tasks.objects.get(id=task_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	team_subtasks_list = models.SubTasks.objects.filter(task=requested_task)

	paginator = Paginator(team_subtasks_list, 3)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'team_subtasks.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'team_subtasks_list':team_subtasks_list, 'pages':pages, 'requested_team':requested_team, 'requested_task':requested_task, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user})


@login_required
def team_subtasks_creation(request, team_id, task_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	requested_task = models.Tasks.objects.get(id=task_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	if request.method == 'POST':
		subtask_creation_form = forms.SubTaskForm(request.POST)
		if subtask_creation_form.is_valid():
			new_subtask = models.SubTasks.objects.create(task=requested_task, subtask=request.POST['subtask'], description=request.POST['description'])
			new_subtask.save()
		return HttpResponseRedirect(reverse('team_subtasks', args=(requested_team.id, requested_task.id,)))
	else:
		subtask_creation_form = forms.SubTaskForm()

	return render(request, 'team_subtasks_creation.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'subtask_creation_form':subtask_creation_form, 'requested_team':requested_team, 'requested_task':requested_task, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user})


@login_required
def subtask_finish(request, team_id, task_id, subtask_id):
	requested_team = models.TeamProfile.objects.get(id=team_id)
	requested_task = models.Tasks.objects.get(id=task_id)
	requested_subtask = models.SubTasks.objects.get(id=subtask_id)
	
	requested_subtask.finish_subtask()
	return HttpResponseRedirect(reverse('team_subtasks', args=(requested_team.id, requested_task.id,)))	


@login_required
def team_reviews(request, team_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	team_reviews_list = models.TeamReview.objects.filter(team=requested_team)

	paginator = Paginator(team_reviews_list, 5)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'team_reviews.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'team_reviews_list':team_reviews_list, 'pages':pages, 'requested_team':requested_team, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user})


@login_required
def team_forum(request, team_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)
	
	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	forum_list = models.Forum.objects.filter(team=requested_team)

	return render(request, 'team_forum.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'forum_list':forum_list, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user, 'requested_team':requested_team})


@login_required
def team_forum_creation(request, team_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	if request.method == 'POST':
		forum_creation_form = forms.ForumForm(request.POST)
		if forum_creation_form.is_valid():
			new_forum = models.Forum.objects.create(team=requested_team, title=request.POST['title'])
			new_forum.save()
			return HttpResponseRedirect(reverse('team_forum', args=(requested_team.id,)))
	else:
		forum_creation_form = forms.ForumForm()

	return render(request, 'team_forum_creation.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'forum_creation_form':forum_creation_form, 'requested_team':requested_team, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user})


@login_required
def team_forum_threads(request, team_id, forum_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	requested_forum = models.Forum.objects.get(id=forum_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	threads_list = models.Thread.objects.filter(forum=requested_forum)

	paginator = Paginator(threads_list, 20)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'team_forum_threads.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'threads_list':threads_list, 'pages':pages, 'requested_team':requested_team, 'requested_forum':requested_forum, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user})


@login_required
def team_forum_threads_creation(request, team_id, forum_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	requested_forum = models.Forum.objects.get(id=forum_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	if request.method == 'POST':
		thread_creation_form = forms.ThreadForm(request.POST)
		if thread_creation_form.is_valid():
			new_thread = models.Thread.objects.create(forum=requested_forum, creator=logged_in_user, title=request.POST['title'])
			new_thread.save()
			return HttpResponseRedirect(reverse('team_forum_threads', args=(requested_team.id, requested_forum.id,)))
	else:
		thread_creation_form = forms.ThreadForm()

	return render(request, 'team_forum_threads_creation.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'thread_creation_form':thread_creation_form, 'requested_team':requested_team, 'requested_forum':requested_forum, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user})


@login_required
def team_forum_posts(request, team_id, forum_id, thread_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	requested_forum = models.Forum.objects.get(id=forum_id)
	requested_thread = models.Thread.objects.get(id=thread_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	posts_list = models.Post.objects.filter(thread=requested_thread)

	paginator = Paginator(posts_list, 20)
	page = request.GET.get('page')
	try:
		pages = paginator.page(page)
	except PageNotAnInteger:
		pages = paginator.page(1)
	except EmptyPage:
		pages = paginator.page(paginator.num_pages)

	return render(request, 'team_forum_posts.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'posts_list':posts_list, 'pages':pages, 'requested_team':requested_team, 'requested_forum':requested_forum, 'requested_thread':requested_thread, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user})


@login_required
def team_forum_posts_creation(request, team_id, forum_id, thread_id):
	logged_in_user = User.objects.get(id=request.user.id)
	requested_team = models.TeamProfile.objects.get(id=team_id)
	requested_forum = models.Forum.objects.get(id=forum_id)
	requested_thread = models.Thread.objects.get(id=thread_id)
	new_messages = models.Message.objects.filter(reciever=request.user, read='N')
	new_messages_count = len(new_messages)
	new_requests = models.Friendship.objects.filter(user=request.user, accepted='I')
	new_requests_count = len(new_requests)
	new_invitations = models.Invitation.objects.filter(user=request.user, accepted='I')
	new_invitations_count = len(new_invitations)

	leader = models.Membership.objects.get(team=requested_team, user_type='LDR')
	try:
		mods = models.Membership.objects.get(team=requested_team, user_type='MOD', user=logged_in_user)
	except models.Membership.DoesNotExist:
		mods = None
	try:
		users = models.Membership.objects.get(team=requested_team, user_type='USR', user=logged_in_user)
	except models.Membership.DoesNotExist:
		users = None

	if request.method == 'POST':
		post_creation_form = forms.PostForm(request.POST)
		if post_creation_form.is_valid():
			new_post = models.Post.objects.create(thread=requested_thread, creator=logged_in_user, title=request.POST['title'], content=request.POST['content'])
			new_post.save()
			logged_in_user.userprofile.increment_posts()
			return HttpResponseRedirect(reverse('team_forum_posts', args=(requested_team.id, requested_forum.id, requested_thread.id,)))
	else:
		post_creation_form = forms.PostForm()

	return render(request, 'team_forum_posts_creation.html', {'new_messages_count':new_messages_count, 'new_requests_count':new_requests_count, 'new_invitations_count':new_invitations_count, 'post_creation_form':post_creation_form, 'requested_team':requested_team, 'requested_forum':requested_forum, 'requested_thread':requested_thread, 'leader':leader, 'mods':mods, 'users':users, 'logged_in_user':logged_in_user})