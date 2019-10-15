import requests
from bs4 import BeautifulSoup
import json 
import time
import pymongo 
import re

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}


def main():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["TestCatalog"]
    mycol = mydb["Cars"]

    brands = getBrands()

    for i in brands:
        time.sleep(1)
        models = getModelLink(i)

        for j in models:
            time.sleep(1)
            data = {}
            data.update({'Make': i})
            modelData = getModel(j)
            data.update({'Model': modelData[0]})
            genDate = getGenInfo(j)
            genArray = []

            for k in range(0,modelData[1]):
                time.sleep(1)
                generationData = {}  
                engines = getEngineLinks(j, k)
                engineArray = []

                for x in range(0,len(engines)):
                    time.sleep(2)
                    print(engines[x])
                    engineArray.append(getEngineData(engines[x],x))
                

                generationData['startDate'] = genDate[k][0]
                if (len(genDate[k]) == 2):
                    generationData['endDate'] = genDate[k][1]
                
                generationData['Engines'] = engineArray

                genArray.append(generationData)


            data['Generations'] = genArray
            mycol.insert_one(data)

def getEngineData(car,engineNumber):
    pageLink = car

    pageResponse = requests.get(pageLink, headers=headers, timeout=120)

    soup = BeautifulSoup(pageResponse.content, "html.parser")

    data = dict()

    dataKey = []
    dataInfo = []

    engineID = car.split("#")
    engineID = engineID[1]
    engineID = engineID[1:]
    engineID = engineID.replace(" ", "_")

    engineInfo = soup.findAll('div', {'id': engineID})
    strInfo = str(engineInfo)
    strInfo = strInfo.replace("RPM<dt>", "RPM</dd><dt>")

    fixedSoup = BeautifulSoup(strInfo, "html.parser")

    engineInfo = fixedSoup.findAll('div', {'id': engineID})

    engineString = ""
    if engineInfo[0] is not None:
        engineString = engineInfo[0].span.text
        engineString = re.sub("[\(\[].*?[\)\]]", "", engineString)
        data.update({'Name':engineString})
    else:
        return data
    specInfo = soup.findAll('div', {'id': engineID})
    
    for i in specInfo:
        for j in i.findAll('dt'):
            dataKey.append(j.text)
        for k in i.findAll('dd'):
            if 'OR' in k.text:
                string = k.text
                string = string.split("OR")
                if "/" in string[0]:
                    string1 = string[0].split("/")
                    dataInfo.append(string1[1])
                else:
                    dataInfo.append(string[0])

            else:
                dataInfo.append(k.text)
    
    for i in engineInfo:
        for j in i.findAll('dt'):
            dataKey.append(j.text)
        for k in i.findAll('dd'):
            if k.br:
                string = str(k)
                string = string.replace("<br/>",":")
                string = string.split(":")
                for text in string:
                    if " HP" in text:
                        dataInfo.append(text)
                    elif "lb-ft" in text:
                        dataInfo.append(text.replace("<dd>",""))
            else:
                dataInfo.append(k.text)

    for x in range(len(dataInfo)):

        data.update({dataKey[x]:dataInfo[x]})
    
    return data

def getEngineLinks(modelLink, generationNumber):
    pageLink = modelLink
    pageResponse = requests.get(pageLink, headers=headers, timeout=120)

    soup = BeautifulSoup(pageResponse.content, "html.parser")

    engineInfo = soup.findAll('div', {'class': 'container carmodel clearfix'})

    engines = []
    for i in engineInfo[generationNumber].findAll('a', {'class': 'engurl semibold'}):
        engines.append ((str)(i['href']))
    return engines

def getModelLink(brand):
    pageLink = "https://www.autoevolution.com/"+brand+"/"
    pageResponse = requests.get(pageLink, headers=headers, timeout=120)

    soup = BeautifulSoup(pageResponse.content, "html.parser")
    models = []
    
    modelInfo = soup.findAll('div', {'class': 'carmod clearfix'})
    
    for i in modelInfo:
        models.append((str)(i.a['href']))
    
    disModelInfo = soup.findAll('div', {'class': 'carmod clearfix disc'})
    for i in disModelInfo:
        models.append((str)(i.a['href']))

    return models

def getModel(modelLink):
    pageLink = modelLink
    pageResponse = requests.get(pageLink, headers=headers, timeout=120)

    soup = BeautifulSoup(pageResponse.content, "html.parser")

    modelInfo = soup.findAll('span', {'itemtype': 'http://schema.org/ListItem'})
    
    modelData = []
    modelName = modelInfo[3].span.text.lower().capitalize()
    modelData.append(modelName)

    generationInfo = soup.findAll('div', {'class': 'container carmodel clearfix'})

    modelData.append(len(generationInfo))

    return modelData

def getGenInfo(modelLink):
    pageLink = modelLink
    pageResponse = requests.get(pageLink, headers=headers, timeout=120)

    soup = BeautifulSoup(pageResponse.content, "html.parser")

    generationInfo = soup.findAll('p', {'class': 'years'})

    generations = []
    for i in generationInfo:
        text = i.a.text
        text = text.replace(" ","")
        text = text.split("-")
        generations.append(text)

    return generations


def getBrands():
    pageLink = "https://www.autoevolution.com/cars/"
    pageResponse = requests.get(pageLink, headers=headers, timeout=120)

    soup = BeautifulSoup(pageResponse.content, "html.parser")
    brandInfo = soup.findAll('div', {'itemtype': 'https://schema.org/Brand'})

    brands = []
    for i in range(35,len(brandInfo)):
        brands.append(brandInfo[i].a['title'].lower())
    
    return brands

if __name__ == "__main__":
    main()
