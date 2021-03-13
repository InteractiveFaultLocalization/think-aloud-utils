import sys

from patterns import patterns

if __name__ == '__main__':
    for i in range(7):
        for pattern in patterns.choose(int(sys.argv[1])):
            print(pattern.short_txt(patterns) + '  ')
        print()
