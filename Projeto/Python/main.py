#arquivo principal, primeiro que deve ser ativado 

import datetime
from browser_functions import init 
from dateutil.relativedelta import relativedelta

hora = datetime.datetime.strptime('2014-05-06 12:00:00', '%Y-%m-%d %H:%M:%S')

while True:#repete para sempre 

	print("esperando")
	while relativedelta(datetime.datetime.now(), hora).hours < 3:#a função init deve rodar de 3 em 3 horas no máximo
		pass

	hora = datetime.datetime.now()

	try:
		init()
	except Exception as e:
		print("ERRO: ",e)
		hora = datetime.datetime.strptime('2014-05-06 12:00:00', '%Y-%m-%d %H:%M:%S')
		continue






