<h1> A Recipe API using TDD </h1>
note: This repository is the fruit of following <a href="https://www.udemy.com/course/django-python-advanced/" _target="Blank">this course</a>.

<h3> Steps to get the project on your computer: </h3>

## Create a directory where you want to clone the project
`````shell script
mkdir recipe-project
`````

## Change into the directory
`````shell script
cd recipe-project
`````

## clone the project
`````shell script
git clone https://github.com/simofirdoussi/recipe-app-api
`````

**Build locally and run**

## Build the Docker image
`````shell script
docker-compose build
`````

## Start the development server
`````shell script
docker-compose run --rm app sh -c "python manage.py runserver"
`````

**Important:**

Adding the necessary packages to the requirements.txt or requirements.dev.txt(for dev only packages) file is necessary before any push.
After the push, a series of checks are run automatically(see .github/worflows/checks.yml), including flake8 and the unit tests. Please make sure to format your code before pushing to the repository.
Flake8 which is a great toolkit for checking your code base against coding style (PEP8), programming errors (like “library imported but unused” and “Undefined name”).

## Documentation
An auto API Documentation has been set using swagger.
`````shell script
http://127.0.0.1:8000/api/docs/
`````
![alt](https://github.com/simofirdoussi/recipe-app-api/blob/main/images/swagger-docs.png)
