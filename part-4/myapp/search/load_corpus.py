import pandas as pd

from myapp.core.utils import load_json_file
from myapp.search.objects import Document

from pandas import json_normalize
import json

_corpus = {}


def load_corpus(path) -> [Document]:
    """
    Load file and transform to dictionary with each document as an object for easier treatment when needed for displaying
     in results, stats, etc.
    :param path:
    :return:
    """
    df = _load_corpus_as_dataframe(path)
    df.apply(_row_to_doc_dict, axis=1)
    return _corpus


def _load_corpus_as_dataframe(path):
    """
    Load documents corpus from file in 'path'
    :return:
    """
    data_list = []

    #read all lines
    with open(path) as f:
        for line in f:
            # Parse the string into a JSON object
            json_data = json.loads(line)
            # Append the JSON object to the list
            data_list.append(json_data)

    # Convert the list of JSON objects to a DataFrame
    df = pd.DataFrame(data_list)
    
    for index, row in df.iterrows():
        screen_name = row['user']['screen_name'] # Access the 'screen_name' key
        profile_pic = row['user']['profile_image_url']

        # Create the 'Url' and 'Hashtags' column for each row
        df.at[index, "Url"] = f"https://twitter.com/{screen_name}/status/{df['id_str'].iloc[index]}"
        df.at[index, "Hashtags"] = len(row['entities']['hashtags'])
        df.at[index, "Profile_pic"] = profile_pic
        df.at[index, "Username"] = screen_name

    df = df.rename(columns={
        "id": "Id",
        "full_text": "Tweet",
        "screen_name": "Username",
        "created_at": "Date",
        "favorite_count": "Likes",
        "retweet_count": "Retweets",
        "lang": "Language"
    })
    return df


def _row_to_doc_dict(row: pd.Series):
    _corpus[row['Id']] = Document(row['Id'], row['Tweet'][0:100], row['Tweet'], row['Date'], row['Likes'],
                                  row['Retweets'],
                                  row['Url'], row['Hashtags'], row['Profile_pic'], row['Username'])
