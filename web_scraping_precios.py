#libreries
from bs4 import BeautifulSoup
import requests
import mysql.connector
import time
#functions
def tiempo():
    a=time.localtime()
    horas=str(a[3])
    minutos=str(a[4])
    if int(horas)<10:
        horas="0"+horas
    if int(minutos)<10:
        minutos="0"+minutos
    tiempoactual=("{}/{}/{}---{}:{}".format(a[2],a[1],a[0],horas,minutos))
    return tiempoactual
def clean(num):
    num=(num.replace("$","")).replace(".","")
    a=num.split(",")
    num=a[0]
    return num

def search(url, tag, tagname):
    title=None
    try:
        get = requests.get(url)
        content = get.content
        html = BeautifulSoup(content, "html.parser")
        price = html.find(tag, class_=tagname)


        if price is not None:
            price = price.text
            price=int(clean(price))
            title=html.find("h1")
            title=(title.text).strip()
        else:
            print(f"the element was not find in the url {url}")

    except Exception as e:
        print(f"Error processing the url provieded {url}: {e}")
    
    finally:
        return [title,price,url]
def opnedb():
    db=mysql.connector.connect(
        host="localhost",
        user="root",
        password="agusnacho99",
        database="web_scraping",
        port="3306"
    )
    cursorsql=db.cursor()
    return db,cursorsql



def update_database(db,cursor,list):
    cursor.execute("update data set day=%s ,price=%s where product=%s",(tiempo(),list[1],list[0]))
    db.commit()

def add(db,cursor,list):
    cursor.execute("insert into data (day,product,price,link) values(%s,%s,%s,%s)",(tiempo(),list[0],list[1],list[2]))
    db.commit() 
    

def is_cheaper(db,cursor,list):
    cursor.execute("select  * from data where product=%s",(list[0],))
    results=cursor.fetchone()
    print(list)
    if results is None:
        add(db,cursor,list)
    else:
        if results[3]<list[1]:
            update_database(db,cursor,list)
            print("el precio de {} aumento de {} a {}".format(results[2],results[3],list[1]))
            print("{}-{}-{}-{}-{}".format(results[0],tiempo(),results[2],list[1],list[2]))
            print("\n \n")
        elif results[3]>list[1]:
            update_database(db,cursor,list)
            print("el precio de {} bajo de {} a {}".format(results[2],results[3],list[1]))
            print("{}-{}-{}-{}-{}".format(results[0],tiempo(),results[2],list[1],list[2]))
            print("\n \n")
        else:
            print("{}-{}-{}-{}-{}".format(results[0],results[1],results[2],results[3],results[4]))
            print("\n \n")
#main

urls=[
      "https://www.mercadolibre.com.ar/samsung-galaxy-s21-fe-gris-oscuro-5g-128-gb-6-gb/p/MLA18760754?pdp_filters=category:MLA1055#searchVariation=MLA18760754&position=4&search_layout=stack&type=product&tracking_id=610b1fee-8aca-4bf1-84dc-eac3deed3766",
      "https://articulo.mercadolibre.com.ar/MLA-1263666282-samsung-galaxy-s21-fe-5g-128-gb-lavanda-6-gb-ram-liberado-_JM?searchVariation=175943680648#searchVariation=175943680648&position=5&search_layout=stack&type=item&tracking_id=ec032957-12a0-48b9-b0f1-d322fed9428e",
      "https://tiendaonline.movistar.com.ar/samsung-galaxy-s21-fe-5g.html",
      "https://tiendaonline.movistar.com.ar/samsung-galaxy-s22-5g-con-cargador-inalambrico.html"]
tags={"page1":["span","andes-money-amount__fraction"],"page2":["span","andes-money-amount__fraction"],"page3":["span","price"],"page4":["span","price"]}

db,cursor=opnedb()


cont=0
for i in tags:
    tag,tagname=tags[i]           
    url=urls[cont]
    data=search(url,tag,tagname)
    is_cheaper(db,cursor,data)
    cont+=1

cursor.close()
db.close()