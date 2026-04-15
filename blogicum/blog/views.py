from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.shortcuts import redirect

from .forms import CommentForm, PostForm, ProfileForm
from .models import Category, Comment, Post


def published_posts():
    return (
        Post.objects.select_related("category")
        .annotate(comment_count=Count("comments"))
        .filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True,
        )
    )


def add_comments_count(posts):
    return posts.annotate(comment_count=Count("comments"))


def index(request):
    post_list = add_comments_count(published_posts().order_by("-pub_date"))
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "blog/index.html", {"page_obj": page_obj})


def post_detail(request, id):
    post = get_object_or_404(Post, id=id)
    is_author = request.user == post.author

    is_published = (
        post.is_published
        and post.pub_date <= timezone.now()
        and post.category.is_published
    )

    if not is_published and not is_author:
        raise Http404("Пост не найден")

    comments = post.comments.all()
    form = CommentForm()

    return render(
        request,
        "blog/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
        },
    )


def category_posts(request, category_slug):
    category = get_object_or_404(Category,
                                 slug=category_slug,
                                 is_published=True)

    post_list = add_comments_count(
        published_posts()
        .filter(
            category=category,
        )
        .order_by("-pub_date")
    )

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/category.html",
        {
            "category": category,
            "page_obj": page_obj,
        },
    )


def registration(request):
    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("login")

    return render(
        request,
        "registration/registration_form.html",  # ИСПРАВЛЕНО: добавлено _form
        {"form": form},
    )


@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("blog:profile", username=user.username)
    else:
        form = ProfileForm(instance=user)

    return render(request, "blog/user.html", {"form": form})


@login_required
def create_post(request):
    form = PostForm(request.POST, request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        if post.pub_date is None:
            post.pub_date = timezone.now()
        post.save()

        return redirect("blog:profile", username=request.user.username)

    return render(request, "blog/create.html", {"form": form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect("blog:post_detail", id=post.id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)

    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", id=post.id)

    return render(
        request, "blog/create.html", {
            "form": form,
            "post": post,
            "is_edit": True
        }
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()

    return redirect("blog:post_detail", id=post.id)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect("blog:post_detail", id=post.id)

    if request.method == "POST":
        post.delete()
        return redirect("blog:profile", username=request.user.username)

    return render(
        request,
        "blog/create.html",
        {
            "form": PostForm(instance=post),
            "post": post,
        },
    )


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if request.user != comment.author:
        return redirect("blog:post_detail", id=post_id)

    form = CommentForm(request.POST or None, instance=comment)

    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", id=post_id)

    return render(request, "blog/create.html", {"form": form, "is_edit": True})


def profile(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username)

    if request.user == user:
        post_list = (
            Post.objects.filter(author=user)
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )
    else:
        post_list = published_posts().filter(author=user).order_by("-pub_date")

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog/profile.html",
        {
            "profile": user,
            "page_obj": page_obj,
        },
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if request.user != comment.author:
        return redirect("blog:post_detail", id=post_id)

    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", id=post_id)

    return render(
        request, "blog/comment.html", {"comment": comment, "post_id": post_id}
    )
