# pylint:disable=invalid-name, line-too-long
"""
Curve Stable Pool with gamma (TODO)

https://etherscan.io/address/0xb576491f1e6e5e62f1d8f26062ee822b40b0e0d4#readContract

"""

from credmark.cmf.types import Address, Contract, Token
from web3.exceptions import (ContractLogicError, ABIFunctionNotFound)


class CurveStableSwapGamma:
    """
    Curve Stable Swap (for 2) with gamma
    """
    FEE_DENOMINATOR = 10 ** 10
    PRECISION = 10 ** 18

    def __init__(self, pool_addr):
        self._pool_addr = pool_addr
        self._pool = Contract(pool_addr)

        """
        In some 2-token contract, it has
        -   A(): _A()/A_PRECISION, e.g. 100
        -   A_precise(): _A(), e.g. 10000
        with A_PRECISION = 100

        In function, it will use A_precise with // A_PRECISION.

        We will simplify this by passing function with A() without // A_PRECISION
        """

        self.A = self._pool.functions.A().call()
        self.gamma = self._pool.functions.gamma().call()
        self.fee = self._pool.functions.fee().call()

        self.balances = []
        self.coins = []
        self.n_coins = 0
        self.coins_mult = []
        for i in range(8):
            try:
                token_addr = self._pool.functions.coins(i).call()
                token_bal = self._pool.functions.balances(i).call()
                self.balances.append(token_bal)
                self.coins.append(Token(token_addr))
                self.coins_mult.append(10 ** (18 + 18 - Token(token_addr).decimals))
                self.n_coins += 1
            except ContractLogicError as _err:
                break

        if self.n_coins != 2:
            raise ValueError(f'Not a 2-pool for {pool_addr} with {self.balances} in {self.coins}')

    def xp(self, xp = None):
        """
        Return scaled balance to level all tokens with 18 decimals.
        """
        if xp is None:
            xp = self.balances.copy()
        for i in range(self.n_coins):
            xp[i] = self.scale_coin(i, xp[i])
        return xp

    def scale_coin(self, i, v):
        """
        Return scaled balance to token i with 18 decimals.
        """
        return (v * self.coins_mult[i]) // self.PRECISION

    def scale_back_coin(self, i, v):
        """
        Return scaled balance to token i with 18 decimals.
        """
        return (v * self.PRECISION) // self.coins_mult[i]

    def estimate_virtual_price(self):
        """
        estimate D
        """
        try:
            lp_token = Token(Address(self._pool.functions.lp_token().call()))
            lp_token_supply = lp_token.total_supply
            virtual_price = self._pool.functions.get_virtual_price().call()

            vp_estimate = (self._get_D(self.xp(), self.A) * self.PRECISION) // lp_token_supply
            return (virtual_price, vp_estimate, vp_estimate - virtual_price)
        except ABIFunctionNotFound:
            return None


    def _get_D(self, _xp, _amp):
        """
        D invariant calculation in non-overflowing integer operations
        iteratively
        A * sum(x_i) * n**n + D = A * D * n**n + D**(n+1) / (n**n * prod(x_i))
        Converging solution:
        D[j+1] = (A * n**n * sum(x_i) - D[j]**(n+1) / (n**n prod(x_i))) / (A * n**n - 1)
        """
        S = 0
        Dprev = 0

        for _x in _xp:
            S += _x
        if S == 0:
            return 0

        D = S
        Ann = _amp * self.n_coins
        for _i in range(255):
            D_P = D
            for _x in _xp:
                D_P = (D_P * D) // (_x * self.n_coins)  # If division by 0, this will be borked: only withdrawal will work. And that is good
            Dprev = D
            D = ((Ann * S + D_P * self.n_coins) * D) // ((Ann - 1) * D + (self.n_coins + 1) * D_P)

            # Equality with the precision of 1
            if D > Dprev:
                if D - Dprev <= 1:
                    return D
            else:
                if Dprev - D <= 1:
                    return D

        # convergence typically occurs in 4 rounds or less, this should be unreachable!
        # if it does happen the pool is borked and LPs can withdraw via `remove_liquidity`
        raise ValueError('not converge for D')

    def self_test(self):
        """
        estimate dy
        """
        for amount in [1,1000, 10000, 100000]:
            x0 = self.get_dy(0, 1, amount)
            y0 = self.get_dy(1, 0, amount)
            try:
                x1 = self._pool.functions.get_dy(0, 1, amount).call()
                x_diff = x0-x1
            except ContractLogicError:
                x1 = None
                x_diff = None
            try:
                y1 = self._pool.functions.get_dy(1, 0, amount).call()
                y_diff = y0-y1
            except ContractLogicError:
                y1 = None
                y_diff = None

            print((amount, (x0,x1,x_diff),(y0,y1,y_diff)))

    def get_dy_xp(self, i, j, _dx, xp):
        """
        get dy with non-scaled dx, xp
        """
        for xp_i,xp_v in enumerate(xp):
            xp[xp_i] = xp_v * (10 ** self.coins[xp_i].decimals)
        _dx = _dx * (10 ** self.coins[i].decimals)

        x = xp[i] + self.scale_coin(i, _dx)
        y = self._get_y(i, j, x, xp)
        dy = xp[j] - y - 1
        fee = self.fee * dy // self.FEE_DENOMINATOR
        return self.coins[j].scaled(self.scale_back_coin(j, dy - fee))

    def get_dy_1(self, i, j, _dx):
        """
        get dy
        """
        xp = self.xp()
        x = xp[i] + self.scale_coin(i, _dx)
        y = self._get_y(i, j, x, xp)
        dy = xp[j] - y - 1
        fee = self.fee * dy // self.FEE_DENOMINATOR
        return self.scale_back_coin(j, dy - fee)

    def get_dy(self, i, j, _dx):
        """
        get dy
        """
        xp = self.xp()
        x = xp[i] + self.scale_coin(i, _dx)
        y = self._get_y(i, j, x, xp)
        dy = xp[j] - y - 1
        fee = self.fee * dy // self.FEE_DENOMINATOR
        return self.scale_back_coin(j, dy - fee)

    def _get_y(self, i, j, x, _xp):
        """
        Calculate x[j] if one makes x[i] = x
        Done by solving quadratic equation iteratively.
        x_1**2 + x_1 * (sum' - (A*n**n - 1) * D / (A * n**n)) = D ** (n + 1) / (n ** (2 * n) * prod' * A)
        x_1**2 + b*x_1 = c
        x_1 = (x_1**2 + c) / (2*x_1 + b)
        """
        # x in the input is converted to the same price/precision

        assert i != j       # dev: same coin
        assert j >= 0       # dev: j below zero
        assert j < self.n_coins  # dev: j above self.n_coins

        # should be unreachable, but good for safety
        assert i >= 0
        assert i < self.n_coins

        A = self.A
        D = self._get_D(_xp, A)
        Ann = A * self.n_coins
        c = D
        S = 0
        _x = 0
        y_prev = 0

        for _i in range(self.n_coins):
            if _i == i:
                _x = x
            elif _i != j:
                _x = _xp[_i]
            else:
                continue
            S += _x
            c = c * D // (_x * self.n_coins)
        c = c * D // (Ann * self.n_coins)
        b = S + D // Ann  # - D
        y = D

        for _i in range(255):
            y_prev = y
            y = (y*y + c) // (2 * y + b - D)
            # Equality with the precision of 1
            if y > y_prev:
                if y - y_prev <= 1:
                    return y
            else:
                if y_prev - y <= 1:
                    return y

        raise ValueError('not converge for y')


    def _get_y_D(self, A, i, _xp, D):
        """
        Calculate x[i] if one reduces D from being calculated for xp to D
        Done by solving quadratic equation iteratively.
        x_1**2 + x_1 * (sum' - (A*n**n - 1) * D / (A * n**n)) = D ** (n + 1) / (n ** (2 * n) * prod' * A)
        x_1**2 + b*x_1 = c
        x_1 = (x_1**2 + c) / (2*x_1 + b)
        """
        # x in the input is converted to the same price/precision

        assert i >= 0  # dev: i below zero
        assert i < self.n_coins  # dev: i above self.n_coins

        Ann = A * self.n_coins
        c = D
        S = 0
        _x = 0
        y_prev = 0

        for _i in range(self.n_coins):
            if _i != i:
                _x = _xp[_i]
            else:
                continue
            S += _x
            c = c * D // (_x * self.n_coins)
        c = c * D // (Ann * self.n_coins)
        b = S + D // Ann
        y = D

        for _i in range(255):
            y_prev = y
            y = (y*y + c) // (2 * y + b - D)
            # Equality with the precision of 1
            if y > y_prev:
                if y - y_prev <= 1:
                    return y
            else:
                if y_prev - y <= 1:
                    return y

        raise ValueError('not converge for D_y')
