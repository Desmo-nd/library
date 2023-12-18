from django.contrib import admin
from .models import AddBook, IssueBook, ReturnBook, AddStudent, Rating, Category

# Register your models here.
from django.contrib.sessions.models import Session

admin.site.register(Session)
from .models import UserExtend

admin.site.register(UserExtend)


class AddBook_Admin(admin.ModelAdmin):
    list_display = ("user", "bookid", "bookname", "author", "subject", "location", "copies", "cover", "publisher",
                    "edition", "libNo", "language", "pages", "Cat")


admin.site.register(AddBook, AddBook_Admin)


class IssueBookAdmin(admin.ModelAdmin):
    list_display = ("user", "book1", "studentid")


admin.site.register(IssueBook, IssueBookAdmin)


class ReturnBookAdmin(admin.ModelAdmin):
    list_display = ("user", "bookid2")


admin.site.register(ReturnBook, ReturnBookAdmin)


class AddStudentAdmin(admin.ModelAdmin):
    list_display = ("user", "username", "studentid")


admin.site.register(AddStudent, AddStudentAdmin)


class RatingAdmin(admin.ModelAdmin):
    list_display = ("user", "rate", "comment")


admin.site.register(Rating, RatingAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'cat_cover')


admin.site.register(Category, CategoryAdmin)
