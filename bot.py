import time
import schedule
import requests
import telegram
from telegram import ParseMode


def telegram_bot_send_message(bot_message):
    bot = telegram.Bot('<TOKEN>') # Telegram Bot Authorization Token
    bot_chatID = bot.get_updates()[0].message.chat_id
    bot.sendMessage(bot_chatID, bot_message, parse_mode=ParseMode.HTML)

def notify():
    your_wishlist = get_wishlist('<STEAM_USER_ID>') # Steam User ID
    games_on_sale = get_games_on_sale(your_wishlist)
    # If there is a game in Wishlist with discount 50% Off or more, sends game sale info to user
    if len(games_on_sale) > 0:
        games_on_sale_short = shorten_sale_info(games_on_sale)
        title = "<b>The games on your Wishlist are on sale (50% Off or more):</b> \n"
        bot_message = title + "\n".join(games_on_sale_short)
    else:
        bot_message = "Oops. Sorry, today there is no sale for the games on your wishlist."
    telegram_bot_send_message(bot_message)

# Gets wishlist with Steam API
def get_wishlist(steam_user_id):
    wishlist_endpoint = 'https://store.steampowered.com/wishlist/id/' + steam_user_id + '/wishlistdata/'
    wishlist = requests.get(wishlist_endpoint).json() 
    return wishlist

# Gets which games are on sale from wishlist
def get_games_on_sale(wishlist):    
    games_on_sale = []
    for appid in wishlist:
        app_details_endpoint = 'https://store.steampowered.com/api/appdetails?appids=' + appid
        app_details = requests.get(app_details_endpoint).json()
        app = app_details[appid]['data']
        if app['is_free'] == False:
            discount_percent = app['price_overview']['discount_percent']
            if discount_percent >= 50:
                games_on_sale.append(app)
    return games_on_sale

def shorten_sale_info(games_on_sale):
    games_info_short = []
    for game in games_on_sale:
        games_info_short.append(game['name']  + ' - Discount: ' + str(game['price_overview']['discount_percent']) +
            '% - Price: ' + game['price_overview']['final_formatted'])
    return games_info_short


def main():
    schedule.every().day.at("12:00").do(notify)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()