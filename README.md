### Online Learning Management System using Flask MongoDB
This project is an Online Learning Management System built using Flask and MongoDB. It allows users to browse and enroll in courses, and enables instructors to add and remove courses.

### Prerequisites
Python 
MongoDB

### Installation and setup
Clone the repository
git clone (https://github.com/AkankshaAkubathini/Akanksha-OnlineLearningManagementSystem.git)
Install dependencies
create a virtual environment in the clone
pip install -r requirements.txt

Setup MongoDB
Install MongoDB
Start MongoDB server
Create a database named "olms" and collections named "login", "admin", "courses", and "cart"
Run the application app.py using flask run

### Functionalities

#### Login / signup page :
Students have to signup as new user to add courses to their cart.
After login they will be redirected to home page where students can browse different courses and choose the courses they want.
A session for the student will be created.
Instructors can also signup and log into the website, they can add or remove courses.

#### Home :
In home page, students can view different courses, both free and premium and can also search for any course easily using search bar.

#### MyCourses :
When students click on add course, depending on the kind of course: free and premium , they are redirected to other pages and finally course gets added to their MyCourses list.

#### Admin :
When admin logs in ,he can view  the information such as which course is taken up by which student.

#### Database:
The courses are stored in courses collection
The login details are stored in login collection 
