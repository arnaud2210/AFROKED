"""import telebot
from telebot import types
from datetime import datetime

# Définir les catégories et les produits
categories = {
    "Fruits": ["Pomme", "Banane", "Orange"],
    "Légumes": ["Carotte", "Tomate", "Concombre"],
}

products = {
    "Pomme": {"prix": 1.5, "image": "data:image/jpeg;base64,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"},
    "Banane": {"prix": 2.0, "image": "data:image/jpeg;base64,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"},
    "Orange": {"prix": 2.5, "image": "https://image.png"},
    "Carotte": {"prix": 1.0, "image": "https://image.png"},
    "Tomate": {"prix": 1.5, "image": "https://image.png"},
    "Concombre": {"prix": 2.0, "image": "https://image.png"},
}

# Panier
panier = {}

TOKEN = "7003324615:AAGSf1JmzWi6nOUYBAm9zvYZlF0HwgxLrE4"

# Créer un bot Telegram
bot = telebot.TeleBot(TOKEN)

# Définir le menu principal
@bot.message_handler(commands=["start"])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        keyboard.add(types.KeyboardButton(category))
    bot.send_message(message.chat.id, "Choisissez une catégorie:", reply_markup=keyboard)

# Gérer la navigation et l'achat
@bot.message_handler(func=lambda message: message.text in categories)
def category_handler(message):
    category = message.text
    products_keyboard = types.InlineKeyboardMarkup()
    for product in categories[category]:
        product_button = types.InlineKeyboardButton(text=product, callback_data=f"product_{product}")
        products_keyboard.add(product_button)
    bot.send_message(message.chat.id, "Choisissez un produit:", reply_markup=products_keyboard)

# Afficher le panier
@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def product_handler(call):
    product_name = call.data[8:]
    product = products[product_name]
    # Gérer l'ajout au panier
    if product_name not in panier:
        panier[product_name] = 1
    else:
        panier[product_name] += 1
    bot.answer_callback_query(call.id, "Produit ajouté au panier")

# Finaliser la commande
@bot.message_handler(func=lambda message: message.text == "Panier")
def cart_handler(message):
    total_price = 0
    for product_name, quantity in panier.items():
        product = products[product_name]
        total_price += product["prix"] * quantity
    
    # Afficher le contenu du panier
    message_text = "**Votre panier:**\n\n"
    for product_name, quantity in panier.items():
        product = products[product_name]
        message_text += f"- {product_name} x {quantity} ({product['prix']}€)\n"
    message_text += f"\n**Total:** {total_price}€\n\n"
    
    # Demander les informations de livraison et de paiement
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Valider la commande"))
    bot.send_message(message.chat.id, message_text, reply_markup=keyboard)

# Gérer la validation de la commande
@bot.message_handler(func=lambda message: message.text == "Valider la commande")
def checkout_handler(message):
    # Demander l'adresse de livraison
    bot.send_message(message.chat.id, "Veuillez entrer votre adresse de livraison:")
    
    # Gérer le paiement
    # ...
    
    # Confirmation de la commande
    bot.send_message(message.chat.id, "Votre commande a été validée !")
    # Envoyer un email de confirmation
    # ...


def checkout_handler(message):
    # Demander l'adresse de livraison
    bot.send_message(message.chat.id, "Veuillez entrer votre adresse de livraison:")

    # Enregistrer l'adresse de livraison
    def get_address(message):
        address = message.text
        # Sauvegarder l'adresse dans votre base de données
        # ...
        
        # Confirmation de la commande
        bot.send_message(message.chat.id, "Votre commande a été validée !")

        # Envoyer un email de confirmation
        # ...

        # Gérer la suite (suivi de la commande, etc.)
        # ...

    bot.register_next_step_handler(message, get_address)

# Démarrer le bot
bot.polling()

"""

import telebot
from telebot import types
import json
from datetime import datetime


# Définir les catégories et les produits
categories = {
    "Fruits": ["Pomme", "Banane", "Orange"],
    "Légumes": ["Carotte", "Tomate", "Concombre"],
}

products = {
    "Pomme": {
        "prix": 1.5,
        "image": "https://e-xportmorocco.com/storage/produits/1645537818.jpeg",
        "description": "Une pomme rouge et juteuse."
    },
    "Banane": {
        "prix": 2.0,
        "image": "https://assets.afcdn.com/story/20230724/2224514_w4205h3153c1cx2103cy1689cxt0cyt0cxb4205cyb3378.jpg",
        "description": "Une banane jaune et sucrée."
    },
    "Orange": {
        "prix": 2.0,
        "image": "https://www.shutterstock.com/shutterstock/photos/2053015835/display_1500/stock-photo-orange-with-sliced-and-green-leaves-isolated-on-white-background-2053015835.jpg",
        "description": "Une banane jaune et sucrée."
    },
    "Concombre": {
        "prix": 2.0,
        "image": "https://media.istockphoto.com/id/91516166/fr/photo/rondelles-de-concombre-sur-fond-blanc.jpg?s=612x612&w=0&k=20&c=Mhu7A5_r1zsIOd3vrwdUz-mWWKr-rybhb_sHmNenHF4=",
        "description": "Une concombre verte."
    },
    "Tomate": {
        "prix": 2.0,
        "image": "https://www.alimentarium.org/sites/default/files/media/image/2016-10/AL001-02%20tomate_0.jpg",
        "description": "Une banane jaune et sucrée."
    },
    "Carotte": {
        "prix": 2.0,
        "image": "https://www.primeale.fr/app/uploads/2022/03/primeale-les-carottes-vrac.jpg",
        "description": "Une banane jaune et sucrée."
    },
    # ...
}

# Panier
panier = {}

TOKEN = "7003324615:AAGSf1JmzWi6nOUYBAm9zvYZlF0HwgxLrE4"

# Créer un bot Telegram
bot = telebot.TeleBot(TOKEN)

# Définir le menu principal
@bot.message_handler(commands=["start"])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        keyboard.add(types.KeyboardButton(category))
    print(message.chat.id)
    bot.send_message(message.chat.id, "Choisissez une catégorie:", reply_markup=keyboard)


# Gérer la navigation et l'achat
@bot.message_handler(func=lambda message: message.text in categories)
def category_handler(message):
    category = message.text
    products_keyboard = types.InlineKeyboardMarkup()
    for product in categories[category]:
        product_button = types.InlineKeyboardButton(text=product, callback_data=f"product_{product}")
        products_keyboard.add(product_button)
    print(message.chat.id)
    bot.send_message(message.chat.id, "Choisissez un produit:", reply_markup=products_keyboard)

# Afficher le produit
@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def product_handler(call):
    product_name = call.data[8:]
    product = products[product_name]
    
    
    # Afficher les détails du produit
    #message_text = f"[Image]({product['image']})\n"
    message_text = f"**{product_name}**\n\n"
    message_text += f"Prix: {product['prix']}€\n"
    message_text += f"Description: {product['description']}\n\n"
    
    # Ajouter des boutons
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton("Ajouter au panier", callback_data=f"add_to_cart_{product_name}"))
    keyboard.add(types.InlineKeyboardButton("Liker", callback_data=f"like_product_{product_name}"))
    # Envoyer la photo du produit
    bot.send_photo(call.message.chat.id, product["image"], caption=message_text, reply_markup=keyboard)
    #bot.send_message(call.message.chat.id, message_text, reply_markup=keyboard)


"""
@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def product_handler(call):
    product_name = call.data[8:]
    product = products[product_name]
    
    # Créer une carte
    card = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    
    # Ajouter l'image du produit
    card.add(types.InlineKeyboardButton(text="️ Image",  url=product["image"]))
    
    # Ajouter les détails du produit
    card.add(types.KeyboardButton(text=f"Nom: {product_name}"))
    card.add(types.KeyboardButton(text=f"Prix: {product['prix']}€"))
    card.add(types.KeyboardButton(text=f"Description: {product['description']}"))
    
    # Ajouter des boutons d'action
    card.add(types.KeyboardButton(text=" Ajouter au panier"))
    card.add(types.KeyboardButton(text="❤️ Liker"))
    
    # Envoyer la carte
    bot.send_message(call.message.chat.id, "**Produit:**", reply_markup=card)
    """



# Gérer l'ajout au panier
@bot.callback_query_handler(func=lambda call: call.data.startswith("add_to_cart_"))
def add_to_cart_handler(call):
    product_name = call.data[12:]
    
    # Ajouter le produit au panier
    if product_name not in panier:
        panier[product_name] = 1
    else:
        panier[product_name] += 1
    
    bot.answer_callback_query(call.id, "Produit ajouté au panier")

# Gérer le like
@bot.callback_query_handler(func=lambda call: call.data.startswith("like_product_"))
def like_product_handler(call):
    product_name = call.data[14:]
    
    # Liker le produit
    # ...
    
    bot.answer_callback_query(call.id, "Produit liké")


# Afficher le panier
@bot.message_handler(commands=["panier"])
def cart_handler(message):
    total_price = 0
    all = []
    for product_name, quantity in panier.items():
        product = products[product_name]
        data = f"{product_name} *** {quantity} *** {product['prix']}"
        all.append(data)
    
        total_price += product["prix"] * quantity
    
    # Afficher le contenu du panier
    message_text = f'**Votre panier:**\n\n{all}\n\n **Total:** {total_price}€\n\n'

    
    # Ajouter un bouton pour finaliser la commande
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Valider la commande"))
    bot.send_message(message.chat.id, message_text, reply_markup=keyboard)


# Gérer la validation de la commande
@bot.message_handler(func=lambda message: message.text == "Valider la commande")
def checkout_handler(message):
    # Demander l'adresse de livraison
    bot.send_message(message.chat.id, "Veuillez entrer votre adresse de livraison:")

    def get_address(message):
        address = message.text
        # Sauvegarder l'adresse de livraison (base de données ou autre)
        # ...
        
        # Confirmation de la commande
        bot.send_message(message.chat.id, "Votre commande a été validée !")

        # Envoyer un email de confirmation (facultatif)
        # ...

        # Gérer la suite (suivi de la commande, etc.)
        # ...

    bot.register_next_step_handler(message, get_address)

# Démarrer le bot
bot.polling()

