import pandas as pd
import re
import math
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class Nutrient:
  def __init__(self, name, amount, divisor):
    self.name = name
    self.amount = int(amount)
    self.divisor = divisor
    if self.divisor == "mg":
      self.amount_gram = round(amount / 1000, 3)
    else:
      self.amount_gram = amount

  def __str__(self):
    if self.divisor == "mg":
      return f"{self.name}: {self.amount_gram}g"
    return f"{self.name}: {self.amount}{self.divisor}"

recipes = pd.read_csv('src/data/recipe_no_dupes.csv')

def runRecsys(inputIndex):

  recipe_contents = recipes.drop(['prep_time', 'cook_time', 'total_time',
                                  'directions', 'cuisine_path', 'timing',
                                  'img_src', 'yield', 'rating',
                                  'servings'],
                                axis = 1)

  nutrition_list= []

  for nutrition in recipe_contents['nutrition']:
    nutrition_list.append(nutrition.rsplit(', '))

  nutrition_list_new = []

  for nutritions in nutrition_list:
    nutrition_item = []
    for nutrition in nutritions:
      nutrition_item.append(removePercentage(nutrition))
    nutrition_list_new.append(nutrition_item)

  nutrition_list = nutrition_list_new

  nutrition_list_new = []


  for nutritions in nutrition_list:
    nutrition_item = []
    for nutrition in nutritions:
      nutrition_item.append(convertObjectNutrient(nutrition))
    nutrition_list_new.append(nutrition_item)

  nutrition_list = nutrition_list_new

  nutrition_type = []

  for i in range(len(nutrition_list)):
    for j in range(len(nutrition_list[i])):
      nutrition_type.append(nutrition_list[i][j].name)

  # Record all scores
  salt_score = []
  sweet_score = []
  bitter_score = []
  umami_score = []
  richness_score = []

  # Get all salt score
  for i in range(len(nutrition_list)):
    sodium = 0.0

    for j in range(len(nutrition_list[i])):
      if nutrition_list[i][j].name == "Sodium":
        sodium = nutrition_list[i][j].amount_gram

    salt_score.append(score_salt(sodium))

  recipe_contents['salt_score'] = salt_score

  
  # Get all sweet score
  for i in range(len(nutrition_list)):
    sugar = 0.0

    for j in range(len(nutrition_list[i])):
      if nutrition_list[i][j].name == "Total Sugars":
        sugar = nutrition_list[i][j].amount_gram

    sweet_score.append(score_sweet(sugar))

  recipe_contents['sweet_score'] = sweet_score

  
  # Get all bitter score
  for i in range(len(nutrition_list)):
    calcium = 0.0
    potassium = 0.0
    iron = 0.0

    for j in range(len(nutrition_list[i])):
      if nutrition_list[i][j].name == "Calcium":
        calcium = nutrition_list[i][j].amount_gram
      elif nutrition_list[i][j].name == "Potassium":
        potassium = nutrition_list[i][j].amount_gram
      elif nutrition_list[i][j].name == "Iron":
        iron = nutrition_list[i][j].amount_gram

    bitter_score.append(score_bitter(calcium, potassium, iron))

  recipe_contents['bitter_score'] = bitter_score

  
  # Get all umami score
  for i in range(len(nutrition_list)):
    protein = 0.0

    for j in range(len(nutrition_list[i])):
      if nutrition_list[i][j].name == "Protein":
        protein = nutrition_list[i][j].amount_gram

    umami_score.append(score_umami(protein))

  recipe_contents['umami_score'] = umami_score

  
  # Get all richness score
  for i in range(len(nutrition_list)):
    total_fat = 0.0
    cholesterol = 0.0

    for j in range(len(nutrition_list[i])):
      if nutrition_list[i][j].name == "Total Fat":
        total_fat = nutrition_list[i][j].amount_gram
      elif nutrition_list[i][j].name == "Cholesterol":
        cholesterol = nutrition_list[i][j].amount_gram

    richness_score.append(score_richness(total_fat, cholesterol))

  recipe_contents['richness_score'] = richness_score

  salt_score_min = recipe_contents['salt_score'].min()
  salt_score_max = recipe_contents['salt_score'].max()
  sweet_score_min = recipe_contents['sweet_score'].min()
  sweet_score_max = recipe_contents['sweet_score'].max()
  bitter_score_min = recipe_contents['bitter_score'].min()
  bitter_score_max = recipe_contents['bitter_score'].max()
  umami_score_min = recipe_contents['umami_score'].min()
  umami_score_max = recipe_contents['umami_score'].max()
  richness_score_min = recipe_contents['richness_score'].min()
  richness_score_max = recipe_contents['richness_score'].max()

  # Min-max normalization [0-1], which is then multiplied by 9 then added 1 for a scale of 1 to 10.
  # Null value will be 0 representing no taste.
  for i in range(len(salt_score)):
    if salt_score[i] != None:
      salt_score[i] = ((salt_score[i] - salt_score_min) / (salt_score_max - salt_score_min)) * 9 + 1
    else:
      salt_score[i] = 0
    if sweet_score[i] != None:
      sweet_score[i] = ((sweet_score[i] - sweet_score_min) / (sweet_score_max - sweet_score_min)) * 9 + 1
    else:
      sweet_score[i] = 0
    if bitter_score[i] != None:
      bitter_score[i] = ((bitter_score[i] - bitter_score_min) / (bitter_score_max - bitter_score_min)) * 9 + 1
    else:
      bitter_score[i] = 0
    if umami_score[i] != None:
      umami_score[i] = ((umami_score[i] - umami_score_min) / (umami_score_max - umami_score_min)) * 9 + 1
    else:
      umami_score[i] = 0
    if richness_score[i] != None:
      richness_score[i] = ((richness_score[i] - richness_score_min) / (richness_score_max - richness_score_min)) * 9 + 1
    else:
      richness_score[i] = 0

  recipe_contents['salt_score'] = salt_score
  recipe_contents['sweet_score'] = sweet_score
  recipe_contents['bitter_score'] = bitter_score
  recipe_contents['umami_score'] = umami_score
  recipe_contents['richness_score'] = richness_score

  recipe_contents.to_csv('src/data/recipe_contents.csv', index = False)

  contents = pd.read_csv('src/data/recipe_contents.csv')

  # Get all taste ratings into a separate dataframe
  taste_combined = contents[['salt_score', 'sweet_score', 'bitter_score', 'umami_score', 'richness_score']]

  cosine = cosine_similarity(taste_combined)

  # similarity_df = pd.DataFrame(cosine,
  #                            index = contents['recipe_name'],
  #                            columns = contents['recipe_name'])
  
  # Input a recipe index
  recipe_index = int(inputIndex)

  top_10_similar_indices = get_top_similar_items(recipe_index, cosine, 10)
  return top_10_similar_indices.tolist()

####################

def removePercentage(string):
    if string[-1] == '%':
      while string[-1] != ' ' and len(string) != 0:
        string = string[:-1]

      return string[:-1]
    return string

def convertObjectNutrient(string):
  name = string.rsplit(' ', 1)[0]
  value = string.rsplit(' ', 1)[1]


  amount = int(re.split('(\d+)', value)[1])
  divisor = re.split('(\d+)', value)[-1]

  objectNutrient = Nutrient(name, amount, divisor)
  return objectNutrient

# Salt score calculation
def score_salt(sodium):
  if (sodium == 0):
    return None
  return math.log(sodium, 10)

# Sugar score calculation
def score_sweet(sugar):
  if (sugar == 0.0):
    return None
  return math.log(sugar, 10)

# Bitter score calculation
def score_bitter(calcium, potassium, iron):
  total = calcium + potassium + iron
  if (total == 0):
    return None

  return math.log(total, 10)

def score_umami(protein):
  if (protein == 0.0):
    return 0.0

  return math.log(protein, 10)

# Richness score calculation
def score_richness(total_fat, cholesterol):
  total = total_fat + cholesterol

  if (total == 0.0):
    return None

  return math.log(total, 10)

def get_top_similar_items(index, cosine, top_k = -1):
  if (top_k == -1):
    similarity_scores = cosine[index]
    top_k_similar_indices = similarity_scores.argsort()[::-1]
  else:
    similarity_scores = cosine[index]
    top_k_similar_indices = similarity_scores.argsort()[::-1][0:top_k + 1]  # Get 11 items

  return top_k_similar_indices[top_k_similar_indices != index]

def get_name_from_index(index):
  return recipes['recipe_name'][index]

def get_index_from_name(name):
  index = recipes.index[recipes['recipe_name'] == name].tolist()
  return index[0]

def get_url_from_index(index):
  return recipes['url'][index]

def get_all_names():
  return recipes['recipe_name'].tolist()
