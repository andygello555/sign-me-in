# Sign-me-in

For when you just want to sleep...

## How it works

1. Syncs with your Google calendar to view all your lectures
1. Choose which calendars to keep track of
1. Enter the search parameters to match every calendar event against. For example:
    - If you are a CS student you might want to have your search parameters be:
        ```cs, lecture, online, pc``` would match a Google calendar event entitled ```CS2800 - Online```
    - **Be careful** to include all your edge cases...
        - Such as any module with a **non-standard course IDs**
        - **Workshops**
    - The search params will be check against both the event's **summary** and **description**, this means you can even include **lecturer names**
1. Enter your uni Microsoft account details
    - This is used to log into the register my attendance website
    - **These details ARE NOT saved or sent anywhere** just kept in memory until the program is terminated
1. The bot will then get started checking your calendar and signing you in!
    - Uses multithreading so calendars can be kept track of (somewhat<sup>[1](#myfootnote1)</sup>) concurrently
    - Will inform you of any wrong-doings/errors

## How to use

#### Prerequisites
- Python >= 3.6
- pip
- A Google account with your uni calendar synced
    - Follow the _Downloading Calendar timetable into Google_ section in [this](https://intranet.royalholloway.ac.uk/staff/assets/docs/pdf/timetabling/timetabling-pdfs-2019-20/how-to-subscribe-to-your-rhul-timetable-via-a-calendar-application-v2-updated.pdf) PDF to do that
- Maybe some sort of server to run the bot on, **not a requirement**

#### Install and setup

1. `git clone` the repository
1. You have to create a Google Calendar API project (don't worry this is **free**)
    - Go to [this](https://www.google.com) page and follow the **first** step
    - Remember to add the downloaded `credentials.json` to the cloned repository
1. Download the [latest version](https://github.com/mozilla/geckodriver/releases) of geckodriver for your OS
    - This enables the bot to open and control FireFox
    - **After downloading**: unzip or untar and place the executable somewhere on your **PATH**
        - If you don't know how to do this for your OS; there are many resources available online
1. **OPTIONAL**: create a virtual environment to hold your python dependencies
    - This helps with containing the whole project dependencies neatly in one place
    - Don't forget to run `source path/to/venv/bin/actiavte` to activate the virtual environment
1. `pip3 install -r requirements.txt` inside the cloned repository
    - This will install all the python dependencies
    - Hopefully it should all install just fine if the steps above were followed
1. Start the bot with `python3 main.py` and follow the instructions from there on out
    - **On first start**: a browser will open
        - This might say that the app is unverified
        - **This is because you have just created the Google Calendar Project and needs time to be verified fully by Google**
        - _However_ you can use the app in an unverified state by clicking on **advanced** on that webpage and continuing without verification
            - This just continues in developer mode, if I'm not mistaken
    - After this, select the Google account that has access to your uni calendar via Google Calendar


<a name="myfootnote1">1</a>: As concurrently as the multithreading library in python can allow
