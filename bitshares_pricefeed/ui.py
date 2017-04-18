from datetime import datetime
from bitshares.price import Price
from prettytable import PrettyTable
import click


def priceChange(new, old):
    if float(old) == 0.0:
        return -1
    else:
        percent = ((float(new) - float(old))) / float(old) * 100
        if percent >= 0:
            return click.style("%.2f" % percent, fg="green")
        else:
            return click.style("%.2f" % percent, fg="red")


def formatPrice(f):
    return click.style("%f.10" % f, fg="yellow")


def formatStd(f):
    return click.style("%.2f" % f, bold=True)


def print_prices(feeds):
    t = PrettyTable([
        "symbol", "collateral",
        "new price", "cer",
        "mean", "median", "wgt. avg.",
        "wgt. std (#)", "blockchain",
        "mssr", "mcr",
        "my last price", "last update",
    ])
    t.align = 'c'
    t.border = True

    for symbol, feed in feeds.items():
        myprice = feed["price"]
        blockchain = float(Price(feed["global_feed"]["settlement_price"]))
        last = float(feed["current_feed"]["settlement_price"])
        age = (str(datetime.utcnow() - feed["current_feed"]["date"]))
        # Get Final Price according to price metric
        t.add_row([
            symbol,
            ("%s") % (feed["short_backing_symbol"]),
            ("%s" % formatPrice(feed["price"])),
            ("%s" % formatPrice(feed["cer"])),
            ("%s (%s)" % (formatPrice(feed["mean"]), priceChange(myprice, feed.get("mean")))),
            ("%s (%s)" % (formatPrice(feed["median"]), priceChange(myprice, feed.get("median")))),
            ("%s (%s)" % (formatPrice(feed["weighted"]), priceChange(myprice, feed.get("weighted")))),
            ("%s (%2d)" % (formatStd(feed["std"]), feed.get("number"))),
            ("%s (%s)" % (formatPrice(blockchain), priceChange(myprice, blockchain))),
            ("%.1f%%" % feed["mssr"]),
            ("%.1f%%" % feed["mcr"]),
            ("%s (%s)" % (formatPrice(last), priceChange(myprice, last))),
            age + " ago"
        ])
    print(t.get_string())


def warning(msg):
    click.echo(
        "[" +
        click.style("Warning", fg="yellow") +
        "] " + msg
    )


def confirmwarning(msg):
    return click.confirm(
        "[" +
        click.style("Warning", fg="yellow") +
        "] " + msg
    )


def alert(msg):
    click.echo(
        "[" +
        click.style("alert", fg="yellow") +
        "] " + msg
    )


def confirmalert(msg):
    return click.confirm(
        "[" +
        click.style("Alert", fg="red") +
        "] " + msg
    )
