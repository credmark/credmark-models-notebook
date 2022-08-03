"""
V3 Liquidity functions
"""


from math import floor, log
from typing import Dict, Optional

import pandas as pd

from src.constants import MAX_TICK, MIN_TICK

UNISWAP_BASE = 1.0001

def tick_to_price(tick):
    """
    tick to price
    """
    return pow(UNISWAP_BASE, tick)

def price_to_tick(price):
    """
    price to tick
    """
    return log(price) / log(UNISWAP_BASE)




def get_liquidity_in_ticks(pool_contract: 'Contract',
                          min_tick: Optional[int] = None,
                          max_tick: Optional[int] = None):
    """
    Get liquidity profile mapped to ticks
    """

    current_liquidity = pool_contract.functions.liquidity().call()
    slot0 = pool_contract.functions.slot0().call()
    current_tick = slot0[1]
    tick_spacing = pool_contract.functions.tickSpacing().call()

    tick_bottom = current_tick // tick_spacing * tick_spacing
    tick_top = tick_bottom + tick_spacing
    assert tick_bottom <= current_tick <= tick_top

    tick_mapping = {}

    liquidity = current_liquidity
    x = 0
    tick_b = tick_bottom

    min_tick = MIN_TICK if min_tick is None else min_tick
    max_tick = MAX_TICK if max_tick is None else max_tick

    while tick_b >= min_tick:
        ticks = pool_contract.functions.ticks(tick_b).call()
        if ticks[1] != 0:
            tick_mapping[tick_b] = ticks[1]
            liquidity -= ticks[1]
        x += 1
        tick_b = tick_bottom - tick_spacing * x

    liquidity = pool_contract.functions.liquidity().call()
    x = 1
    tick_b = tick_bottom + tick_spacing
    while tick_b <= max_tick:
        ticks = pool_contract.functions.ticks(tick_b).call()
        if ticks[1] != 0:
            tick_mapping[tick_b] = ticks[1]
            liquidity += ticks[1]
        x += 1
        tick_b = tick_bottom + tick_spacing * x

    return tick_mapping

def get_amount_in_ticks(pool_contract: 'Contract', token0: 'Token', token1: 'Token', tick_mapping: Dict[int, int], should_print_tick = False):
    """
    Reference: https://github.com/atiselsts/uniswap-v3-liquidity-math/blob/master/subgraph-liquidity-range-example.py
    """

    decimals0 = token0.decimals
    decimals1 = token1.decimals

    slot0 = pool_contract.functions.slot0().call()
    current_tick = slot0[1]
    current_price = tick_to_price(current_tick)
    adjusted_current_price = current_price / (10 ** (decimals1 - decimals0))

    tick_spacing = pool_contract.functions.tickSpacing().call()

    current_range_bottom_tick = floor(current_tick / tick_spacing) * tick_spacing
    current_price = tick_to_price(current_tick)

    liquidity = 0

    token_amounts = []

    min_tick = min(tick_mapping.keys())
    max_tick = max(tick_mapping.keys())

    for tick in range(min_tick, max_tick, tick_spacing):
        liquidity += tick_mapping.get(tick, 0)

        tick_bottom = tick
        tick_top = tick_bottom + tick_spacing

        sa = tick_to_price(tick_bottom // 2)
        sb = tick_to_price(tick_top // 2)

        # Compute the amounts of tokens potentially in the range
        amount1 = int(liquidity * (sb - sa))
        amount0 = int(amount1 / (sb * sa))

        if tick < current_range_bottom_tick:
            token_amounts.append((tick, amount0, amount1, liquidity))
        elif tick == current_range_bottom_tick:
            # Print the real amounts of the two assets needed to be swapped to move out of the current tick range
            sp = tick_to_price(current_tick / 2)
            amount0 = int(liquidity * (sb - sp) / (sp * sb))
            amount1 = int(liquidity * (sp - sa))

            token_amounts.append((tick, amount0, amount1, liquidity))
            print(f"{amount0:.2f} {token0} and {amount1:.2f} {token1} remaining in the current tick range")
        else:
            token_amounts.append((tick, amount0, amount1, liquidity))
            if should_print_tick:
                adjusted_amount0 = amount0 / (10 ** decimals0)
                adjusted_amount1 = amount1 / (10 ** decimals1)
                print(f"{adjusted_amount0:.2f} {token0} locked, potentially worth {adjusted_amount1:.2f} {token1}")

        tick += tick_spacing

    df_pool = (
        pd.DataFrame(token_amounts, columns=['tick', 'token0', 'token1','liquidity'])
        .astype({'tick': 'int', 'token0': 'float', 'token1': 'float', 'liquidity': 'float'})
        .assign(token0_locked = lambda x: x.token0,
                token1_locked = lambda x: x.token1)

        .assign(token0_locked = lambda x: x.token0_locked.where(x.tick >= current_range_bottom_tick, 0),
                token1_locked = lambda x: x.token1_locked.where(x.tick <= current_range_bottom_tick, 0))
        .assign(token0_scaled = lambda x: x.token0 / 10**decimals0,
                token1_scaled = lambda x: x.token1 / 10**decimals1,
                token0_prop = lambda x: x.token0 / token0.balance_of(pool_contract.address.checksum),
                token1_prop = lambda x: x.token1 / token1.balance_of(pool_contract.address.checksum))
        .assign(token0_locked_scaled = lambda x: x.token0_locked / 10**decimals0,
                token1_locked_scaled = lambda x: x.token1_locked / 10**decimals1,
                token0_locked_prop = lambda x: x.token0_locked / token0.balance_of(pool_contract.address.checksum),
                token1_locked_prop = lambda x: x.token1_locked / token1.balance_of(pool_contract.address.checksum))
        )

    return df_pool


if __name__ == '__main__':
    pool_min_tick = 191150
    pool_max_tick = 198080

    pool = Contract(address='0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640')

    get_liquidity_profile(pool, pool_min_tick, pool_max_tick)
