from flask import Flask, render_template, request
import pandas as pd
from scipy.sparse.linalg import svds
import numpy as np

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def recommend():
    userid = request.form.get('userid')

    userRatings, animes_df = prepare_data()
    calc_pred_ratings_df = svd(userRatings)
    watchedRecommendations = findRecommendations(userid, userRatings, calc_pred_ratings_df, animes_df)

    return render_template('index.html', column_names=watchedRecommendations.columns.values, row_data=list(watchedRecommendations.values.tolist()),
                           link_column="Anime_ID", zip=zip)

def prepare_data():
    # Reading data from CSV files into DataFrames
    animes_df = pd.read_csv('anime_info.dat',  delimiter='\t')
    ratings_df = pd.read_csv('anime_ratings.dat',  delimiter='\t')

    #Merge the two tables
    ratings = pd.merge(animes_df, ratings_df, left_on='anime_ids', right_on='Anime_ID').drop(['genre','type','episodes','rating', 'members'], axis=1)

    #Get Table with only anime_id and user_id
    userRatings = ratings.pivot_table(index=['User_ID'],columns=['Anime_ID'],values='Feedback')

    return userRatings, animes_df

def svd(userRatings):
    avg_ratings = userRatings.mean(axis=1)

    #Center each users ratings around 0
    userRatings_centered = userRatings.sub(avg_ratings, axis = 0)

    #Fill in the missing data with 0s
    userRatings_normed = userRatings_centered.fillna(0)

    #Decompose the matrix
    U, sigma, Vt = svds(userRatings_normed.to_numpy(), k = 10)

    #Convert sigma into a diagonal matrix
    sigma = np.diag(sigma)

    #Dot product of U and sigma
    U_sigma = np.dot(U, sigma)

    #Dot product of result and Vt
    U_sigma_Vt = np.dot(U_sigma, Vt)

    #Add back on the rowmeans contained in avg_ratings
    uncentered_ratings = U_sigma_Vt + avg_ratings.values.reshape(-1, 1)

    #Create DataFrame of the results
    calc_pred_ratings_df = pd.DataFrame(uncentered_ratings, index = userRatings.index, columns = userRatings.columns)

    return calc_pred_ratings_df

def findRecommendations(select_userid, userRatings, calc_pred_ratings_df, animes_df):
    # Step 3: Recommend n anime from not watched anime
    values_threshold = 8
    values_arr = calc_pred_ratings_df.values
    #get if user has watched
    hasWatched = userRatings.iloc[[select_userid]].notnull().transpose()
    hasWatched.columns = ['Has Watched?']
    
    #np.where(hasWatched[]how]
    
    #get if the ratings greater than threshhold
    recommendations_id = calc_pred_ratings_df.apply(lambda row: row[row > values_threshold], axis=1)
    recommendations_id = recommendations_id.iloc[[select_userid]].transpose()
    recommendations_id.columns = ['Rating']
    
    #extract column from hasWatched
    extracted_col = hasWatched['Has Watched?']
    
    recommendations_id = pd.concat([recommendations_id, extracted_col], axis=1)
    # Filter the DataFrame to include only rows where the "Has Watched?" column is True
    watched_recommendations = recommendations_id[recommendations_id['Has Watched?'] == False].sort_values(by='Rating', ascending=False).drop(columns=['Has Watched?', 'Rating'])
    watched_recommendations = pd.merge(watched_recommendations, animes_df, left_on='Anime_ID', right_on='anime_ids')

    return watched_recommendations.head()


#type localhost:3000 into search bar
if __name__ == '__main__':
    app.run(port=3000, debug = True)