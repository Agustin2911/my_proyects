#sistema de control de stock
#bibliotecas
import time 
import mysql.connector
#funciones
def actualizar(base,cursor):
    tiempo=time.localtime()
    mes=tiempo[1]
    dias=tiempo[2]
    minutos=tiempo[4]
    horas=tiempo[3]
    mes=tiempocorrecto(mes)
    dias=tiempocorrecto(dias)
    horas=tiempocorrecto(horas)
    minutos=tiempocorrecto(minutos)
    actual=int(str(tiempo[0])+mes+dias+horas+minutos)
    cursor.execute("select * from actualizaciones where fecha<=%s",(actual,))
    resultado=cursor.fetchall()
    for i in resultado:
        info=existe(cursor,i[1],i[4])
        sumarinventario(base,cursor,info,i[2])
        cursor.execute("DELETE FROM actualizaciones where id=%s",(i[0],))
        base.commit()
    cursor.execute("select * from salidas where fecha<=%s",(actual,))
    resultado=cursor.fetchall()
    for i in resultado:
        info=existe(cursor,i[1],i[4])
        restarinventario(base,cursor,info,i[2])
        cursor.execute("DELETE FROM salidas where id=%s",(i[0],))
        base.commit()

    
def vencida(tiemposoli):
    tiemposoli = int(tiemposoli)
    tiempo=time.localtime()
    mes=tiempo[1]
    dias=tiempo[2]
    minutos=tiempo[4]
    horas=tiempo[3]
    mes=tiempocorrecto(mes)
    dias=tiempocorrecto(dias)
    horas=tiempocorrecto(horas)
    minutos=tiempocorrecto(minutos)
    actual=int(str(tiempo[0])+mes+dias+horas+minutos)
    rf=False
    if actual>=int(tiemposoli):
        rf=True
    return rf

def tiempocorrecto(tiempo):
    if tiempo<10:
        tiempo="0"+str(tiempo)
    else:
        tiempo=str(tiempo)
    return tiempo


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


def agregardatos(base,cursor):
    """Esta funcion sirve para agregar datos al archivo csv. Esta pide como parametros la matriz principal para tener los datos de la ficha de stock
    y luego se puede manejar facilmente y el id por las razones anteriores y para poder agregar datos a la ficha . esta devuelve la matriz y el id """
    seguir = 1

    while seguir== 1:
        producto=input("Ingrese un producto: ")
        cant_unidades=int(input("Ingrese la cantidad de unidades del producto: "))
        valorxunidad=int(input("Ingrese el valor por unidad del producto: "))
        valortotal=valorxunidad*int(cant_unidades)
        sucursal=(input("Ingrese la sucursal donde se encuentra el stock: ").strip()).replace(" ","_")
        observaciones=input("Observaciones del producto: ").replace(" ","_")
        horadeentrada=tiempo()
        reponer = "no" if cant_unidades > 5 else "si"
        cursor.execute("insert into ficha_de_stock(producto,stock,valorporunidad,total,sucursal,stocksucursal,descripcion,ultimoingreso,reponer) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",(producto,cant_unidades,valorxunidad,valortotal,sucursal,cant_unidades,observaciones,horadeentrada,reponer))
        base.commit()
        seguir=int(input("Desea seguir agregando productos a la ficha? \n 1 = Si \n 0 = No \nSeguir: "))
        while seguir != 1 and seguir != 0:
            print("respuesta incorrecta")
            seguir=int(input("Desea seguir agregando productos a la ficha? \n Si = 1 \n No = 0 \n Seguir: "))

def existe(cursor,producto,sucursal):
    cursor.execute("SELECT * FROM ficha_de_stock WHERE producto = %s and sucursal= %s", (producto,sucursal))
    resultado = cursor.fetchone()
    while resultado is None:
        print("El producto no existe o no se encuentra en esa sucursal.")
        producto = input("Ingrese el producto a modificar: ")
        sucursal=input("ingrese la sucursal donde se encuentra el producto: ")
        cursor.execute("SELECT * FROM ficha_de_stock WHERE producto = %s and sucursal= %s", (producto,sucursal))
        resultado = cursor.fetchone()
    return resultado

def sumarinventario(base,cursor,resultado,nuevoinv):
    unidades = resultado[2] + nuevoinv
    total = unidades * resultado[3]
    ingreso = tiempo()
    reponer = "no" if unidades > 5 else "si"

    cursor.execute("UPDATE ficha_de_stock SET stock = %s, total = %s, stocksucursal = %s, ultimoingreso = %s, reponer = %s WHERE id = %s",(unidades, total, unidades, ingreso, reponer, resultado[0]))
    base.commit()

def restarinventario(base,cursor, resultado,unidadessalientes):
    resta= True if resultado[2]-unidadessalientes>=0 else False
    while resta==False:
        print("no hay suficientes unidades para esta salida, la cantidad de unidades disponibles son : {}".format(resultado[2]))
        unidadessalientes=int(input("ingrese la cantidad de unidades que salen: "))
        resta= True if resultado[2]-unidadessalientes>=0 else False
    
    unidades = resultado[2] - unidadessalientes
    total = unidades * resultado[3]
    ingreso = tiempo()
    reponer = "no" if unidades > 5 else "si"

    cursor.execute("UPDATE ficha_de_stock SET stock = %s, total = %s, stocksucursal = %s, ultimoingreso = %s, reponer = %s WHERE id = %s",(unidades, total, unidades, ingreso, reponer, resultado[0]))
    base.commit()
    
def verficha(cursor):
    cursor.execute("select * from ficha_de_stock")
    resultados=cursor.fetchall()
    for i in resultados:
        print("{} | {} | {} | {} | {} | {} | {} | {} | {} | {}".format(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9]))

def areponer(cursor):
    cursor.execute("select * from ficha_de_stock where reponer='si'")
    resultados=cursor.fetchall()
    for i in resultados:
        print("{} | {} | {} | {} | {} | {} | {} | {} | {} | {}".format(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9]))

def segunsucursal(cursor,s):
    cursor.execute("select * from ficha_de_stock where sucursal=%s",(s,))
    resultados=cursor.fetchall()
    for i in resultados:
        print("{} | {} | {} | {} | {} | {} | {} | {} | {} | {}".format(i[0],i[1],i[2],i[3],i[4],i[5],i[6],i[7],i[8],i[9]))

def total(cursor):
    cursor.execute("select total from ficha_de_stock")
    resultados=cursor.fetchall()
    total=0
    for i in resultados:
        total+=i[0]
    print("este es el total de toda la ficha {}".format(total))


def solicitud(cursor,base,resultado,cantidad,fecha,sucursal):
    cursor.execute("insert into actualizaciones (producto,cantidad,fecha,sucursal) values(%s,%s,%s,%s)",(resultado[1],cantidad,fecha,sucursal))
    base.commit()
    print("se ha guardado el futuro ingreso")

def solicitud2(cursor,base,resultado,cantidad,fecha,sucursal):
    cursor.execute("insert into salidas (producto,cantidad,fecha,sucursal) values(%s,%s,%s,%s)",(resultado[1],cantidad,fecha,sucursal))
    base.commit()
    print("se ha guardado el futuro ingreso")


def suficiente(cursor,producto,sucursal,cantidad):
    cursor.execute("select stock from ficha_de_stock where producto=%s and sucursal=%s",(producto,sucursal))
    resultado=cursor.fetchone()
    return True if resultado[0]-cantidad>=0 else False

def eliminar(base,cursor,producto,sucursal):
    cursor.execute("select id from ficha_de_stock where producto=%s and sucursal= %s",(producto,sucursal))
    resultado=cursor.fetchone()
    cursor.execute("delete from ficha_de_stock where id=%s",(resultado[0],))
    base.commit()

#programa principal
matrizprincipal=[]
mibasededatos=mysql.connector.connect(
        host="localhost",
        user="root",
        password="agusnacho99",
        database="stock",
        port="3306"
    )
micursor=mibasededatos.cursor()
actualizar(mibasededatos,micursor)
while True: 
    opcion=int(input("Seleccione una de las siguientes opciones: \n 1- Ingresar un producto nuevo.  \n 2- Ingresar una entrada de stock de un producto actual.  \n 3- Ingresar una salida de stock de un producto actual. \n 4- Crear un futuro ingreso. \n 5- Ver el total de la ficha. \n 6- Ver la ficha completa. \n 7- Ver los productos a reponer \n 8-filtrar productos segun la sucursal \n 9-generar una futura salida. \n 10-eliminar producto. \n 11- Terminar los cambios. \n Seleccione: "))
    while opcion not in [1,2,3,4,5,6,7,8,9,10,11]: 
            print("Opcion no valida!")
            opcion=int(input("Seleccione una de las siguientes opciones: \n 1- Ingresar un producto nuevo.  \n 2- Ingresar una entrada de stock de un producto actual.  \n 3- Ingresar una salida de stock de un producto actual. \n 4- Crear un futuro ingreso. \n 5- Ver el total de la ficha. \n 6- Ver la ficha completa. \n 7- Ver los productos a reponer \n 8-filtrar productos segun la sucursal \n 9-generar una futura salida. \n 10-eliminar producto. \n 11- Terminar los cambios. \n Seleccione: "))
    if opcion==1: 
        agregardatos(mibasededatos,micursor)
    elif opcion ==2:
        producto=(input("ingrese el producto a modificar: ")).strip()
        sucursal=input("ingrese la sucursal donde se encuentra el producto: ").strip()
        resultado=existe(micursor,producto,sucursal)
        nuevoinv = int(input("Ingrese la cantidad de nuevas unidades: "))
        sumarinventario(mibasededatos,micursor,resultado,nuevoinv)
    elif opcion ==3:
        producto=(input("ingrese el producto a modificar: ")).strip()
        sucursal=input("ingrese la sucursal donde se encuentra el producto: ").strip()
        resultado=existe(micursor,producto,sucursal)
        unidadessalientes=int(input("ingrese la cantidad de unidades que salen: "))
        restarinventario(mibasededatos,micursor,resultado)
    elif opcion ==4:
        producto=input(("ingrese el producto que se le va a crear un futuro ingreso:: ")).strip()
        sucursal=(input("ingrese la sucursal donde se encuentra el producto: ")).strip()
        resultado=existe(micursor,producto,sucursal)
        cantidad=int(input("Ingrese la cantidad de nuevas unidades de este producto: "))
        fecha=input("Ingrese la fecha del futuro ingreso. (Por ejemplo: 2018 10 8---> año/mes/dia) \n Fecha: ")
        fecha=(fecha+input("Ingrese la hora de entrada del siguiente producto (Por ejemplo 15 32---> hora/minutos) \n Hora: ")).replace(" ","")
        solicitud(micursor,mibasededatos,resultado,cantidad,fecha,sucursal)
    elif opcion ==5:
        total(micursor)
    elif opcion ==6:
        verficha(micursor)
    elif opcion ==7:
        areponer(micursor)
    elif opcion ==8:
        sucursal=input("ingrese la sucursal de la cual quiere ver su mercaderia: ")
        segunsucursal(micursor,sucursal)
    elif opcion==9:
        producto=(input("ingrese el producto que se le va a crear una futura salida:: ")).strip()
        sucursal=(input("ingrese la sucursal donde se encuentra el producto: ")).strip()
        resultado=existe(micursor,producto,sucursal)
        cantidad=int(input("Ingrese la cantidad de unidades que salen de este producto: "))
        ess=suficiente(micursor,producto,sucursal,cantidad)
        while ess==False:
            print("no hay suficientes unidades para esta futura salida")
            cantidad=int(input("Ingrese la cantidad de unidades que salen de este producto: "))
            ess=suficiente(micursor,producto,sucursal,cantidad)
        fecha=input("Ingrese la fecha del futuro ingreso. (Por ejemplo: 2018 10 8---> año/mes/dia) \n Fecha: ")
        fecha=(fecha+input("Ingrese la hora de entrada del siguiente producto (Por ejemplo 15 32---> hora/minutos) \n Hora: ")).replace(" ","")
        solicitud2(micursor,mibasededatos,resultado,cantidad,fecha,sucursal)
    elif opcion ==10:
        producto=(input("seleccione el producto que desea borrar: ")).strip()
        sucursal=(input("seleccione la sucursal en donde se encuentra el producto: ")).strip()
        eliminar(mibasededatos,micursor,producto,sucursal)
    elif opcion==11:
        break

micursor.close()
mibasededatos.close()