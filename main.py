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
        "Config file not found. Pls create a config file under this path named config.yaml"
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

print(f"Successfully loaded {len(target_list)} orders")

crawl_every = config.get("crawl_every")
if crawl_every is None:
    crawl_every = True

if not crawl_every:
    print(
        "WARNING: crawl_every is set to false, all orders will match list crawled from the first order"
    )

# preprocess arraies, this is for 'follow'
target_list_key_as_name = {}
target_list_key_as_id = {}
for target in target_list:
    target_list_key_as_name[target["name"]] = target
    target_list_key_as_id[target["id"]] = target

clear_existing = config.get("clear_existing")
if clear_existing is None:
    clear_existing = False
if clear_existing:
    print(
        "WARNING: clear_existing is set to true, meals that are already been ordered will be cleared"
    )


def is_any_remaining(meal_to_check):
    if meal_to_check.get("id") is None or meal_to_check.get("remaining") == "0":
        print(
            f"{meal_to_check.get('type')} {meal_to_check.get('chinese_name')}"
            f" sold out"
        )
        return False


def does_hit_rule(rules_to_check, meal_to_check, print_hit=True):
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


def match_meal(rules_to_check, meals_to_check, print_hit=True):
    if rules_to_check.get("random") is not None and rules_to_check.get("random"):
        return get_random_hit_meal(meals_to_check, rules_to_check, print_hit)
    for meal_to_check in meals_to_check:
        if does_hit_rule(
            rules_to_check, meal_to_check, print_hit
        ) and not is_any_remaining(meal_to_check):
            return meal_to_check


def get_random_hit_meal(meals_to_proceed, match_rule, print_hit=True):
    hit_meals = []

    if match_rule is None:
        hit_meals = meals_to_proceed
    else:
        for single_meal in meals_to_proceed:
            if does_hit_rule(match_rule, single_meal, False) and not is_any_remaining(
                single_meal
            ):
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


meal_list = None

print()
for target in target_list:
    print(f"Processing order for {target.get('name')} - {target.get('id')}")
    session = requests.session()
    kcisorder.login(target.get("id"), target.get("password"), session)
    print("Logged in")

    clear_existing_local = target.get("clear_existing")

    if crawl_every or meal_list is None:
        print("Getting meals")
        meal_list = kcisorder.get_meals(session)

    rules = {}
    rules["lunch"] = target.get("lunch") or []
    rules["dinner"] = target.get("dinner") or []

    if target.get("follow") is not None:
        for following in target.get("follow"):
            try:
                rules["lunch"] += target_list_key_as_id[following]["lunch"]
                rules["dinner"] += target_list_key_as_id[following]["dinner"]
            except KeyError:
                print(f"WARNING: cannot find rules for {following}")
    if target.get("follow_by_name") is not None:
        for following in target.get("follow_by_name"):
            try:
                rules["lunch"] += target_list_key_as_name[following]["lunch"]
                rules["dinner"] += target_list_key_as_name[following]["dinner"]
            except KeyError:
                print(f"WARNING: cannot find rules for {following}")

    if meal_list is None:
        print(
            "Failed to get meal list. Pls check your internet connection and credentials! Skipping this order"
        )
        continue
    # print(json.dumps(meals))
    print("Matching meals")
    meals_to_order = []
    for day in meal_list:  # day structure: {"lunch": [], "dinner": []}
        for key, meals in day.items():
            if meals is None or len(meals) == 0:
                continue
            flag_done_finding_meal = False
            for rule in rules[key]:
                meal_hit = match_meal(rule, meals)
                if meal_hit is not None and len(meal_hit) != 0:
                    flag_done_finding_meal = True
                    meals_to_order.append(meal_hit)
                if flag_done_finding_meal:
                    break
            if not flag_done_finding_meal:
                print("No match, skips")

    if clear_existing_local or (clear_existing_local is None and clear_existing):
        print("Clearing existing orders")
        kcisorder.clear_meals_ordered(session)

    print("Submitting the following: ")
    print(json.dumps(meals_to_order))

    kcisorder.submit_order(session, meals_to_order)

    print()

print("All done")
