import re
import requests
import traceback
from bs4 import BeautifulSoup
from requests import session

base_url = "https://ordering.kcisec.com/ordering/" # ends with /
login_url = base_url + "login.asp?action=login"
index_url = base_url + "index.asp"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

def login(username: str, password: str, request_session: requests.Session):
    headers = {
        "User-Agent": user_agent,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "User": username,
        "Pwd": password
    }

    try:
        response = request_session.post(login_url, headers=headers, data=payload)
        response.raise_for_status()
        return request_session
    except requests.exceptions.RequestException:
        traceback.print_exc()
        return None

def get_meal(request_session: requests.Session):
    response = get_request(request_session, index_url, headers={"User-Agent": user_agent})
    if response is None:
        return None

    soup = BeautifulSoup(response.text.encode('iso-8859-1').decode('gbk'), 'html.parser')
    side_menu_weeks = soup.find("dl", class_="submenu")
    if side_menu_weeks is None:
        print("kcisorder: Failed to get menu items!")
        return None
    order_dates = side_menu_weeks.find_all("a")
    # gets: <a href="?d0=2024/9/8&amp;d=1">SUN (9.8)</a>
    # from sunday to saturday

    meal_list = []

    for order_date in order_dates:
        arg = order_date.get("href")
        url = index_url + arg
        response = get_request(request_session, url, headers={"User-Agent": user_agent})
        if response is None:
            continue

        # all cafeterias
        soup_lunch_dinner = (BeautifulSoup(response.text.encode('iso-8859-1').decode('gbk'), 'html.parser')
                             .find_all("div", class_="col-xs-8 col-xs-offset-4"))

        day_meal_list = [] # should be two elements, lunch and dinner
        # lunch and dinner
        lunch = True
        for lunch_dinner in soup_lunch_dinner:
            # meals in lunch or dinner
            lunch_dinner_meal_list = []
            soup_cafeteria_list = lunch_dinner.find_all("div", class_="collapse in")
            # for every cafeteria
            for soup_cafeteria_index in range(len(soup_cafeteria_list)):

                soup_cafeteria = soup_cafeteria_list[soup_cafeteria_index]
                # cafeteria_meal_list = []
                # meals in a single cafeteria
                soup_meal_list = (soup_cafeteria.find('div', class_='row', recursive=False)
                                  .find_all("div", recursive=False))
                last_meal = None
                for j in range(len(soup_meal_list)):

                    soup_meal = soup_meal_list[j]

                    if (j % 2) == 1:
                        if last_meal is not None:
                            lunch_dinner_meal_list.append(last_meal)

                        description_soup = soup_meal.find("div", class_="col-xs-12")
                        description = None
                        if description_soup is not None:
                            description = (re.search("</h4>(.*?)$", description_soup.decode_contents(), re.DOTALL)
                                           .group(1).strip().replace("<br/>", '\n'))
                        last_meal["description"] = description
                        continue

                    rows = (soup_meal.find('div', class_='col-xs-6', style='padding-left: 0px')
                            .find_all(recursive=False))

                    # first: name
                    names = rows[0].find("div", class_="dish-name").find_all('h5')
                    chinese_name = names[0].text
                    english_name = names[1].text

                    # second: remaining
                    remaining = rows[1].find("strong").text

                    # third: order button
                    meal_id = None
                    add_to_cart_a = rows[2].find("a")
                    if add_to_cart_a is not None:
                        add_to_cart_url = add_to_cart_a.get("href")
                        meal_id = re.search(r"buy_car.asp\?id=(\d+)", add_to_cart_url).group(1)

                    # a single meal
                    last_meal = {
                        "chinese_name": chinese_name,
                        "english_name": english_name,
                        "remaining": remaining,
                        "id": meal_id,
                        "cafeteria": soup_cafeteria_index + 1,
                        "type": "lunch" if lunch else "dinner"
                    }

                    # cafeteria_meal_list.append(conclusion)

                # if len(cafeteria_meal_list) <= 0:
                #     continue
                # lunch_dinner_meal_list.append(cafeteria_meal_list)

            day_meal_list.append(lunch_dinner_meal_list)
            lunch = False

        meal_list.append(day_meal_list)

    return meal_list

def add_to_cart(meal_id: str, request_session: requests.Session):
    # whoever named cart as "buy_car" is a genius :trumbsup::trumbsup::trumbsup:
    get_request(request_session, base_url + f"buy_car.asp?id={meal_id}", headers={"User-Agent": user_agent})

def get_request(request_session: requests.Session, url, headers = None, payload=None):
    try:
        response = request_session.get(url, headers=headers, data=payload)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        return None

def submit_order(request_session: requests.Session, meal_list: list):
    headers = {
        "User-Agent": user_agent,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = []
    for meal in meal_list:
        payload.append(("reaID", meal.get("id")))

    response = post_request(
        request_session, base_url + "orders.asp?action=order_ok",
        headers=headers, payload=payload)

    if response is None:
        return None

    return response

def post_request(request_session: requests.Session, url, headers = None, payload=None):
    try:
        response = request_session.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        return None