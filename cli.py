import argparse
import sys
import pandas as pd
from datetime import datetime
from src.data.incremental_loader import IncrementalLoader
from src.engine.backtester import Backtester
from src.strategy.sma_cross import SMACrossStrategy
from src.strategy.rsi_reversal import RSIReversalStrategy
from src.strategy.bb_meanrev import BBMeanReversionStrategy
from src.report.metrics import calculate_metrics
from src.report.plots import plot_equity_curve, plot_drawdown
from src.report.summary import compare_results

STRATEGIES = {
    'sma_cross': SMACrossStrategy,
    'rsi_reversal': RSIReversalStrategy,
    'bb_meanrev': BBMeanReversionStrategy
}

def get_strategy(name, args):
    if name == 'sma_cross':
        return SMACrossStrategy(fast=args.fast, slow=args.slow)
    elif name == 'rsi_reversal':
        return RSIReversalStrategy(rsi_period=args.rsi_period, oversold=args.oversold, overbought=args.overbought)
    elif name == 'bb_meanrev':
        return BBMeanReversionStrategy(bb_period=args.bb_period, bb_std=args.bb_std, exit_mode=args.bb_exit_mode)
    else:
        raise ValueError(f"Unknown strategy: {name}")

def run_backtest(loader, exchange, symbol, timeframe, since, until, strategy_name, strategy_obj, args):
    # Fetch Data
    # Fix: convert 'since' to required format if needed
    if len(since) == 10: since += ' 00:00:00'
    if until and len(until) == 10: until += ' 00:00:00'
    
    df = loader.fetch_data(symbol, timeframe, since, until)
    if df.empty:
        print(f"No data found for {symbol} {timeframe}")
        return None

    # Init Backtester
    backtester = Backtester(
        initial_capital=args.cash,
        fee=args.fee,
        slippage=args.slippage,
        position_size_pct=args.position_size,
        stop_loss_pct=args.stop_loss,
        take_profit_pct=args.take_profit
    )
    
    # Run
    equity_curve = backtester.run(df, strategy_obj)
    
    # Metrics
    metrics = calculate_metrics(equity_curve, backtester.trades, args.cash)
    metrics['strategy'] = strategy_name
    metrics['timeframe'] = timeframe
    metrics['symbol'] = symbol
    
    return metrics, equity_curve, backtester.trades

def command_run(args):
    loader = IncrementalLoader()
    strategy = get_strategy(args.strategy, args)
    
    print(f"Running {args.strategy} on {args.symbol} {args.timeframe}...")
    result = run_backtest(loader, args.exchange, args.symbol, args.timeframe, args.since, args.until, args.strategy, strategy, args)
    
    if result:
        metrics, equity_curve, trades = result
        print("\n--- Results ---")
        for k, v in metrics.items():
            if isinstance(v, float):
                print(f"{k}: {v:.4f}")
            else:
                print(f"{k}: {v}")
                
        if not args.no_plot:
            plot_equity_curve(equity_curve, title=f"{args.strategy} - {args.symbol} {args.timeframe}")
            plot_drawdown(equity_curve, title=f"Drawdown - {args.strategy}")

def command_batch(args):
    loader = IncrementalLoader()
    strategy = get_strategy(args.strategy, args)
    timeframes = args.timeframes.split(',')
    
    results = []
    
    for tf in timeframes:
        tf = tf.strip()
        print(f"Running {args.strategy} on {tf}...")
        res = run_backtest(loader, args.exchange, args.symbol, tf, args.since, args.until, args.strategy, strategy, args)
        if res:
            metrics, _, _ = res
            results.append(metrics)
            
    if results:
        df_results = compare_results(results)
        print("\n--- Batch Results ---")
        print(df_results.to_string())

def command_compare(args):
    loader = IncrementalLoader()
    strategies = args.strategies.split(',')
    
    timeframes = args.timeframes.split(',') if args.timeframes else [args.timeframe]
    
    results = []
    
    for str_name in strategies:
        str_name = str_name.strip()
        strategy = get_strategy(str_name, args)
        
        for tf in timeframes:
            tf = tf.strip()
            print(f"Running {str_name} on {tf}...")
            res = run_backtest(loader, args.exchange, args.symbol, tf, args.since, args.until, str_name, strategy, args)
            if res:
                metrics, _, _ = res
                results.append(metrics)
                
    if results:
        df_results = compare_results(results)
        print("\n--- Comparison Ranking ---")
        print(df_results.to_string())
        
        if args.export:
            df_results.to_csv(args.export, index=False)
            print(f"\nSaved results to {args.export}")

def main():
    parser = argparse.ArgumentParser(description='Crypto Spot Backtester')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Common Arguments
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument('--exchange', default='binance', help='Exchange ID (default: binance)')
    common_parser.add_argument('--symbol', default='BTC/USDT', help='Symbol (default: BTC/USDT)')
    common_parser.add_argument('--since', required=True, help='Start date (YYYY-MM-DD HH:MM:SS)')
    common_parser.add_argument('--until', help='End date (YYYY-MM-DD HH:MM:SS)')
    common_parser.add_argument('--cash', type=float, default=10000, help='Initial capital')
    common_parser.add_argument('--fee', type=float, default=0.001, help='Trading fee (0.001 = 0.1%)')
    common_parser.add_argument('--slippage', type=float, default=0.0005, help='Slippage (0.0005 = 0.05%)')
    common_parser.add_argument('--position_size', type=float, default=0.2, help='Position size as % of cash (0.2 = 20%)')
    common_parser.add_argument('--stop_loss', type=float, help='Stop loss % (e.g. 0.03)')
    common_parser.add_argument('--take_profit', type=float, help='Take profit % (e.g. 0.06)')
    
    # Strategy Params
    common_parser.add_argument('--fast', type=int, default=20, help='SMA Fast period')
    common_parser.add_argument('--slow', type=int, default=50, help='SMA Slow period')
    common_parser.add_argument('--rsi_period', type=int, default=14, help='RSI period')
    common_parser.add_argument('--oversold', type=int, default=30, help='RSI Oversold level')
    common_parser.add_argument('--overbought', type=int, default=70, help='RSI Overbought level')
    common_parser.add_argument('--bb_period', type=int, default=20, help='Bollinger Bands period')
    common_parser.add_argument('--bb_std', type=float, default=2.0, help='Bollinger Bands Std Dev')
    common_parser.add_argument('--bb_exit_mode', choices=['mid', 'upper'], default='mid', help='BB Exit Mode')
    common_parser.add_argument('--no_plot', action='store_true', help='Disable plotting')

    # Run Command
    parser_run = subparsers.add_parser('run', parents=[common_parser], help='Run single strategy')
    parser_run.add_argument('--strategy', required=True, choices=STRATEGIES.keys(), help='Strategy name')
    parser_run.add_argument('--timeframe', default='1d', help='Timeframe')

    # Batch Command
    parser_batch = subparsers.add_parser('batch', parents=[common_parser], help='Run batch timeframes')
    parser_batch.add_argument('--strategy', required=True, choices=STRATEGIES.keys(), help='Strategy name')
    parser_batch.add_argument('--timeframes', required=True, help='Comma separated timeframes (e.g. 1h,4h,1d)')

    # Compare Command
    parser_compare = subparsers.add_parser('compare', parents=[common_parser], help='Compare strategies')
    parser_compare.add_argument('--strategies', required=True, help='Comma separated strategies')
    parser_compare.add_argument('--timeframe', default='1d', help='Timeframe (single)')
    parser_compare.add_argument('--timeframes', help='Comma separated timeframes (optional override)')
    parser_compare.add_argument('--export', help='CSV file to export results')

    args = parser.parse_args()

    if args.command == 'run':
        command_run(args)
    elif args.command == 'batch':
        command_batch(args)
    elif args.command == 'compare':
        command_compare(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
