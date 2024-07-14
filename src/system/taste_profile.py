import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

recipe_contents = pd.read_csv('src/data/recipe_contents.csv')

taste_combined = recipe_contents[['salt_score', 'sweet_score', 'bitter_score', 'umami_score', 'richness_score']]
cosine = cosine_similarity(taste_combined)

# Order of scores: [salt_score, sweet_score, bitter_score, umami_score, richness_score]
def getTasteProfile(index):
  tasteProfile = recipe_contents.iloc[index, 4:].to_string(header = False, index = False)
  tasteProfile = [eval(i) for i in tasteProfile.split("\n")]

  return tasteProfile

def getCosineSimilarity(index1, index2):
  return cosine[index1][index2]

