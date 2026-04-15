from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published")
    list_editable = ("is_published",)
    search_fields = ("title",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published")
    list_editable = ("is_published",)
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "pub_date", "is_published", "image")
    list_editable = ("is_published",)
    list_filter = ("category", "is_published")
    search_fields = ("title", "text")
