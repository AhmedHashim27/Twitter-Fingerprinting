import tweepy
import requests

consumer_key = "Vqixgr3RIMAJOpiBd01nf2Viz"
consumer_secret = "jRuakXNaQUtV1WNv8GSPkzAsHXTXC8jcOS7enXKS6oN8WIKRBd"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

def get_user_tweets(screen_name, return_dict):
    print("Getting Tweets from", screen_name)
    alltweets = []
    try:
        new_tweets = api.user_timeline(screen_name = screen_name, count=200, include_rts=False, exclude_replies=False)
        alltweets.extend(new_tweets)
        oldest = alltweets[-1].id - 1
        while len(new_tweets) > 0:      
            new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest, include_rts=False, exclude_replies=False)
            alltweets.extend(new_tweets)
            oldest = alltweets[-1].id - 1
    except:
        return

    print('Done User: ', screen_name)
    outtweets = [tweet.text for tweet in alltweets]
    outtweets_time = [tweet.created_at for tweet in alltweets]
    media = []
    try:
        for tweet in alltweets:
            if "media" in tweet.extended_entities:
                media.append(tweet.extended_entities["media"])
    except:
        pass
    return_dict[screen_name] = [outtweets, outtweets_time, media]
    return outtweets
    

def get_daily_time(acc_1, acc_2):
    time_acc_1 = [i.hour for i in acc_1]
    time_acc_2 = [i.hour for i in acc_2]
    diff = 1
    for i in range(24):
        diff += abs(time_acc_1.count(i) - time_acc_2.count(i))
    return diff

def compare_media(acc_1, acc_2):
    similarity = 1
    for i in acc1:
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