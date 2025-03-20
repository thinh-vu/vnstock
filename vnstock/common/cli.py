## WORKS
## sample command: stock quote history --symbol ACB --start 2024-01-02 --end 2024-07-10 --interval 1D

import click
from vnstock import Vnstock
import logging
import click_repl

# Configure logging to show only critical messages
logging.basicConfig(level=logging.CRITICAL)

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """VNStock CLI"""
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        click_repl.repl(ctx, prompt_kwargs={'message': '> '})

@cli.command()
def quit():
    """Quit the REPL"""
    raise EOFError()

@cli.command()
def exit():
    """Exit the REPL"""
    raise EOFError()

@cli.group()
@click.pass_context
def stock(ctx):
    """Commands related to stock data"""
    pass

@stock.group()
@click.option('--source', default='VCI', help='Data source')
@click.pass_context
def quote(ctx, source):
    """Quote commands"""
    ctx.obj['source'] = source

@quote.command()
@click.option('--symbol', required=True, help='Stock symbol to retrieve data for.')
@click.option('--start', required=True, help='Start date for historical data')
@click.option('--end', required=True, help='End date for historical data')
@click.option('--interval', default='1D', help='Interval for historical data')
@click.pass_context
def history(ctx, symbol, start, end, interval):
    """Get historical data"""
    source = ctx.obj['source']
    quote = Vnstock(source=source).stock(symbol=symbol).quote
    data = quote.history(start=start, end=end, interval=interval)
    click.echo(data)

if __name__ == '__main__':
    cli()