import twitter
import dataset


def setup_db(connection_string):
    db = dataset.connect(connection_string)

    connections = db['connection']
    users = db['user']
    tweets = db['tweet']
    medias = db['media']
    mentions = db['mention']
    urls = db['url']
    hashtags = db['hashtag']

    tweets.create_index(['tweet_id'])
    medias.create_index(['tweet_id'])
    mentions.create_index(['user_id'])
    mentions.create_index(['mentioned_user_id'])
    urls.create_index(['tweet_id'])
    hashtags.create_index(['tweet_id'])
    users.create_index(['user_id'])
    connections.create_index(['friend_id'])
    connections.create_index(['follower_id'])

    return db


def insert_if_missing(db, user_ids=[], is_seed=False):
    user_table = db['user']
    if is_seed:
        is_seed = 1
    else:
        is_seed = 0

    for _id in user_ids:
        user = user_table.find_one(user_id=_id)

        if not user:
            data = dict(user_id=_id, profile_collected=0, is_scored=0,
                        followers_collected=0, friends_collected=0,
                        tweets_collected=0, is_seed=is_seed)
            user_table.insert(data, ensure=True)


def setup_seeds(db, consumer_key, consumer_secret, access_key,
                access_secret, screen_names=[], user_ids=[]):
    kwargs = {
        'include_entities': False
    }

    if screen_names:
        kwargs['screen_name'] = screen_names
    elif user_ids:
        kwargs['user_id'] = user_ids
    else:
        return None

    api = get_api(consumer_key, consumer_secret, access_key, access_secret)
    profiles = api.UsersLookup(**kwargs)
    new_user_ids = [p.id for p in profiles]

    insert_if_missing(db, new_user_ids, is_seed=True)


def get_api(consumer_key, consumer_secret, access_key, access_secret):
    api = twitter.Api(consumer_key=consumer_key,
                      consumer_secret=consumer_secret,
                      access_token_key=access_key,
                      access_token_secret=access_secret,
                      sleep_on_rate_limit=True)
    return api
