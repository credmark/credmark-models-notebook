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
    PRECISION = 10 ** 18
    A_MULTIPLIER = 10000

    MIN_GAMMA = 10**10
    MAX_GAMMA = 2 * 10**16

    @property
    def MIN_A(self):
        return self.n_coins**self.n_coins * self.A_MULTIPLIER // 10

    @property
    def MAX_A(self):
        return self.n_coins**self.n_coins * self.A_MULTIPLIER * 100000

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
        self.is_killed = self._pool.functions.is_killed().call()
        self.price_scale = self._pool.functions.price_scale().call()
        self.D = self._pool.functions.D().call()
        self.fee_gamma = self._pool.functions.fee_gamma().call()
        self.mid_fee = self._pool.functions.mid_fee().call()
        self.out_fee = self._pool.functions.out_fee().call()

        self._balances = []
        self.coins = []
        self.n_coins = 0
        self.coins_mult = []
        for i in range(8):
            try:
                token_addr = self._pool.functions.coins(i).call()
                token_bal = self._pool.functions.balances(i).call()
                self._balances.append(token_bal)
                self.coins.append(Token(token_addr))
                self.coins_mult.append(10 ** (18 - Token(token_addr).decimals))
                self.n_coins += 1
            except ContractLogicError as _err:
                break

        print(f'{pool_addr} for {self.n_coins} coins loaded')

    def _A_gamma(self):
        return [self.A, self.gamma].copy()


    def xp(self, xp = None):
        """
        Return scaled balance to level all tokens with 18 decimals.
        """
        if xp is None:
            xp = self._balances.copy()
        # for i in range(self.n_coins):
        #     xp[i] = self.scale_coin(i, xp[i])
        # return xp
        return [self.balances[0] * self.coins_mult[0],
                (self.balances[1] * self.coins_mult[1] * self.price_scale) // self.PRECISION]

    @property
    def scaled_balances(self):
        """
        return scaled balances
        """
        return [self.coins[n].scaled(bal) for n, bal in enumerate(self._balances)]

    @property
    def balances(self):
        """
        return scaled balances
        """
        return self._balances.copy()

    @property
    def coins_symbol(self):
        """
        return coins' symbol
        """
        return [tok.symbol for tok in self.coins]

    @property
    def coins_decimals(self):
        """
        return coins' decimals
        """
        return [tok.decimals for tok in self.coins]

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

    def self_test(self, i = 0, j = 1):
        """
        Run self-test for running this and smart contract's implementations.
        """
        print(f'Self-test for {self._pool_addr} with various amount')

        print('Test get_dy_dx0 with current balance')
        print(f'Exchange ({i} for {j}), ({j} for {i})')
        print('(this, web3, difference)')

        for amount in [1,1000, 10000, 100000, 10000000000000000]:
            x0 = self.get_dy_dx0(i, j, amount)
            y0 = self.get_dy_dx0(j, i, amount)
            try:
                x1 = self._pool.functions.get_dy(i, j, amount).call()
                x_diff = x0-x1
            except ContractLogicError:
                x1 = None
                x_diff = None
            try:
                y1 = self._pool.functions.get_dy(j, i, amount).call()
                y_diff = y0-y1
            except ContractLogicError:
                y1 = None
                y_diff = None

            print((amount, (x0,x1,x_diff),(y0,y1,y_diff), x_diff == 0 and y_diff == 0))

        print('Test get_dy_dx0_xp0/get_dy_dx_xp/get_dy_dx_xp with current balance')

        for (n, m) in [(i, j), (j, i)]:
            amount = int(100 * 10 ** self.coins[n].decimals)
            x0 = self._pool.functions.get_dy(n, m, amount).call()
            x1 = self.get_dy_dx0(n, m, amount)
            x2 = self.get_dy_dx0_xp0(n, m, amount, self._balances)
            x3 = int(self.get_dy_dx(n, m,
                                self.coins[n].scaled(amount))
                * (10 ** self.coins[m].decimals))
            x4 = int(self.get_dy_dx_xp(n, m,
                                self.coins[n].scaled(amount),
                                [self.coins[i].scaled(v) for i, v in enumerate(self._balances)])
                * (10 ** self.coins[m].decimals))
            x01_diff = x0 - x1
            x12_diff = x2 - x1
            x23_diff = x3 - x2
            x34_diff = x4 - x3
            print(((n, m), amount, (x0,x1,x2,x3,x4, x01_diff, x12_diff, x23_diff, x34_diff)))

    def get_dy_dx0(self, i, j, _dx):
        """
        get dy with non-scaled dx0, returns non-scaled dy
        """
        assert i != j  # dev: same input and output coin
        assert i < self.n_coins  # dev: coin index out of range
        assert j < self.n_coins  # dev: coin index out of range

        price_scale = self.price_scale * self.coins_mult[1]
        xp = self._balances.copy()

        A_gamma = self._A_gamma()
        D = self.D
        D2 = self.newton_D(A_gamma[0], A_gamma[1], self.xp())

        print(f'{xp=} {D=} {D2=}')

        xp[i] += _dx
        xp = [xp[0] * self.coins_mult[0], (xp[1] * price_scale) // self.PRECISION]

        print(f'{xp=} {A_gamma=} {D=} {j=} {price_scale=}')

        y = self.newton_y(A_gamma[0], A_gamma[1], xp, D, j)
        dy = xp[j] - y - 1
        xp[j] = y
        if j > 0:
            dy = (dy * self.PRECISION) // price_scale
        else:
            dy //= self.coins_mult[0]
        dy -= (self._fee(xp) * dy) // 10**10

        return dy

    def _fee(self, xp):
        """
        f = fee_gamma / (fee_gamma + (1 - K))
        where
        K = prod(x) / (sum(x) / N)**N
        (all normalized to 1e18)
        """
        fee_gamma = self.fee_gamma
        f = xp[0] + xp[1]  # sum
        f = fee_gamma * 10**18 // (
            fee_gamma + 10**18 - (10**18 * self.n_coins**self.n_coins) * xp[0] // f * xp[1] // f
        )
        return (self.mid_fee * f + self.out_fee * (10**18 - f)) // 10**18

    def newton_y(self, ANN, gamma, x, D, i):
        """
        Calculating x[i] given other balances x[0..self.n_coins-1] and invariant D
        ANN = A * N**N
        """
        # Safety checks
        assert ANN > self.MIN_A - 1 and ANN < self.MAX_A + 1  # dev: unsafe values A
        assert gamma > self.MIN_GAMMA - 1 and gamma < self.MAX_GAMMA + 1  # dev: unsafe values gamma
        assert D > 10**17 - 1 and D < 10**15 * 10**18 + 1 # dev: unsafe values D

        x_j = x[1 - i]
        y = D**2 // (x_j * self.n_coins**2)
        K0_i = ((10**18 * self.n_coins) * x_j) // D
        # S_i = x_j

        # frac = x_j * 1e18 / D => frac = K0_i / self.n_coins
        assert (K0_i > 10**16*self.n_coins - 1) and (K0_i < 10**20*self.n_coins + 1)  # dev: unsafe values x[i]

        # x_sorted[self.n_coins] = x
        # x_sorted[i] = 0
        # x_sorted = self.sort(x_sorted)  # From high to low
        # x[not i] instead of x_sorted since x_soted has only 1 element

        convergence_limit = max(max(x_j // 10**14, D // 10**14), 100)

        for j in range(255):
            y_prev = y

            K0 = (K0_i * y * self.n_coins) // D
            S = x_j + y

            _g1k0 = gamma + 10**18
            if _g1k0 > K0:
                _g1k0 = _g1k0 - K0 + 1
            else:
                _g1k0 = K0 - _g1k0 + 1

            # D / (A * N**N) * _g1k0**2 / gamma**2
            mul1 = (((10**18 * D) // gamma * _g1k0) // gamma * _g1k0 * self.A_MULTIPLIER) // ANN

            # 2*K0 / _g1k0
            mul2 = 10**18 + ((2 * 10**18) * K0) // _g1k0

            yfprime = 10**18 * y + S * mul2 + mul1
            _dyfprime = D * mul2
            if yfprime < _dyfprime:
                y = y_prev // 2
                continue
            else:
                yfprime -= _dyfprime
            fprime = yfprime // y

            # y -= f / f_prime;  y = (y * fprime - f) / fprime
            # y = (yfprime + 10**18 * D - 10**18 * S) // fprime + mul1 // fprime * (10**18 - K0) // K0
            y_minus = mul1 // fprime
            y_plus = (yfprime + 10**18 * D) // fprime + (y_minus * 10**18) // K0
            y_minus += (10**18 * S) // fprime

            if y_plus < y_minus:
                y = y_prev // 2
            else:
                y = y_plus - y_minus

            diff = 0
            if y > y_prev:
                diff = y - y_prev
            else:
                diff = y_prev - y
            if diff < max(convergence_limit, y // 10**14):
                frac = (y * 10**18) // D
                assert (frac > 10**16 - 1) and (frac < 10**20 + 1)  # dev: unsafe value for y
                return y

        raise ValueError(f"Did not converge for y {(y, y_prev, y - y_prev)}")


    def _exchange(self, sender, mvalue, i, j, dx, min_dy, use_eth: bool):
        assert not self.is_killed  # dev: the pool is killed
        assert i != j  # dev: coin index out of range
        assert i < self.n_coins  # dev: coin index out of range
        assert j < self.n_coins  # dev: coin index out of range
        assert dx > 0  # dev: do not exchange 0 coins

        A_gamma = self._A_gamma()
        xp = self.balances
        p = 0
        dy = 0

        _coins = coins

        if use_eth and i == ETH_INDEX:
            assert mvalue == dx  # dev: incorrect eth amount
        else:
            assert mvalue == 0  # dev: nonzero eth amount
            assert ERC20(_coins[i]).transferFrom(sender, self, dx)
            if i == ETH_INDEX:
                WETH(_coins[i]).withdraw(dx)

        y = xp[j]
        x0 = xp[i]
        xp[i] = x0 + dx
        self.balances[i] = xp[i]

        price_scale = self.price_scale

        xp = [xp[0] * self.coin_mult[0], xp[1] * price_scale * self.coin_mult[1] / self.PRECISION]

        prec_i = self.coin_mult[0]
        prec_j = self.coin_mult[1]
        if i == 1:
            prec_i = self.coin_mult[1]
            prec_j = self.coin_mult[0]

        # In case ramp is happening
        t = self.future_A_gamma_time
        if t > 0:
            x0 *= prec_i
            if i > 0:
                x0 = x0 * price_scale / self.PRECISION
            x1 = xp[i]  # Back up old value in xp
            xp[i] = x0
            self.D = self.newton_D(A_gamma[0], A_gamma[1], xp)
            xp[i] = x1  # And restore
            if block.timestamp >= t:
                self.future_A_gamma_time = 1

        dy = xp[j] - self.newton_y(A_gamma[0], A_gamma[1], xp, self.D, j)
        # Not defining new "y" here to have less variables / make subsequent calls cheaper
        xp[j] -= dy
        dy -= 1

        if j > 0:
            dy = dy * self.PRECISION / price_scale
        dy /= prec_j

        dy -= self._fee(xp) * dy / 10**10
        assert dy >= min_dy, "Slippage"
        y -= dy

        self.balances[j] = y

        if use_eth and j == ETH_INDEX:
            raw_call(sender, b"", value=dy)
        else:
            if j == ETH_INDEX:
                WETH(_coins[j]).deposit(value=dy)
            assert ERC20(_coins[j]).transfer(sender, dy)

        y *= prec_j
        if j > 0:
            y = y * price_scale / self.PRECISION
        xp[j] = y

        # Calculate price
        if dx > 10**5 and dy > 10**5:
            _dx = dx * prec_i
            _dy = dy * prec_j
            if i == 0:
                p = _dx * 10**18 / _dy
            else:  # j == 0
                p = _dy * 10**18 / _dx

        self.tweak_price(A_gamma, xp, p, 0)

        return dy


    def exchange(i, j, dx, min_dy, use_eth: bool = False):
        """
        Exchange using WETH by default
        """
        return self._exchange(msg.sender, msg.value, i, j, dx, min_dy, use_eth)


    def exchange_underlying(i, j, dx, min_dy):
        """
        Exchange using ETH
        """
        return self._exchange(msg.sender, msg.value, i, j, dx, min_dy, True)


    def get_dy_dx0_xp0(self, i, j, _dx, xp):
        """
        get dy with non-scaled dx and xp, returns non-scaled dy
        """
        ...

    def get_dy_dx(self, i, j, _dx):
        """
        get dy with scaled (human) dx, returns non-scaled dy
        """
        ...

    def get_dy_dx_xp(self, i, j, _dx, xp):
        """
        get dy with scaled (human) dx and xp, returns non-scaled dy (use self.coins[j].scaled)
        """
        ...

    def _get_D(self, _xp, _amp):
        ...

    def newton_D(self, ANN, gamma, x_unsorted):
        """
        Finding the invariant using Newton method.
        ANN is higher by the factor A_MULTIPLIER
        ANN is already A * N**N

        Currently uses 60k gas
        """
        # Safety checks
        assert ANN > self.MIN_A - 1 and ANN < self.MAX_A + 1  # dev: unsafe values A
        assert gamma > self.MIN_GAMMA - 1 and gamma < self.MAX_GAMMA + 1  # dev: unsafe values gamma

        print(f'{x_unsorted=}')

        # Initial value of invariant D is that for constant-product invariant
        x = x_unsorted
        if x[0] < x[1]:
            x = [x_unsorted[1], x_unsorted[0]]

        assert x[0] > 10**9 - 1 and x[0] < 10**15 * 10**18 + 1  # dev: unsafe values x[0]
        assert x[1] * 10**18 / x[0] > 10**14-1  # dev: unsafe values x[i] (input)

        D = self.n_coins * self.geometric_mean(x, False)
        S = x[0] + x[1]

        print(f'{D=}')

        for i in range(255):
            D_prev = D

            # K0 = 10**18
            # for _x in x:
            #     K0 = K0 * _x * self.n_coins / D
            # collapsed for 2 coins
            K0 = ((10**18 * self.n_coins**2) * x[0] * x[1]) // D // D

            _g1k0 = gamma + 10**18
            if _g1k0 > K0:
                _g1k0 = _g1k0 - K0 + 1
            else:
                _g1k0 = K0 - _g1k0 + 1

            # D / (A * N**N) * _g1k0**2 / gamma**2
            mul1 = (((10**18 * D) // gamma * _g1k0) // gamma * _g1k0 * self.A_MULTIPLIER) // ANN

            # 2*N*K0 / _g1k0
            mul2 = ((2 * 10**18) * self.n_coins * K0) // _g1k0

            neg_fprime = (S + (S * mul2) // 10**18) + (mul1 * self.n_coins) // K0 - (mul2 * D) // 10**18

            # D -= f / fprime
            D_plus = (D * (neg_fprime + S)) // neg_fprime
            D_minus = (D*D) // neg_fprime
            if 10**18 > K0:
                D_minus += ((D * (mul1 // neg_fprime)) // 10**18 * (10**18 - K0)) // K0
            else:
                D_minus -= ((D * (mul1 // neg_fprime)) // 10**18 * (K0 - 10**18)) // K0

            if D_plus > D_minus:
                D = D_plus - D_minus
            else:
                D = (D_minus - D_plus) // 2

            diff = 0
            if D > D_prev:
                diff = D - D_prev
            else:
                diff = D_prev - D
            if diff * 10**14 < max(10**16, D):  # Could reduce precision for gas efficiency here
                # Test that we are safe with the next newton_y
                for _x in x:
                    frac = (_x * 10**18) // D
                    assert (frac > 10**16 - 1) and (frac < 10**20 + 1)  # dev: unsafe values x[i]
                return D

        raise ValueError(f"Did not converge for D {(D, D_prev, D - D_prev)}")


    def geometric_mean(self, unsorted_x, sort):
        """
        (x[0] * x[1] * ...) ** (1/N)
        """
        x = unsorted_x.copy()
        if sort and x[0] < x[1]:
            x = [unsorted_x[1], unsorted_x[0]]

        D = x[0]
        diff = 0

        for i in range(255):
            D_prev = D
            # tmp = 10**18
            # for _x in x:
            #     tmp = tmp * _x / D
            # D = D * ((self.n_coins - 1) * 10**18 + tmp) / (self.n_coins * 10**18)
            # line below makes it for 2 coins

            D = (D + (x[0] * x[1]) // D) // self.n_coins
            if D > D_prev:
                diff = D - D_prev
            else:
                diff = D_prev - D
            if diff <= 1 or diff * 10**18 < D:
                return D

        raise ValueError(f"Did not converge for geometric_mean {(D, D_prev, D - D_prev)}")
