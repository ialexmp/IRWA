import json


class Document:
    """
    Original corpus data as an object
    """

    def __init__(self, id, title, description, doc_date, likes, retweets, url, hashtags, profile_pic, username):
        self.id = id
        self.title = title
        self.description = description
        self.doc_date = doc_date
        self.likes = likes
        self.retweets = retweets
        self.url = url
        self.hashtags = hashtags
        self.profile_pic = profile_pic
        self.username = username

    def to_json(self):
        return self.__dict__

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)


class StatsDocument:
    """
    Original corpus data as an object
    """

    def __init__(self, id, title, description, doc_date, url, count):
        self.id = id
        self.title = title
        self.description = description
        self.doc_date = doc_date
        self.url = url
        self.count = count

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)


class ResultItem:
    def __init__(self, id, title, description, doc_date, url, profile_pic, username, ranking):
        self.id = id
        self.title = title
        self.description = description
        self.doc_date = doc_date
        self.url = url
        self.profile_pic = profile_pic
        self.username = username
        self.ranking = ranking
        
class Session_IP:
    """
    Original corpus data as an object
    """

    def __init__(self, user_ip, adress):
        self.ip = user_ip
        self.platform = adress["platform"]["name"] + " " + adress["platform"]["version"]
        self.browser = adress["browser"]["name"]

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)
    
class Session_History:
    """
    Original corpus data as an object
    """

    def __init__(self, session):
        self.session = session

    def __str__(self):
        """
        Print the object content as a JSON string
        """
        return json.dumps(self)
