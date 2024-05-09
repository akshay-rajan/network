from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import User, Post, Like



def index(request):
    """Display paginated posts and let the user create a new post"""

    if request.method == "POST":
        post = request.POST["post"]
        user = request.user
        newpost = Post(creator=user, text=post)
        newpost.save()

    # Fetch all current posts and posts liked by the user
    user = request.user
    posts = Post.objects.order_by('-timestamp')
    if user.is_authenticated:
        liked_posts = [post for post in posts if Like.objects.filter(post=post, user=user).exists()]
    else:
        liked_posts = []

    # Pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get('page', 1)
    current_posts = paginator.page(page)

    return render(request, "network/index.html", {
        "current_posts": current_posts,
        "liked_posts": liked_posts,
        "paginator": paginator,
        "user" : user
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile(request, username):
    """Display the profile of a user and let a user follow or unfollow others"""

    user = request.user
    this_user = User.objects.get(username=username)
    follow_status = user.following.filter(id=this_user.id).exists()
    if request.method == "POST":
        if follow_status:
            user.following.remove(this_user)
        else:
            user.following.add(this_user)
        follow_status = user.following.filter(id=this_user.id).exists()

    follower_count = this_user.followers.count()
    following_count = this_user.following.count()
    posts = Post.objects.filter(creator=this_user).order_by("-timestamp")
    if user.is_authenticated:
        liked_posts = [post for post in posts if Like.objects.filter(post=post, user=user).exists()]
    else:
        liked_posts = []
    return render(request, "network/profile.html", {
        "this_user":this_user,
        "followers": follower_count,
        "following": following_count,
        "follow_status": follow_status,
        "posts": posts,
        "liked_posts": liked_posts,
        "user": user
    })


def following(request):
    """Display paginated posts from people followed by the user"""

    user = request.user
    following = user.following.all()
    posts = Post.objects.filter(creator__in=following).order_by("-timestamp")
    if user.is_authenticated:
        liked_posts = [post for post in posts if Like.objects.filter(post=post, user=user).exists()]
    else:
        liked_posts = []
    paginator = Paginator(posts, 10)
    page = request.GET.get('page', 1)
    posts = paginator.page(page)

    return render(request, "network/following.html", {
        "posts": posts,
        "liked_posts": liked_posts,
        "paginator": paginator,
        "user" : user
    })


def edit(request, postID):
    if request.method == "PUT":
        post = Post.objects.get(id=postID)
        data = json.loads(request.body.decode('utf-8'))
        newText = data.get('text')
        post.text = newText
        post.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def like_status(request, postID):
    post = Post.objects.get(id=postID)
    user = request.user
    liked = Like.objects.filter(user=user, post=post).exists()
    return JsonResponse({'isLiked': liked})



def like(request, postID):
    if request.method == "PUT":
        user = request.user
        post = Post.objects.get(id=postID)

        liked = Like.objects.filter(user=user, post=post).exists()
        if liked:
            Like.objects.filter(user=user, post=post).delete()
            return JsonResponse({'success': True, 'message': 'Unliked'})
        else:
            Like.objects.create(user=user, post=post)
            return JsonResponse({'success': True, 'message': 'Liked'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

