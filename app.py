from flask import Flask, render_template, request, redirect, url_for, Response
import re
import random
from bs4 import BeautifulSoup
import requests
import numpy as np
import json

from src.system.taste_recsys import runRecsys, get_name_from_index, get_url_from_index, get_all_names, get_index_from_name
from src.system.taste_profile import getTasteProfile, getCosineSimilarity
from src.system.image_scrape import getImageUrl

app = Flask(__name__)

RECIPE_LIST = get_all_names()

@app.route('/')
def index():
    return "Hello world"

@app.route('/_autocomplete', methods=['GET'])
def autocomplete():
    return Response(json.dumps(RECIPE_LIST), mimetype='application/json')

@app.route('/recsys/', methods = ['GET','POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        index = get_index_from_name(name)
        return redirect(url_for('displayRecsys', index = index))
    if request.method == 'GET':
        return render_template('recsys_post.html')


@app.route('/recsys/<int:index>/')
def displayRecsys(index):
    stringList = runRecsys(index)
    stringList = re.sub("[\[\]]", "", stringList)
    
    topList = stringList.split(" ")

    i = 0
    while i < len(topList):
        if topList[i] == '':
            topList.pop(i)
        else:
            topList[i] = int(topList[i])
            i += 1
    
    mainName = get_name_from_index(index)
    mainScore = getTasteProfile(index)
    mainImage = getImageUrl(index)
    main = [mainName, mainScore, mainImage]
    print(main[2])

    topListItem = []

    for itemIndex in topList:
        itemName = get_name_from_index(itemIndex)
        itemUrl = get_url_from_index(itemIndex)
        itemTasteProfile = getTasteProfile(itemIndex)
        itemCosineWithMain = getCosineSimilarity(index, itemIndex)
        itemCosineWithMain = (itemCosineWithMain * 100).round(2)
        itemImage = getImageUrl(itemIndex)
        topListItem.append([itemName, itemUrl, itemTasteProfile, itemCosineWithMain, itemImage])

    return render_template("recsys_result.html", 
                        topListItem = topListItem, 
                        main = main)

@app.route('/recsys_testing/', methods = ['GET','POST'])
def submitTest():
    if request.method == 'POST':
        index = request.form['index']
        print(request)
        return redirect(url_for('testRecsys', index = index))
    if request.method == 'GET':
        return render_template('recsys_testing.html')

@app.route('/recsys_testing/<int:index>/')
def testRecsys(index):
    stringList = runRecsys(index)
    stringList = re.sub("[\[\]]", "", stringList)
    
    topList = stringList.split(" ")

    i = 0
    while i < len(topList):
        if topList[i] == '':
            topList.pop(i)
        else:
            topList[i] = int(topList[i])
            i += 1
    
    mainName = get_name_from_index(index)
    mainScore = getTasteProfile(index)
    mainImage = getImageUrl(index)
    main = [mainName, mainScore, mainImage]

    recommendedItem = []
    randomItem = []
    randNum = random.randint(0, 961)

    itemIndex = topList[0]
    itemName = get_name_from_index(itemIndex)
    itemUrl = get_url_from_index(itemIndex)
    itemImage = getImageUrl(itemIndex)
    recommendedItem.append([itemName, itemUrl, itemImage])

    
    randomItemName = get_name_from_index(randNum)
    randomItemUrl = get_url_from_index(randNum)
    randomItemImage = getImageUrl(randNum)
    randomItem.append([randomItemName, randomItemUrl, randomItemImage])

    randomAB = [recommendedItem, randomItem]
    randOrder = random.sample(range(2), 2)
    print(randOrder)

    # Clean up for horrible list management
    item1 = randomAB[randOrder[0]][0]
    item2 = randomAB[randOrder[1]][0]

    return render_template("recsys_testing.html", 
                           item1 = item1, 
                           item2 = item2,
                           main = main)

@app.route('/image/')
def testImage():
    url = "https://wuthering.gg/characters/encore"

    try:
        response = requests.get(url)
        html_content = response.text

        soup = BeautifulSoup(html_content, features="lxml")
        img_tag = soup.find('img')
        # img_link = (tree.find('img')[0]).attr['src']

        if img_tag:
            # Extract the src attribute of the img tag
            img_link = img_tag.get('src')
            print("Image URL:", img_link)
        else:
            img_link = None
            print("No image found on the page.")

    except requests.RequestException as e:
        print("Error fetching page:", e)
    except AttributeError as e:
        print("Error parsing HTML:", e)

    return render_template("recsys_image_test.html",
                           img_link = img_link)



# @app.route('/test/')
# def testHtml():
#     form = SearchForm(request.form)
#     return render_template("test.html", form=form)



if __name__ == '__main__':
    app.run(debug = True)