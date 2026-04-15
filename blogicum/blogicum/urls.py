"""blogicum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from blog import views
from django.conf import settings
from django.conf.urls import handler403, handler404, handler500
from django.contrib import admin
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.urls import include, path, re_path
from django.views.static import serve


def logout_view(request):
    logout(request)
    return redirect("blog:index")


urlpatterns = [
    path("auth/registration/", views.registration, name="registration"),
    path("auth/logout/", logout_view, name="logout"),
    path("auth/", include("django.contrib.auth.urls")),
    path("", include("blog.urls")),
    path("pages/", include("pages.urls")),
    path("admin/", admin.site.urls),
]


def csrf_failure(request, reason=""):
    return render(request, "pages/403csrf.html", status=403)


def page_not_found(request, exception):
    return render(request, "pages/404.html", status=404)


def server_error(request):
    return render(request, "pages/500.html", status=500)


handler403 = "blogicum.urls.csrf_failure"
handler404 = "blogicum.urls.page_not_found"
handler500 = "blogicum.urls.server_error"

urlpatterns += [
    re_path(r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$",
            serve,
            {"document_root": settings.STATIC_URL}),
]
