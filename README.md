# CoWin Slot Notifier
A command line tool to fetch, display and notify about CoWin vaccination slots through E-Mail, based on Pincode or District, filtered by age.

# Installation
_Recommended to be used in a python virtual environment._
- Create a python virtualenv and activate it.
```
$ python3 -m venv env
$ source env/bin/activate
```
- Install the tool using pip
```
(env)$ pip install .
```

# Usage
- Use as `cowin-notifier` through shell
```
(env)$ cowin-notifier --help
Usage: cowin-notifier [OPTIONS] DATE

  Sends E-Mail Notification for available CoWin Slots on DATE

Options:
  -v, --verbose            Display verbose information
  -p, --pincode TEXT       Pincode to search by
  -d, --district TEXT      District to search by
  -s, --state TEXT         State for district to search by
  -a, --age-group INTEGER  Age Group to filter by
  --help                   Show this message and exit.
```

# Example
Notify for slots in "south west delhi, delhi" starting from 9th May, 2021
```
(env)$ cowin-notifier 9-5-2021 -d 'south west delhi' -s delhi
```
OR
```
(env)$ cowin-notifier 9-5-2021 --district='south west delhi' --state=delhi
```

