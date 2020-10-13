# Sign-me-in

For when you just want to sleep...

## How it works

1. Syncs with your Google calendar to view all your lectures
1. Choose which uni calendars to keep track of
    - Of course all calendars that you want to keep track of must be synced to the chosen Google account
    - **Tested the bot watching 2 calendars** and you could probably get away with watching a couple more (hardware dependant)
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
    - Don't forget to run `source path/to/venv/bin/activate` to activate the virtual environment
1. `pip3 install -r requirements.txt` inside the cloned repository
    - This will install all the python dependencies
    - Hopefully it should all install just fine if the steps above were followed
1. Start the bot with `python3 main.py` and follow the instructions from there on out
    - **On first start**: a browser will open
        - This might say that the app is unverified
        - **This is because you have just created the Google Calendar Project and needs time to be verified fully by Google**
        - _However_ you can use the app in an unverified state by clicking on **advanced** on that webpage and continuing without verification
            - This just continues in developer mode, if I'm not mistaken
        - If you want to get your app verified by Google for whatever reason. Then look elsewhere because I personally have no idea.
    - After this, select the Google account that has access to your uni calendar via Google Calendar

## Questions you might have

Q. _Why does the bot schedule to sign me in at such random times?_
A. **Because *they are* random times. The bot will purposefully choose a time between 10% and 75% of the way through an event. This is to try and stop any potential bot checkers from blacklisting your IP. If you were scheduled to be signed in on the dot every time, it might be a bit suspicious. I don't know if Campus Connect has any bot checkers (they probably don't) but it's better to be safe than sorry.**

Q. _Why 10% and 75%?_
A. **Just to be safe. I've had a couple of lectures where the sign-in was only made available a couple of minutes into the lecture. Even though the bot will keep checking to see if it can sign in after every couple of seconds when it knows there is a timetabled lecture, it's better to sign-in once and only once to avoid re-opening a Selenium browser multiple times as this could lead to high memory usage.<sup>[2](#myfootnote2)</sup>**

Q. _Why was Google Calendar used to keep track of events and not just have the bot constantly checking Campus Connect if there is a sign-in button?_
A. **Mostly due to me using Google Calendar, as well as some other things:**
- **Bot checking (again): If you have a bot that's continuously checking on Campus Connect then it might be flagged as a bot and blocked**
- **Lots of selenium browser instances needed: If you want to keep track of 3 calendars at once this involves 3 Selenium browsers opening and closing every time you want to check for a sign-in. Of course you could stagger these checks but it might lead to memory leaks from closing all those browsers which would lead to the running machine being slowed down gradually**
- **Bit more sophisticated**


<a name="myfootnote1">1</a>: As concurrently as the multithreading library in python can allow
<a name="myfootnote2">2</a>: If you want to change this, there are two constants inside  `workers.py`: `SCHEDULE_START_PERCENT` and `SCHEDULE_END_PERCENT` which can be easily changed to different percentages.