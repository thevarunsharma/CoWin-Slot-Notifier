# CoWin Slot Notifier
A command line tool to fetch, display and notify about CoWin vaccination slots through E-Mail, based on Pincode or District, filtered by age.

## Installation
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

### Important Note about credentials
1. Create a text file `credentials` and place it in the same (top-level directory).
```
$ > credentials
``` 
2. To this file add the list of recipients in one of the following formats, one in each line
```
RECIPIENT_NAME <RECIPIENT_EMAIL_ADDRESS>
```
OR
```
RECIPIENT_EMAIL_ADDRESS
```
example: `John Doe <johndoe@xyz.com>` or `johndoe@xyz.com`

## Usage
- Use as `cowin-notifier` through shell
```
(env)$ cowin-notifier --help
Usage: cowin-notifier [OPTIONS]

  Sends E-Mail Notification for available CoWin Slots

Options:
  -v, --verbose               Display verbose information
  -p, --pincode TEXT          Pincode to search by
  -d, --district TEXT         District to search by
  -s, --state TEXT            State for district to search by
  -a, --age-group INTEGER     Age Group to filter by
  -c, --check-period INTEGER  Number of days in future to be checked
  -r, --recur-period INTEGER  Frequency of recurring updation in seconds
  --vaccine TEXT              Specific vaccine
  --dose INTEGER              Dose 1 or 2
  --help                      Show this message and exit.
```

- Upon running the tool, you will be prompted for your email and password for sending emails. Currently, __*only Outlook Mail is supported*__; Any non-outlook email id will result in authentication error.

## Example
Notify for slots in "south west delhi, delhi"
```
(env)$ cowin-notifier -d 'south west delhi' -s delhi
```
OR
```
(env)$ cowin-notifier --district='south west delhi' --state=delhi
```

