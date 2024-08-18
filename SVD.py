from flask import Flask, render_template, request, jsonify
import pandas as pd
from surprise import Reader, Dataset, SVD
from surprise.model_selection import cross_validate
from collections import defaultdict 
import sys
import statistics

app = Flask(__name__)

global animes_df
global top_n
global ratings_df

@app.before_first_request
@app.route('/get_ratings')
def calculatedata():
    global animes_df
    global ratings_df
    animes_df, ratings_df = read_data()
    ratings = ratings_df.to_json()
    return jsonify(ratings)

@app.route('/', methods=['GET','POST'])
def recommend():
    userid = request.form.get('userid')
    tags_list = getTags(animes_df)
    top_n, results = svd(ratings_df)

    average_rmse = sum(results['test_rmse']) / len(results['test_rmse'])
    average_mae = sum(results['test_mae']) / len(results['test_mae'])

    std_dev_rmse = statistics.stdev(results['test_rmse'])
    std_dev_mae = statistics.stdev(results['test_mae'])

    if (userid is None):
        userid = 0

    watchedRecommendations = pd.DataFrame()
    watchedRecommendations = getdf(animes_df, int(userid), top_n)

    return render_template('index.html',
                        column_names=watchedRecommendations.columns.values,
                        row_data=list(watchedRecommendations.values.tolist()),
                        link_column="Anime_ID",
                        tags_list=tags_list,
                        average_rmse = average_rmse,
                        average_mae = average_mae,
                        std_dev_rmse = std_dev_rmse,
                        std_dev_mae = std_dev_mae,
                        zip=zip)

@app.route('/get_anime')
def get_anime():
    unique_anime = getAnime(animes_df)
    return jsonify(unique_anime)

@app.route('/submit_anime_likes', methods=['POST'])
def submit_anime_likes():
    global ratings_df

    data = request.get_json()
    user_id = getUserID()
    for anime_like in data:
        df = getAnimeID(anime_like, user_id)
        new_row = df.iloc[0]
        ratings_df.loc[-1] = new_row
        ratings_df.index = ratings_df.index + 1
        ratings_df = ratings_df.sort_index()

    return jsonify({'message': 'Anime likes received successfully'})

def read_data():
    # Reading data from CSV files into DataFrames
    animes_df = pd.read_csv('anime_info.dat',  delimiter='\t')
    ratings_df = pd.read_csv('anime_ratings.dat',  delimiter='\t')

    return animes_df, ratings_df

def svd(ratings):
    reader = Reader(rating_scale=(0,10))

    data = Dataset.load_from_df(ratings[['User_ID', 'Anime_ID', 'Feedback']], reader)

    svd = SVD() 
    results = cross_validate(svd, data, measures=['RMSE', 'MAE'], cv=10, verbose=False)

    trainset = data.build_full_trainset()
    svd.fit(trainset)

    # Then predict ratings for all pairs (u, i) that are NOT in the training set.
    testset = trainset.build_anti_testset()
    predictions = svd.test(testset)

    top_n = get_top_n(predictions, n=10)

    return top_n, results

def get_top_n(predictions, n=10):
    """Return the top-N recommendation for each user from a set of predictions.

    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 10.

    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...] of size n.
    """

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

def getdf(animes_df, userid, top_n):
    df = pd.DataFrame([(uid, iid, rating) for uid, ratings in top_n.items() for iid, rating in ratings],
                  columns=['User_ID', 'Anime_ID', 'Rating'])
    
    # Filter the DataFrame for the specific user
    specific_user_df = df[df['User_ID'] == userid]

    # Merge specific_user_df with animes_df based on anime_id
    merged_df = pd.merge(specific_user_df, animes_df, left_on='Anime_ID', right_on='anime_ids', how='inner').drop(columns=['User_ID', 'Anime_ID', 'Rating', 'anime_ids'])

    return merged_df

def getTags(animes_df):
    unique_tags = animes_df['genre'].str.split(',').explode().str.strip().unique()

    return unique_tags

def getAnime(animes_df):
    unique_animes = animes_df['name'].explode().drop_duplicates().tolist()

    return unique_animes

def getAnimeID(animesLikes, user_id):
    # Merge animeLikes with animes_df on name (case-sensitive)
    merged_df = animes_df[animes_df['name'].isin(animesLikes)]
    merged_df.insert(2, "Feedback", animesLikes[1])
    merged_df.insert(0, "User_ID", user_id)

    # Extract the ID if there's a match, otherwise None
    anime_id = merged_df.drop(columns=['name', 'genre', 'type', 'episodes', 'rating', 'members'])
    anime_id.rename(columns={'anime_ids':'Anime_ID'}, inplace=True)
    print(anime_id, file=sys.stderr)
    return anime_id

def getUserID():
    global user_id
    unique_user_ids = ratings_df['User_ID'].unique()
    highest_user_id = unique_user_ids.max()

    user_id = highest_user_id + 1
    return highest_user_id+1


#type localhost:3000 into search bar
if __name__ == '__main__':
    app.run(port=3000, debug = True)