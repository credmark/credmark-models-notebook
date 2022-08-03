#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import sys
from IPython.terminal.embed import InteractiveShellEmbed

ipshell = InteractiveShellEmbed()
ipshell.run_line_magic("load_ext", "credmark.cmf.ipython")

param = {'chain_id': 1,
 'block_number': None,
 'model_loader_path': ['../../credmark-models-py/models'],
 'chain_to_provider_url': {'1': 'http://192.168.68.122:10444'},
 'api_url': None,
 'use_local_models': '*',
 'register_utility_global': True}

context, model_loader = ipshell.run_line_magic("cmf", "param")

import math
import sys

# default pool id is the 0.3% USDC/ETH pool
POOL_ID = "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"

TICK_BASE = 1.0001

def tick_to_price(tick):
    return TICK_BASE ** tick

# Not all ticks can be initialized. Tick spacing is determined by the pool's fee tier.
def fee_tier_to_tick_spacing(fee_tier):
    return {
        500: 10,
        3000: 60,
        10000: 200
    }.get(fee_tier, 60)


# get pool info
current_tick = 194878
tick_spacing = 10

tick_mapping = {191150: 345073104699360, 198080: -345073104699360}

token0 = Token(address='0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48')
token1 = Token(address='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2')
decimals0 = token0.decimals
decimals1 = token1.decimals


# Start from zero; if we were iterating from the current tick, would start from the pool's total liquidity
liquidity = 0

# Find the boundaries of the price range
min_tick = min(tick_mapping.keys())
max_tick = max(tick_mapping.keys())

# Compute the tick range. This code would work as well in Python: `current_tick // tick_spacing * tick_spacing`
# However, using floor() is more portable.
current_range_bottom_tick = math.floor(current_tick / tick_spacing) * tick_spacing

current_price = tick_to_price(current_tick)
adjusted_current_price = current_price / (10 ** (decimals1 - decimals0))

# Sum up all tokens in the pool
total_amount0 = 0
total_amount1 = 0

token_amounts = []

# Iterate over the tick map starting from the bottom
tick = min_tick
while tick <= max_tick:
    liquidity_delta = tick_mapping.get(tick, 0)
    liquidity += liquidity_delta

    price = tick_to_price(tick)
    adjusted_price = price / (10 ** (decimals1 - decimals0))
    tokens = "{} for {}".format(token1, token0)

    should_print_tick = liquidity != 0
    if should_print_tick:
        print("ticks=[{}, {}], bottom tick price={:.6f} {}".format(tick, tick + tick_spacing, adjusted_price, tokens))

    # Compute square roots of prices corresponding to the bottom and top ticks
    bottom_tick = tick
    top_tick = bottom_tick + tick_spacing
    sa = tick_to_price(bottom_tick // 2)
    sb = tick_to_price(top_tick // 2)

    if tick < current_range_bottom_tick:
        # Compute the amounts of tokens potentially in the range
        amount1 = liquidity * (sb - sa)
        amount0 = amount1 / (sb * sa)

        # Only token1 locked
        total_amount1 += amount1

        token_amounts.append((tick, 0, amount1))
        if should_print_tick:
            adjusted_amount0 = amount0 / (10 ** decimals0)
            adjusted_amount1 = amount1 / (10 ** decimals1)
            print("        {:.2f} {} locked, potentially worth {:.2f} {}".format(adjusted_amount1, token1, adjusted_amount0, token0))

    elif tick == current_range_bottom_tick:
        # Always print the current tick. It normally has both assets locked
        print("        Current tick, both assets present!")
        print("        Current price={:.6f} {}".format(1 / adjusted_current_price, tokens))

        # Print the real amounts of the two assets needed to be swapped to move out of the current tick range
        current_sqrt_price = tick_to_price(current_tick / 2)
        amount0actual = liquidity * (sb - current_sqrt_price) / (current_sqrt_price * sb)
        amount1actual = liquidity * (current_sqrt_price - sa)
        adjusted_amount0actual = amount0actual / (10 ** decimals0)
        adjusted_amount1actual = amount1actual / (10 ** decimals1)

        total_amount0 += amount0actual
        total_amount1 += amount1actual

        print("        {:.2f} {} and {:.2f} {} remaining in the current tick range".format(
            adjusted_amount0actual, token0, adjusted_amount1actual, token1))

        token_amounts.append((tick, amount0actual, amount1actual))

    else:
        # Compute the amounts of tokens potentially in the range
        amount1 = liquidity * (sb - sa)
        amount0 = amount1 / (sb * sa)

        # Only token0 locked
        total_amount0 += amount0

        token_amounts.append((tick, amount0, 0))
        if should_print_tick:
            adjusted_amount0 = amount0 / (10 ** decimals0)
            adjusted_amount1 = amount1 / (10 ** decimals1)
            print("        {:.2f} {} locked, potentially worth {:.2f} {}".format(adjusted_amount0, token0, adjusted_amount1, token1))

    tick += tick_spacing

print("In total: {:.2f} {} and {:.2f} {}".format(
      total_amount0 / 10 ** decimals0, token0, total_amount1 / 10 ** decimals1, token1))


df_pool = pd.DataFrame(token_amounts, columns=['tick','token0', 'token1'])
df_pool.loc[:, 'token0'] = df_pool.loc[:, 'token0'] / 2995507735
df_pool.loc[:, 'token1'] = df_pool.loc[:, 'token1'] / 999999999871526500
df_pool.plot(x='tick', y = ['token0', 'token1'], kind='line')

ipshell()

df_pool