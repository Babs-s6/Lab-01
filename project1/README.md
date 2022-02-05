
# Project 1

ENGO 651  
This is my **Website** which you can search a book and leave a comment about it.
This website has different parts contains:
1. Make an account by registering for website
2. login to website 
3. search a book
4. see the details about the book; the details are ISBN, Title, Author, Year published, and also reviews
5. Users can leave comments (rate the book from 1 to 5 and leave a text comment as well)
6. API access: Users can make GET request (/api/<isbn>) and see the resulting JSON which follows the specific format
7. logout the website


---
- **books.csv file:**   
Contains information about books.  
- **import.py file:**   
Reads the data from books.csv file and insert data to the database.
- **application.py file:**  
Routes for the web application is created in this file.  (**RUN THIS**)
---


### templates folder:  
- **index.html file:**  
This is the first page and the login page.  
- **register.html file:**  
This page is for new users who still do not have an account, and requires them to register
- **search.html file:**  
Users will be able to search for a book by its ISBN or title or author name. 
This page should find any matches from the database and shows the results after the user submit the information, even if just part of a title, ISBN or author name are typed.  
- **book_page.html file:**  
After choosing one book from search page, the user can see the details about that book in this new page. 
It also shows the reviews on that book. 
Users can leave comments and rate the book (from 1 to 5), and submit it.  
---