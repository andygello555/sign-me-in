# Sign-me-in

For when you just want to sleep...

### How it works

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
    - Uses multithreading so calendars can be kept track of (somewhat[^bignote]) concurrently
    - Will inform you of any wrong-doings/errors

[^bignote]: As conncurrently as the multithreading library in python can allow
