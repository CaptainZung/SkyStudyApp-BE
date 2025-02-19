# SkyStudyApp Backend 👋

This is the backend project for SkyStudyApp, developed using Django, integrated with MongoDB, and providing RESTful APIs.

--------------------------------------------------
I. INSTALLATION GUIDE

1. Environment Requirements:
   - Python 3.8 or later.
   - MongoDB (Atlas or Local).
   - Pip (Python package manager).

2. Project Installation:
   - Install the required libraries by running:
     ```bash
     pip install -r requirements.txt
     ```

3. Database Configuration:
   - The project uses `djongo` to connect to MongoDB.
   - Update the database connection details in `settings.py` if necessary.

4. Running the Project:
   - Execute the following commands:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     python manage.py runserver
     ```
   - The server will be available at `http://127.0.0.1:8000`.

--------------------------------------------------
II. LIBRARIES USED

Below is the list of main libraries used in the project:

### Dependencies:
- asgiref==3.8.1
- certifi==2024.8.30
- chardet==3.0.4
- Django==3.2
- djongo==1.3.6
- djangorestframework==3.12.4
- dnspython==1.16.0
- googletrans==4.0.0rc1
- mongoengine==0.29.1
- numpy==2.0.1
- pandas==2.2.2
- pymongo==3.11.0
- python-dateutil==2.9.0.post0
- pytz==2024.1
- sqlparse==0.2.4
- tzdata==2023.4

Happy coding! 🚀
