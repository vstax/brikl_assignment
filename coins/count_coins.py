import sys
import math

def makeChange(coinList, amount):
    minCoins = [0] * (amount + 1)

    for coin in range(1, amount + 1):
        count = math.inf
        for c in coinList:
            if c <= coin and minCoins[coin - c] + 1 < count:
                count = minCoins[coin - c] + 1
        minCoins[coin] = count
    return minCoins[amount] if minCoins[amount] != math.inf else -1

def test_makeChange():
    assert(makeChange([1, 5, 7, 9, 11], 25) == 3)
    assert(makeChange([1, 5, 7, 9, 11], 14) == 2)
    assert(makeChange([7, 9], 20) == -1)
    assert(makeChange([1, 5, 7, 9, 11], 0) == 0)

def main():
    # Just a basic interface without extra checks
    amount = int(sys.argv[-1])
    coinList = [int(coin) for coin in ''.join(sys.argv[1:-1])[1:-1].split(',')]
    print(makeChange(coinList, amount))

if __name__ == '__main__' :
        sys.exit(main())
