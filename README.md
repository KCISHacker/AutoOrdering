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