# bkkcsirip

This is a rather rudimentary script that periodically checks the (not actually
public) [BKK notice API](http://www.bkk.hu/apps/bkkinfo/lista-api.php) and posts
about irregularities on Twitter. See it in action on the
[@bkkcsirip](https://twitter.com/bkkcsirip) Twitter account.

## Usage

The application requires a Redis instance so that it can determine which of the
notices is new or changed. The following environment variables are used for
configuration:

- **BKKCSIRIP_TWITTER_APP_KEY**
- **BKKCSIRIP_TWITTER_APP_SECRET**
- **BKKCSIRIP_TWITTER_USER_KEY**
- **BKKCSIRIP_TWITTER_USER_SECRET**
- **BKKCSIRIP_REDIS_URL** (optional): the URL for the Redis instance to use
  (default: `redis://localhost:6379/0`)
- **BKKCSIRIP_DATE_LOCALE** (optional): override the date locale used in the
  tweets
- **BKKCSIRIP_CHECK_INTERVAL** (optional): the amount of time to wait between
  checks, in seconds (default: `60`)
