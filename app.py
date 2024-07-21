from flask import Flask, render_template, request, redirect, url_for, Response
import random
import requests
import numpy as np
import json

from src.system.taste_recsys import runRecsys, get_name_from_index, get_url_from_index, get_all_names, get_index_from_name, get_top_similar_items
from src.system.taste_profile import getTasteProfile, getCosineSimilarity, getCosineAll
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
    # stringList = runRecsys(index)
    # # print(stringList)
    # stringList = re.sub("[\[\]]", "", stringList)
    
    # topList = stringList.split(" ")
    topList = runRecsys(index)

    # i = 0
    # while i < len(topList):
    #     if topList[i] == '':
    #         topList.pop(i)
    #     else:
    #         topList[i] = int(topList[i])
    #         i += 1
    
    mainName = get_name_from_index(index)
    mainScore = getTasteProfile(index)
    mainImage = getImageUrl(index)
    main = [mainName, mainScore, mainImage]

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
        name = request.form['name']
        index = get_index_from_name(name)
        return redirect(url_for('testRecsys', index = index))
    if request.method == 'GET':
        return render_template('recsys_post_testing.html')

@app.route('/recsys_testing/<int:index>/')
def testRecsys(index):
    # stringList = runRecsys(index)
    # stringList = re.sub("[\[\]]", "", stringList)
    
    # topList = stringList.split(" ")

    # i = 0
    # while i < len(topList):
    #     if topList[i] == '':
    #         topList.pop(i)
    #     else:
    #         topList[i] = int(topList[i])
    #         i += 1
    topList = runRecsys(index)
    
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
    itemCosineWithMain = getCosineSimilarity(index, itemIndex)
    itemCosineWithMain = (itemCosineWithMain * 100).round(2)
    recommendedItem.append([itemName, itemUrl, itemImage, itemCosineWithMain])

    
    randomItemName = get_name_from_index(randNum)
    randomItemUrl = get_url_from_index(randNum)
    randomItemImage = getImageUrl(randNum)
    randomItemCosineWithMain = getCosineSimilarity(index, randNum)
    randomItemCosineWithMain = (randomItemCosineWithMain * 100).round(2)
    randomItem.append([randomItemName, randomItemUrl, randomItemImage, randomItemCosineWithMain])

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

# @app.route('/recsys_testing_single/', methods = ['GET','POST'])
# def submitTestSingle():
#     if request.method == 'POST':
#         name = request.form['name']
#         index = get_index_from_name(name)
#         return redirect(url_for('testRecsys', index = index))
#     if request.method == 'GET':
#         return render_template('recsys_post_testing_single.html')

# @app.route('/recsys_testing_single/<int:index>')
# def testRecsysSingle(index):
#     cosine = getCosineAll()
#     listSimilarity = get_top_similar_items(index, cosine)
#     print(listSimilarity.tolist())
#     return listSimilarity.tolist()


# @app.route('/test/')
# def testHtml():
    
#     return render_template("test.html")



if __name__ == '__main__':
    app.run(debug = True)