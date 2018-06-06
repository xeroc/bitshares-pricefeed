# Price Feed Script for BitShares

## Installation 

Ubuntu 16.04 LTS

Start the installation

```
cd ~
pip3 install bitshares-pricefeed --user
```

Create config.yml
```
bitshares-pricefeed create
```

Add a feed producer name to the config.yml file just created
```
vim config.yml
# The producer name(s)
producer: your_witness_name
```

Enter Credentials

```
bitshares-pricefeed addkey
```

You will need to enter your cli wallet encryption passphrase. If you
don't have a pybitshares wallet, yet, one will be created:

```
Wallet Encryption Passphrase:
Repeat for confirmation:
```

You will need to enter your Private Key (Active key) here. Hit enter the second time it asks you.

```
Private Key (wif) [Enter to quit]:
```

Manually run the feed update

```
bitshares-pricefeed update
```

Create a place for a logfile

```
sudo touch /var/log/bitshare-pricefeed.log
sudo chown ubuntu /var/log/bitshare-pricefeed.log
```

Add to cron, where PASSWD is your Wallet Encryption Passphrase. This logic will send stdin and sterr to the logfile.

```
$ crontab -e

SHELL=/bin/bash
PATH=/home/ubuntu/bin:/home/ubuntu/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
UNLOCK="PASSWD"

0,15,30,45 * * * * bitshares-pricefeed --configfile /home/ubuntu/config.yml --skip-critical --no-confirm-warning update >> /var/log/bitshares-pricefeed.log 2>&1
```

## Help

```
# bitshares-pricefeed --help
Usage: bitshares-pricefeed [OPTIONS] COMMAND [ARGS]...

Options:
  --configfile TEXT
  --confirm-warning / --no-confirm-warning
                                  Need for manual confirmation of warnings
  --skip-critical / --no-skip-critical
                                  Skip critical feeds
  --help                          Show this message and exit.

Commands:
  addkey  Add a private key to the wallet
  create  Create config file
  update  Update price feed for assets
```

## Sources

The following data sources are currently avialable:

Name | Status | Assets type | API Key | Description
 --- | ---    | ---         | ---     |   ---
 AEX |  OK    |   Crypto    | No      | last and volume (in quote currency) from CEX ticker api with 15 sec delay 
Big.One | KO | Crypto | Yes | not implemented
BitcoinAverage | KO | Crypto | No | used API is deprecated not maintained anymore, need to be upgraded to ApiV2
Bitcoin Indonesia | KO | Crypto | No | not working anymore, API has changed
Bitcoin Venezuela | OK | Crypto | No | ticker from api with 15 minutes delay, no volume
Bitstamp | OK | Crypto | No | last and volume (in quote currency) from CEX ticker api
Bittrex | OK | Crypto | No | last and volume (in quote currency) from summary api (bulk)
ChBTC | WARN | Crypto | No | but price is wierd, seems shutdown? last and volume (in quote currency) from ticker api
Coincap | OK | ALTCAP & ALTCAP.X | No | use provided market cap, no volume
Coinmarketcap | OK | Crypto | No | volume weighted average of all prices reported at each market, volume in USD, 5 minutes delay (see https://coinmarketcap.com/faq/). TODO: Migrate to v2 before 30 November 2018
Currencylayer | OK | FIAT, BTC | Yes | ticker from api, only USD as base and hourly updated with free subscription, no volume info. From various source (https://currencylayer.com/faq)
Fixer | OK | FIAT | Yes |  Very similar to CurrencyLayer, ticker from api, daily from European Central Bank, only EUR with free subscription, no volume info.
Google | OK | FIAT, Stocks | No | 4d moving average with 1h scale of "last" price, no volume, 15 minutes delay
Graphene | OK | Crypto, FIAT, Stocks | No | last and volume (in quote currency) from Bitshares DEX in realtime
Huobi | KO | Crypto | No | not working anymore, API has changed
LBank | OK | Crypto | No | last and volume (in quote currency) from CEX API in realtime
OkCoin  | OK | Crypto | No | last and volume (in quote currency) from CEX API in realtime
OpenExchangeRates | OK | FIAT, BTC | Yes | ticker from api, only USD as base and hourly updated with free subscription, no volume info. From unknown sources except Bitcoin wich is from CoinDesk (https://openexchangerates.org/faq#sources)
Poloniex | OK | Crypto | No | last and volume (in quote currency) from CEX API in realtime
Quantl | OK | Commodities | Yes | daily price from London Bullion Market Association (LBMA), no volume
ZB | OK | Crypto | No |last and volume (in quote currency) from CEX API in realtime
AlphaVantage | OK | FIAT, Stocks, BTC | Yes | last from unknown source for currencies and from iex for stocks. volume only for stocks (in nb of shares).
IEX  | OK | Stocks | No | last ("IEX real time price", "15 minute delayed price", "Close" or "Previous close") and volume. 
RobinHood | OK | Stocks | No | last, no volume, from unknown source in real time
WorldCoinIndex | OK | Crypto | Yes| volume weighted price, sum of market volume.
BitsharesFeed | OK | Crypto (MPA) | No | current feed price in Bitshares DEX, no volume.


## Development

To run tests you need get API kays for the providers, and register them as environment variables:

```
export QUANDL_APIKEY=
export OPENEXCHANGERATE_APIKEY=
export FIXER_APIKEY=
export CURRENCYLAYER_APIKEY=
export ALPHAVANTAGE_APIKEY=
export WORLDCOININDEX_APIKEY= 
```

To run all tests use:  `pytest`.

To run a specific test: `pytest -k bitcoinvenezuela`.

# IMPORTANT NOTE

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
