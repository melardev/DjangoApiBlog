# Introduction
This is a Django rest framework Blog api, it is an uncompleted project.
If you want a more advanced project look at the E-commerce Api written in Django in my Github repository.

# Getting started
1. Git clone the project
2. Execute reset_all.ps1 to reset the migrations, the database and seed the database.

# Features Implemented so far
- Seed all the models with faker
- Some controllers are already finished: Articles, Like, User Subscription and Comment

# Useful commands
python3 manage.py shell -i ipython
python3 manage.py shell_plus --notebook
%load_ext autoreload

# Steps

# TODO
- Paginator does not update his default offset or limit fields
if we change them in views.py
- Why some comment replies point to a different article than the replied comment
- 