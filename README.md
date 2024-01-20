# Restaurant API

This is project that provide rest api and system management for Restaurant.

## API Features

- Authentication
- Searching, Filtering, Ordering/Sorting
- Pagination and Throttling
- Category
- Menu Item
- User group management
- Cart management
- Order management

## Installation and Runing

- clone this repo `https://github.com/dotpep/restaurant-api`
- `cd restaurant-api`

- insatall `python` > 3.8
- install pipenv for virtual environment `pip insatall pipenv`

- create virtual enviroment `pipenv shell`
- install dependencies `pipenv install`

- `python manage.py runserver`

You should now be able to access the API at `http://localhost:8000/`

Admin panel `http://localhost:8000/admin/`
username: admin
password: admin

- you can activate pipenv venv in powershell by `pipenv shell`, `&.virtualenvs\restaurant-api-your_specific_project_hash\Scripts\activate.sh`
- Check python version `pip --version` or Use pyenv to install multiple python version `pip install pyenv`
- Verify that all dependencies are installed correctly `pipenv graph`
- models `python manage.py makemigrations` and `python manage.py migrate`

Use requiremetns.txt and standard venv instead pipenv

- `python venv env`
- `env\Scripts\activate`
- `pip install -r requiremets.txt`

## Documentation

### Demonstration

### ER-diagram

- [\docs\ERD](docs\ERD\README.md)

![Database Entity Design ER-D](docs\ERD\ER-D_restaurantapi.png)

## LICENCE

This project is licensed under the [MIT License](LICENSE).
