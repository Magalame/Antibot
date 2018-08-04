# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 22:07:16 2018

@author: noudy
"""
import win32com.server.register,win32com.client
from win32com.server import localserver
import pythoncom
from pythoncom import com_error
import sys
import pickle
import time
     
class Document:
    
    def __init__(self,idDoc,titre="TitreEx"):
        self.idDoc = int(idDoc)
        self.titre = str(titre)
        self.dictZones = {}
        self.idZoneCourante = 0
        
    def DefinieZone(self,idZone,texte=""):
        self.dictZones[idZone] = self.ZoneDeTexte(idZone,texte)
        
    def printDoc(self):
        for idZone,Zone in self.dictZones.items():
            print(idZone,":",Zone.texte)
            
    def SupprimeZone(self,idZone):
        del self.dictZones[idZone]
    
    class ZoneDeTexte:
        def __init__(self,idZone,texte=""):
            self.idZone = int(idZone)
            self.texte = str(texte)
            
            
    
            
class Correcteur:
    def __init__(self, serveur=None,antidote=None,langue="",outil="C",versionApi="2.0"):

        self.serveur = serveur
        if serveur == None:
            self.serveur = win32com.client.Dispatch("Correcteur.Antidote") # si on l'assigne plutôt dans les paramètres, ça bugue 
          
        self.antidote = antidote
        if antidote == None:
            self.antidote = win32com.client.Dispatch("Antidote.ApiOle")
        self.outil = outil
        self.langue = ""
        self.versionApi = versionApi
        
    def Televerse(self,doc):
        self.serveur.AjouteDoc(pickle.dumps(doc))
        
    def TeleverseDocs(self,docs):
        pickledDocs = pickle.dumps(docs)
        self.serveur.AjouteDocs(pickledDocs)
        
    def Telecharge(self,idDoc):
        return pickle.loads(self.serveur.RecupereDoc(idDoc))
    
    def TelechargeDocs(self,idDocListe):
        docs = self.serveur.RecupereDocs(pickle.dumps(idDocListe))
        return pickle.loads(docs)
    
    def Corrige(self,idDoc):
        self.serveur.DefinieDocCourant(idDoc)
        self.antidote.LanceOutilDispatch2(self.serveur,self.outil,self.langue,self.versionApi)
    
    def CorrigeDoc(self,idDoc,attendre=True,d=0.5,telecharger=False):
        if not attendre:
            self.Corrige(self,idDoc)
        else:
            self.AttendreActivationApp(self.Corrige,idDoc,d=d)
            if telecharger:#disponible seulement si l'app a deu le temps d'effectuer la correction
                return self.Telecharge(idDoc)
        
    def CorrigeDocs(self,idDocListe,attendre=True,d=0.5,telecharger=False):
        res = []
        for idDoc in idDocListe:
            res.append(self.CorrigeDoc(idDoc,attendre=attendre,d=d,telecharger=telecharger))
        return res
    
    def CorrigeDeMeme(self,doc,d=0.5):
        self.Televerse(doc)
        self.AttendreActivationApp(self.CorrigeDoc,doc.idDoc,d=d)
        return self.Telecharge(doc.idDoc)
    
    def CorrigeEtAttends(self,idDoc,d=0.5):
        self.AttendreActivationApp(self.CorrigeDoc,idDoc,d=d)
    
    def AttendreActivationApp(self,fonction,*args,d=0.5):
        tmp = self.serveur.compteActiveApplication
        res = fonction(*args)
        while(self.serveur.compteActiveApplication == tmp):
            time.sleep(d)
        return res
    
    def SupprimeDoc(self,idDoc):
        self.serveur.SupprimeDocs([int(idDoc)])
        
    def SupprimeDocs(self,idDocListe):
        self.serveur.SupprimeDocs(idDocListe)
        

def run(fn,*args):
    try:
        fn(*args)
    except com_error as error:
        tmp = error
        hr,msg,exc,arg = tmp.args
        print(exc[2])
