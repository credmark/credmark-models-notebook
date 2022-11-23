# pylint: disable=protected-access, not-context-manager, invalid-name, line-too-long, too-many-nested-blocks, try-except-raise, unsupported-membership-test

"""
Test curve
"""

from credmark.cmf.ipython import create_cmf
from web3 import HTTPProvider, Web3

from curve_pool import CurveStableSwap
from curve_poolGamma import CurveStableSwapGamma

LINK = '0xF178C0b5Bb7e7aBF4e12A4838C7b7c5bA2C623c0'
STETH = '0xDC24316b9AE028F1497c275EB9192a3Ea0f67022'
FRAXUSDC = '0xdcef968d416a41cdac0ed8702fac8128a64241a2'
EURT = '0xfd5db7463a3ab53fd211b4af195c5bccc1a03890'
CVXETH = '0xb576491f1e6e5e62f1d8f26062ee822b40b0e0d4'

THREE_POOL = '0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7'
tricrypto2 = '0xd51a44d3fae010294c616388b506acda1bfaae46'

if __name__ == '__main__':

    end_block = None
    end_block = 15968579

    end_block = 16024367

    cmf_param = {
                 'block_number': end_block,
                 'chain_to_provider_url': {'1': 'http://192.168.68.122:8545'},
                 'api_url': 'http://192.168.68.122:8700'
                }

    context, _model_loader = create_cmf(cmf_param)
    context._web3 = Web3(HTTPProvider(context.web3.provider.endpoint_uri, request_kwargs={'timeout': 3600 * 10}))
    context._web3.eth.default_block = int(context.block_number)
    end_block = int(context.block_number)

    three_pool = CurveStableSwap(THREE_POOL)
    print(three_pool.estimate_virtual_price())

    print((
        three_pool.get_dy_dx(0, 1, 1),
        three_pool.get_dy_dx(1, 0, 1),
        three_pool.get_dy_dx(1, 2, 1),
        three_pool.get_dy_dx(2, 1, 1),
        three_pool.get_dy_dx(0, 2, 1),
        three_pool.get_dy_dx(2, 0, 1)
        ))

    # use three_pool.coins[1].scaled()
    print(three_pool.get_dy_dx_xp(0, 1, 1, [5, 5, 5]))

    three_pool.self_test(0, 1)
    three_pool.self_test(1, 2)
    three_pool.self_test(0, 2)

    three_pool.get_dy_dx_xp(0, 1, 1, [5, 5, 5])

    three_pool.get_dy_dx(0, 1, 1)

    eurt = CurveStableSwap(EURT)
    print(eurt.estimate_virtual_price())
    eurt.self_test()

    fraxusdc = CurveStableSwap(FRAXUSDC)
    print(fraxusdc.estimate_virtual_price())
    fraxusdc.self_test()

    link = CurveStableSwap(LINK)
    print(link.estimate_virtual_price())
    link.self_test()

    steth = CurveStableSwap(STETH)
    print(steth.estimate_virtual_price())
    steth.self_test()

    print(steth.coins[1].scaled(steth.get_dy_dx_xp(0, 1, 1, [5, 5])))

    if False:
        cvxeth = CurveStableSwapGamma(CVXETH)
        cvxeth.self_test()
