from telebot import types
from v1 import get_all_categories, get_all_products_by_category, get_product_details, add_to_cart, get_shopping_cart
import telebot

TOKEN = "7003324615:AAGSf1JmzWi6nOUYBAm9zvYZlF0HwgxLrE4"
MINI_APP_LINK = "https://t.me/afroked_bot/afromark"

# Créer un bot Telegram
bot = telebot.TeleBot(TOKEN)

message_for_welcome = """
    🎉🛍️ Bienvenue sur notre incroyable bot e-commerce ! 🛍️🎉

    🌟 Découvrez une expérience de shopping unique et passionnante, juste à portée de clic. 🌟

    💼 Parcourez notre sélection exclusive de produits de qualité, soigneusement choisis pour vous. 💼

    💬 Vous avez des questions ? Besoin de conseils ? Nous sommes là pour vous aider à tout moment ! 💬

    🚀 Voici quelques commandes que vous pouvez utiliser pour commencer :

    ➡️ /start - Commencez votre achat
    ➡️ /catalog - Voir le catalogue de produits
    ➡️ /mycart - Voir ce que vous avez dans votre panier
    ➡️ /myreceipt - Voir votre facture

    💌 Prêt à commencer votre aventure de shopping ? Cliquez sur les boutons ci-dessus et laissez-vous emporter ! 💌
    """

# Message de bienvenue
@bot.message_handler(commands=['start'])
def welcome_message(message):
    user_id = message.chat.id
    bot.send_message(user_id, message_for_welcome)
    # get all categories
    _, categories = get_all_categories()
    print(categories)
    # return all categories in button
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        keyboard.add(types.KeyboardButton(category["name"]))
    print(f"{message.chat.id}: start conversation")
    bot.send_message(message.chat.id, "Choisissez une catégorie:", reply_markup=keyboard)


_, categories = get_all_categories()
# Gérer la navigation et l'achat
@bot.message_handler(func=lambda message: message.text in [category['name'] for category in categories])
def category_handler(message):
    category_name = message.text
    category_id = next(category['id'] for category in categories if category['name'] == category_name)  # Récupérer l'ID de la catégorie
    
    products_keyboard = types.InlineKeyboardMarkup()
    _, products = get_all_products_by_category(category_id)
    for product in products:
        product_button = types.InlineKeyboardButton(text=product["name"], callback_data=f"product_{product['id']}_{category_id}")  # Passer l'ID de la catégorie
        products_keyboard.add(product_button)
    print(f"{message.chat.id}: choose categorie {category_name}")
    bot.send_message(message.chat.id, "Choisissez un produit:", reply_markup=products_keyboard)


# Afficher le produit
@bot.callback_query_handler(func=lambda call: call.data.startswith("product_"))
def product_handler(call):
    data_parts = call.data.split("_")
    product_id = data_parts[1]
    category_id = data_parts[2]  # Récupérer l'ID de la catégorie
    
    # Récupérer les produits
    _, product = get_product_details(product_id)
    
    # Afficher les détails du produit
    #message_text = f"[Image]({product['image']})\n"
    message_text = f"{product['name']} ({product['stock']})\n\n"
    message_text += f"Prix: {product['price']} FCFA\n\n"
    message_text += f"{product['description']}\n\n"
    
    # Ajouter des boutons
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton("Ajouter au panier", callback_data=f"add_to_cart_{product_id}"))
    keyboard.add(types.InlineKeyboardButton("Liker", callback_data=f"like_product_{product_id}"))
    # Envoyer la photo du produit
    print(f"{call.message.chat.id}: Get product {[product['name']]} detail")
    bot.send_photo(call.message.chat.id, product["image"], caption=message_text, reply_markup=keyboard)

# Ajout au panier
@bot.callback_query_handler(func=lambda call: call.data.startswith("add_to_cart_"))
def add_to_cart_handler(call):
    data_parts = call.data.split("_")
    product_id = data_parts[3]

    # Ajouter le produit au panier
    status, _ = add_to_cart(product_id, 1, call.message.chat.id)

    if status == 200:
        bot.answer_callback_query(call.id, "Produit ajouté au panier")
        print(f"{call.message.chat.id}: Add product {[product_id]} detail")
    else:
        bot.answer_callback_query(call.id, "Une erreur est survenue")
        print(f"{call.message.chat.id}: Error when adding {[product_id]}")

# Liker un produit
@bot.callback_query_handler(func=lambda call: call.data.startswith("like_product_"))
def like_product_handler(call):
    data_parts = call.data.split("_")
    product_id = data_parts[2]
    
    # Liker le produit
    print(f"{call.message.chat.id}: Like product {[product_id]}")
    
    bot.answer_callback_query(call.id, "Produit liké")

# Afficher les details du panier
@bot.message_handler(commands=['mycart'])
def cart_handler(message):
    all_items = []

    _, receipt = get_shopping_cart(message.chat.id)

    if 'data' not in receipt:
        message_text = receipt["detail"]
        bot.send_message(message.chat.id, message_text, parse_mode="Markdown")

    else:
        for detail in receipt["data"]:
            if detail:
                item_data = f"{detail['product_name']} - Quantité: {detail['quantity']} - Prix unitaire: {detail['unit_price']} - Prix total: {detail['total_unit']} FCFA"
                all_items.append(item_data)
            else:
                item_data = f"{detail['detail']}"
                all_items.append(item_data)

        if all_items:
            cart_contents = "\n\n".join(all_items)
            message_text = f"**Votre panier:**\n\n{cart_contents}\n\n**Total:** {receipt['total_price']} FCFA"
        else:
            message_text = "Votre panier est vide."
        
        print(f"{message.chat.id}: Get cart and receipt")
        bot.send_message(message.chat.id, message_text, parse_mode="Markdown")

@bot.message_handler(commands=['catalog'])
def view_catalog(message):
    button_text = "Ouvrir"
    mini_app_url = MINI_APP_LINK
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=button_text, url=mini_app_url))

    print(f"{message.chat.id}: View all product")
    
    bot.send_message(message.chat.id, "Consulter tous les catalogues en cliquant sur le bouton suivant:", reply_markup=keyboard)


# Démarrer le bot
bot.polling()
