import asyncio
import os
from dotenv import load_dotenv
import praw

from telegram.ext import Application

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_POST_COUNT = int(os.getenv("REDDIT_POST_COUNT"))
REDDIT_SUBREDDIT = os.getenv("REDDIT_SUBREDDIT")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
    password=REDDIT_PASSWORD,
    username=REDDIT_USERNAME,
)
reddit.read_only = True


application = Application.builder().token(
    TELEGRAM_BOT_TOKEN).build()


async def checkRedditApi():
    send_ids = []
    try:
        with open(REDDIT_SUBREDDIT+".txt", "r") as f:
            send_ids = f.readlines()
    except FileNotFoundError:
        send_ids = []

    for submission in reddit.subreddit(REDDIT_SUBREDDIT).new(limit=REDDIT_POST_COUNT):
        # get newest reddit posts
        id = submission.id
        title = submission.title
        preview_url = submission.url
        if hasattr(submission, 'gallery_data'):
            media_id = submission.gallery_data['items'][0]['media_id']
            url = submission.media_metadata[media_id]['s']['u']
            preview_url = url.split("?")[0].replace("preview", "i")

        # check if it already has been send before
        if any(id == x.rstrip('\r\n') for x in send_ids):
            continue
            # send them through application.bot.send_message
        try:
            await application.bot.send_photo(TELEGRAM_CHAT_ID, preview_url,
                                             caption="""
{}
https://reddit.com/{}

""".format(title, id))
        except:
            pass

            # write id to a file
        with open(REDDIT_SUBREDDIT+".txt", "a+") as f:
            f.write(id + "\n")


async def main():
    async with application:
        await application.initialize()
        await checkRedditApi()
        await application.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
