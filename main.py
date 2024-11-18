import re
import kcisorder
import requests
import json
import yaml
import os
import random

print("Ordering system for KCIS")
print()

print("Loading config file")
if not os.path.exists("config.yaml"):
    print(
        "Config file not found. Pls create a config file under this path named config.json"
    )
    exit(1)

# with open("config.json", "r") as f:
#    config = json.load(f)

config = None
with open("config.yaml") as stream:
    try:
        config = yaml.load(stream, Loader=yaml.SafeLoader)
    except yaml.YAMLError as exc:
        print("Cannot read config.yaml, check ur syntax!")
        print(exc)

if config is None:
    print("Cannot read config.yaml, check ur syntax!")
    exit(1)

target_list = config.get("orders")
if target_list is None:
    print("No orders found in config file")
    exit(1)

crawl_every = config.get("crawl_every")
if crawl_every is None:
    crawl_every = True

if not crawl_every:
    print(
        "WARNING: Crawling is off, all meal lists will be as crawled from the first account"
    )


def does_hit_rule(rules_to_check, meal_to_check, print_hit=True):
    if meal_to_check.get("id") is None or meal_to_check.get("remaining") == "0":
        # print(
        #     f"{meal_to_check.get('type')} {meal_to_check.get('id')} - {meal_to_check.get('chinese_name')}"
        #     f" sold out"
        # )
        return False
    if not (
        rules_to_check.get("cafeteria") is None
        or rules_to_check.get("cafeteria") == meal_to_check.get("cafeteria")
    ):
        return False
    meal_description = (
        f"{meal_to_check.get('chinese_name')}\n{meal_to_check.get('english_name')}"
        f"\n{meal_to_check.get('description')}"
    )
    # print(meal_description)
    # print()
    matches = rules_to_check.get("match")

    if matches is None:
        return True

    for regex in matches:
        if regex is None:
            continue
        regex_pattern = regex.get("regex")

        if regex_pattern is None:
            return True
        pattern = re.compile(regex_pattern)
        search_result = pattern.search(meal_description)
        if regex.get("not") is not None and regex.get("not"):
            if search_result:
                return False
            continue
        if not search_result:
            return False
    if print_hit:
        print(
            f"Hit {meal_to_check.get('type')} {meal_to_check.get('id')} - {meal_to_check.get('chinese_name')}"
            f" (match: {rules_to_check})"
        )
    return True


def get_hit_rule(rules_to_check, meals_to_check, print_hit=True):
    if rules_to_check.get("random") is not None and rules_to_check.get("random"):
        return get_random_hit_meal(meals_to_check, rules_to_check, print_hit)
    for meal_to_check in meals_to_check:
        if does_hit_rule(rules_to_check, meal_to_check, print_hit):
            return meal_to_check


def get_random_hit_meal(meals_to_proceed, match_rule, print_hit=True):
    hit_meals = []

    if match_rule is None:
        hit_meals = meals_to_proceed
    else:
        for single_meal in meals_to_proceed:
            if does_hit_rule(match_rule, single_meal, False):
                hit_meals.append(single_meal)

    if len(hit_meals) == 0:
        return

    random_index = random.randint(0, len(hit_meals) - 1)
    random_meal = hit_meals[random_index]

    if print_hit:
        print(
            f"Hit {random_meal.get('type')} {random_meal.get('id')} - {random_meal.get('chinese_name')}"
            f" (random: {match_rule})"
        )

    return random_meal


meals = None

print()
for target in target_list:
    print(f"Processing order for {target.get('name')} - {target.get('id')}")
    session = requests.session()
    kcisorder.login(target.get("id"), target.get("password"), session)
    print("Logged in")

    if crawl_every or meals is None:
        print("Getting meals")
        meals = kcisorder.get_meal(session)

    if meals is None:
        print(
            "Failed to get meal list. Pls check your internet connection and credentials! Skipping this order"
        )
        continue
    # print(json.dumps(meals))
    print("Matching meals")
    meals_to_order = []
    for day in meals:
        for lunch_dinner_i in range(len(day)):
            lunch_dinner = day[lunch_dinner_i]
            if (lunch_dinner is None) or (len(lunch_dinner) == 0):
                continue
            flag_done_finding_meal = False
            rules = target.get("lunch") if lunch_dinner_i == 0 else target.get("dinner")
            for rule in rules:
                hit_meal = get_hit_rule(rule, lunch_dinner)
                if hit_meal is not None and len(hit_meal) != 0:
                    flag_done_finding_meal = True
                    meals_to_order.append(hit_meal)

                if flag_done_finding_meal:
                    break
            if not flag_done_finding_meal:
                print("No match, skips")

    print("Submitting the following: ")
    print(json.dumps(meals_to_order))

    kcisorder.submit_order(session, meals_to_order)

    print()

print("All done")
