import click
import logging
import yaml
from datetime import datetime
from bitshares.price import Price
from prettytable import PrettyTable
from functools import update_wrapper
from bitshares import BitShares
from bitshares.instance import set_shared_bitshares_instance
log = logging.getLogger(__name__)


def verbose(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        global log
        verbosity = [
            "critical", "error", "warn", "info", "debug"
        ][int(min(ctx.obj.get("verbose", 0), 4))]
        log.setLevel(getattr(logging, verbosity.upper()))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, verbosity.upper()))
        ch.setFormatter(formatter)
        log.addHandler(ch)

        # GrapheneAPI logging
        if ctx.obj["verbose"] > 4:
            verbosity = [
                "critical", "error", "warn", "info", "debug"
            ][int(min(ctx.obj.get("verbose", 4) - 4, 4))]
            log = logging.getLogger("grapheneapi")
            log.setLevel(getattr(logging, verbosity.upper()))
            log.addHandler(ch)

        if ctx.obj["verbose"] > 8:
            verbosity = [
                "critical", "error", "warn", "info", "debug"
            ][int(min(ctx.obj.get("verbose", 8) - 8, 4))]
            log = logging.getLogger("graphenebase")
            log.setLevel(getattr(logging, verbosity.upper()))
            log.addHandler(ch)

        return ctx.invoke(f, *args, **kwargs)
    return update_wrapper(new_func, f)


def chain(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        ctx.bitshares = BitShares(
            ctx.config["node"],
            bundle=True,   # We bundle many feeds into a single tx
            **ctx.obj
        )
        set_shared_bitshares_instance(ctx.bitshares)
        return ctx.invoke(f, *args, **kwargs)
    return update_wrapper(new_func, f)


def unlock(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        if not ctx.obj.get("unsigned", False):
            if ctx.bitshares.wallet.created():
                pwd = click.prompt("Current Wallet Passphrase", hide_input=True)
                ctx.bitshares.wallet.unlock(pwd)
            else:
                click.echo("No wallet installed yet. Creating ...")
                pwd = click.prompt("Wallet Encryption Passphrase", hide_input=True, confirmation_prompt=True)
                ctx.bitshares.wallet.create(pwd)
        return ctx.invoke(f, *args, **kwargs)
    return update_wrapper(new_func, f)


def configfile(f):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        ctx.config = yaml.load(open(ctx.obj["configfile"]))
        return ctx.invoke(f, *args, **kwargs)
    return update_wrapper(new_func, f)


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
    return click.style("%.10f" % f, fg="yellow")


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
        if "current_feed" in feed and feed["current_feed"]:
            last = float(feed["current_feed"]["settlement_price"])
            age = (str(datetime.utcnow() - feed["current_feed"]["date"]))
        else:
            last = -1.0
            age = "unknown"
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
