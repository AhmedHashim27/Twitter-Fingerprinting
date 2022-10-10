# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
import random
import time
import multiprocessing
import os
from tf import tf
import similarity
import dateutil.parser
from os import listdir
from os.path import isfile, join
import json
import tweepy



consumer_key = "Vqixgr3RIMAJOpiBd01nf2Viz"
consumer_secret = "jRuakXNaQUtV1WNv8GSPkzAsHXTXC8jcOS7enXKS6oN8WIKRBd"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


def index(request):

    related_accounts = {}
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    tweets = {}
    jobs = []

    if request.method == "POST":
        accs = [x.replace("\r", "") for x in request.POST["accounts"].split("\n")]
        print(accs)
    else:
        accs = ['Mr_MO_LA', 'DazinOff', 'BrewJimmy', 'GoodVibezzOnlyx', 'AkshayDeshkar1', 'kimjeymi']
    accs_pictures = {}
    filter_quality = .3

    output_accs = []

    for acc in accs:
        try:
            p = multiprocessing.Process(target=similarity.get_user_tweets, args=(acc, return_dict))
            jobs.append(p)
            p.start()
        except:
            print("Getting tweets Failed!\n\n")
    
    for proc in jobs:
        proc.join()

    for i in accs:
        try:
            if len(return_dict[i][3]) > 1:
                accs_pictures[i] = return_dict[i][3]
            else: 
                accs_pictures[i] = "https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png"
        except:
            accs_pictures[i] = "https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png"
    for i in accs:
        tweets[i] = ' '.join(return_dict[i][0])

    print("-"*30)

    if len(tweets.keys()) < 2:
        print("Not enough ACCs")
        exit()

    ref, data = tf(tweets)
    visited = []
    for ind, ary in enumerate(ref):
        for i, el in enumerate(ary):
            if i != ind:
                if str(ind) + "_" + str(i) in visited:
                    continue
                visited.append(str(i) + "_" + str(ind))
                tfidf = el
                try:
                    acc_1 = return_dict[accs[ind]]
                    acc_2 = return_dict[accs[i]]
                except:
                    print(return_dict[accs[i]], return_dict[accs[ind]])

                hours1 = acc_1[1]
                hours2 = acc_2[1]

                time_similarity = 5 * ( 1 / similarity.get_daily_time(hours1, hours2) )
                media_similarity = 5 * ( 1 / similarity.compare_media(acc_1[2], acc_2[2]))

                el += time_similarity
                el += media_similarity
                el = min(el, 100)

                similar = False
                if el >= filter_quality:
                    related_accounts[ind] = None
                    related_accounts[i] = None
                    similar = True
                    print(ind, i)

                similarity_percentage_round = round(int(el*100)/10)*10
                gender = ""
                age = ""
                if acc_1[4] == acc_2[4]:
                    gender = acc_1[4]

                if acc_1[5] == acc_2[5]:
                    age = acc_1[5]
                output_accs.append({"id": "_".join([str(ind), str(i)]), "name": accs[ind] + " & " + accs[i], "hours1": hours1, "hours2": hours2, "tfidf": min(99, tfidf*100)+1, "media": min(99, media_similarity*100)+1, "hours_sim": min(99, time_similarity*100)+1, "acc1_profile": accs[ind], "acc2_profile": accs[i], "similarity": similar, "similarity_percentage": int(el*100), "similarity_percentage_round": int(similarity_percentage_round), "gender": gender, "age": age})
    accounts = []
    x = 0
    for acc in tweets:
        if x in related_accounts:
            accounts.append(acc)
        x += 1

    context = {'name': 'Dashboard', "accs": output_accs, "profile_picture": accs_pictures}
    return render(request, 'home/index.html', context)


def input(request):
    html_template = loader.get_template('home/input.html')
    return HttpResponse(html_template.render({}, request))

def analyze(request):
    if request.method == "POST":
        process = request.POST["submit"]
        account = request.POST["account"]
        if process == "Tracking":
            print("track")
            return redirect("/track/" + account + "/")
        else:
            acc_dir = "Twitter-Accounts/Big_Analysis_" + account + "/"
            if os.path.isdir(acc_dir):
                return redirect("/track/" + account + "/")
            os.system("python3 big_analysis.py " + account + " > /dev/null 2>&1 &")
            return redirect("/input/")

def track(request, account):
    out = []
    accs_pictures = {}
    acc_dir = "Twitter-Accounts/Big_Analysis_" + account + "/"
    if os.path.isdir(acc_dir):
        accs = [f for f in listdir(acc_dir) if os.path.isdir(join(acc_dir, f))]
        for acc in accs[:-2]:
            file = join(acc_dir, acc) + "/data"
            image = join(acc_dir, acc) + "/logo"
            if isfile(file):
                with open(file, "r") as f:
                    out.extend(json.loads(f.read()))
                with open(image, "r") as f:
                    accs_pictures[acc] = f.read()
                    
        try:
            profile_picture = api.get_user(screen_name=account).profile_image_url.replace("normal", "bigger")
        except:
            profile_picture = "https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png"
        accs_pictures[account] = profile_picture
        context = {'name': account, "accs": out, "profile_picture": accs_pictures}
        return render(request, 'home/index.html', context)
    return redirect("/input/")

def pages(request):
    context = {}
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
