import tweepy
import re
import time
import random
import tracery
from tracery.modifiers import base_english
import pickle
import scraper
import logging

logging.basicConfig(filename='logging-twitterbot.log', filemode='w', format='%(asctime)s - [%(levelname)s] - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO) #TODO rimetti DEBUG)
log = logging.getLogger()

key = pickle.load(open("key.p", "rb"))
CONSUMER_KEY = key["CONSUMER_KEY"]
CONSUMER_SECRET = key["CONSUMER_SECRET"]
ACCESS_TOKEN = key["ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = key["ACCESS_TOKEN_SECRET"]
ACCOUNT_ID = key["ACCOUNT_ID"]

woeids = {
        "Canada": 23424775,
        "Ireland": 23424803,
        "UK": 23424975,
        "Australia": 23424748,
        "South Africa": 23424942,
        "United States": 23424775
    }

# dictionary that contains popular hashtags and not yet popular hashtags
try:
    hashtag = pickle.load(open("hashtags.p", "rb"))
    log.info("Loaded old hashtags.")
except Exception:
    hashtag = {"popular": [], "notYet": {}}


def get_trending_hashtags(api, tracery):
    for k in woeids.keys():
        r = api.trends_place(woeids[k])
        for el in r[0]["trends"]:
            # Check if is an hashtag
            if re.search("#[A-Za-z0-9]+", el["name"]) is not None:
                if el["name"] in hashtag["notYet"].keys():
                    # The given hashtag is already in the dictionary, so increase the counter
                    count = hashtag["notYet"][el["name"]][1]
                    hashtag["notYet"][el["name"]] = (time.time(), count + 1)
                else:
                    # The given hashtag is not in the dictionary, store it
                    hashtag["notYet"][el["name"]] = (time.time(), 1)

    tracery["_hashtag"] = hashtag["popular"] + ["\\" + x for x in hashtag["notYet"].keys()]
    return tracery


def delete_old_hashtags():
    """
    Revise the hashtags by promoting to popular those ones that appear more than 4 times and
    delete those that didn't become popular in 1 month
    """
    t = time.time()
    for h in hashtag["notYet"].keys():
        if hashtag["notYet"][h][1] > 4:
            hashtag["popular"].append("\\" + h)
            continue
        if t - hashtag["notYet"][h][0] > 2419200:  # the difference is greater than 1 month
            # This hashtag is not popular, delete it with a probability of 40%
            if random.random() < 0.4:
                hashtag["notYet"].pop(h)


def main():
    log.info("Start Twitterbot.")

    for i in range(3):
        try:
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
            api = tweepy.API(auth)
            log.info("Successful Twitter OAuth authentication.")
        except Exception as e:
            if i == 2:
                log.error("Error in authentication. No other attempt. End of program.\n"+e)
                exit(1)
            else:
                log.info("Error in authentication, new attempt.")

    # Load tracery
    try:
        rules_b = pickle.load(open("black_card_tracery.p", "rb"))
        log.info("Loaded BlackCard-tracery.")

        rules_w = pickle.load(open("white_card_tracery.p", "rb"))
        log.info("Loaded WhiteCard-tracery.")
    except Exception as e:
        log.error("Error while loading tracery.\n"+e)
        exit(1)

    grammar_b = tracery.Grammar(rules_b)
    grammar_b.add_modifiers(base_english)

    # Load Twitter username and password
    try:
        login = pickle.load(open("login.p", "rb"))
        log.info("Loaded Twitter credentials.")
    except Exception as e:
        log.error("Error while loading Twitter credentials.\n" + e)
        exit(1)

    t = time.time()
    while True:
        # Get trending hashtags
        rules_w = get_trending_hashtags(api, rules_w)
        log.info("Get trending hashtag.")

        pickle.dump(hashtag, open("hashtags.p", "wb"))
        log.info("Dumped hashtags.")

        pickle.dump(rules_w, open("white_card_tracery.p", "wb"))
        log.info("Dumped WhiteCard-tracery.")

        grammar_w = tracery.Grammar(rules_w)
        grammar_w.add_modifiers(base_english)

        choices = grammar_w.flatten("#origin#").split(" -*- ")
        less_than_25 = True
        for c in choices:
            if len(c) > 25:
                less_than_25 = False
                break

        if less_than_25:
            log.info("Posting Twitter Poll.")

            # Post the Twitter Poll
            # Start a driver for a web browser
            driver = scraper.init_driver()

            try:
                # Log in to Twitter
                username = login["username"]
                password = login["password"]
                scraper.login_twitter(driver, username, password)

                log.info("Successfull Twitter login.")

                scraper.make_poll(driver, grammar_b.flatten("#origin#"), choices[0], choices[1], choices[2], choices[3])
                log.info("Successfull post.")
            except Exception as e:
                log.error("Error while posting twitter poll.\n" + e)
            finally:
                # Close the driver:
                scraper.close_driver(driver)
        else:
            log.info("Posting simple tweet.")
            # Post a Tweet
            try:
                api.update_status(grammar_b.flatten("#origin#") + "\nA) " + choices[0] + "\nB) " + choices[1] + "\nC) " + choices[2] + "\nD) " + choices[3])
                log.info("Successfull post.")
            except Exception as e:
                log.error("Error while posting simple tweet.\n" + e)

        delete_old_hashtags()
        log.info("Revised hashtags.")

        if time.time() - t < 86400:  # 1 day
            log.info("Sleep for " + str(86400 - (time.time() - t)) + "s")
            time.sleep(86400 - (time.time() - t))
        t = time.time()


if __name__ == "__main__":
    main()
