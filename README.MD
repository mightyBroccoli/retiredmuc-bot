## XMPP Retired MUC Bot
The repository houses a simple bot build to redirect joining user of MUC room A to room b.

### requirements
The easiest way to setup a clean Python project environment is to use a virtual environment inside the cloned
repository directory. The following bash lines install the `python-virtualenv` module, create the virtual environment
using Python3 and finally install all dependencies listed in the requirements file.

```bash
# Debian
apt install python-virtualenv

# Arch
pacman -S python-virtualenv

# create a venv folder inside the cloned repository
mkdir venv
virtualenv -p python3 venv/

source ./venv/bin/activate
pip install -r requirements.txt
```

### configuration
The configuration effort is quite low and should be for the most part be self-explanatory.
The message section features the message templates the bot will use to reply to message / group messages. To further
customize the user experience some variables are available, to for example directly tag the user.

The room section lists the room a / b the bot connects, redirects to.
The key is the room the bot tries to join and the value is the redirect target.

### pre-commit framework
This project utilizes the [pre-commit](https://pre-commit.com/) framework to automate various small hick-ups that tend
to happen prior to committing.

To use the framework it is necessary to follow these steps:
```bash
# install the pre-commit hook
pre-commit install

# to test your staged files manually run
pre-commit run
