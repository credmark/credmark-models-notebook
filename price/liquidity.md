pp = [ models(block_number=14841257-x,local=True).price.dex_blended(Token('UST'))
       for x in range(0, 70000, 1000)]

Liquidity dried-up

self.goto_block(14730670) as of 2022, 5, 7, 15, 53, 10

1. price stopped moving, price stopped moving, no more localized liquidity from both side. only depegged.

DAI/UST

self.goto_block(14730670) # last swap
datetime.datetime(2022, 5, 25, 10, 3, 44

from models.credmark.protocols.dexes.uniswap.liquidity import plot_liquidity, plot_liquidity_amount

df_pool_mod = plot_liquidity_amount(context,pool_addr='0x973a67726227ce2747d5710eb44a53fb9abfd02a')

df_pool_mod[['price', 'token0_locked_scaled', 'token1_locked_scaled']]

models().uniswap_v3.get_pool_info(address='0x973a67726227ce2747d5710eb44a53fb9abfd02a')

 'full_tick_liquidity0': 4874.734697768009,
 'full_tick_liquidity1': 43815.618153183794,
 'lower_tick_liquidity0': 48782.700353537344,
 'lower_tick_liquidity1': 48660.902003840085,
 'upper_tick_liquidity0': 0.0,
 'upper_tick_liquidity1': 0.0,
 'one_tick_liquidity0_ori': 4874.734697768009,
 'one_tick_liquidity1_ori': 4869.37570553072,
 'one_tick_liquidity0': 4874.734697767048,
 'one_tick_liquidity1': 4869.37570553072,

self.goto_block(14841257)

datetime.datetime(2022, 5, 25, 10, 3, 44)

models.uniswap_v3.get_pool_info(address='0x973a67726227ce2747d5710eb44a53fb9abfd02a')

 'full_tick_liquidity0': 0.0,
 'full_tick_liquidity1': 0.0,
 'lower_tick_liquidity0': 0.0,
 'lower_tick_liquidity1': 0.0,
 'upper_tick_liquidity0': 0.0,
 'upper_tick_liquidity1': 0.0,
 'one_tick_liquidity0_ori': 0.0,
 'one_tick_liquidity1_ori': 0.0,
 'one_tick_liquidity0': 0.0,
 'one_tick_liquidity1': 0.0,
 'virtual_liquidity0': 0.0,
 'virtual_liquidity1': 0.0,

2. price stopped moving, left with dozens of depegged token

self.goto_block(14841257)

0x92995d179a5528334356cb4dc5c6cbb1c068696c

df_pool_mod = plot_liquidity_amount(context, pool_addr='0x92995d179a5528334356cb4dc5c6cbb1c068696c')

df_pool_mod[['price', 'token0_locked_scaled', 'token1_locked_scaled']]

models.uniswap_v3.get_pool_info(address='0x92995d179a5528334356cb4dc5c6cbb1c068696c')

{'address': '0x92995d179a5528334356cb4dc5c6cbb1c068696c',
 'sqrtPriceX96': 7.972874502048038e+34,
 'current_tick': 276450,
 'tick_bottom': 276450,
 'tick_top': 276460,
 'observationIndex': 61,
 'observationCardinality': 100,
 'observationCardinalityNext': 100,
 'feeProtocol': 0,
 'unlocked': True,
 'liquidity': 0.0,
 'full_tick_liquidity0': 0.0,
 'full_tick_liquidity1': 0.0,
 'lower_tick_liquidity0': 99.438983,
 'lower_tick_liquidity1': 100.64917707548331,
 'upper_tick_liquidity0': 0.0,
 'upper_tick_liquidity1': 0.0,
 'one_tick_liquidity0_ori': 0.0,
 'one_tick_liquidity1_ori': 10.067182351771592,
 'one_tick_liquidity0': 0.0,
 'one_tick_liquidity1': 0.0,

models(14841257).price.dex_pool(symbol="UST", weight_power=4, return_type=Some).to_dataframe().to_csv('14841257_ust_2.csv')

models(14841257).uniswap_v3.get_pool_info(address='0x92995d179a5528334356cb4dc5c6cbb1c068696c')


3.

till they are drained today

from models.credmark.protocols.dexes.uniswap.liquidity import plot_liquidity, plot_liquidity_amount
df_pool_mod, pool_contract = plot_liquidity_amount(context, '0x92995d179a5528334356cb4dc5c6cbb1c068696c', None, None)
df_pool_mod.to_csv('pool_0x92995d179a5528334356cb4dc5c6cbb1c068696c_15396536.csv')


models(14103367).uniswap_v3.get_pool_info({'address': '0x5777d92f208679db4b9778590fa3cab3ac9e2168', 'price_slug': 'uniswap-v3.get-weighted-price'})

 'current_tick': -276324,
 'tick_bottom': -276324,
 'tick_top': -276323,
 'liquidity': 9.72869735215361e+23,
 'full_tick_liquidity0': 48639774.50548711,
 'full_tick_liquidity1': 0.0,

adjusted
 'one_tick_liquidity0': 47104754.769827075,
 'one_tick_liquidity1': 47104879.306979,

unadjusted
 'one_tick_liquidity0': 47107109.948688544,
 'one_tick_liquidity1': 47104879.306979,


three tools



1. overall

models(14841257).price.dex_pool(symbol='UST (Wormhole)')

2. get pool info

models(14841257).uniswap_v3.get_pool_info(address='0x92995d179a5528334356cb4dc5c6cbb1c068696c')

3. liquidity profile

from models.credmark.protocols.dexes.uniswap.liquidity import plot_liquidity, plot_liquidity_amount
df_pool_mod, pool_contract = plot_liquidity_amount(context, pool_addr='0x92995d179a5528334356cb4dc5c6cbb1c068696c', upper_range=10000, lower_range=10000)
pool_contract
pool_contract.functions.liquidity().call()

Sufficient liquidity from swaping in and out.
