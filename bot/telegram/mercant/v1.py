import requests

#LOCAL_BASE_URL="https://afroked.onrender.com/api"

LOCAL_BASE_URL="http://localhost:8000/api"


# Save or login with bot user to get token
def login(user_id):
    # prepare data content
    data = {"user_id": user_id, "plateform": "telegram"}
    # send request to api
    response = requests.post(f"{LOCAL_BASE_URL}/bot/login", json=data)
    # Get token in response
    token = response.json()["token"]

    return response.status_code, token

def validate_user_infos(user_data, user_id:int):
    # get token from login
    _ , token = login(user_id)
    # login with token in headers
    headers = {"Authorization": f"Bearer {token}"}
    # prepare data content
    data = {"full_name": user_data["full_name"], "contact": user_data["contact"]}
    # send request to api
    response = requests.put(f"{LOCAL_BASE_URL}/bot/infos", json=data, headers=headers)
    # return response
    return response.status_code, response.json()

def get_all_categories():
    response = requests.get(f"{LOCAL_BASE_URL}/categories/all")
    # return list of categories
    return response.status_code, response.json()

def get_all_orders(user_id:int):
    # get token from login
    _ , token = login(user_id)
    # login with token in headers
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{LOCAL_BASE_URL}/bot/orders/all", headers=headers)
    # return details of shopping cart
    return response.status_code, response.json()

def validate_order(seller_id:int, user_id:int):
    # get token from login
    _ , token = login(user_id)
    # login with token in headers
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.put(f"{LOCAL_BASE_URL}/bot/orders/validate/{seller_id}", headers=headers)
    # return details of shopping cart
    return response.status_code, response.json()

def create_product(collection: dict, user_id:int):
    # get token from login
    _ , token = login(user_id)
    # login with token in headers
    headers = {"Authorization": f"Bearer {token}"}
    # prepare data content
    data = {
        "name": collection["name"],
        "price": float(collection["price"]),
        "stock": int(collection["stock"]),
        "description": collection["description"],
        "image": collection["image"],
        "category_id": collection["category_id"],
        "currency": "FCFA"
    }
    # send request to api
    response = requests.post(f"{LOCAL_BASE_URL}/bot/products/create", json=data, headers=headers)

    return response.status_code, response.json()

def search_item(search_term: str, user_id: int):
    # get token from login
    _ , token = login(user_id)
    # login with token in headers
    headers = {"Authorization": f"Bearer {token}"}
    # prepare data content
    data = {"search_term": search_term}
    # send request to api
    response = requests.post(f"{LOCAL_BASE_URL}/bot/products/search", headers=headers, params=data)
    return response.status_code, response.json()

def delete_product(product_id: str, user_id: int):
    # get token from login
    _ , token = login(user_id)
    # login with token in headers
    headers = {"Authorization": f"Bearer {token}"}
    # send request to api
    response = requests.delete(f"{LOCAL_BASE_URL}/bot/products/{product_id}", headers=headers)
    return response.status_code, response.json()
