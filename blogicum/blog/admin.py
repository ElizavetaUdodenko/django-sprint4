from django.contrib import admin

from .models import Category, Location, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at'
    )
    list_editable = (
        'author',
        'location',
        'category',
        'is_published',
    )
    list_display_links = (
        'title',
        'text',
    )
    search_fields = (
        'title',
        'author',
        'location',
        'category',
    )
    list_filter = (
        'location',
        'category',
    )
    empty_value_display = 'Не задано'


class PostInLine(admin.TabularInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInLine,
    )
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'created_at'
    )
    list_editable = (
        'slug',
        'is_published',
    )
    list_display_links = (
        'title',
        'description',
    )
    search_fields = (
        'title',
        'slug',
    )
    list_filter = (
        'title',
    )
    empty_value_display = 'Не задано'


class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostInLine,
    )
    list_display = (
        'name',
        'is_published',
        'created_at'
    )
    list_display_links = (
        'name',
    )
    search_fields = (
        'name',
    )
    empty_value_display = 'Не задано'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
