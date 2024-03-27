import telebot
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from telebot import types

# Initialisation de l'application FastAPI
app = FastAPI()

# Token du bot à obtenir auprès du BotFather sur Telegram
TOKEN = '7003324615:AAGSf1JmzWi6nOUYBAm9zvYZlF0HwgxLrE4'

# Création de l'instance du bot
bot = telebot.TeleBot(TOKEN)

# Dictionnaire des produits avec leurs prix et quantités disponibles
products = {
    'Produit 1': {'prix': 10, 'quantite': 10, 'photo': 'https://e-xportmorocco.com/storage/produits/1645537818.jpeg', 'details': 'Description du produit 1'},
    'Produit 2': {'prix': 20, 'quantite': 15, 'photo': 'https://assets.afcdn.com/story/20230724/2224514_w4205h3153c1cx2103cy1689cxt0cyt0cxb4205cyb3378.jpg', 'details': 'Description du produit 2'},
    'Produit 3': {'prix': 15, 'quantite': 8, 'photo': 'https://e-xportmorocco.com/storage/produits/1645537818.jpeg', 'details': 'Description du produit 3'}
}

# Panier de chaque utilisateur (stocké temporairement en mémoire)
user_carts = {}

# Commande pour afficher les catégories de produits
@bot.message_handler(commands=['start'])
def send_categories(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for category in products.keys():
        markup.add(types.KeyboardButton(category))
    bot.send_message(message.chat.id, "Choisissez une catégorie :", reply_markup=markup)

# Gérer la sélection de la catégorie et afficher les produits
@bot.message_handler(func=lambda message: message.text in products.keys())
def handle_category(message):
    product_name = message.text
    product = products[product_name]
    user_id = message.chat.id

    # Vérifier si le produit est disponible en stock
    if product['quantite'] > 0:
        # Ajouter le produit au panier de l'utilisateur
        if user_id not in user_carts:
            user_carts[user_id] = {}
        if product_name not in user_carts[user_id]:
            user_carts[user_id][product_name] = 0
        user_carts[user_id][product_name] += 1
        product['quantite'] -= 1
        bot.send_message(user_id, f"{product_name} a été ajouté à votre panier.")
    else:
        bot.send_message(user_id, "Désolé, ce produit est actuellement en rupture de stock.")

# Commande pour afficher le contenu du panier
@bot.message_handler(commands=['panier'])
def view_cart(message):
    user_id = message.chat.id

    if user_id in user_carts and user_carts[user_id]:
        cart_content = "\n".join([f"{product}: {quantity}" for product, quantity in user_carts[user_id].items()])
        bot.send_message(user_id, f"Contenu du panier :\n{cart_content}")

        # Création de l'URL pour la page web du panier
        web_link = f"http://votreserveur.com/panier/{user_id}"
        
        # Création du contenu de la réponse Inline Query
        inline_query_result = types.InlineQueryResultArticle(
            id='1',
            title='Ouvrir le panier dans le bot',
            input_message_content=types.InputTextMessageContent(web_link)
        )

        # Envoi de la réponse Inline Query
        bot.send_message(user_id, "Cliquez sur le bouton ci-dessous pour ouvrir votre panier dans le bot :",
                         reply_markup=create_cart_inline_keyboard(user_id))
        bot.answer_inline_query(message.inline_query.id, [inline_query_result])
    else:
        bot.send_message(user_id, "Votre panier est vide.")

def create_cart_inline_keyboard(user_id):
    web_link = f"http://votreserveur.com/panier/{user_id}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Ouvrir le panier", url=web_link))
    return markup


"""# Commande pour afficher le contenu du panier
@bot.message_handler(commands=['panier'])
def view_cart(message):
    user_id = message.chat.id

    if user_id in user_carts and user_carts[user_id]:
        cart_content = "\n".join([f"{product}: {quantity}" for product, quantity in user_carts[user_id].items()])
        bot.send_message(user_id, f"Contenu du panier :\n{cart_content}")
    else:
        bot.send_message(user_id, "Votre panier est vide.")"""

# Route pour afficher la page web du panier
@app.get('/panier/{user_id}', response_class=HTMLResponse)
async def show_cart(request: Request, user_id: int):
    if user_id in user_carts and user_carts[user_id]:
        cart_content = user_carts[user_id]
        return HTMLResponse(open("panier.html").read() % {'user_id': user_id, 'cart': cart_content, 'products': products})
    else:
        raise HTTPException(status_code=404, detail="Votre panier est vide.")

# Route pour ajouter ou retirer un produit du panier depuis l'interface web
@app.post('/update_cart/{user_id}')
async def update_cart(request: Request, user_id: int, action: str = Form(...)):
    action_parts = action.split('_')
    product_name = '_'.join(action_parts[1:])
    if action.startswith('add') and products[product_name]['quantite'] > 0:
        if user_id not in user_carts:
            user_carts[user_id] = {}
        if product_name not in user_carts[user_id]:
            user_carts[user_id][product_name] = 0
        user_carts[user_id][product_name] += 1
        products[product_name]['quantite'] -= 1
    elif action.startswith('remove') and product_name in user_carts[user_id]:
        user_carts[user_id][product_name] -= 1
        if user_carts[user_id][product_name] == 0:
            del user_carts[user_id][product_name]
        products[product_name]['quantite'] += 1
    else:
        raise HTTPException(status_code=400, detail="Action invalide")
    return {"message": "Panier mis à jour avec succès"}

# Route pour ouvrir la page web du panier dans le bot
@app.post('/open_cart_in_bot/{user_id}')
async def open_cart_in_bot(user_id: int):
    if user_id in user_carts and user_carts[user_id]:
        web_link = f"http://localhost:8000/panier/{user_id}"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Ouvrir le panier", url=web_link))
        bot.send_message(user_id, "Cliquez sur le bouton ci-dessous pour ouvrir votre panier dans le bot :", reply_markup=markup)
        return {"message": "Bouton pour ouvrir le panier envoyé avec succès"}
    else:
        raise HTTPException(status_code=404, detail="Votre panier est vide.")

# Lancer le bot
def start_bot():
    bot.polling()

# Lancer l'application FastAPI
if __name__ == "__main__":
    import threading
    threading.Thread(target=start_bot).start()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

