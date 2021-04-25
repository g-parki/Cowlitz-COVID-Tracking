class Release:
        def __init__(self, datestring, href, cases):
            import datetime
            
            self.datestr = datestring
            self.datedate = datetime.datetime.strptime(datestring, "%m/%d/%Y").date()
            self.link =  href
            self.cases = cases

def SendMessage(msg):
    import os
    from twilio.rest import Client

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    message = client.messages.create(body= msg, from_='+13092049586',to='+13604423825')
    
    print(message.sid)

    return None

def SendErrorText(error):
        errormessage = error.args[0][0]['message']
        errorcode = error.args[0][0]['code']

        output = f"Error sending tweet. Code {errorcode}: {errormessage}"
        SendMessage(output)

def PostMediaTweet(filePath, textStatus):
    import tweepy
    import os

    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET_KEY = os.getenv('TWITTER_API_SECRET_KEY')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(TWITTER_API_KEY,TWITTER_API_SECRET_KEY)
    auth.set_access_token(TWITTER_ACCESS_TOKEN,TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    
    try:
        api.update_with_media(filePath, status= textStatus)
    except tweepy.TweepError as e:
        SendErrorText(e)