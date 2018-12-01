import tweepy
import os
import sys
import time
import threading

# Note: At the initial time of this writing (November 2018), tweepy required this patch:
# https://github.com/tweepy/tweepy/issues/1081#issuecomment-423486837 and this PR:
# https://github.com/tweepy/tweepy/pull/1109
# The original version of this script was written for Python 3.6.7.


def main():
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_token_secret = ""
    my_account = ""

# These have to be exported to your environment. The keys and secrets are
# available in your Twitter developer account app settings, and you should
# know the username of your Twitter account.
    envvarlist = (
        'TWITTER_CONSUMER_KEY',
        'TWITTER_CONSUMER_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'MY_TWITTER_ACCOUNT'
        )
    for envvar in envvarlist:
        if envvar not in os.environ:  # Exit if any of there aren't available.
            print(f"Script requires environmental variable {envvar}, exiting.")
            exit(-1)
        else:
            consumer_key = os.environ['TWITTER_CONSUMER_KEY']  # Otherwise set.
            consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
            access_token = os.environ['TWITTER_ACCESS_TOKEN']
            access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
            my_account = os.environ['MY_TWITTER_ACCOUNT']
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)  # Authorize,
        auth.set_access_token(access_token, access_token_secret)  # Set token,
        api = tweepy.API(auth)  # Get an API connection.

        if len(sys.argv) == 1:  # The script requires an argument, hint here.
            print("This script needs one argument. Try \"help\" for options.")
            exit(-1)
        if str(sys.argv[1]) == "help":  # Read help,
            show_help()
        if str(sys.argv[1]) == "dm":  # Send a DM to someone,
            send_dm(api)
        if str(sys.argv[1]) == "foll":  # See if there were follower changes.
            show_followers_and_unfollowers(api, my_account)
        if str(sys.argv[1]) == "act":  # See limited activity.
            show_activity(api, my_account)
    except Exception as e:
        print(f"Exception: {e}")


def show_help():
    help_message = """
otherthings can be run with the following arguments:
"otherthings.py help" --> shows this message.
"otherthings.py dm" --> interactively sends a DM.
"otherthings.py foll" --> shows new followers and unfollowers.
"otherthings.py act" --> shows a limited activity report.
"""
    print(f"{help_message}")


# This will change for the better if Tweepy updates to the new Twitter DM API.
def send_dm(api):
    print("Sending a DM.")
    username = input("Username to DM: ")
    if len(username) > 0:
        message = input(f"Message to send to {username}: ")
        if len(message) > 0:
            confirmation = input(
                f"Type \"y\" to send {username} the message \"{message}\": "
                )
            if confirmation == "y":
                print("Sending DM.")
                try:
                    user = api.get_user(screen_name=username)
                    event = {
                        "event": {
                            "type": "message_create",
                            "message_create": {
                                "target": {
                                    "recipient_id": user.id
                                },
                                "message_data": {
                                    "text": message
                                }
                            }
                        }
                    }
                    api.send_direct_message_new(event)

                except Exception as e:
                    print(f"Exception while sending DM: {e}")
            else:
                print("\"y\" wasn't typed; exiting without sending message.")
        else:
            print("Sorry, that message was too short.")
    else:
        print("Sorry, that name was too short.")


def show_followers_and_unfollowers(api, account):

    new_follower_list_file = os.path.join(
        sys.path[0], 'newlist.txt')  # For new results
    old_follower_list_file = os.path.join(
        sys.path[0], 'oldlist.txt')  # For old results
    follow_changes_history_file = os.path.join(
        sys.path[0], 'followchangeshistory.txt')  # For results over time.

    spinner = Spinner()  # Some visual feedback that we're working.
    spinner.start()

    try:
        ids = []
        # Get current followers for the user, as ID numbers.
        for page in tweepy.Cursor(api.followers_ids, screen_name=account).pages():
                ids.extend(page)
                # Don't hit the API too fast. For accounts with many followers,
                # this may need to be increased as much as 60s.
                time.sleep(1)

        with open(new_follower_list_file, 'w') as file:  # Write out new results.
            for id in ids:
                file.write("%s\n" % id)
        file.close()

    except Exception as e:
        print(f"Exception: {e}")
        spinner.stop()
    # If there is an old follower list file, see if it can be opened.
    if os.path.isfile(old_follower_list_file):
        try:
            open(old_follower_list_file)
            pass
        except IOError as e:
            print(f"Unable to open old follower list file: {e}.")
            spinner.stop()
    else:
        # If there isn't an old one, create one with the same info in the new one.
        print("No file at the old follower list location, creating one.")
        with open(old_follower_list_file, 'w') as file:
            for id in ids:
                file.write("%s\n" % id)
        file.close()

    try:
        old_id_set = set(line.strip() for line in open(
            old_follower_list_file))  # Now for some set math. A set of the old IDs,
        new_id_set = set(line.strip() for line in open(
            new_follower_list_file))  # A set of the new IDs.
        # Unfollowers are IDs found only in the old file set:
        unfollowers = (old_id_set - new_id_set)
        # New followers are IDs found only in the new file set:
        followers = (new_id_set - old_id_set)

        # Let's only do work here if the sets aren't equal.
        if old_id_set != new_id_set:
            # We'll concatenate a nice status report for the end of this operation,
            # and the history file.
            status_report = ""
            status_report += f"\nFollow changes as of {time.ctime()}:\n"
            # If the followers set isn't equal to an empty set, report on its contents:
            if followers != set():
                status_report += lookup_user_for_list(api, False, followers)
            # If the unfollowers set isn't equal to an empty set, report on its contents:
            if unfollowers != set():
                status_report += lookup_user_for_list(api, True, unfollowers)
            # Write out the status report to the history file:
            with open(follow_changes_history_file, 'a', encoding='utf-8') as file:
                file.write(status_report)
                file.close
            print(status_report)  # Share the completed status report.
        else:
            print("\nThere were no follow changes.")
        # When we get through this successfully, remove the old list
        # and rename the new list to the old list.
        os.remove(old_follower_list_file)
        os.rename(new_follower_list_file, old_follower_list_file)

    except Exception as e:
        print(f"Exception: {e}")
        spinner.stop()
    spinner.stop()


def lookup_user_for_list(api, isUnfollowerList, followers):
    status_report_title = "-- New Unfollowers:\n" if isUnfollowerList else "-- New Followers:\n"
    status_report_additions = status_report_title
    for follower in followers:  # Append usernames to status report string.
        try:
            real_name = get_name_for_id(api, follower, None)
        except Exception as e:
            real_name = "RemovedUser" # When Twitter removes an account, no user.
            pass
        status_report_additions += f"---- {real_name}\n"
    return status_report_additions

def show_activity(api, account):
    try:
        print("Mentions:")
        mentions = api.mentions_timeline(10)
        for mention in mentions:
            text = mention.text.replace("\n", " ")
            print(f"-- {mention.user.name}: {text}")
        print("\nMy tweets:")
        tweets = api.user_timeline(screen_name=account, count=10)
        for tweet in tweets:
            text = tweet.text.replace("\n", " ")
            print(f"-- {text}")
            print(f"---- {tweet.favorite_count} favorites, {tweet.retweet_count} retweets")
        dms = api.direct_messages(count=10) # This API from the patch appears to need a little work.
        print("\nLast DMs:")
        username_cache_dictionary = {}
        for dm in dms:
            for event in dm.events:
                try:
                    message_text = event['message_create']['message_data']['text']
                    message_sender = event['message_create']['sender_id']
                    message_recipient = event['message_create']['target']['recipient_id']
                    sender_name = get_name_for_id(api, message_sender, username_cache_dictionary)
                    if not message_sender in username_cache_dictionary:
                        username_cache_dictionary[message_sender] = sender_name
                    recipient_name = get_name_for_id(api, message_recipient, username_cache_dictionary)
                    if not message_recipient in username_cache_dictionary:
                        username_cache_dictionary[message_recipient] = recipient_name
                    text = message_text.replace("\n", " ")
                    print(f"{sender_name} --> {recipient_name}: \"{text}\"")
                except KeyError: # Let's not stop for a key error.
                    print(f"There was an error getting a direct message, continuing.")
                    pass
            break # Stop after one since this data is repeated.
    except Exception as e:
        print(f"Exception: {e}")


def get_name_for_id(api, id, optional_username_cache_dictionary):
    if optional_username_cache_dictionary is not None:
        if id in optional_username_cache_dictionary:
            return optional_username_cache_dictionary[id]
    user = api.get_user(id)
    name = user.screen_name
    time.sleep(1)
    return name


class Spinner:  # https://stackoverflow.com/a/39504463/119717 (MIT)
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\':
                yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay):
            self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)


if __name__ == "__main__":
    main()
