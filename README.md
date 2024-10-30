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

If you need to schedule the program, you can use crontab:

```bash
crontab -e
```

For more info about crontab, visit [Wikipedia](https://en.wikipedia.org/wiki/Cron) or generate config useing [this website](https://crontab.guru/)