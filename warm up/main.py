from __future__ import annotations

import random
import typing
from functools import partial


class Expression(object):
    def __init__(self, *args: Expression, operator: str = '?', is_priority: bool = False):
        self.arguments: typing.Tuple[Expression] = args
        self.operator = operator
        self.is_priority = is_priority

    def __str__(self):
        if self.is_priority:
            return '(' + f' {self.operator} '.join(map(str, self.arguments)) + ')'
        else:
            return f' {self.operator} '.join(map(str, self.arguments))

    def __len__(self):
        return sum(map(len, self.arguments))

Add = partial(Expression, operator='+')
Subtract = partial(Expression, operator='-')
Multiply = partial(Expression, operator='×')
Divide = partial(Expression, operator='/')


class Integer(Expression):
    def __init__(self, value: int):
        super().__init__(operator='')
        self.value = value

    def __str__(self):
        return str(self.value)

    def __len__(self):
        return len(str(self.value))


def generate(*expressions: typing.Callable, depth: int = 3, largest: int = 9999, min_arity: int = 2,
             max_arity: int = 3, root: bool = True):
    if depth > 0:
        if root:
            current_expression = random.choice([e for e in expressions if e != Integer])
        else:
            current_expression = random.choice(expressions)
        if current_expression != Integer:
            current_arity = random.randint(min_arity, max_arity)
            args = [generate(*expressions, depth=depth - 1, largest=largest, root=False) for _ in range(current_arity)]
            return current_expression(*args, is_priority=random.choice([True, False]))
        else:
            return current_expression(random.randint(0, largest))
    else:
        return Integer(random.randint(0, largest))


if __name__ == '__main__':
    with open('warm_up.html', 'w') as f:
        f.write('<html><body>')
        for i in range(48):
            root = generate(Add, Subtract, Multiply, Integer, largest=1000, max_arity=2, depth=3)
            while not (20 <= len(root) <= 25):
                root = generate(Add, Subtract, Multiply, Integer, largest=1000, max_arity=2, depth=3)
            root.is_priority = False
            f.write(f'<p>feladat ID = {len(root)}.{i}</p>')
            f.write('<p style="font-style: italic">Kezdés időpontja (nap, óra:perc):</p>'
                    '<p style="font-style: italic">Vsz. azonosító (szám):</p>')
            f.write('<p><span style="font-weight: bold">Kérjük végezze el az álábbi műveleteket!</span><br/>'
                    'Megkérném Önt, hogy a következő feladat végrehajtásához ne használja a számítógépet.<br/>'
                    'Kérem, a feladat végrehajtása során minden olyan dolgot mondjon ki hangosan '
                    'ami az eszébe jut a megoldás közben.</p>')
            print(f'complexity = {len(root)}')
            f.write(f'<p style="page-break-after: always; text-align: center">{root}</p>')
        f.write('</body></html>')
