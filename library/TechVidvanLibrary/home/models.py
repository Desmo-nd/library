from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import CharField, TextField
from datetime import datetime, timedelta


class UserExtend(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.IntegerField()
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    def __str__(self):
        return self.user.username


class Category(models.Model):
    category_name = models.CharField(max_length=30)
    cat_cover = models.ImageField(upload_to='category_cover/')

    def __str__(self):
        return self.category_name


class AddBook(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    bookid = CharField(max_length=10)
    bookname = CharField(max_length=50)
    author = CharField(max_length=40, default='Desmond')
    location = CharField(max_length=20, default='23rd floor')
    subject = TextField(max_length=1000)
    copies = models.IntegerField(default='0')
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    pdf = models.FileField(upload_to='books/', blank=True, null=True)
    publisher = models.CharField(max_length=30, default='desmond')
    libNo = models.CharField(max_length=30, default='0001')
    edition = models.CharField(max_length=30, default='1')
    language = models.CharField(max_length=15, default='English')
    pages = models.IntegerField(default=300)
    quantity = models.IntegerField(default=0)
    Cat = models.ForeignKey(Category, default=1, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.bookname) + "[" + str(self.bookid) + ']'


def expiry():
    return datetime.today() + timedelta(days=15)


class IssueBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    studentid = CharField(max_length=20)
    book1 = models.CharField(max_length=20)
    issuedate = models.DateField(auto_now=True)
    expirydate = models.DateField(default=expiry)

    def __str__(self):
        return self.studentid


class ReturnBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bookid2 = models.CharField(max_length=20)


class AddStudent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    username = models.CharField(max_length=30)
    studentid = models.CharField(max_length=20)
    semail = models.CharField(max_length=30)
    phone = models.CharField(max_length=10, default='0700000000')
    password = models.CharField(max_length=20, default='00000000')

    def __str__(self):
        return '{} [{}]'.format(self.username, self.studentid)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fname = models.CharField(max_length=30)
    lname = models.CharField(max_length=30)
    sname = models.CharField(max_length=30)
    studentid = models.CharField(max_length=20)
    semail = models.CharField(max_length=30)
    phone = models.CharField(max_length=10, default='0700000000')
    password = models.CharField(max_length=20, default='00000000')

    def __str__(self):
        return '{} [{}]'.format(self.sname, self.studentid)


class Reading(models.Model):
    book = models.ForeignKey(AddBook, on_delete=models.CASCADE)
    reader = models.ForeignKey(User, on_delete=models.CASCADE)
    date_read = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book} - Currently reading by {self.reader.username}"


class ReadBook(models.Model):
    book = models.ForeignKey(AddBook, on_delete=models.CASCADE)
    reader = models.ForeignKey(User, on_delete=models.CASCADE)
    date_read = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book} - Read by {self.reader.username}"


class BorrowedBook(models.Model):
    book = models.ForeignKey(AddBook, on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    date_borrowed = models.DateTimeField(auto_now_add=True)
    expirydate = models.DateField(default=expiry)
    def __str__(self):
        return f"{self.book} - Borrowed by {self.borrower.username}"


class Rating(models.Model):
    book = models.ForeignKey(AddBook, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rate = models.IntegerField(choices=((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')))
    comment = models.TextField(max_length=250, default='It is good')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book.bookid} - {self.user.username}"



class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message} - {self.recipient.username}"