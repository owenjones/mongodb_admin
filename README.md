# MongoDB Admin
A set of helper scripts for bulk administration of MongoDB users/databases

## Create User Accounts
```
usage: make_users.py [-h] [--output] [--debug] file

bulk create MongoDB databases and users

positional arguments:
  file          csv file to load users from

optional arguments:
  -h, --help    show this help message and exit
  --output, -o  save csv output for successful and unsuccessful user creations
  --debug, -v   print debug messages to the terminal
```

## Modify User Accounts
```
usage: modify_users.py [-h] [--output] [--debug] file

bulk modify MongoDB users

positional arguments:
  file          csv file to load users from

optional arguments:
  -h, --help    show this help message and exit
  --output, -o  save csv output for successful and unsuccessful modifications
  --debug, -v   print debug messages to the terminal
```
