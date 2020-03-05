# SMS - Stock Management System

## Project Setup

### Requirements
- Python3+

### Steps
- Clone the repository
- Create a Python virtual env and install all dependencies
```shell script
$ python3 -m venv venv  # Create a Python virtual environment inside venv folder
$ source venv/bin/activate  # Activate virtual environment
$ pip install -r dev-requirements.txt  # Install all dependencies (dev)
# From now on you should always activate this environment when working on the project
```
- Create a database
```shell script
$ psql  # login to Postgres client
$ CREATE DATABASE dev_sms;  # create database named "dev_sms"

```
- Create a `.env` file and set the env vars following `env.example`
  - You'll need to set the database name you created in the previous step
  - Remember to set your email and password as Admin
```shell script
$ cat env.example > .env  # Copy env.example contents to a new .env file
```
- Run `flask deploy`
  - It will call the method `app.commands.deploy` which makes the database migrations, creates the Admin User, roles and the main Stock model instance.
- Run `flask run`
- Access `http://localhost:5000` and login with your admin account
