from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from datetime import datetime
import pyodbc
import numpy as np
from string_functions import string_to_int,stopwords
from bd_functions import inseri_tweets,inseri_imgs,normaliza_tweets

def minerar(driver,promovido,hora,palavra,xpath_element,sub_xpath_path,sub_xpath_img):#minera todos os tweets presentes na tela
	tweets = []
	elements = driver.find_elements_by_xpath(xpath_element)#coleta tweets pelo xpath deles
	for e in elements:#para cada tweet coleta as informacoes
		spans = e.find_elements_by_xpath(sub_xpath_path)

		try:
			favorites = string_to_int(spans[len(spans) - 1].text if len(spans) > 0 else "")
		except Exception:
			favorites = 0
		try:
			retweets = string_to_int(spans[len(spans) - 3].text if len(spans) > 0 else "")
		except Exception:
			retweets = 0
		try:
			coments = string_to_int(spans[len(spans) - 5].text if len(spans) > 0 else "")
		except Exception:
			coments = 0
		try: 
			imgs = e.find_elements_by_xpath(sub_xpath_img)
			imgs_links = [img.get_attribute("src") for img in imgs]
		except Exception:
			imgs_links = []

		if favorites == "" and retweets == "" and coments =="" and e.text == palavra:
			continue

		tweets+=[{
		"pesquisa":palavra,
		"promovido":promovido,
		"text":e.text,
		"favorites":favorites,
		"retweets":retweets,
		"coments":coments,
		"imgs_links":imgs_links,
		"data_extracao":hora
		}]
	return tweets

    
    
    
def coleta_palavra(driver,palavra,promovido,hora):#da palavra que representa um trend coletará tweets relacionados com a palavra
	print("iniciando pesquisa: ",palavra)
	#estabelecemos o link para pesquisa o xpath da barra de pesquisa
	explore_link = "https://twitter.com/explore"
	xpath_search = '//*[@id="react-root"]/div/div/div[2]/header/div[2]/div[1]/div[1]/div/div[2]/div/div/div/form/div[1]/div/div/div[2]/input'
	#precisamos de um termo da palavra que não é uma stopword para estabelecer o xpath dos tweets
	pos = 0
	termo = palavra.split(" ")[pos]
	while termo in stopwords():
		termo = palavra.split(" ")[pos]
		pos += 1

	#xpath dos tweets muda de acordo com palavra ser uma hashtag ou não
	if "#" in palavra:
		xpath_element = "//a[contains( translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),     '" + termo.lower() + "'   )]/parent::span/parent::div"
	else:
		xpath_element = "//span[contains( translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),     '" + termo.lower() + "'   )]/parent::div"

	#temos um sub xpath para as metricas do tweet e outro para as imagens
	sub_xpath_path = "./parent::div/parent::div//span"
	sub_xpath_img = "./parent::div/parent::div//img"
	
	#entramos no link
	driver.get(explore_link)
	time.sleep(5)

	#definimos a barra de pesquisa e pesquisamos a palavra
	search = driver.find_element_by_xpath(xpath_search)
	search.send_keys(palavra)
	search.send_keys(Keys.ENTER)
	time.sleep(2)

	#definimos o body
	body = driver.find_element_by_tag_name('body')

	#colocaremos os tweets nesse array
	tweets = []

	for i in range(0,40):#repetiremos esse processo algumas vezes de forma reduntante para garantir que coletemos o maximo de tweets possivel
		print("processo - ",i)
		#coletamos tweets se houver erro tentamos novamente após 5 segundos
		try:
			tweets += minerar(driver,promovido,hora,palavra,xpath_element,sub_xpath_path,sub_xpath_img)
		except Exception:
			time.sleep(5)
			tweets += minerar(driver,promovido,hora,palavra,xpath_element,sub_xpath_path,sub_xpath_img)
		#descemos na página
		for d in range(0,50):
			body.send_keys(Keys.DOWN)

	return tweets
    

def init():#inicia processo de coletar tweets relacionados com os treends do momento
	print("iniciando")
	#iniciando driver
	driver = webdriver.Chrome("C:/Users/brunostorer/Desktop/Analise_Tweets/chromedriver.exe")

	try:

		#acessando trends
		link_trends = "https://twitter.com/i/trends"

		driver.get(link_trends)

		time.sleep(5)

		#coletando trends no momento

		#coleta textos das trends e assuntos promovidos
		xpath_trends = '//span[contains(text(),"Trending")]/parent::div/parent::div/parent::div/div[2]'

		trends = driver.find_elements_by_xpath(xpath_trends)

		trends_texts = []
		for t in trends:
		    if len(t.text) > 0:
		        trends_texts += [{"text":t.text,
		        					"promoted":t.find_element_by_xpath("./parent::div//span[contains(text(),'Trending')]").text}]
		print("TRENDING:",trends_texts)


		#coletando informações 

		tweets = []

		hora = datetime.today().strftime('%Y-%m-%d %H:%M:%S') #hora da atividade

		#para cada trend iremos coletar uma quantia generosa de tweets relacionados
		for text_trend in trends_texts:
			text = text_trend["text"]
			promovido = text_trend["promoted"]
			tweets += coleta_palavra(driver,text,promovido,hora)

		driver.close()
			
		

		#normalizaremos a base e deletamos duplicatas
		df_tweets = pd.DataFrame(tweets).drop_duplicates(["text"])
		tweets,imgs = normaliza_tweets(df_tweets)

		#inserimos bases normalizadas no banco de dados da azure
		inseri_tweets(tweets)
		inseri_imgs(imgs)
		print("finalizado")
		
	except Exception as e:
		driver.close()
		raise e