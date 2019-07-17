import requests
import sqlite3
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
from prettytable import from_db_cursor
from os import system

ALLKEYSHOPURL = 'allkeyshop.com/blog/'
STEAMURL = 'store.steampowered.com/app/'

conn = sqlite3.connect('gamehunter.db')
c = conn.cursor()

class Hunter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_game_record(self, url):
        if ALLKEYSHOPURL.lower() in url.lower():
            r = requests.get(url)
            soup = BeautifulSoup(r.content, 'lxml')
            title = soup.find('span', {'itemprop': 'name'}).text.strip()
            cheapest_row = soup.find('div', {'class': 'offers-table-row'})
            merchant = cheapest_row.find('span', {'class': 'offers-merchant-name'}).text
            price = cheapest_row.find('span', {'itemprop': 'price'})['content']
            return {'title': title, 'merchant': merchant, 'price': price, 'url': url}
        elif STEAMURL.lower() in url.lower():
            currency_payload = {'cc': 'de'}
            r = requests.get(url, params=currency_payload)
            soup = BeautifulSoup(r.content, 'lxml')
            title = soup.find('span', {'itemprop': 'name'}).text.strip()
            price = soup.find('div', {'data-price-final': True})['data-price-final']
            price = price[:-2] + '.' + price[-2:]
            return {'title': title, 'merchant': 'steam', 'price': price, 'url': url}

    def db_add_user(self, user_id, username):
        try:
            with conn:
                c.execute("INSERT INTO users VALUES (:user_id, :username)", {'user_id': user_id, 'username': username})
        except sqlite3.IntegrityError:
            pass

    def db_add_game(self, game_record):
        try:
            with conn:
                c.execute("INSERT INTO games VALUES (:title, :merchant, :price, :url)", game_record)
        except sqlite3.IntegrityError:
            pass

    def db_add_wish(self, user_id, wished_price, url):
        try:
            with conn:
                c.execute("INSERT INTO wishlist VALUES (:user_id, :wished_price, :url)",
                          {'user_id': user_id, 'wished_price': wished_price, 'url': url})
        except sqlite3.IntegrityError:
            print('You already have that on your wishlist!')



    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')


    @commands.command()
    async def addwish(self, ctx, wished_price, *, url):
        game_record = self.get_game_record(url)
        self.db_add_game(game_record)
        self.db_add_user(ctx.author.id, ctx.author.name)
        self.db_add_wish(ctx.author.id, wished_price, url)
        await ctx.send('Game added to wishlist!')



def setup(bot):
    bot.add_cog(Hunter(bot))

# def main():
#     username = input("input your username: ")
#     user_id = input('Input your user_id: ')
#     add_user(user_id, username)
#     while True:
#         print('1. Add new game to watch list')
#         print('2. See your game list')
#         print('3. Exit')
#         user_input = input('Make selection: ')
#         if user_input == '1':
#             url = input('Paste in the url from allkeyshop/steam: ').strip()
#             wished_price = input('Input price that you are willing to pay in euro: ')
#             game_record = get_game_record(url)
#             add_game(game_record)
#             add_wish(user_id, wished_price, url)
#             system('cls')
#         if user_input == '2':
#             system('cls')
#             print_wishlist(get_wish_list(user_id))
#         if user_input == '3':
#             break
#         else:
#             pass
#
#
# def get_game_record(url):
#     if ALLKEYSHOPURL.lower() in url.lower():
#         r = requests.get(url)
#         soup = BeautifulSoup(r.content, 'lxml')
#         title = soup.find('span', {'itemprop': 'name'}).text.strip()
#         cheapest_row = soup.find('div', {'class': 'offers-table-row'})
#         merchant = cheapest_row.find('span', {'class': 'offers-merchant-name'}).text
#         price = cheapest_row.find('span', {'itemprop': 'price'})['content']
#         return {'title': title, 'merchant': merchant, 'price': price, 'url': url}
#     elif STEAMURL.lower() in url.lower():
#         currency_payload = {'cc': 'de'}
#         r = requests.get(url, params=currency_payload)
#         soup = BeautifulSoup(r.content, 'lxml')
#         title = soup.find('span', {'itemprop': 'name'}).text.strip()
#         price = soup.find('div', {'data-price-final': True})['data-price-final']
#         price = price[:-2] + '.' + price[-2:]
#         return {'title': title, 'merchant': 'steam', 'price': price, 'url': url}
#
#
# # probably transform to a decorator when discord api is introduced
# def add_user(user_id, username):
#     try:
#         with conn:
#             c.execute("INSERT INTO users VALUES (:user_id, :username)", {'user_id': user_id,'username': username})
#     except sqlite3.IntegrityError:
#         pass
#
#
# def add_game(game_record):
#     try:
#         with conn:
#             c.execute("INSERT INTO games VALUES (:title, :merchant, :price, :url)", game_record)
#     except sqlite3.IntegrityError:
#         pass
#
#
# def add_wish(user_id, wished_price, url):
#     try:
#         with conn:
#             c.execute("INSERT INTO wishlist VALUES (:user_id, :wished_price, :url)",
#                       {'user_id': user_id, 'wished_price': wished_price, 'url': url})
#     except sqlite3.IntegrityError:
#         print('You already have that on your wishlist!')
#
#
# def get_wish_list(user_id):
#     with conn:
#         return c.execute("""SELECT title, wished_price, price
#         FROM wishlist, games
#         WHERE user_id = :user_id AND wishlist.url = games.url""",
#                   {'user_id': user_id})
#
#         #return c.fetchall()
#
#
# def print_wishlist(wishlist):
#     data = from_db_cursor(wishlist)
#     print(data)
#
#
#
# if __name__ == '__main__':
#     main()
#     conn.close()
