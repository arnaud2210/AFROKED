from telebot import types
from firebase import upload_file
from v1 import (create_product, get_all_categories, search_item)
import telebot
import uuid
import os


TOKEN = "7046351585:AAHwegbBHwaVBcFXSJK9NrBXB4nkt7cS_Bg"

# Créer un bot Telegram
bot = telebot.TeleBot(TOKEN)

print("Bot server loading...")
print("Bot is ready !")

message_for_welcome = """
    Bienvenue sur notre bot marchand ! 🛍️

    Je suis là pour vous aider à gérer votre boutique en ligne de manière efficace et simple. Voici ce que vous pouvez faire avec ce bot :

    📦 **Gérer vos produits** :
    - Ajoutez de nouveaux produits à votre boutique.
    - Consultez et mettez à jour la liste de vos produits existants.
    - Supprimez les produits qui ne sont plus disponibles.

    🛒 **Suivre les commandes** :
    - Visualisez les commandes passées par vos clients.
    - Marquez les commandes comme traitées ou en cours de traitement.

    📢 **Gérer les demandes** :
    - Consultez les demandes spéciales des clients.
    - Répondez aux demandes pour fournir un service personnalisé.

    📊 **Accès aux statistiques** :
    - Obtenez des statistiques sur les ventes et les performances de votre boutique.

    N'hésitez pas à utiliser les commandes et les fonctionnalités disponibles pour optimiser la gestion de votre boutique en ligne. Si vous avez des questions ou besoin d'assistance, n'hésitez pas à me contacter à tout moment !

    Bonne journée et bon commerce ! 🌟
"""

currencies = ["FCFA", "EURO", "DOLLAR"]

# Message de bienvenue
@bot.message_handler(commands=['start'])
def welcome_message(message):
    user_id = message.chat.id
    print(f"{user_id}: start conversation")
    bot.send_message(user_id, message_for_welcome)


product = {}

# Initiation de l'envoi de l'annonce
@bot.message_handler(commands=["newproduct"])
def start_creation_product(message):
    print(f"{message.chat.id}: Product creation")
    bot.send_message(message.chat.id, "🙎‍♂️ Veuillez envoyer le nom du produit:")
    bot.register_next_step_handler(message, get_product_name)


def get_product_name(message):
    print(f"{message.chat.id} -> Get product name")
    if message.text:
        product["name"] = message.text
        bot.send_message(message.chat.id, "Veuillez envoyer le prix du produit:")
        bot.register_next_step_handler(message, get_product_price)
    else:
        bot.send_message(message.chat.id, "Le nom est requis. Veuillez réessayer.")
        bot.register_next_step_handler(message, get_product_name)


def get_product_price(message):
    print(f"{message.chat.id} -> Get product price")
    if message.text:
        product["price"] = message.text
        bot.send_message(message.chat.id, "Veuillez envoyer le stock total du produit:")
        bot.register_next_step_handler(message, get_product_stock)
    else:
        bot.send_message(message.chat.id, "Le prix est requis. Veuillez réessayer.")
        bot.register_next_step_handler(message, get_product_price)


def get_product_stock(message):
    print(f"{message.chat.id} -> Get product stock")
    if message.text:
        product["stock"] = message.text
        bot.send_message(message.chat.id, "Veuillez la description du produit:")
        bot.register_next_step_handler(message, get_product_description)
    else:
        bot.send_message(message.chat.id, "Le nombre en stock est requis. Veuillez réessayer.")
        bot.register_next_step_handler(message, get_product_stock)


def get_product_description(message):
    print(f"{message.chat.id} -> Get product description")
    if message.text:
        product["description"] = message.text
         # get all categories
        _, categories = get_all_categories()
        # return all categories in button
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for category in categories:
            keyboard.add(types.KeyboardButton(category["name"]))
        
        bot.send_message(message.chat.id, "Veuillez choisir la catégorie auquelle appartient votre produit:", reply_markup=keyboard)
        #bot.register_next_step_handler(message, choose_category)
    else:
        bot.send_message(message.chat.id, "La description est requise. Veuillez réessayer.")
        bot.register_next_step_handler(message, get_product_description)


def choose_category(message):
     # get all categories
    _, categories = get_all_categories()
    # return all categories in button
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories:
        keyboard.add(types.KeyboardButton(category["name"]))
    
    bot.send_message(message.chat.id, "Veuillez choisir la catégorie auquelle appartient votre produit:", reply_markup=keyboard)


_, categories = get_all_categories()

@bot.message_handler(func=lambda message: message.text in [category['name'] for category in categories])
def get_product_category(message):
    print(f"{message.chat.id} -> Get product category")

    category_name = message.text
    category_id = next(category['id'] for category in categories if category['name'] == category_name)
    
    if message.text:
        product["category_id"] = category_id
        currencies_keyboard = types.InlineKeyboardMarkup()

        for currency in currencies:
            currency_button = types.InlineKeyboardButton(text=currency, callback_data=f"currency_{currency}")
            currencies_keyboard.add(currency_button)
        bot.send_message(message.chat.id, "Veuillez choisir la monnaie:", reply_markup=currencies_keyboard)
        
    else:
        bot.send_message(message.chat.id, "La description est requise. Veuillez réessayer.")
        bot.register_next_step_handler(message, choose_category)


@bot.callback_query_handler(func=lambda call: call.data.startswith("currency_"))
def currency_handler(call):
    data_parts = call.data.split("_")
    currency_name = data_parts[1]

    product["currency"] = currency_name

    bot.send_message(call.message.chat.id, "Veuillez envoyer une photo:")
    bot.register_next_step_handler(call.message, get_product_image)


def get_product_image(message):
    print(f"{message.chat.id} -> Get product image")
    if message.photo:

        file_id = message.photo[-1].file_id
        #print(file_id)
        file_info = bot.get_file(file_id)
        #print(file_info)

        file_path_normalized = file_info.file_path.replace('\\', '/')
        file_name = f"{str(uuid.uuid4())}_{file_path_normalized.split('/')[-1]}"
        downloaded_file = bot.download_file(file_info.file_path)

        FILE_PATH = "medias/"

        file_path = os.path.join(FILE_PATH, file_name)
        with open(file_path, "wb") as file:
            file.write(downloaded_file)
        
        product["image"] = upload_file(file_path)

        print(product)

        # call api to save announcement
        status, response = create_product(product, message.chat.id)
        print(response)

        if status == 200:
            message_text = f"{response['name']} ({response['stock']})\n\n"
            message_text += f"Prix: {response['price']} {response['currency']}\n\n"
            message_text += f"{response['description']}\n\n"
            message_text += "✅ Votre produit a été enregistrée avec succès. Merci!"
            
            print(f"{message.chat.id}: Product with {response['id']} created")

            bot.send_photo(message.chat.id, response["image"], caption=message_text)
        else:
            bot.send_message(message.chat.id, "Une erreur s'est produite. Veuillez réessayez")

    else:
        bot.send_message(message.chat.id, "Veuillez envoyer une photo.")
        bot.register_next_step_handler(message, get_product_image)


# Effectuer une recherche
@bot.message_handler(commands=['search'])
def start_search(message):
    print(f"{message.chat.id}: Start search")
    bot.send_message(message.chat.id, "Veuillez entrer le nom du produit:")
    bot.register_next_step_handler(message, get_search_query)

def get_search_query(message):
    print(f"{message.chat.id} -> Get search term query")
    if message.text:
        status, response = search_item(message.text, message.chat.id)
        
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



# Démarrer le bot
bot.polling()

print("Server is shutting down ...")
