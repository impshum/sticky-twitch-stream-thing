from requests import get
from time import sleep
import praw

twitch_client_id = 'XXXX'
target_user = 'XXXX'

client_id = 'XXXX'
client_secret = 'XXXX'
reddit_user = 'XXXX'
reddit_pass = 'XXXX'
target_sub = 'XXXX'


reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent='Sticky Twitch Stream Thing (by /u/impshum)',
                     username=reddit_user,
                     password=reddit_pass)

start_time = ''
stickied_id = ''


def set_start_time(started):
    global start_time
    start_time = started


def set_stickied_id(id):
    global stickied_id
    stickied_id = id


def set_sticky(stickied_id):
    submission = reddit.submission(id=stickied_id)
    submission.mod.sticky()


def find_stickiness():
    for post in reddit.subreddit(target_sub).new(limit=100):
        if post.stickied or post.title.startswith(f'{target_user} started playing'):
            id = post.id
            reddit.submission(id=id).delete()
            set_stickied_id('')
            print('deleted')


def get_stream():
    data = get(f'https://api.twitch.tv/kraken/streams/{target_user}?client_id={twitch_client_id}').json()
    if data['stream'] and data['stream']['stream_type'] == 'live':
        started = data['stream']['created_at'][11:-4]
        if started != start_time:
            id = data['stream']['_id']
            game = data['stream']['game']
            name = data['stream']['channel']['display_name']
            url = data['stream']['channel']['url']

            if len(stickied_id):
                reddit.submission(id=stickied_id).delete()

            msg = f'{name} started playing {game} at {started}'
            posted = reddit.subreddit(target_sub).submit(msg, url=url)
            set_stickied_id(posted)
            set_start_time(started)
            set_sticky(stickied_id)
            print(msg)
        else:
            print('Already done')
    else:
        print('Not streaming')
        if len(stickied_id):
            find_stickiness()


def main():
    find_stickiness()
    while 1:
        get_stream()
        sleep(30)


if __name__ == '__main__':
    main()
