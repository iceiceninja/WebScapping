from bs4 import BeautifulSoup
import requests
import mysql.connector
import sys

# Connect to database
database = mysql.connector.connect(host="localhost", user="iceiceninja", password="", database="food")
cursor = database.cursor()

# Returns if table already exist with said name
def doesTableExist(tableName):
    cursor.execute('show tables')
    for table in cursor:
        if table[0].decode() == tableName:
            return True
        
    return False

# Prints all data within table
def printData(tableName):
    cursor.execute('select * from %s' % tableName)

    for data in cursor:
        print("Name: %-80s Price: %-10s" % (data[0], data[1]))
        print("===")

def main():

    if not doesTableExist(sys.argv[1]):    

        # Grab menu of requested resturant
        URL = "https://www.fastfoodmenuprices.com/%s-prices" % (sys.argv[1])
        response = requests.get(URL)

        # Creates table for resturant with fields for the name and price of type string
        cursor.execute('create table %s(foodName varchar(255), cost varchar(255))' % sys.argv[1])

        # Parse through html to find table of foods and prices
        html = BeautifulSoup(response.text, 'html.parser')
        rows = html.find_all('tr')

        # Get name and price of each item
        for i in range(2, len(rows)):

            try:
                name = rows[i].find('td', {"class": "column-1"}).text
                price = rows[i].find('span').text

                # If item has a price insert it into the table
                if price:
                    cursor.execute('insert into %s(foodName, cost) values("%s", "%s")' % (sys.argv[1], name, price))
                    database.commit()

            except AttributeError:
                continue

        printData(sys.argv[1])

    else:
        printData(sys.argv[1])

main()