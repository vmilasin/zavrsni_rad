from django.contrib import admin
from .models import Category, SubCategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	pass

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
	pass