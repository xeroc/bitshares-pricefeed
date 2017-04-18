#!/usr/bin/env python3

import click
import yaml
import logging
from pprint import pprint
from functools import update_wrapper
from bitshares import BitShares
from bitshares.instance import set_shared_bitshares_instance
from bitshares.price import Price
from .pricefeed import Feed
from . import ui
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
        ctx.bitshares = BitShares(bundle=True, **ctx.obj)
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


@click.group()
@click.option(
    "--configfile",
    default="config.yml",
    type=click.File('r'),
)
@click.option(
    "--confirm-warning/--no-confirm-warning",
    help="Need for manual confirmation of warnings",
    default=True,
)
@click.option(
    "--skip-critical/--no-skip-critical",
    help="Skip critical feeds",
    default=False,
)
@click.pass_context
def main(ctx, **kwargs):
    ctx.obj = {}
    for k, v in kwargs.items():
        ctx.obj[k] = v
    ctx.obj["config"] = yaml.load(kwargs["configfile"])


@main.command()
@click.argument(
    "assets",
    nargs=-1,
    required=False,
)
@click.pass_context
@chain
def update(ctx, assets):
    feed = Feed(config=ctx.obj["config"])
    feed.fetch()
    feed.derive(assets)
    prices = feed.get_prices()
    ui.print_prices(prices)

    for symbol, price in prices.items():
        flags = price["flags"]

        # Prices that don't move sufficiently, or are not too old, can
        # be skipped right away
        if "min_change" not in flags and "over_max_age" not in flags:
            continue

        if (
            ctx.obj["confirm_warning"] and
            "over_warn_change" in flags and
            "skip_change" not in flags
        ):
            if not ui.confirmwarning(
                "Price change for %s has been above 'warn_change'. Please confirm!" % symbol
            ):
                continue

        if "skip_change" in flags:
            if ctx.obj["skip_critical"]:
                ui.alert(
                    "Price change for %s has been above 'skip_change'. Skipping!" % symbol
                )
            else:
                if not ui.confirmalert(
                    "Price change for %s has been above 'skip_change'. Please confirm to still publish, else feed will be skipped!" % symbol
                ):
                    pass
                else:
                    continue

        settlement_price = Price(price["price"], quote=symbol, base=price["short_backing_symbol"])
        cer = Price(price["cer"], quote=symbol, base=price["short_backing_symbol"])
        ctx.bitshares.publish_price_feed(
            symbol,
            settlement_price=settlement_price,
            cer=cer,
            mssr=price["mssr"],
            mcr=price["mcr"],
            account=ctx.obj["config"]["producer"]
        )

    ctx.bitshares.txbuffer.broadcast()


if __name__ == '__main__':
    main()
