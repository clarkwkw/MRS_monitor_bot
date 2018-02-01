# MRS_monitor_bot
This is a Telegram bot for monitoring MRS page of CUHK

## Dependencies
- Python 3
- telegram
- pymongo
- schedule

## Usage
1. Get a Telegram bot token
2. Clone the repository and install required dependencies
3. Setup a MongoDB with a database named `MKTG-studies`
4. In the database, create 2 collections `Studies` and `Subscribed`
5. In SSH, issue the command `screen`
6. In screen, issue the command `python3 start.py`
7. Follow the instructions to provide necessary credentials
8. Detatch the screen by [Control] + [A] then [Control] + [D]

To check the status of the backend program, issue the command `screen -r` in SSH to attach the screen.
