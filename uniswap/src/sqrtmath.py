import math
import src.constants as constants

class SqrtPriceMath:
	def __init__(self, hi=0):
		self.hi = hi

	def rshift(self, val, n):
		return (val) >> n

	def mulShift(self, val, mulBy, shift_n):
		return self.rshift(val*mulBy, shift_n)

	def multiplyIn256(self, x, y):
		product = x * y
		#TODO HOW SHOULD I CORRECTLY CAST THIS AS INT?
		return (int(product) & constants.MAX_UINT256)

	def addIn256(self, x, y):
		summ = x + y
		return (summ & constants.MAX_UINT256)

	def mulDivRoundingUp(self,a, b, denominator):
		product = a * b
		result = product // denominator

		if product % denominator != 0:
			result += 1

		return result

	def getAmount0Delta(self, sqrtRatioAX96, sqrtRatioBX96, liquidity, roundUp):
		if sqrtRatioAX96 == sqrtRatioBX96:
		 	return 0

		if sqrtRatioAX96 > sqrtRatioBX96:
			sqrtRatioAX96, sqrtRatioBX96 = sqrtRatioBX96, sqrtRatioAX96
		numerator1 = liquidity << 96
		numerator2 = sqrtRatioBX96 - sqrtRatioAX96

		if roundUp:
			# print("sqrtRatioAX96: ", sqrtRatioAX96)
			# print("sqrtRatioBX96: ", sqrtRatioBX96)
			# print("liquidity: ", liquidity)
			# print("ROUNDING: ", self.mulDivRoundingUp(self.mulDivRoundingUp(numerator1, numerator2, sqrtRatioBX96), 1, sqrtRatioAX96) )
			return self.mulDivRoundingUp(self.mulDivRoundingUp(numerator1, numerator2, sqrtRatioBX96), 1, sqrtRatioAX96)
		else:
			# print(numerator2)
			# print(numerator1)
			# print(sqrtRatioBX96)
			# print(sqrtRatioAX96)
			# print("HELLLLLO: ", ((numerator2 * numerator1) // sqrtRatioBX96) // sqrtRatioAX96)
			return ((numerator2 * numerator1) // sqrtRatioBX96) // sqrtRatioAX96

	def getAmount1Delta(self, sqrtRatioAX96, sqrtRatioBX96, liquidity, roundUp):
		if sqrtRatioAX96 == sqrtRatioBX96:
		 	return 0

		if sqrtRatioAX96 > sqrtRatioBX96:
			sqrtRatioAX96, sqrtRatioBX96 = sqrtRatioBX96, sqrtRatioAX96

		if roundUp:
			#print("Ro: ", self.mulDivRoundingUp(liquidity, (sqrtRatioBX96 - sqrtRatioAX96), constants.Q96))
			return self.mulDivRoundingUp(liquidity, (sqrtRatioBX96 - sqrtRatioAX96), constants.Q96)
		else:
			#print("HELLO liquidity: ", liquidity)
			return (liquidity * (sqrtRatioBX96 - sqrtRatioAX96)) // constants.Q96

	def getNextSqrtPriceFromInput(self, sqrtPX96, liquidity, amountIn, zeroForOne):
		print("SQR AMOUNT IN: ", amountIn)
		if zeroForOne:
			return self.getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96, liquidity, amountIn, True)
		else:
			return self.getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96, liquidity, amountIn, True)


	def getNextSqrtPriceFromOutput(self, sqrtPX96, liquidity, amountOut, zeroForOne):
		print("SQR AMOUNT OUT: ", amountOut)
		if zeroForOne:
			return self.getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96, liquidity, amountOut, False)
		else:
			return self.getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96, liquidity, amountOut, False)


	def getNextSqrtPriceFromAmount0RoundingUp(self, sqrtPX96, liquidity, amount, add):
		if amount == 0:
			return sqrtPX96

		numerator1 = liquidity << 96

		if add:
			product = self.multiplyIn256(amount, sqrtPX96)
			if product // amount == sqrtPX96:
				denominator = self.addIn256(numerator1, product)
				if denominator >= numerator1:
					return self.mulDivRoundingUp(numerator1, sqrtPX96, denominator)
			return self.mulDivRoundingUp(numerator1, 1, (numerator1 // sqrtPX96) + amount)
		else:
			product = self.multiplyIn256(amount, sqrtPX96)

			denominator = numerator1 - product

			return self.mulDivRoundingUp(numerator1, sqrtPX96, denominator)

	def getNextSqrtPriceFromAmount1RoundingDown(self, sqrtPX96, liquidity, amount, add):
		print("GET NEXT SQRT: ", amount)
		if add:
			quotient = (amount << 96) // liquidity if amount <= constants.MAX_UINT160 else (amount * constants.Q96) // liquidity
			return sqrtPX96 + quotient
		else:
			quotient = self.mulDivRoundingUp(amount, constants.Q96, liquidity)
			return sqrtPX96 - quotient

	def mostSignificantBit(self, x):
		powersOf2 = [(128, 2 ** 128), (64, 2 ** 64), (32, 2 ** 32), (16, 2 ** 16), (8, 2 ** 8), (4, 2 ** 4), (2, 2 ** 2), (1, 2 ** 1)]
		msb = 0
		for index, val in enumerate(powersOf2):
			if x >= val[1]:
				x = x >> val[0]
				msb += val[0]

		return msb

	def getSqrtRatioAtTick(self, tick):
		absTick = (abs(tick))
		ratio = 0xfffcb933bd6fad37aa2d162d1a594001 if ((absTick & 0x1) != 0) else 0x100000000000000000000000000000000
		if ((absTick & 0x2) != 0):
			ratio = self.mulShift(ratio, 0xfff97272373d413259a46990580e213a, 128)
		if ((absTick & 0x4) != 0):
			ratio = self.mulShift(ratio, 0xfff2e50f5f656932ef12357cf3c7fdcc, 128)
		if ((absTick & 0x8) != 0):
			ratio = self.mulShift(ratio, 0xffe5caca7e10e4e61c3624eaa0941cd0, 128)
		if ((absTick & 0x10) != 0):
			ratio = self.mulShift(ratio, 0xffcb9843d60f6159c9db58835c926644, 128)
		if ((absTick & 0x20) != 0):
			ratio = self.mulShift(ratio, 0xff973b41fa98c081472e6896dfb254c0, 128)
		if ((absTick & 0x40) != 0):
			ratio = self.mulShift(ratio, 0xff2ea16466c96a3843ec78b326b52861, 128)
		if ((absTick & 0x80) != 0):
			ratio = self.mulShift(ratio, 0xfe5dee046a99a2a811c461f1969c3053, 128)
		if ((absTick & 0x100) != 0):
			ratio = self.mulShift(ratio, 0xfcbe86c7900a88aedcffc83b479aa3a4, 128)
		if ((absTick & 0x200) != 0):
			ratio = self.mulShift(ratio, 0xf987a7253ac413176f2b074cf7815e54, 128)
		if ((absTick & 0x400) != 0):
			ratio = self.mulShift(ratio, 0xf3392b0822b70005940c7a398e4b70f3, 128)
		if ((absTick & 0x800) != 0):
			ratio = self.mulShift(ratio, 0xe7159475a2c29b7443b29c7fa6e889d9, 128)
		if ((absTick & 0x1000) != 0):
			ratio = self.mulShift(ratio, 0xd097f3bdfd2022b8845ad8f792aa5825, 128)
		if ((absTick & 0x2000) != 0):
			ratio = self.mulShift(ratio, 0xa9f746462d870fdf8a65dc1f90e061e5, 128)
		if ((absTick & 0x4000) != 0):
			ratio = self.mulShift(ratio, 0x70d869a156d2a1b890bb3df62baf32f7, 128)
		if ((absTick & 0x8000) != 0):
			ratio = self.mulShift(ratio, 0x31be135f97d08fd981231505542fcfa6, 128)
		if ((absTick & 0x10000) != 0):
			ratio = self.mulShift(ratio, 0x9aa508b5b7a84e1c677de54f3e99bc9, 128)
		if ((absTick & 0x20000) != 0):
			ratio = self.mulShift(ratio, 0x5d6af8dedb81196699c329225ee604, 128)
		if ((absTick & 0x40000) != 0):
			ratio = self.mulShift(ratio, 0x2216e584f5fa1ea926041bedfe98, 128)
		if ((absTick & 0x80000) != 0):
			ratio = self.mulShift(ratio, 0x48a170391f7dc42444e8fa2, 128)

		if tick > 0:
			ratio = constants.MAX_UINT256 // ratio

		if ratio % constants.Q32 > 0:
			return ratio // constants.Q32 + 1
		else:
			return ratio // constants.Q32

	def getTickAtSqrtRatio(self, sqrtRatioX96):
		#TODO HOW SHOULD I CORRECTLY CAST THIS AS INT?
		sqrtRatioX128 = int(sqrtRatioX96) << 32
		msb = self.mostSignificantBit(sqrtRatioX128)
		r = 0
		if msb >= 128:
			r = sqrtRatioX128 >> msb  - 127
		else:
			r = sqrtRatioX128 << 127 - msb

		log2 = (msb - 128) << 64

		for i in range(14):
			r = (r*r) >> 127
			f = r >> 128
			log2 = log2 | (f << 63 - i)
			r = r >> f

		logSqrt1001 = log2 * 255738958999603826347141

		tickLow = (logSqrt1001 - 3402992956809132418596140100660247210) >> 128

		tickHigh = (logSqrt1001 + 291339464771989622907027621153398088495) >> 128

		if tickLow == tickHigh:
			return tickLow
		elif self.getSqrtRatioAtTick(tickHigh) <= sqrtRatioX96:
			return tickHigh
		else:
			return tickLow

	def addDelta(self, x, y):
		if y < 0:
			return x - (y * -1)
		else:
			return x + y
