#Aqui estão funções para interagir com banco de dados da azure

from datetime import datetime
import pyodbc
import time
import pandas as pd
import numpy as np
import uuid


def credenciais():#adquire credenciais para acessar twitter
	credenciais = pd.read_json("credenciais.json",orient = "index").transpose()
	server = credenciais["server"].tolist()[0]
	database = credenciais["database"].tolist()[0]
	username = credenciais["username"].tolist()[0]
	password = credenciais["password"].tolist()[0]
	driver = credenciais["driver"].tolist()[0]

	return server,database,username,password,driver

def inseri_tweets(tweets):#insere informações na tabela tweets
	server,database,username,password,driver = credenciais()
	cnxn = pyodbc.connect('DRIVER='+str(driver)+';SERVER='+str(server)+';DATABASE='+str(database)+';PORT=1433;UID='+str(username)+';PWD='+ str(password))
	cursor = cnxn.cursor()

	for row in tweets.iterrows():
		row = row[1]
		dados = (row["pesquisa"],row["promovido"],row["text"].replace("'",""),row["favorites"],row["retweets"],row["coments"],row["imgs_id"], row["data_extracao"])
		cursor.execute("INSERT INTO tweets(pesquisa,promovido,text,favorites,retweets,coments,imgs_id, data_extracao) VALUES ('%s','%s','%s',%s,%s,%s,'%s','%s')" % dados)
		cursor.commit()

	cursor.close()

def inseri_imgs(imgs):#insere informações na tabela imgs
	server,database,username,password,driver = credenciais()

	cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';PORT=1433;UID='+username+';PWD='+ password)
	cursor = cnxn.cursor()
	
	for row in imgs.iterrows():
		row = row[1]
		dados = (row["id"],row["img1"],row["img2"], row["img3"])
		cursor.execute("INSERT INTO imgs(id,img1,img2,img3) VALUES ('%s','%s','%s','%s')" % dados)
		cursor.commit()
	cursor.close()

#função que pesquisa trend e coleta tweets dela

def normaliza_tweets(tweets):#coleta a tabela tweets e normaliza ela retirnando informações de imagens dela e criando uma segunda tabela para imagens, no fim retorna a tweets normalizado com a imgs normalizada
	imgs = []
	novo_tweets = []
	for row in tweets.iterrows():
		row = row[1]
		if len(row["imgs_links"]) <= 0:
			novo_tweets+=[{
			"pesquisa":row["pesquisa"],
			"promovido":row["promovido"],
			"text":row["text"],
			"favorites":row["favorites"],
			"retweets":row["retweets"],
			"coments":row["coments"],
			"imgs_id":0,
			"data_extracao":row["data_extracao"]
			}]
			continue

		try:
			img1 = row["imgs_links"][0]
		except Exception:
			img1 = ""

		try:
			img2 = row["imgs_links"][1]
		except Exception:
			img2 = ""

		try:
			img3 = row["imgs_links"][2]
		except Exception:
			img3 = ""

		row_id = str(uuid.uuid4())

		imgs += [{
		"id" : row_id,
		"img1": img1,
		"img2":img2,
		"img3":img3
		}]

		novo_tweets+=[{
		"pesquisa":row["pesquisa"],
		"promovido":row["promovido"],
		"text":row["text"],
		"favorites":row["favorites"],
		"retweets":row["retweets"],
		"coments":row["coments"],
		"imgs_id":row_id,
		"data_extracao":row["data_extracao"]
		}]


	imgs = pd.DataFrame(imgs)
	novo_tweets = pd.DataFrame(novo_tweets)

	return novo_tweets,imgs


