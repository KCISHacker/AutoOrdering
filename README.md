# AutoOrdering
A script that selects meals by regular expressions and then orders them

## How to use

Clone repo:
```bash
git clone https://www.github.com/KCISHacker/AutoOrdering
cd AutoOrdering
```

It is recommended to use venv:

```bash
python -m venv ordering
source ordering/bin/activate # activate venv
```

Install packages:

```bash
python -m pip install -r requirements.txt
```

Now you can run the program by:
```bash
python main.py
```
For how to configure, check example file [config.example.yaml](./config.example.yaml)

## Schedule

***Notice that your device must be turned on during the time scheduled*** 

***It is suggested to host it on a server***

### On Windows
Use Task Scheduler(`taskschd.msc`) to schedule running

For more info anout Task Scheduler, see [Wikipedia](https://en.m.wikipedia.org/wiki/Windows_Task_Scheduler)

### On Linux, BSD, and other Unix-like system
Use cron:

```bash
crontab -e
```

For more info about crontab, visit [Wikipedia](https://en.wikipedia.org/wiki/Cron), [Arch Wiki](https://wiki.archlinux.org/title/Cron) or generate config using [this website](https://crontab.guru/)

### On MacOS
Use cron, or use [**launchd**](https://en.m.wikipedia.org/wiki/Launchd)

## Importing

If you want to make your own client, you may want to import [kcisorder](./kcisorder)

Functions:
| Function Name | Parameters | Purpose |
|--------------|------------|----------|
| `login` | `username: str`<br>`password: str`<br>`request_session: requests.Session` | Authenticates a user to the ordering system by sending login credentials. Returns the session object if successful, None if failed. |
| `get_meal` | `request_session: requests.Session` | Retrieves the full weekly meal menu. Scrapes information including meal names (in Chinese and English), remaining quantities, cafeteria numbers, and meal types (lunch/dinner). Returns a nested list of meal data. |
| `add_to_cart` | `meal_id: str`<br>`request_session: requests.Session` | Adds a specific meal to the user's shopping cart using the meal's ID. Adding or removing meals from cart does not effect the `submit_order` function.|
| `submit_order` | `request_session: requests.Session`<br>`meal_list: list` | Submits the final order for the meals. Takes a list of meals and sends them to the ordering endpoint. |
