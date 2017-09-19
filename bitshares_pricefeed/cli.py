#!/usr/bin/env python3

import click
import os
import logging
from pprint import pprint
from bitshares.price import Price
from .pricefeed import Feed
from uptick.decorators import (
    verbose,
    chain,
    unlock,
)
from .ui import (
    configfile,
    print_prices,
    confirmwarning,
    confirmalert,
    alert,
)
log = logging.getLogger(__name__)


@click.group()
@click.option(
    "--configfile",
    default="config.yml",
    # type=click.File('r'),
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


@main.command()
@click.argument(
    "example",
    default="default"
)
@click.pass_context
def create(ctx, example):
    """ Create config file
    """
    import shutil
    this_dir, this_filename = os.path.split(__file__)
    default_config_file = os.path.join(this_dir, "examples", example + ".yaml")
    config_file = ctx.obj["configfile"]
    shutil.copyfile(
        default_config_file,
        config_file
    )
    click.echo("Config file created: %s" % config_file)


@main.command()
@click.argument(
    "assets",
    nargs=-1,
    required=False,
)
@click.pass_context
@configfile
@chain
@unlock
def update(ctx, assets):
    """ Update price feed for assets
    """
    feed = Feed(config=ctx.config)
    feed.fetch()
    feed.derive(assets)
    prices = feed.get_prices()
    print_prices(prices)

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
            if not confirmwarning(
                "Price change for %s (%f) has been above 'warn_change'.  Please confirm!" % (
                    symbol,
                    price["priceChange"]
                )
            ):
                continue

        if "skip_change" in flags:
            if ctx.obj["skip_critical"]:
                alert(
                    "Price change for %s (%f) has been above 'skip_change'.  Skipping!" % (
                        symbol,
                        price["priceChange"],
                    )
                )
                continue
            else:
                if not confirmalert(
                    "Price change for %s (%f) has been above 'skip_change'. Please confirm to still publish, else feed will be skipped!" % (
                        symbol,
                        price["priceChange"],
                    )
                ):
                    continue

        settlement_price = Price(price["price"], quote=symbol, base=price["short_backing_symbol"])
        cer = Price(price["cer"], quote=symbol, base=price["short_backing_symbol"])
        ctx.bitshares.publish_price_feed(
            symbol,
            settlement_price=settlement_price,
            cer=cer,
            mssr=price["mssr"],
            mcr=price["mcr"],
            account=ctx.config["producer"]
        )

    # Always ask for confirmation if this flag is set to true
    if "confirm" in ctx.config and ctx.config["confirm"]:
        ctx.bitshares.txbuffer.constructTx()
        pprint(ctx.bitshares.txbuffer.json())
        if not confirmwarning(
            "Please confirm"
        ):
            return

    if ctx.bitshares.txbuffer.ops:
        ctx.bitshares.txbuffer.broadcast()


if __name__ == '__main__':
    main()
