# AnaliseTwitter

Esse projeto tem como objetivo a criação de um relatório capaz de apresentar dados diários sobre assuntos em alta no twitter e emoções expressas em textos relacionados aos mesmos.

O projeto consiste em duas partas:

Parte 1 - Python

Foi montado um robô com python capaz de minerar dados do twitter e subi-los em um banco de dados do microsoft Azure processados em formato tabular. O robô basicamente adquire os textos, os assuntos dos mesmos, quantidades de compartilhamentos, favoritos, comentarios, data de publicação e imagens contidas em conjunto do texto, subindo então essas informações em formato tabular ao banco de dados.

Parte 2 - PowerBi

Uma vez no banco de dados são chamados por consulta atrvés de um arquivo powerbi que se utiliza de apis de serviços cognitivos da Azure para fazer uma análise dos sentimentos dos textos e então exibir os assuntos em alta e os sentimentos dos usuarios, favoritos, compartilhamentos, entre outras informações de cada um. Assim é criado um relatório capaz de exibir em tempo real essas informações se o robô em python estiver 24 horas dentro de uma virtual machine subindo informações no banco de dados.