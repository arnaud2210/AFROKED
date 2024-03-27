from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging

# Remplacez "VOTRE_TOKEN" par le véritable token de votre bot Telegram
TOKEN = "7003324615:AAGSf1JmzWi6nOUYBAm9zvYZlF0HwgxLrE4"

# Définir les états pour le gestionnaire de conversation
PRODUCTS, VIEW_PRODUCT, ADD_TO_CART, VIEW_CART, CHECKOUT = range(5)

# Base de données fictive pour les produits (simulant la récupération depuis la base de données)
products_db = {
    501: {"id": 501, "name": "Product A", "description": "Description of Product A", "price": 19.99, "image_url": "https://www.google.com/imgres?imgurl=https%3A%2F%2Fphotos6.spartoo.ch%2Fphotos%2F188%2F18806709%2F18806709_500_A.jpg&tbnid=1uHWNR1DIoI-FM&vet=12ahUKEwiLvY6creKEAxWOAfsDHTZEBaQQMygDegQIARB3..i&imgrefurl=https%3A%2F%2Ffr.spartoo.ch%2FHavaianas-ESPADRILLE-ECO-x18806709.php&docid=5LwH_fbCvw6rjM&w=500&h=500&q=espadrille&client=firefox-b-d&ved=2ahUKEwiLvY6creKEAxWOAfsDHTZEBaQQMygDegQIARB3"},
    502: {"id": 502, "name": "Product B", "description": "Description of Product B", "price": 29.99, "image_url": "https://www.google.com/imgres?imgurl=https%3A%2F%2Fphotos6.spartoo.ch%2Fphotos%2F188%2F18806708%2F18806708_500_A.jpg&tbnid=8V7RV0T_rZDIZM&vet=10CB0QMyjeAWoXChMI4Leena3ihAMVAAAAAB0AAAAAEAo..i&imgrefurl=https%3A%2F%2Ffr.spartoo.ch%2FHavaianas-ESPADRILLE-ECO-x18806708.php&docid=mPbIpcFt--Br3M&w=500&h=500&itg=1&q=espadrille&client=firefox-b-d&ved=0CB0QMyjeAWoXChMI4Leena3ihAMVAAAAAB0AAAAAEAo"},
    503: {"id": 503,"name": "Product C", "description": "Description of Product C", "price": 9.99, "image_url": "https://www.google.com/imgres?imgurl=https%3A%2F%2Fstatic.kiabi.com%2Fimages%2Fespadrille-en-toile-bleu-navy-xh450_1_frb1.jpg&tbnid=xB7T1Elsarg1HM&vet=10CBEQMyjAAmoXChMI4Leena3ihAMVAAAAAB0AAAAAEBw..i&imgrefurl=https%3A%2F%2Fwww.kiabi.com%2Fespadrille-en-toile-bleu-navy_P641687C641688&docid=NmSi4T10Xhb25M&w=810&h=1080&q=espadrille&client=firefox-b-d&ved=0CBEQMyjAAmoXChMI4Leena3ihAMVAAAAAB0AAAAAEBw"},
}

# Utilisateurs fictifs (simulant la récupération depuis la base de données)
users_db = {
    101: {"id": 101, "cart": {}, "preferences": set()},
}

# Commande pour démarrer le bot
async def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    print(user_id)
    if user_id not in users_db:
        users_db[user_id] = {"cart": {}, "preferences": set()}
    context.user_data["cart"] = users_db[user_id]["cart"]
    context.user_data["preferences"] = users_db[user_id]["preferences"]
    await update.message.reply_text("Bienvenue dans notre boutique en ligne !")
    return PRODUCTS

# Afficher les produits disponibles
async def show_products(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [
            InlineKeyboardButton(product["name"], callback_data=str(product_id))
            for product_id, product in products_db.items()
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Voici nos produits :", reply_markup=reply_markup)
    return VIEW_PRODUCT

# Afficher les détails d'un produit avec une image
async def view_product(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    product_id = int(query.data)
    product = products_db[product_id]
    context.user_data["current_product"] = product
    """
    await query.edit_message_media(
        media=product["image_url"],
        #caption=f"{product['name']}\n\n{product['description']}\n\nPrix : {product['price']} €",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Ajouter au panier", callback_data='add_to_cart')],
                [InlineKeyboardButton("Liker", callback_data='like_product')],
            ]
        ),
    )"""
    await query.edit_message_text(
        text=f"{product['name']}\n\n{product['description']}\n\nPrix : {product['price']} €\n\n[Image]({product['image_url']})",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Ajouter au panier", callback_data='add_to_cart')],
                [InlineKeyboardButton("Liker", callback_data='like_product')],
            ]
        ),
    )
    return ADD_TO_CART

# Ajouter un produit au panier
async def add_to_cart(update: Update, context: CallbackContext) -> int:
    product = context.user_data["current_product"]
    user_id = update.callback_query.from_user.id
    if product["id"] not in context.user_data.get("cart",{}):
        context.user_data["cart"][product["id"]] = {"quantity": 0, "price": product["price"]}
    context.user_data["cart"][product["id"]]["quantity"] += 1
    print(context.user_data.get("cart",{}))
    await update.callback_query.edit_message_text(f"{product['name']} ajouté au panier !")
    return VIEW_PRODUCT

# Liker un produit
"""async def like_product(update: Update, context: CallbackContext) -> int:
    product = context.user_data["current_product"]
    user_id = update.callback_query.from_user.id
    context.user_data["preferences"].add(product["id"])
    await update.callback_query.edit_message_text(f"{product['name']} ajouté à vos préférences !")
    return VIEW_PRODUCT"""

async def like_product(update: Update, context: CallbackContext) -> int:
    product = context.user_data["current_product"]
    if product:
        user_id = update.callback_query.from_user.id
        preferences = context.user_data.setdefault("preferences", set())
        preferences.add(product.get("id"))
        print(preferences)
        await update.callback_query.edit_message_text(f"{product.get('name')} ajouté à vos préférences !")
    return VIEW_PRODUCT


# Visualiser le panier
"""async def view_cart(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    product = context.user_data["current_product"]
    cart = context.user_data["cart"]
    if not cart:
        await update.message.reply_text("Votre panier est vide.")
    else:
        total_price = sum(item["quantity"] * item["price"] for item in cart.values())
        cart_text = "\n".join(
            [
                f"{product['name']} x{item['quantity']} - {item['quantity'] * item['price']} €"
                for product_id, item in cart.items()
            ]
        )
        await update.message.reply_text(
            f"Votre panier :\n{cart_text}\n\nTotal : {total_price} €",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Passer la commande", callback_data='checkout')]]),
        )
    return VIEW_CART"""


async def view_cart(update: Update, context: CallbackContext) -> int:
    print("Entering view_cart")
    user_id = update.message.from_user.id
    cart = context.user_data.get("cart", {})
    
    if not cart:
        update.message.reply_text("Votre panier est vide.")
    else:
        total_price = 0
        cart_text = ""

        for product_id, item in cart.items():
            product = products_db.get(product_id)
            print(product, "ok")
            if product:
                product_name = product.get("name")
                quantity = item.get("quantity")
                subtotal = item.get("quantity") * item.get("price")
                total_price += subtotal

                cart_text += f"{product_name} x{quantity} - {subtotal} €\n"

        await update.message.reply_text(
            f"Votre panier :\n{cart_text}\n\nTotal : {total_price} €",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Passer la commande", callback_data='checkout')]]),
        )

    return CHECKOUT


# Passer une commande
async def checkout(update: Update, context: CallbackContext) -> int:
    print("Entering checkout")
    user_id = update.message.from_user.id
    cart = context.user_data["cart"]
    total_price = sum(item["quantity"] * item["price"] for item in cart.values())
    # Simuler le processus de commande (dans un système réel, vous intégreriez le traitement des commandes ici)
    await update.message.reply_text(f"Commande passée avec succès !\nTotal : {total_price} €")
    # Réinitialiser le panier
    context.user_data["cart"] = {}
    return VIEW_CART


# Annuler les commandes
async def cancel(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    context.user_data.clear()  # Réinitialiser toutes les données utilisateur
    await update.message.reply_text("La commande a été annulée. La conversation a été réinitialisée.")
    
    # Retourner à l'état initial (par exemple, PRODUCTS)
    return PRODUCTS
    

# Gestionnaire de conversation
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        PRODUCTS: [CommandHandler('products', show_products)],
        VIEW_PRODUCT: [CallbackQueryHandler(view_product)],
        ADD_TO_CART: [CallbackQueryHandler(add_to_cart), CallbackQueryHandler(like_product)],
        VIEW_CART: [CommandHandler('cart', view_cart)],
        CHECKOUT: [MessageHandler(filters.Regex('^Passer la commande$'), checkout)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    dp = Application.builder().token(TOKEN).build()
    dp.add_handler(conv_handler)

    # Démarrer le bot
    dp.run_polling()


if __name__ == '__main__':
    main()
