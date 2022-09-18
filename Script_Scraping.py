# -*- coding: utf-8 -*-
"""
Created on Tue May 25 01:04:14 2021

@author: belha
"""
#Importation
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as pyplot
from bs4 import BeautifulSoup
from time import time, sleep
from warnings import warn
from IPython.core.display import clear_output
import re


##Scraping de données
#Nécessaire pour timer
%timeit
debut= time()
clear_output(wait = True)
warn("Scraping en cours")
sleep(1)

#Variable de comptage
page_scrap=0
film_scrap_total=0


#Je commence par créer un fichier data1 qui prends la structure de mon fichier final et je mets des "None" à chaque variable sinon je au moment de scrapper les données peuvent être décalés en cas de valeurs manquantes
data1 = {'Film' : None,'Note' : None,'Score' : None,'N_Votes' : None,'Durée' : None,'Type' : None,'Sortie' : None,'Date de sortie' : None,'Budget' : None,'Pays' : None,
                'Revenus Générés le premier W-E aux USA' : None,'Revenus Générés aux USA' : None,'Revenus Générés dans le Monde' : None, 'Sound Mix' : None,'Color' : None,'Aspect_ratio' : None}

#data2 me sert de temporaire pour chaque film
data2= []

#data3 représente mon fichier de stockage
data3 = []

#dataf représente le fichier final qui sera un dataframe
dataf=[]





#J'appelle "elem" le premier élément de chaque page étant donné qu'il y a 50 films par page, la boucle parcours tout les éléments avec un pas de 50
#De plus pour pouvoir concaténer ce nombre avec mon url je le mets en "str"
elem = [str(i) for i in range(1,13100,50)]





# Boucle#1

for j in elem:
    clear_output(wait = True)
    Temps_ecoule = time() - debut
#La variable j parcourt le vecteur elem (1, 51, 101 ...) et sert de marqueur pour l'url
#Je vais chercher les pages en fonction du "elem" créé précédement
    
    
    #étant donné que ma boucle#1 se répète tout les 50 films, je peux m'en servir pour compter les pages
    
    film_scrap_current_page=0
    #Suite de message disponible à l'output
    warn("Scraping en cours")
    
    print('Page en cours de scraping {} \n\n'.format(page_scrap+1))
    
    print('Mise à jour a chaque page:\n')
    print('     Page scrapés {}'.format(page_scrap))
    print('     Films scrapés au total {}'.format(film_scrap_total))
    print('     Temps écoulé: {} '.format(Temps_ecoule))
    print('     Vitesse: {} page/s       {} film/s \n \n'.format(page_scrap/Temps_ecoule,film_scrap_total/Temps_ecoule))
    
    page_scrap = page_scrap+1
    
    
    #Url répertorie les pages du site par tranche de 50 films
    url =  'https://www.imdb.com/search/title/?at=0&num_votes=5000,&sort=user_rating,desc&start=' + j + '&title_type=feature'
    
    
    #res_global stock le contenu html des pages sélectionné par "url"
    res_global = requests.get(url)
    
    
            
    #J'utilise la fonction beautifulSoup puis je recupère la "div" qui m'intéresse et je stock dans la variable "stock_film"       
    html = BeautifulSoup(res_global.text, 'html.parser')
    stock_film = html.find_all('div', {'class':'lister-item mode-advanced'})

    
    
    
   # Boucle#2

    for current_film in stock_film:
        
        
        #Mes 2 variables films sont incrémentés à chaque itération de la boucle#2 cependant la variable current_page est réinitialisé à chaque boucle#1
        film_scrap_current_page = film_scrap_current_page + 1
        film_scrap_total = film_scrap_total + 1
        print('{} films scrapés  sur les 50 de la page {}'.format(film_scrap_current_page,page_scrap))
        
        
        
        
        
        
        #Je crée un data temporaire appelé data2 qui se réinitialise a chaque itération de la boucle#2
        data2 = data1.copy()

        #Toute les données ne sont pas récupérable sur la page principale je dois donc rentrer dans chaque film pour y trouver les données manquantes
        url_current_film = 'https://www.imdb.com' + current_film.find('a')['href'] 
        
        response_film = requests.get(url_current_film)
        
        #Comme précédemment on stock la page html du site mais cette fois pour chaque film
        html_current_film = BeautifulSoup(response_film.text, 'html.parser')
        
        #Cette fois pour atteindre la partie qui nous intéresse on doit rentrer dans 3 div
        body = html_current_film.find('div', class_='pagecontent')                 
        detail = body.find('div', {'class' : 'article', 'id' : 'titleDetails'})
        data_current_film = detail.find_all('div', class_ = 'txt-block')
           
        #Les données suivantes (de film à Type) sont récupérables sur la page principale
        data2['Film'] = current_film.h3.a.text.strip()
        data2['Note'] = float(current_film.strong.text)
        
        #Si je ne fais pas le "if" il garde l'ancienne valeur de 'score'
        data2['Score'] = current_film.find('span', {'class':'metascore favorable'})
        if data2['Score'] is None:
            data2['Score'] = None
        else:
            data2['Score'] = int(data2['Score'].text)
            
        data2['N_Votes'] = int(current_film.find('span', {'name':'nv'})['data-value'])
        data2['Type'] = current_film.find('span', {'class':'genre'}).text.strip()
        
         
        
        
        #Boucle#3
        for dcf in data_current_film:  
            #data_current_film contient le reste des données à scraper. La variable dcf me permet de parcourir parmi les films
            if not dcf.h4:
                det = None
                continue
            else :
                det = dcf.h4.text.strip()
            if  det == 'Runtime:':
                data2['Durée'] = int(dcf.time.text.replace('min','').strip())
                
            elif det == 'Budget:':
                data2['Budget'] = dcf.contents[2].strip()
                
            elif det == 'Opening Weekend USA:':
                data2['Revenus Générés le premier W-E aux USA'] = dcf.contents[2].strip()
                
            elif det == 'Gross USA:':
                data2['Revenus Générés aux USA'] = dcf.contents[2].strip()
                
            elif det == 'Cumulative Worldwide Gross:':
                data2['Revenus Générés dans le Monde'] = dcf.contents[2].strip()
                
            elif det == 'Release Date:':
                data2['Sortie'] = dcf.contents[2].strip()
                if data2['Sortie'] : 
                    data2['Date de sortie'] ="".join(data2['Sortie'].split()[:-1])
                    data2['Pays'] = data2['Sortie'].split()[-1][1:-1]
                else : 
                    data2['Date_sortie'] = None
                    data2['Pays_sortie'] = None
                
            elif det == 'Sound Mix:':
                data2['Sound Mix'] = dcf.a.text.strip()
                
            elif det == 'Color:':
                data2['Color'] = dcf.a.text.strip()
                
            elif det == 'Aspect Ratio:':
                data2['Aspect_ratio'] = dcf.contents[2].strip()
                
        #Une fois ces infos récupérés je les ajoute au fichier dataf        
        data3.append(data2)
        
#Message de fin
warn("Scraping Terminé")
clear_output(wait = True)
Temps_ecoule = time() - debut
print("Fin de scraping!!! \n \n Détails : \n")
print('     Page scrapés {}'.format(page_scrap))
print('     Films scrapés au total {} '.format(film_scrap_total))
print('     Temps écoulé au total: {}min'.format(Temps_ecoule / 60))
print('     Vitesse: {} page/s       {} film/s \n \n'.format(page_scrap/Temps_ecoule,film_scrap_total/Temps_ecoule))    





### Mettre les données scrapés dans un dataframe
dataf=pd.DataFrame(data3,columns=['Film','Note','Score','N_Votes','Durée',
                'Type','Sortie','Date de sortie','Année','Pays','Devise','Budget','Revenus Générés le premier W-E aux USA',
                'Revenus Générés aux USA','Revenus Générés dans le Monde','Sound Mix','Color'])









##Manipulation de données

#Création d'une colonne Date avec seulement l'année

s  = dataf["Date de sortie"]
i=0
l_temp=0
Annee_temp=[]
Annee=[]

for i in range(len(s)):
    if s[i] is None:
        s[i]=None
    else:
        l_temp = len(s[i])
        s1=s[i]
        l_start=l_temp - 4
        Annee_temp=s1[l_start:]
        if Annee_temp.upper() != Annee_temp:
            Annee_temp=None
        Annee.append(Annee_temp)
dataf["Année"]=Annee

#Gestion de la variable budget et de la devise
s_budget  = dataf["Budget"]
i=0
a=0
Devise=[]
Montant=[]
for i in range(len(s_budget)):
    a=s_budget[i]
    #Pour les None de la variable Budget je renvoi None
    if a == None :
        Budget_temp=None
        devise=None
        montant=None
    
    #Je distingue ensuite 2 cas, ceux où la devise est le dollars (1 caractere) et les autres devises(3 caracteres)
    elif a[0]=="$" :
        Budget_temp=a.replace(",","")
        devise=Budget_temp[0]
        montant=Budget_temp[1:]
    else:
        Budget_temp=a.replace(",","")
        devise=Budget_temp[0:3]
        montant=Budget_temp[3:]
    Devise.append(devise)
    Montant.append(montant)
dataf["Budget"]=Montant
dataf["Devise"]=Devise

#Gestion des revenus(meme procédé que pour le budget)
##Week-end USA
s_we  = dataf["Revenus Générés le premier W-E aux USA"]
i=0
a=0
Montant=[]
for i in range(len(s_we)):
    a=s_we[i]
    
    if a == None :
        we_temp=None
        montant=None
    
    
    elif a[0]=="$" :
        we_temp=a.replace(",","")
        montant=we_temp[1:]
    else:
        we_temp=a.replace(",","")
        montant=we_temp[3:]
    Montant.append(montant)
dataf["Revenus Générés le premier W-E aux USA"]=Montant    


##USA
s_USA  = dataf["Revenus Générés aux USA"]
i=0
a=0
Montant=[]
for i in range(len(s_USA)):
    a=s_USA[i]
    
    if a == None :
        USA_temp=None
        montant=None
    
    
    elif a[0]=="$" :
        USA_temp=a.replace(",","")
        montant=USA_temp[1:]
    else:
        USA_temp=a.replace(",","")
        montant=USA_temp[3:]
    Montant.append(montant)
Montant
dataf["Revenus Générés aux USA"]=Montant 

##World
s_w  = dataf["Revenus Générés dans le Monde"]
i=0
a=0
Montant=[]
for i in range(len(s_w)):
    a=s_w[i]
    
    if a == None :
        w_temp=None
        montant=None
    
    
    elif a[0]=="$" :
        w_temp=a.replace(",","")
        montant=w_temp[1:]
    else:
        w_temp=a.replace(",","")
        montant=w_temp[3:]
    Montant.append(montant)
dataf["Revenus Générés dans le Monde"]=Montant        
    
#J'aurai pu mettre les 3 dans une meme boucle mais pour un soucis de compréhension du code je ne l'ai pas fait    

## Exportation des données dans un csv
dataf.to_csv('data.csv')