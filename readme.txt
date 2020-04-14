# Python version 3.7.5

1. Create virtual environment
2. python manage.py migrate
3. python script.py [n|p]
p - proceed (from the last record in the database)
n - new (clearing database)

Script's work:
1. Creates a file with all combinations of 1, 2, 3 letters.
2. Using library requests-future (https://pypi.org/project/requests-futures/) the script simulates ajax requests to
https://allo.ua/.
3. Makes request until status_code == 200. This was made according to overcome the 429 Too many requests error occurring.
So it must do as much requests as can be done.
4. Puts data into database (id, query_string, response_tip).