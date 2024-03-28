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

def get_all_categories():
    response = requests.get(f"{LOCAL_BASE_URL}/categories/all")
    # return list of categories
    return response.status_code, response.json()

def get_all_products_by_category(category_id:str):
    # send request to api
    response = requests.get(f"{LOCAL_BASE_URL}/categories/{category_id}/products")
    return response.status_code, response.json()

def get_all_products():
    response = requests.get(f"{LOCAL_BASE_URL}/products/all")
    # return list of products
    return response.status_code, response.json()

def get_product_details(product_id):
    response = requests.get(f"{LOCAL_BASE_URL}/products/{product_id}")
    # return details of product
    return response.status_code, response.json()

def add_to_cart(product_id, quantity, user_id:int):
    # get token from login
    _ , token = login(user_id)
    # login with token in headers
    headers = {"Authorization": f"Bearer {token}"}
    # prepare data content
    data = [{"product_id": product_id, "quantity": quantity}]
    # send request to api
    response = requests.post(f"{LOCAL_BASE_URL}/cart/create", json=data, headers=headers)

    return response.status_code, response.json()

def get_shopping_cart(user_id:int):
    # get token from login
    _ , token = login(user_id)
    # login with token in headers
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{LOCAL_BASE_URL}/cart/me", headers=headers)
    # return details of product
    return response.status_code, response.json()

