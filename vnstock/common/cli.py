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



## INTERACTIVE CLI

# import click
# from vnstock import Vnstock
# import logging
# import click_repl

# # Configure logging to show only critical messages
# logging.basicConfig(level=logging.CRITICAL)

# @click.group(invoke_without_command=True)
# @click.pass_context
# def cli(ctx):
#     """VNStock CLI"""
#     ctx.ensure_object(dict)
#     if ctx.invoked_subcommand is None:
#         click_repl.repl(ctx, prompt_kwargs={'message': '> '})

# @cli.command()
# def quit():
#     """Quit the REPL"""
#     raise EOFError()

# @cli.command()
# def exit():
#     """Exit the REPL"""
#     raise EOFError()

# @cli.group()
# @click.option('--symbol', default=None, help='Stock symbol to retrieve data for.')
# @click.option('--source', default='VCI', help='Data source')
# @click.pass_context
# def stock(ctx, symbol, source):
#     """Commands related to stock data"""
#     ctx.obj['symbol'] = symbol
#     ctx.obj['source'] = source
#     ctx.obj['stock'] = Vnstock(source=source).stock(symbol=symbol)

# @stock.group()
# @click.pass_context
# def company(ctx):
#     """Company commands"""
#     ctx.obj['company'] = ctx.obj['stock'].company

# @company.command()
# @click.pass_context
# def overview(ctx):
#     """Get company overview"""
#     data = ctx.obj['company'].overview()
#     click.echo(data)

# @company.command()
# @click.pass_context
# def profile(ctx):
#     """Get company profile"""
#     data = ctx.obj['company'].profile()
#     click.echo(data)

# @company.command()
# @click.pass_context
# def shareholders(ctx):
#     """Get company shareholders"""
#     data = ctx.obj['company'].shareholders()
#     click.echo(data)

# @stock.group()
# @click.pass_context
# def finance(ctx):
#     """Finance commands"""
#     ctx.obj['finance'] = ctx.obj['stock'].finance

# @finance.command()
# @click.option('--period', default='quarter', help='Period of the financial statements')
# @click.option('--lang', default='en', help='Language of the financial statements')
# @click.pass_context
# def balance_sheet(ctx, period, lang):
#     """Get balance sheet"""
#     data = ctx.obj['finance'].balance_sheet(period=period, lang=lang)
#     click.echo(data)

# @finance.command()
# @click.option('--period', default='quarter', help='Period of the financial statements')
# @click.option('--lang', default='en', help='Language of the financial statements')
# @click.pass_context
# def income_statement(ctx, period, lang):
#     """Get income statement"""
#     data = ctx.obj['finance'].income_statement(period=period, lang=lang)
#     click.echo(data)

# @finance.command()
# @click.option('--period', default='quarter', help='Period of the financial statements')
# @click.option('--lang', default='en', help='Language of the financial statements')
# @click.pass_context
# def cash_flow(ctx, period, lang):
#     """Get cash flow"""
#     data = ctx.obj['finance'].cash_flow(period=period, lang=lang)
#     click.echo(data)

# @finance.command()
# @click.option('--lang', default='en', help='Language of the financial ratios')
# @click.pass_context
# def ratio(ctx, lang):
#     """Get financial ratios"""
#     data = ctx.obj['finance'].ratio(lang=lang)
#     click.echo(data)

# @stock.group()
# @click.pass_context
# def quote(ctx):
#     """Quote commands"""
#     ctx.obj['quote'] = ctx.obj['stock'].quote

# @quote.command()
# @click.option('--start', default=None, help='Start date for historical data')
# @click.option('--end', default=None, help='End date for historical data')
# @click.option('--interval', default='1D', help='Interval for historical data')
# @click.pass_context
# def history(ctx, start, end, interval):
#     """Get historical data"""
#     data = ctx.obj['quote'].history(start=start, end=end, interval=interval)
#     click.echo(data)

# if __name__ == '__main__':
#     cli()