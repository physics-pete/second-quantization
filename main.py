from abc import ABC
from typing import List, Tuple
from dataclasses import dataclass
from enum import Enum
import functools 
import operator

class Terminal:
    BOLD = '\033[1m'
    NORM = '\033[0m'
    GREEN = '\033[92m'
    CYAN = '\033[96m'

class LeadingSign(Enum):
    POSITIVE = ""
    NEGATIVE = "-"

class Expression(ABC):
    leading_sign = LeadingSign.POSITIVE

    def __add__(self, other: 'Expression') -> 'Expression':
        return Addition(self, other)
    
    def __mul__(self, other: 'Expression') -> 'Expression':
        return Multiplication(self, other)

class Symbol(Expression):

    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return self.name
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Symbol) and (self.name == other.name)

ZERO = Symbol('0')

class Addition(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        self.lhs = lhs
        self.rhs = rhs
        self.complex_expression = True

    def __repr__(self) -> str:
        return f"({repr(self.lhs)} + {repr(self.rhs)})"
    
class Multiplication(Expression):
    def __init__(self, lhs: Expression, rhs: Expression):
        self.lhs = lhs
        self.rhs = rhs

    def __repr__(self) -> str:
        return f"{repr(self.lhs)}⋅{repr(self.rhs)}"


class Operator(Expression):
    def __init__(self, name: str, dagger: bool = False):
        self.name = name 
        self._dagger = dagger
    
    @property
    def dagger(self) -> 'Operator':
        return Operator(self.name, ~self._dagger)

    def apply(self, ket: 'Ket') -> Expression:
        return Multiplication(self, ket)

    def __repr__(self) -> str:
        return f'{Terminal.BOLD}{self.name}{Terminal.NORM}{"†" if self._dagger else ""}'
    


class FermionicCreationOperator(Operator):
    def __init__(self, symbol: Symbol):
        super().__init__('c')
        self.symbol = symbol

    @property
    def dagger(self) -> Operator:
        return FermionAnnihilationOperator(self.symbol)
    
    def apply(self, ket: 'FermionKet') -> Expression:
        return ket.create(self.symbol)

    def __repr__(self):
        return f'{Terminal.BOLD}{Terminal.GREEN}{self.name}_{self.symbol}†{Terminal.NORM}'
    
class FermionAnnihilationOperator(Operator):
    def __init__(self, symbol: Symbol):
        super().__init__('c')
        self.symbol = symbol

    def apply(self, ket: 'FermionKet') -> Expression:
        return ket.destroy(self.symbol)

    @property
    def dagger(self) -> Operator:
        return FermionicCreationOperator(self.symbol)

    def __repr__(self):
        return f'{Terminal.BOLD}{Terminal.GREEN}{self.name}_{self.symbol}{Terminal.NORM}'

@dataclass
class Occupation:
    symbol: Symbol
    number: int = 1

    def __repr__(self) -> str:
        if self.number == 1:
            return repr(self.symbol)
        elif self.number > 1:
            return f'{self.number}.{repr(self.symbol)}'
        return ''

class Ket(Expression):
    def __init__(self, *state: List[Occupation]):
        self.state =  state

    def create(self, symbol: Symbol):
        raise NotImplemented('create for Ket not implemented')
    
    def destroy(self, symbol: Symbol):
        raise NotImplemented('destroy for Ket not implemented')
    
    def order(self):
        raise NotImplemented('order for Ket not implemented')

    def __eq__(self, rhs):
        return (
            isinstance(rhs, Ket)
            and (len(self.state) == len(rhs.state))
            and functools.reduce(
                operator.and_, 
                [l == r for l, r in zip(self.state, rhs.state)]
                )
        )
            

    def __repr__(self) -> str:
        return f'{Terminal.CYAN}{self.leading_sign.value}|{", ".join([repr(s) for s in self.state])}⟩{Terminal.NORM}'
    
class Bra(Expression):
    def __init__(self, *state: List[Occupation]):
        self.state =  state

    def __repr__(self) -> str:
        return f'{Terminal.CYAN}⟨{", ".join([repr(s) for s in self.state])}|{Terminal.NORM}'

class FermionKet(Ket):
    def __init__(self, *state: List[Symbol]) -> 'FermionKet':
        super().__init__(*[Occupation(s) for s in state])

    def create(self, symbol: Symbol) -> Expression:
        result = [o for o in self.state if o.symbol == symbol]

        if len(result) == 0:
            new_ket = FermionKet(symbol, *[o.symbol for o in self.state])
            new_ket.leading_sign = self.leading_sign
            return new_ket
        
        return ZERO
    
    def destroy(self, symbol: Symbol) -> Expression:
        result = [index for index, o in enumerate(self.state) if o.symbol == symbol]

        if len(result) == 0:
            return ZERO
        
        if len(result) > 1:
            raise ValueError(f'Fermion Ket should not have more than one state {symbol}')
        
        eveness_indicator = result[0]
        if self.leading_sign == LeadingSign.NEGATIVE:
            eveness_indicator += 1

        is_index_even = (eveness_indicator % 2 == 0)

        new_ket = FermionKet(*[o.symbol for o in self.state if o.symbol != symbol])
        new_ket.leading_sign = LeadingSign.POSITIVE if is_index_even else LeadingSign.NEGATIVE

        return new_ket
    
    def order(self) -> 'FermionKet':
        if len(self.state) <= 1:
            return self

        result = self.state
        commutations = 0

        for i in range(len(self.state)):
            minimum = min(result[i:], key=lambda o: o.symbol.name)
            index_minimum = result.index(minimum, i)
            commutations += index_minimum - i

            left = list(result[:i])
            right = [r for r in result[i:] if r != minimum]
            result = left + [minimum] + right


        commutations += 0 if self.leading_sign == LeadingSign.POSITIVE else 1

        new_fermion_ket = FermionKet(*[r.symbol for r in result])
        new_fermion_ket.leading_sign = LeadingSign.POSITIVE if commutations % 2 == 0 else LeadingSign.NEGATIVE

        return new_fermion_ket




class FermionBra(Bra):
    def __init__(self, *state: List[Symbol]):
        super().__init__(*[Occupation(s) for s in state])

# shorthand notation
F =  FermionAnnihilationOperator
Fd = FermionicCreationOperator

def expand_multiplication(multiplication: Multiplication) -> Expression:
    lhs = multiplication.lhs
    rhs = multiplication.rhs

    if isinstance(lhs, Addition): 
        # Rule: (a + b) * c -> a * c + b * c
        return Addition(expand(lhs.lhs * rhs), expand(lhs.rhs * rhs))
    elif isinstance(rhs, Addition):
        # Rule: a * (b + c) -> a * b + a * c
        return expand(Addition(expand(lhs * rhs.lhs), expand(lhs * rhs.rhs)))
    else:
        lhs = expand(lhs)
        rhs = expand(rhs)

        if isinstance(lhs, Multiplication): #root swap (a * b) * c -> a * (b * c)
            return Multiplication(lhs.lhs, Multiplication(lhs.rhs, rhs))
        else: 
            return Multiplication(lhs, rhs)
    
def expand_addition(addition: Addition) -> Expression:
    lhs = addition.lhs
    rhs = addition.rhs

    return Addition(expand(lhs), expand(rhs))

def expand(expression: Expression) -> Expression:
    if isinstance(expression, Multiplication):
        return expand_multiplication(expression)
    elif isinstance(expression, Addition):
        return expand_addition(expression)
    else:
        return expression

def full_expand(expression: Expression) -> Expression:
    old_representation = ""
    while repr(expression) != old_representation:
        old_representation = repr(expression)
        expression = expand(expression)

    return expression

def simplify_multiplication(multiplication: Multiplication) -> Expression:
    lhs = multiplication.lhs
    rhs = multiplication.rhs

    if isinstance(lhs, Operator) and isinstance(rhs, Ket):
        return lhs.apply(rhs)
    if (lhs == ZERO) or (rhs == ZERO):
        return ZERO
    
    return Multiplication(simplify(lhs), simplify(rhs))

def simplify_addition(addition: Addition) -> Expression:
    if addition.lhs == ZERO:
        return simplify(addition.rhs)
    elif addition.rhs == ZERO:
        return simplify(addition.lhs)
    
    return Addition(simplify(addition.lhs), simplify(addition.rhs))
def simplify(expression: Expression) -> Expression:
    
    if isinstance(expression, Addition):
        return simplify_addition(expression)
    elif isinstance(expression, Multiplication):
        return simplify_multiplication(expression)
    elif isinstance(expression, Ket):
        return expression.order()

    return expression

def full_simplify(expression: Expression) -> Expression:
    old_representation = ""
    while repr(expression) != old_representation:
        old_representation = repr(expression)
        expression = simplify(expression)

    return expression

def summarize_addition(addition: Addition) -> Expression:
    lhs = addition.lhs
    rhs = addition.rhs

    if isinstance(lhs, Multiplication) and isinstance(rhs, Multiplication):
        if isinstance(lhs.rhs, Ket) and lhs.rhs == rhs.rhs:
            return Multiplication(Addition(summarize(lhs.lhs), summarize(rhs.lhs)), rhs.rhs)
        
    return Addition(summarize(lhs), summarize(rhs))


def summarize(expression: Expression) -> Expression:
    if isinstance(expression, Addition):
        return summarize_addition(expression)

    return expression

def full_summarize(expression: Expression) -> Expression:
    old_representation = ""
    while repr(expression) != old_representation:
        old_representation = repr(expression)
        expression = summarize(expression)

    return expression

if __name__ == '__main__':
    ou = Symbol('1↑')
    od = Symbol('1↓')
    tu = Symbol('2↑')
    td = Symbol('2↓')

    e1 = Symbol('E1')
    e2 = Symbol('E2')
    j = Symbol('J')

    H1 = e1 * (Fd(ou) * F(ou) + Fd(od) * F(od))
    H2 = e2 * (Fd(tu) * F(tu) + Fd(td) * F(td))
    WW = j * (Fd(ou) * F(ou) + Fd(ou) * F(tu) + Fd(tu) * F(ou) + Fd(tu) * F(tu))

    H = H1 + H2 + WW
    
    states_to_test = [
        FermionKet(ou, od),
        FermionKet(ou, tu),
        FermionKet(ou, td),
        FermionKet(od, tu),
        FermionKet(od, td),
        FermionKet(tu, td),
    ]

    for state in states_to_test:
        print(f"H{state} = ", end='')
        new_state = full_simplify(full_expand(H * state))
        print(new_state)
        #summerized = full_summarize(new_state)
        #print(summerized)




