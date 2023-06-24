import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .models import Post, Like, Recommendation


# A function to generate recommendations for a user
def generate_recommendations(user):

    likes = Like.objects.all()

    likes_df = pd.DataFrame(list(likes.values('user_id', 'post_id')))

    # Create a pivot table of likes with users as rows and posts as columns, then convert to np array
    likes_matrix = likes_df.pivot_table(index='user_id', columns='post_id', aggfunc='size', fill_value=0)
    likes_array = np.array(likes_matrix)

    # Calculate the cosine similarity between users
    user_similarity = cosine_similarity(likes_array)

    user_index = list(likes_matrix.index).index(user.id)  # Get the index of the user in likes_matrix list
    user_scores = user_similarity[user_index]  # Get the similarity scores of the input user with other users
    sorted_indices = np.argsort(-user_scores)  # Sort the scores in descending order and get the indices
    top_users = sorted_indices[1:11]  # Get the top 10 most similar users (excluding the input user)

    # Get the posts liked by the top users
    top_posts = likes_matrix.iloc[top_users].sum(axis=0)
    sorted_posts = np.argsort(-top_posts)  # Sort the posts by the number of likes and get the indices

    # Get the top 10 most liked posts (excluding the ones already liked by the input user)
    recommended_posts = [post for post, id in sorted_posts.items() if post not in likes_matrix.columns[likes_matrix.loc[user.id] > 0]][:10]

    # Create or update recommendations for the input user
    for post_id in recommended_posts:
        post = Post.objects.get(id=(post_id))
        recommendation, created = Recommendation.objects.get_or_create(user=user)
        recommendation.post.add(post)
        if not created:
            recommendation.score += 1
            recommendation.save()
