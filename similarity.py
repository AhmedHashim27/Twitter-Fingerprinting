import tweepy
import requests
import os
import json
import dateutil.parser
from m3inference import M3Twitter

consumer_key = "Vqixgr3RIMAJOpiBd01nf2Viz"
consumer_secret = "jRuakXNaQUtV1WNv8GSPkzAsHXTXC8jcOS7enXKS6oN8WIKRBd"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

cached_hours = {}

x = M3Twitter()
x.twitter_init("Vqixgr3RIMAJOpiBd01nf2Viz", "jRuakXNaQUtV1WNv8GSPkzAsHXTXC8jcOS7enXKS6oN8WIKRBd", "943540381010063369-SJla9uZxTMtBz7G9gIDYMs6utnjtQHn", "5pdIqco95c0zsw7TBDLocdUy4Lhe9987EOA0rFIsEK25F")

def get_user_tweets(screen_name, return_dict_acc):
    print("Getting Tweets from", screen_name)
    alltweets = []
    outtweets = []
    outtweets_time = []
    text_path = "Twitter-Accounts/" + screen_name + "/text"
    media_path = "Twitter-Accounts/" + screen_name + "/media"
    hours_path = "Twitter-Accounts/" + screen_name + "/hours"
    m3_res = x.infer_screen_name(screen_name)
    g = m3_res['output']['gender']
    gender = "male" if g["male"] > g["female"] else "female"
    ages = m3_res['output']['age']
    age = 0
    n = list(ages.keys())[0]
    for k in ages:
        if ages[n] < ages[k]:
            n = k
            age = k
    if os.path.isdir("Twitter-Accounts/" + screen_name + "/"):
        if os.path.isfile(text_path) and os.path.isfile(media_path) and os.path.isfile(hours_path):
            text = json.loads(open(text_path, "r").read())
            media = json.loads(open(media_path, "r").read())
            hours = json.loads(open(hours_path, "r").read())
            try:
                profile_picture = api.get_user(screen_name=screen_name).profile_image_url.replace("normal", "bigger")
            except:
                profile_picture = ""

            print('(CACHED) Done User: ', screen_name)
            return_dict_acc[screen_name] = [text, hours, media, profile_picture, gender, age]
            return
    else:
        os.mkdir("Twitter-Accounts/" + screen_name + "/")

    try:
        new_tweets = api.user_timeline(screen_name = screen_name, count=200, include_rts=False, exclude_replies=False)
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1
        while len(new_tweets) > 0:      
            new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest, include_rts=False, exclude_replies=False)
            alltweets.extend(new_tweets)
            oldest = alltweets[-1].id - 1
        print('Done User: ', screen_name)
        outtweets = [tweet.text for tweet in alltweets]
        outtweets_time = [tweet.created_at for tweet in alltweets]
    except:
        outtweets = ["Dummy_text"]
        outtweets_time = []

    try:
        media = []
        for tweet in alltweets:
            if "media" in tweet.extended_entities:
                media.append(tweet.extended_entities["media"])
    except:
        pass

    
    try:
        profile_picture = api.get_user(screen_name=screen_name).profile_image_url.replace("normal", "bigger")
    except:
        profile_picture = ""

    with open(text_path, "w") as f:
        f.write(json.dumps(outtweets))

    with open(media_path, "w") as f:
        f.write(json.dumps(media))

    with open(hours_path, "w") as f:
        hours = output_hours(outtweets_time, screen_name)
        f.write(json.dumps(hours))



    return_dict_acc[screen_name] = [outtweets, hours, media, profile_picture, gender, age]
    return return_dict_acc[screen_name]
    

def get_daily_time(acc_1, acc_2):
    diff = 1
    if len(acc_1) == 0 or len(acc_2) == 0:
        return 100
    for i in range(24):
        diff += abs(acc_1[i] - acc_2[i])
    return diff

def output_hours(acc, name):
    global cached_hours
    if name in cached_hours:
        return cached_hours[name]
    try:
        hours = [[int(x.hour) for x in acc].count(j) for j in range(24)]
    except:
        try:
            hours = [[int(dateutil.parser.parse(x).hour) for x in acc].count(j) for j in range(24)]
        except:
            hours = []
    cached_hours[name] = hours
    return hours

def compare_media(acc_1, acc_2):
    similarity = 1
    if len(acc_1) == 0 or len(acc_2) == 0:
        return 100
    for i in acc_1:
        for j in acc2:
            r = requests.post(
                "https://api.deepai.org/api/image-similarity",
                data={
                    'image1': i["media_url"],
                    'image2': j["media_url"],
                },
                headers={'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'}
            )
            similarity += int(r.json()["output"]["distance"])
    return similarity
