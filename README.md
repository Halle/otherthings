## otherthings

**otherthings** is a python script, intended to be run in the terminal, which I wrote to scratch a very specific itch: what are the major routes by which I find myself checking Twitter when I would prefer to be on a break, and what are the most minimal-possible accomodations to them?

The most consistent way that breaks are subverted is via a desire not to be rude to an acquaintance who DMs me. I get an email notification of a DM, it's someone whose email I don't know, and I have to log in to answer. I've always wanted a way to respond to these DM email notifications via email, but I like this even better: you can just send a DM without line breaks from the command line. It's the perfect way to just let someone know you're on a break but would be happy to talk to them via email, or slow-chat with them from the command line in a minimal way that keeps you out of your timeline. This is otherthings' "dm" argument.

The related issue is if you worry that someone might mention you on Twitter in a way you'd rather not be oblivious to (otherthings' "act" argument shows you recent activity including mentions), and perhaps should respond to ("dm" is the proposed way to do this, assuming it's someone you can DM).

The less-flattering runners-up to these two big routes are the usual ego stuff: do I have new followers/unfollowers, are people liking my last pre-break tweets. otherthings' "foll" argument shows changes in your followers and saves those changes to a history file since they way it calculates this is transient and non-repeatable (foll is short for both followers and folly), and "act" shows your recent tweets and their likes.

## Requirements

You need an approved Twitter developer account (get one at https://developer.twitter.com) and an app in that account that is able to log in, and will give you the keys and secrets needed to do these operations from your local machine. 

That means that you also need a website you can enter into the Twitter developer application process (I think saying you're a hobbyist should be sufficient for this app) and enter into the various app fields which require a site. 

Once you have this set up, the script operates under the expectation that those values are exported environmental variables, along with an environmental variable which is the name of your account. 

You also need to install the Python Twitter library Tweepy. I used Python and Tweepy 3.6. In the 1.0 version, Tweepy needs a patch, which is described at the top of the script file.

## Philosophy

I wrote this on a Sunday morning (yesterday morning, at the time of writing this README for the first time) and the goals were that the script should be entirely self-contained and the most maintainably-minimal implementation of the requirements, i.e. no stack, no hosting, no structured data or data persistence, and that it should be manually run by the person whose account it is intended to check, only when they feel the need. That is the reason for decisions like using text files for transient data operations and keeping a textual history. 

I would consider it more of a success if I never altered it again and just enjoyed its simplicity than if it got more features – the perfect Sunday-morning fix to a real problem. The more features it gets, the more likely it is to become something similar to a CLI Twitter client, which defeats the goal of taking a break, even if it's cute.

The other philosophical feeling is that these are things you shouldn't easily trust others to do on your behalf, so this keeps a 1:1 relationship between the party responsible for the Twitter developer app and the party whose account the script operates.

I guess the strongest philosophical position here is that I think it's the Twitter timeline that human brains need a break from, but that it's personal connections and ego desires that are the vectors that get us back in front of that timeline, so those are the things that a tool for taking a break should gently, but very minimally, accomodate.

## Assumptions

My Twitter account has been immovably fixed at about 930 followers for several years now. Apparently everyone who enjoys my writing and preoccupations on Twitter already knows about them 😂 . That means that this script could have very different implications for someone with a lot of followers or more dm activity or any number of different usages from my genx, not-especially-social-media-compatible self. I'm pretty sure at least that the sleep times for paging through follower lists would have to be increased, but there are probably other assumption mismatches.

## Usage

run `python otherthings.py help` to see usage. If you want to see old follower/unfollower info, it is stored in a file generated at the same level as the script which is called followchangeshistory.txt. It should be ignored by the .gitignore along with the other text files the script creates.

## Why is it called otherthings?

That's what you'll think about instead of the things in the Twitter timeline.
