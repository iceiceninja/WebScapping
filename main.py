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
    tables = cursor.fetchall()
    for table in tables:
        if table[0].decode() == tableName:
            return True
        
    return False

# Prints all data within table
def printData(tableName, maxPrice):
    cursor.execute('select * from %s order by CAST(SUBSTR(cost FROM 2) AS FLOAT)' % tableName)

    rows = cursor.fetchall()
    for row in rows:
        price = row[1].replace('$','')
        if float(price) <= float(maxPrice.replace('$', '')):
            print("Name: %-120s Price: %-10s" % (row[0], row[1]))
            print('===========================================================')
            
def printThree(tableName, maxPrice):
    print()
    print("%s's top three choices:" % tableName)
    print()
    cursor.execute('select * from %s order by CAST(SUBSTR(cost FROM 2) AS FLOAT) desc LIMIT 3' % tableName)

    rows = cursor.fetchall()
    for row in rows:
        price = row[1].replace('$','')
        if float(price) <= float(maxPrice.replace('$', '')):
            print("Name: %-120s Price: %-10s" % (row[0], row[1]))
            print('===========================================================')
            
def main():
    print("Hello! Welcome to Josh's Cheapskate Food Picker (JCFP).")
    maxPrice = input("How much do you want to spend? (Default is $15) ")
    resturant = input("Where do you want to eat? ")
    if maxPrice == '': #sets default value if no value is entered
        maxPrice = '$15'
    if resturant == '':
        #If no restuarant is specified it prints the top three options from each restraunt 
        #that we have a database for, eventually restricted by distance from location
        cursor.execute('show tables')
        tables = cursor.fetchall()
        for table in tables:
            #printThree(table[0], maxPrice)
            splitTuple = str(table).split("'")
            printThree(splitTuple[1], maxPrice)
    else:
        if not doesTableExist(resturant):#You can replace all refrences of restraunt with sys.argv[1] to have it all in one command   
            print(resturant)
            # Grab menu of requested resturant
            URL = "https://www.fastfoodmenuprices.com/%s-prices" % (restraunt)
            response = requests.get(URL)

            # Creates table for resturant with fields for the name and price of type string
            cursor.execute('create table %s(foodName varchar(255), cost varchar(255))' % resturant)

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
                        cursor.execute('insert into %s(foodName, cost) values("%s", "%s")' % (resturant, name, price))
                        database.commit()

                except AttributeError:
                    continue
            printData(resturant, maxPrice)#sys.argv[1]

        else:
            printData(resturant, maxPrice)#sys.argv[1]

main()