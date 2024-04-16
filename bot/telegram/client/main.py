from telebot import types
from firebase import upload_file
from v1 import (get_all_categories, get_all_products_by_category, get_product_details, 
                add_to_cart, get_shopping_cart, validate_shopping_cart, create_advertise,
                search_item)
import telebot
import os

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
    ➡️ /advertise - Faire une demande
    ➡️ /catalog - Voir le catalogue de produits
    ➡️ /mycart - Voir ce que vous avez dans votre panier
    ➡️ /myreceipt - Voir votre facture
    ➡️ /search - Recherche produit

    💌 Prêt à commencer votre aventure de shopping ? Cliquez sur les boutons ci-dessus et laissez-vous emporter ! 💌
    """

print("Bot server loading...")
print("Bot is ready !")

# Message de bienvenue
@bot.message_handler(commands=['start'])
def welcome_message(message):
    user_id = message.chat.id
    bot.send_message(user_id, message_for_welcome)
    # get all categories
    _, categories = get_all_categories()
    # return all categories in button
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        keyboard.add(types.KeyboardButton(category["name"]))
    print(f"{user_id}: start conversation")
    bot.send_message(message.chat.id, "🛠️ Choisissez une catégorie:", reply_markup=keyboard)


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
    bot.send_message(message.chat.id, "🛍️ Choisissez un produit:", reply_markup=products_keyboard)


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
    message_text += f"Prix: {product['price']} {product['currency']}\n\n"
    message_text += f"{product['description']}\n\n"
    
    # Ajouter des boutons
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(types.InlineKeyboardButton("🛒 Ajouter au panier", callback_data=f"add_to_cart_{product_id}"))
    #keyboard.add(types.InlineKeyboardButton("Liker", callback_data=f"like_product_{product_id}"))
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
        message_text = "Votre panier est vide"
        print(f"{message.chat.id}: {receipt['detail']}")
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

            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="✅ Valider mon panier", callback_data=f"validate_cart_{receipt['cart_id']}"))
        else:
            bot.send_message(message.chat.id, "Veuillez réessayer s'il vous plait.")

        print(f"{message.chat.id}: Get cart {[receipt['cart_id']]}")
        bot.send_message(message.chat.id, message_text, parse_mode="Markdown", reply_markup=keyboard)

# Valider le contenu du panier
@bot.callback_query_handler(func=lambda call: call.data.startswith("validate_cart_"))
def validate_cart(call):
    data_parts = call.data.split("_")
    cart_id = data_parts[2]

    status, _ = validate_shopping_cart(cart_id, call.message.chat.id)

    if status == 200:
        print(f"{call.message.chat.id}: Validate shopping cart")
        bot.send_message(call.message.chat.id, "Votre panier a été validé !")
    else:
        bot.send_message(call.message.chat.id, "Une erreur s'est produite, veuillez reconsulter votre panier.")

# Accédez à l'interface web
@bot.message_handler(commands=['catalog'])
def view_catalog(message):
    button_text = "Ouvrir"
    mini_app_url = MINI_APP_LINK
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=button_text, url=mini_app_url))

    print(f"{message.chat.id}: View all product")
    
    bot.send_message(message.chat.id, "Consulter tous les catalogues en cliquant sur le bouton suivant:", reply_markup=keyboard)

# Effectuer une recherche
@bot.message_handler(commands=['search'])
def start_search(message):
    print(f"{message.chat.id}: Start search")
    bot.send_message(message.chat.id, "Veuillez entrer le nom du produit:")
    bot.register_next_step_handler(message, get_search_query)

def get_search_query(message):
    print(f"{message.chat.id} -> Get search term query")
    if message.text:
        status, response = search_item(message.text)
        
        if status == 200:
            for product in response:
                message_text = f"{product['name']} ({product['stock']})\n\n"
                message_text += f"Prix: {product['price']} {product['currency']}\n\n"
                message_text += f"{product['description']}\n\n"
                bot.send_photo(message.chat.id, product["image"], caption=message_text)
        else:
            bot.send_message(message.chat.id, "Aucun produit trouvé sous ce nom")
        
    else:
        bot.send_message(message.chat.id, "Le nom du produit est requis. Veuillez réessayer.")
        bot.register_next_step_handler(message, get_search_query)


##########################################
# Make announcement
##########################################


# Dictionary to save user announcement informations
user_infos = {}

# Initiation de l'envoi de l'annonce
@bot.message_handler(commands=["advertise"])
def start_annonce(message):
    print(f"{message.chat.id}: Make annoncement")
    bot.send_message(message.chat.id, "🙎‍♂️ Veuillez envoyer votre nom complet:")
    bot.register_next_step_handler(message, get_full_name)


def get_full_name(message):
    print(f"{message.chat.id} -> Get full name")
    if message.text:
        user_infos["full_name"] = message.text
        bot.send_message(message.chat.id, "📱 Veuillez envoyer votre numéro de contact:")
        bot.register_next_step_handler(message, get_phone)
    else:
        bot.send_message(message.chat.id, "Le nom complet est requis. Veuillez réessayer.")
        bot.register_next_step_handler(message, get_full_name)


def get_phone(message):
    print(f"{message.chat.id} -> Get phone")
    if message.text:
        user_infos["phone"] = message.text

        bot.send_message(message.chat.id, "📤 Veuillez envoyer une description de votre demande ou annonce:")
        bot.register_next_step_handler(message, get_description)
    else:
        bot.send_message(message.chat.id, "Le numéro de contact est requis. Veuillez réessayer.")
        bot.register_next_step_handler(message, get_phone)


def get_description(message):
    print(f"{message.chat.id} -> Get description")
    if message.text:
        user_infos["content"] = message.text
        bot.send_message(message.chat.id, "Veuillez envoyer une photo:")
        bot.register_next_step_handler(message, get_picture)
    else:
        bot.send_message(message.chat.id, "La description est requise. Veuillez réessayer.")
        bot.register_next_step_handler(message, get_description)


def get_picture(message):
    print(f"{message.chat.id} -> Get photo")
    if message.photo:

        file_id = message.photo[-1].file_id
        #print(file_id)
        file_info = bot.get_file(file_id)
        #print(file_info)

        file_path_normalized = file_info.file_path.replace('\\', '/')
        file_name = f"{file_info.file_unique_id}_{file_path_normalized.split('/')[-1]}" #_{file_info.file_path.split('/')[-1]} 
        downloaded_file = bot.download_file(file_info.file_path)

        FILE_PATH = "photos/"

        file_path = os.path.join(FILE_PATH, file_name)
        with open(file_path, "wb") as file:
            file.write(downloaded_file)
        
        user_infos["image"] = upload_file(file_path)

        # call api to save announcement
        status, response = create_advertise(user_infos, message.chat.id)

        if status == 200:
            message_text = f"**** RESUME DE VOTRE DEMANDE *****\n\n"
            message_text += f"Propriétaire: {response['full_name']}\n"
            message_text += f"Contact(s): {response['phone']}\n\n"
            message_text += f"{response['content']}\n\n"
            
            print(f"{message.chat.id}: send user annoncement")

            bot.send_photo(message.chat.id, response["image"], caption=message_text)
            bot.send_message(message.chat.id, "✅ Votre annonce a été enregistrée avec succès. Merci!")
        else:
            bot.send_message(message.chat.id, "Une erreur s'est produite. Veuillez réessayez")

    else:
        bot.send_message(message.chat.id, "Veuillez envoyer une photo (facultatif).")
        bot.register_next_step_handler(message, get_picture)


"""@bot.message_handler(func=lambda message: True)
def store_annonce(message):
    # Vérifier si le message provient de la commande /annonce
    if message.text.startswith("/advertise"):
        return
    
    status, _ = create_advertise(message.text, message.chat.id)

    if status == 200:
        print(f"{message.chat.id}: send user annoncement")
        bot.send_message(message.chat.id, "✅ Votre demande a été enregistrée avec succès.")
    else:
        bot.send_message(message.chat.id, "Une erreur s'est produite. Veuillez réessayez")
"""

@bot.message_handler(commands=["cancel"])
def cancel_annonce(message):
    # Réinitialiser les informations de l'utilisateur
    user_infos.clear()
    bot.send_message(message.chat.id, "Votre demande a été annulée. Vous pouvez démarrer une nouvelle demande avec /advertise.")


# Démarrer le bot
bot.polling()

print("Server is shutting down ...")