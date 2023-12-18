from datetime import date
import PyPDF2
from PyPDF2 import PdfFileReader
from django.contrib import messages
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as dj_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from datetime import date, timedelta
from django.utils import timezone
from .models import IssueBook, UserExtend, AddBook, ReturnBook, AddStudent, ReadBook, BorrowedBook, Rating, Category, \
    Reading, Notification
from django.contrib import messages
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404


def index(request):
    categories = Category.objects.all()
    category_data = []
    for category in categories:
        count = AddBook.objects.filter(Cat=category).count()
        books = AddBook.objects.filter(Cat=category)  # Filter books by category
        category_data.append({
            'name': category.category_name,
            'count': count,
            'image_url': category.cat_cover.url if category.cat_cover else None,
            'books': books,
            'id': category.id
        })
    category_data = sorted(category_data, key=lambda x: x['count'], reverse=True)
    context = {
        'category_data': category_data
    }
    top_read_books = AddBook.objects.annotate(read_count=Count('readbook')).order_by('-read_count')[:3]
    book_count = AddBook.objects.count()
    student_count = User.objects.count()
    issued_count = IssueBook.objects.count()
    context = {
        'category_data': category_data,
        'top_read_books': top_read_books,
        'book_count': book_count,
        'student_count': student_count,
        'issued_count': issued_count
    }
    return render(request, 'index.html', context)


def stafflogin(request):
    if request.session.has_key('is_logged'):
        return redirect('dash_board')
    return render(request, 'stafflogin.html')


def staffsignup(request):
    return render(request, 'staffsignup.html')


def dashboard(request):
    Book = AddBook.objects.all()
    return render(request, 'dashboard.html', {'Book': Book})


def addbook(request):
    user_name = request.user.username
    Book = AddBook.objects.all()
    return render(request, 'addbook.html', {'Book': Book, 'user_name': user_name})


def SignupBackend(request):
    if request.method == 'POST':
        uname = request.POST["uname"]
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        email = request.POST["email"]
        phone = request.POST['phone']
        password = request.POST['password']
        userprofile = UserExtend(phone=phone)
        if request.method == 'POST':
            try:
                UserExists = User.objects.get(username=request.POST['uname'])
                messages.error(request, " Username already taken, Try something else!!!")
                return redirect("staffsignup")
            except User.DoesNotExist:
                if len(uname) > 10:
                    messages.error(request, " Username must be max 15 characters, Please try again")
                    return redirect("staffsignup")

                if not uname.isalnum():
                    messages.error(request, " Username should only contain letters and numbers, Please try again")
                    return redirect("staffsignup")

        # create the user
        user = User.objects.create_user(uname, email, password)
        user.first_name = fname
        user.last_name = lname
        user.email = email
        user.save()
        userprofile.user = user
        userprofile.save()
        messages.success(request, " Your account has been successfully created")
        return redirect("stafflogin")
    else:
        return HttpResponse('404 - NOT FOUND ')




def LoginBackend(request):
    if request.method == 'POST':
        loginuname = request.POST['loginuname']
        loginpassword = request.POST['loginpassword']
        RegisteredUser = authenticate(request, username=loginuname, password=loginpassword)
        if RegisteredUser is not None and RegisteredUser.is_active:
            if RegisteredUser.is_superuser:
                dj_login(request, RegisteredUser)
                request.session['user_id'] = RegisteredUser.id

                return redirect('dash_board') 
                 # Redirect to admin site
            else:
                dj_login(request, RegisteredUser)
                # Set the 'user_id' key in the session
                request.session['user_id'] = RegisteredUser.id

                return redirect('userpage')  # Redirect to user page
        else:
            error_message = "Invalid login credentials."
            return render(request, 'stafflogin.html', {'error_message': error_message})
    else:
        return render(request, 'stafflogin.html')



@login_required(login_url='/login/')
def AddBookSubmission(request):
    if request.method == "POST":
        user1 = request.user
        bookid = request.POST["bookid"]
        bookname = request.POST["bookname"]
        author = request.POST["author"]
        subject = request.POST["subject"]
        location = request.POST["location"]
        copies = int(request.POST["copies"])
        publisher = request.POST["publisher"]
        libNo = request.POST["libNo"]
        edition = request.POST["edition"]
        cover = request.FILES['cover']
        pdf = request.FILES['pdf']
        language = request.POST["language"]
        pages = request.POST["pages"]
        category_id = request.POST["Cat"]  

        category = get_object_or_404(Category, pk=category_id)

        add = AddBook(user=user1, bookid=bookid, bookname=bookname, subject=subject, copies=copies,
                      location=location, author=author, cover=cover, pdf=pdf, publisher=publisher,
                      libNo=libNo, edition=edition, language=language, pages=pages, Cat=category)  
        add.save()
        Book = AddBook.objects.all()
        messages.success(request, "Book added successfully.")

    return render(request, 'dashboard.html', {'Book': Book})


@login_required(login_url='/login/')
def deletebook(request, id):
    user1 = request.user
    AddBook_info = AddBook.objects.get(id=id)
    AddBook_info.delete()
    return redirect("dashboard")


def bookissue(request):
    return render(request, 'bookissue.html')


def returnbook(request):
    return render(request, 'returnbook.html')


def HandleLogout(request):
    if request.session.has_key('user_id'):
        del request.session['user_id']
    logout(request)
    return redirect('/')


def issuebooksubmission(request):
    if request.method == 'POST':
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        studentid = request.POST['studentid']
        book1 = request.POST['book1']
        addbook = get_object_or_404(AddBook, bookid=book1)

        if addbook.copies > 0:
            obj = IssueBook(user=user1, studentid=studentid, book1=book1)
            obj.save()
            addbook.copies -= 1
            addbook.save()
        else:
            messages.error(request, "No copies available for this book.")

        issue_books = IssueBook.objects.all()
        return render(request, 'bookissue.html', {'Issue': issue_books})

    return redirect('/')


def returnbooksubmission(request):
    if request.method == 'POST':
        user_id = request.session["user_id"]
        user1 = User.objects.get(id=user_id)
        bookid2 = request.POST['bookid2']
        store1 = AddBook.objects.filter(bookid=bookid2)

        def return_book(returnbook):
            if returnbook.copies == "Issued":
                returnbook.copies = "Not-Issued"
                obj1 = ReturnBook(user=user1, bookid2=bookid2)
                obj = IssueBook.objects.filter(book1=bookid2)
                obj.delete()
                obj1.save()
                returnbook.save()
            else:
                messages.error(request, " Book not  issued !!!")

        returncategorylist = list(set(map(return_book, store1)))
        Return = ReturnBook.objects.all()
        return render(request, 'returnbook.html', {'Return': Return})
    return redirect('/')


# def Search(request):
#     query2 = request.GET["query2"]
#     Book = AddBook.objects.filter(bookname__icontains=query2)
#     params = {'Book': Book}
#     return render(request, 'bookdetails.html', params)

def Search(request):
    query2 = request.GET["query2"]
    book = get_object_or_404(AddBook, bookname__icontains=query2)
    ratings = Rating.objects.filter(book=book)
    rate = [rating.rate for rating in ratings]
    average_rating = calculate_average_rating(rate)
    context = {
        'book': book,
        'ratings': ratings,
        'average_rating': average_rating
    }
    return render(request, 'bookdetails.html', context)


def editbookdetails(request, id):
    user = request.user
    Book = AddBook.objects.get(id=id)
    return render(request, 'editdetails.html', {'Book': Book})


def updatedetails(request, id):
    if request.method == "POST":
        user = request.user
        add = AddBook.objects.get(id=id)
        add.bookid = request.POST["bookid"]
        add.bookname = request.POST["bookname"]
        add.subject = request.POST["subject"]
        add.ContactNumber = request.POST['category']
        add.save()
        return redirect("dashboard")


def addstudent(request):
    user = request.user
    return render(request, 'addstudent.html')


def viewstudents(request):
    user = request.user
    Student = AddStudent.objects.all()
    return render(request, 'viewstudents.html', {'Student': Student})


def Searchstudent(request):
    user = request.user
    query3 = request.GET["query3"]
    Student = AddStudent.objects.filter(studentid__icontains=query3)
    params = {'Student': Student}
    return render(request, 'viewstudents.html', params)


def addstudentsubmission(request):
    if request.method == "POST":
        user = request.user
        user1 = request.user
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        username = request.POST["username"]

        studentid = request.POST["studentid"]
        semail = request.POST["semail"]
        phone = request.POST["phone"]
        password = request.POST['password']
        add = AddStudent(user=user1, fname=fname, lname=lname, sname=username, studentid=studentid, semail=semail,
                         password=password, phone=phone)
        add.save()
        Student = AddStudent.objects.all()
        return render(request, 'addstudent.html', {'Student': Student})


def viewissuedbook(request):
    issued_books = IssueBook.objects.all()
    borrowed_books = BorrowedBook.objects.all()
    
    lis = []
    
    for issue in issued_books:
        issdate = issue.issuedate.strftime('%d-%m-%Y')
        expdate = issue.expirydate.strftime('%d-%m-%Y')
        days = (date.today() - issue.issuedate).days
        fine = max(0, days - 15) * 30
        
        book = AddBook.objects.filter(bookid=issue.book1).first()
        student = AddStudent.objects.filter(studentid=issue.studentid).first()
        
        if book and student:
            t = (student.username, student.studentid, book.bookname, book.bookid, book.subject, issdate, expdate, fine)
            lis.append(t)

            # Send notification for issued books nearing due date
            notification_days_before_due = 1  # Adjust the number of days as desired
            notification_date = issue.expirydate - timedelta(days=notification_days_before_due)

            if date.today() >= notification_date:
                notification_message = f"Your issued book '{book.bookname}' is due soon. Please return it by {issue.expirydate.strftime('%d-%m-%Y')}."
                Notification.objects.create(recipient=student.user, message=notification_message)
    
    return render(request, 'viewissuedbook.html', {'lis': lis})

def student_signup(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        sname = request.POST['sname']
        studentid = request.POST['studentid']
        semail = request.POST['semail']
        phone = request.POST["phone"]
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            try:
                user_exists = User.objects.get(username=sname)
                messages.error(request, "Username already taken. Please try a different username.")
                return redirect("student_signup")
            except User.DoesNotExist:
                pass
        try:
            user_exists = User.objects.get(username=sname)
            messages.error(request, "Username already taken. Please try a different username.")
            return redirect("student_signup")
        except User.DoesNotExist:
            pass
        user = User.objects.create_user(username=sname, password=password)
        user.fname = fname
        user.lname = lname
        user.semail = semail
        user.phone = phone
        user.save()

        student = AddStudent(user=user, fname=fname, lname=lname, sname=sname, studentid=studentid,
                             semail=semail, phone=phone)
        student.save()

        messages.success(request, "Your account has been created successfully. You can now log in.")
        return redirect("/")

    return render(request, "student_signup.html")


def userpage(request):
    books = AddBook.objects.all()
    categories = Category.objects.all()
    category_data = []
    for category in categories:
        count = AddBook.objects.filter(Cat=category).count()
        category_data.append({
            'name': category.category_name,
            'count': count,
            'image_url': category.cat_cover.url if category.cat_cover else None
        })
    category_data = sorted(category_data, key=lambda x: x['count'], reverse=True)
    context = {
        'books': books,
        'categories': categories,
        'category_data': category_data
    }
    return render(request, 'userpage.html', context)

def bookdetails(request, bookid):
    book = get_object_or_404(AddBook, bookid=bookid)
    similar_books = AddBook.objects.filter(Cat=book.Cat).exclude(id=book.id)
    ratings = Rating.objects.filter(book=book)
    rate = [rating.rate for rating in ratings]
    average_rating = calculate_average_rating(rate)
    context = {
        'book': book,
        'similar_books': similar_books,
        'ratings': ratings,
        'average_rating': average_rating
    }
    return render(request, 'bookdetails.html', context)

def dash_board(request):
    admin_count = User.objects.filter(is_superuser=True).count()
    book_count = AddBook.objects.count()
    student_count = User.objects.count()
    issued_count = IssueBook.objects.count()
    categories = Category.objects.all()
    category_data = []
    for category in categories:
        count = AddBook.objects.filter(Cat=category).count()
        category_data.append({
            'name': category.category_name,
            'count': count,
            'image_url': category.cat_cover.url if category.cat_cover else None
        })
    category_data = sorted(category_data, key=lambda x: x['count'], reverse=True)

    context = {
        'admin_count': admin_count,
        'book_count': book_count,
        'student_count': student_count,
        'issued_count': issued_count,
        'categories': categories,
        'category_data': category_data
    }
    top_read_books = AddBook.objects.annotate(read_count=Count('readbook')).order_by('-read_count')[:13 ]
    book_count = AddBook.objects.count()
    student_count = User.objects.count()
    issued_count = IssueBook.objects.count()
    context = {
        'category_data': category_data,
        'top_read_books': top_read_books,
        'book_count': book_count,
        'student_count': student_count,
        'issued_count': issued_count
    }
    return render(request, 'dash_board.html', context)


def my_books(request):
    user = request.user
    reading = Reading.objects.filter(reader=user).order_by('-date_read')
    borrowed = BorrowedBook.objects.filter(borrower=user).order_by('-date_borrowed')
    read = ReadBook.objects.filter(reader=user).order_by('-date_read')

    all_books = AddBook.objects.all()
    context = {
        'borrowed': borrowed,
        'read': read,
        'reading': reading,
        'all_books': all_books,
    }

    categories = Category.objects.all()
    category_data = []
    for category in categories:
        count = all_books.filter(Cat=category).count()  
        books = all_books.filter(Cat=category)          
        category_data.append({
            'name': category.category_name,
            'count': count,
            'image_url': category.cat_cover.url if category.cat_cover else None,
            'books': books,
            'id': category.id
        })

    category_data = sorted(category_data, key=lambda x: x['count'], reverse=True)

    context['category_data'] = category_data
    return render(request, 'mybooks.html', context)


def currently_reading(request, book_id):
    book = AddBook.objects.get(bookid=book_id)
    reader = request.user
    if request.method == 'POST':
        Reading.objects.create(book=book, reader=reader)
        return redirect('my_books')
    return render(request, 'my_books')


def borrow_book(request, book_id):
    book = AddBook.objects.get(id=book_id)
    borrower = request.user
    
    if request.method == 'POST':
        if BorrowedBook.objects.filter(book=book, borrower=borrower).exists():
            messages.error(request, "You have already borrowed this book.")
        else:
            BorrowedBook.objects.create(book=book, borrower=borrower)
            
            date_borrowed = datetime.now().date()
            expiry_date = date_borrowed + timedelta(days=15)
            
            subject = 'Book Borrowed Notification'
            message = f'You have successfully borrowed the book "{book.bookname}". Please return it by {expiry_date}.'
            from_email = 'mwrigdesmond.com'
            to_email = [borrower.email]
            send_mail(subject, message, from_email, to_email)
            
            messages.success(request, "Book borrowed successfully. Please return it by the due date.")
        
        return redirect('my_books')
    
    # Check if book is overdue
    borrowed_book = BorrowedBook.objects.filter(book=book, borrower=borrower).first()
    is_book_overdue = False
    if borrowed_book and borrowed_book.return_date < datetime.now().date():
        is_book_overdue = True
    
    context = {
        'book': book,
        'is_book_overdue': is_book_overdue
    }
    return render(request, 'my_books', context)


def mark_as_read(request, book_id):
    book = AddBook.objects.get(bookid=book_id)
    reader = request.user
    if request.method == 'POST':
        ReadBook.objects.create(book=book, reader=reader)
        return redirect('my_books')
    return redirect('my_books')


def rate_book(request, bookid):
    book = get_object_or_404(AddBook, bookid=bookid)
    if request.method == 'POST':
        rate = request.POST.get('rating')
        comment = request.POST.get('review')
        if rate and comment:
            rating = Rating.objects.create(book=book, user=request.user, rate=rate, comment=comment)
            return redirect('bookdetails', bookid=book.bookid)
    else:
        form = None

    return render(request, 'bookdetails.html')


def calculate_average_rating(rate):
    if not rate:
        return 0

    total_ratings = len(rate)
    total_sum = sum(rate)
    average_rating = total_sum / total_ratings

    return round(average_rating, 1)


def category_count(request):
    category_count = AddBook.objects.values('category').annotate(count=Count('category'))
    return render(request, 'userpage.html', {'category_counts': category_count})


def bookcategory(request, category_id=None):
    categories = Category.objects.all()

    if category_id:
        category = get_object_or_404(Category, id=category_id)
        books = AddBook.objects.filter(Cat=category)
        context = {
            'category_name': category.category_name,
            'books': books
        }
    else:
        categories = Category.objects.all()
        context = {
            'categories': categories
        }

    return render(request, 'category.html', context)


def pdf_reader(request, bookid):
    book = get_object_or_404(AddBook, bookid=bookid)

    # Check if the 'pdf' attribute has a file associated with it
    if book.pdf and book.pdf.url:
        context = {
            'book': book
        }
        return render(request, 'pdf_reader.html', context)
    else:
        return HttpResponse("This book does not have a PDF available.")


def readbook(request, bookid):
    book = get_object_or_404(AddBook, bookid=bookid)
    if book.pdf:
        with open(book.pdf.path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{book.bookname}.pdf"'
            return response
    return HttpResponse("PDF not available for this book.")

def profile(request):
    user = request.user
    
    if request.method == 'POST':
        profile_pic = request.FILES.get('profile_pic')
        if profile_pic:
            user.profile_pic = profile_pic
            user.save()
            return redirect('profile')
    
    return render(request, 'profile.html', {'user': user})

from django.http import JsonResponse

def check_borrowed(request, book_id):
    book = AddBook.objects.get(id=book_id)
    borrower = request.user
    
    is_borrowed = BorrowedBook.objects.filter(book=book, borrower=borrower).exists()
    
    return JsonResponse({'is_borrowed': is_borrowed})
