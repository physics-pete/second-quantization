from abc import ABC
from typing import List, Union, Dict, Tuple
from enum import Enum

class Sign(Enum):
    POSITIVE = ""
    NEGATIVE = "-"

    def __repr__(self):
        return self.value
    
    def __str__(self):
        return self.value

    def __mul__(self, rhs: 'Sign') -> 'Sign':
        return Sign.POSITIVE if self == rhs else Sign.NEGATIVE

    def __neg__(self) -> 'Sign':
        return Sign.NEGATIVE if self == Sign.POSITIVE else Sign.POSITIVE
    
    def number(self) -> int:
        return 1 if self == Sign.POSITIVE else -1
    
    def from_number(number) -> 'Sign':
        return Sign.POSITIVE if number >= 0 else Sign.NEGATIVE

class Expression(ABC):
    def __init__(self, sign: Sign = Sign.POSITIVE):
        self.sign = sign

    def __add__(self, other: 'Expression') -> 'Addition':
        return Addition(self, other)
    
    def __sub__(self, other: 'Expression') -> 'Addition':
        return Addition(self, -other)

    def __mul__(self, other: 'Expression') -> 'Multiplication':
        return Multiplication(self, other)

    def mul_sign(self, sign: Sign) -> 'Expression':
        this = self.copy()
        this.sign *= sign 
        return this

    def __neg__(self) -> 'Expression':
        raise NotImplementedError('unary negative was not implemented for this class')

    def copy(self) -> 'Expression':
        raise NotImplementedError('copy was not implemented for this class')

    def expand(self) -> 'Expression':
        return self

    def simplify(self) -> 'Expression':
       return self
    
    def __hash__(self) -> int:
        return hash(self.sign)


class Symbol(Expression):
    def __init__(self, name: str, sign: Sign = Sign.POSITIVE):
        self.name = name
        self.sign = sign

    def __repr__(self):
        return f'{self.sign}{self.name}'
    
    def __neg__(self):
        return Symbol(self.name, -self.sign)
    
    def __lt__(self, other):
        return self.name < other.name
    
    def __eq__(self, other: 'Symbol') -> bool:
        return (
            isinstance(other, Symbol) 
            and self.name == other.name 
            and self.sign == other.sign
        )
    
    def __hash__(self):
        return hash((self.name, self.sign))

    def copy(self):
        return Symbol(self.name, self.sign)
    
class Integer(Expression):
    def __init__(self, number: int, sign: Sign = Sign.POSITIVE):
        self.number = number
        self.sign = sign

    def __repr__(self):
        return f'{self.sign}{self.number}'
    
    def __neg__(self):
        return Integer(self.number, -self.sign)
    
    def __eq__(self, other):
        return isinstance(other, Integer) and self.number == other.number and self.sign == other.sign
    
    def copy(self):
        return Integer(self.number, self.sign)
    
    def add(self, other: 'Integer'):
        a = self.sign.number() * self.number
        b = other.sign.number() * other.number

        r = a + b
        return Integer(abs(r), Sign.from_number(r))
    
    @classmethod
    def ZERO(cls):
        return Integer(0)

    @classmethod
    def ONE(cls):
        return Integer(1)
    
    def __hash__(self) -> int:
        return hash((self.number, self.sign))

class Addition(Expression):
    def __init__(self, lhs: Expression, rhs: Expression, sign: Sign = Sign.POSITIVE):
        super().__init__(sign)
        self.lhs = lhs
        self.rhs = rhs

        if lhs.sign == Sign.NEGATIVE and rhs.sign == Sign.NEGATIVE:
            super().__init__(sign * Sign.NEGATIVE)
            self.lhs.sign = Sign.POSITIVE
            self.rhs.sign = Sign.POSITIVE

    def __neg__(self):
        return Addition(self.lhs, self.rhs, -self.sign)

    def __repr__(self):
        if self.rhs.sign == Sign.NEGATIVE:
            return f'{self.sign}({self.lhs} - {-self.rhs})'
        return f'{self.sign}({self.lhs} + {self.rhs})'
    
    def copy(self):
        return Addition(self.lhs, self.rhs, self.sign)
    
    def simplify(self) -> Expression:
         if isinstance(self.lhs, Integer) and isinstance(self.rhs, Integer):
             return self.lhs.add(self.rhs).mul_sign(self.sign)
         elif isinstance(self.lhs, Integer) and self.lhs == Integer(0):
             return self.rhs.mul_sign(self.sign)
         elif isinstance(self.rhs, Integer) and self.rhs == Integer(0):
             return self.lhs.mul_sign(self.sign)
         
         return Addition(self.lhs.simplify(), self.rhs.simplify(), self.sign)
         
    def expand(self) -> Expression:
        return Addition(self.lhs.expand(), self.rhs.expand(), self.sign)

    def __hash__(self) -> int:
        return hash((self.lhs, self.rhs, self.sign))

    
class Multiplication(Expression):
    def __init__(self, lhs: Expression, rhs: Expression, sign: Sign = Sign.POSITIVE):
        super().__init__(sign * lhs.sign * rhs.sign)
        self.lhs = lhs
        self.rhs = rhs

        if self.__should_be_swapped(self.lhs, self.rhs):
            self.lhs, self.rhs = self.rhs, self.lhs

        self.lhs.sign = Sign.POSITIVE
        self.rhs.sign = Sign.POSITIVE

    def __should_be_swapped(self, lhs: Expression, rhs: Expression):
        return (
            (isinstance(rhs, Integer) and not isinstance(lhs, Integer))
            or (isinstance(rhs, Symbol) and not isinstance(lhs, (Symbol, Integer)))
            or (isinstance(rhs, Symbol) and isinstance(lhs, Symbol) and rhs < lhs)
        )

    def __neg__(self) -> 'Multiplication':
        return Multiplication(self.lhs, self.rhs, sign=-self.sign)

    def __repr__(self):
        return f'{self.sign}[{self.lhs}⋅{self.rhs}]'
    
    def copy(self):
        return Multiplication(self.lhs, self.rhs, self.sign)
    
    def expand(self):
        if isinstance(self.lhs, Addition):
            rhs = self.rhs.copy().expand()
            return Addition(
                Multiplication(self.lhs.lhs.expand(), rhs, self.sign),
                Multiplication(self.lhs.rhs.expand(), rhs, self.sign)
            )
        elif isinstance(self.rhs, Addition):
            lhs = self.lhs.copy().expand()
            return Addition(
                Multiplication(lhs, self.rhs.lhs.expand(), self.sign),
                Multiplication(lhs, self.rhs.rhs.expand(), self.sign)
            )
        elif isinstance(self.lhs, Multiplication):
            return Multiplication(
                self.lhs.lhs.expand(), 
                Multiplication(self.lhs.rhs.expand(), self.rhs.expand(), self.lhs.sign), 
                self.sign)
        elif (isinstance(self.rhs, Multiplication) and isinstance(self.rhs.lhs, (Symbol, Integer)) and not isinstance(self.lhs, (Symbol, Integer))):
            return Multiplication(
                self.rhs.lhs,
                Multiplication(self.lhs.expand(), self.rhs.rhs.expand(), self.rhs.sign),
                self.sign)
        elif (isinstance(self.rhs, Multiplication) and isinstance(self.rhs.lhs, Integer) and isinstance(self.lhs, Symbol)):
            return Multiplication(
                self.rhs.lhs,
                Multiplication(self.lhs, self.rhs.rhs.expand(), self.rhs.sign),
                self.sign
            )
        
        return Multiplication(self.lhs.expand(), self.rhs.expand(), self.sign)
    
    def simplify(self) -> Expression:
        if isinstance(self.rhs, Ket) and isinstance(self.lhs, Operator):
            return self.lhs.apply(self.rhs).mul_sign(self.sign)
        elif ((isinstance(self.rhs, Integer) and self.rhs == Integer(0))
            or (isinstance(self.lhs, Integer) and self.lhs == Integer(0))
            ):
            return Integer(0)
        elif (isinstance(self.rhs, Integer) and self.rhs == Integer(1)):
            return self.lhs.mul_sign(self.sign)
        elif (isinstance(self.lhs, Integer) and self.lhs == Integer(1)):
            return self.rhs.mul_sign(self.sign)
        elif isinstance(self.lhs, Bra) and isinstance(self.rhs, Ket):
            return self.lhs.inner(self.rhs).mul_sign(self.sign)
        
        return Multiplication(self.lhs.simplify(), self.rhs.simplify(), self.sign)

    def __hash__(self) -> int:
        return hash((self.lhs, self.rhs, self.sign))

class Ket(Expression):
    def __init__(self, state: Union[None, Tuple[Symbol], List[Symbol], Dict[Symbol, int]] = None, sign=Sign.POSITIVE):
        super().__init__(sign)

        if isinstance(state,dict):
            self.state = {k:v for k, v in state.items()}
        elif isinstance(state, list) or isinstance(state, tuple):
            self.state = {k:1 for k in state}
        elif state == None:
            self.state = {}
        
    def __neg__(self):
        raise NotImplementedError('unary negative was not implemented for Ket') 
        
    def __repr__(self):
        lst = ', '.join([
            f'{s}{"" if n == 1 else ":" + str(n)}'
            for s, n in self.state.items()
        ])
        return f'{self.sign}|{lst}⟩'
    
    def copy(self):
        raise NotImplementedError('copy was not implemented for Ket') 
    
    def create(self, state: Symbol) -> 'Ket':
        raise NotImplementedError('create was not implemented for Ket') 
    
    def annihilate(self, state: Symbol) -> 'Ket':
        raise NotImplementedError('annihilate was not implemented for Ket') 

    def __hash__(self) -> int:
        return hash((self.sign, *self.state))

class Bra(Expression):
    def __init__(self, state: Union[None, Tuple[Symbol], List[Symbol], Dict[Symbol, int]] = None, sign=Sign.POSITIVE):
        super().__init__(sign)

        if isinstance(state,dict):
            self.state = {k:v for k, v in state.items()}
        elif isinstance(state, list) or isinstance(state, tuple):
            self.state = {k:1 for k in state}
        elif state == None:
            self.state = {}
        
    def __neg__(self):
        raise NotImplementedError('unary negative was not implemented for Ket') 
        
    def __repr__(self):
        lst = ', '.join([
            f'{s}{"" if n == 1 else ":" + str(n)}'
            for s, n in self.state.items()
        ])
        return f'{self.sign}⟨{lst}|'
    
    def copy(self):
        raise NotImplementedError('copy was not implemented for Ket') 
    
    def create(self, state: Symbol) -> 'Ket':
        raise NotImplementedError('create was not implemented for Ket') 
    
    def annihilate(self, state: Symbol) -> 'Ket':
        raise NotImplementedError('annihilate was not implemented for Ket')

    def inner(self, ket: Ket):
        if len(self.state) != len(ket.state):
            return Integer.ZERO()
        
        is_the_same = all([
            b_state == k_state and b_number == k_number
            for (b_state, b_number), (k_state, k_number) in zip(self.state.items(), ket.state.items())
        ])

        return Integer.ONE() if is_the_same else Integer.ZERO()

    def __hash__(self) -> int:
        return hash((self.sign, *self.state))

class FermionKet(Ket):
    def __init__(self, *state: List[Symbol], sign=Sign.POSITIVE):
        ordered, order_sign = FermionKet._order(state)
        super().__init__(ordered, sign * order_sign)

    def __neg__(self):
        return FermionKet(*list(self.state.keys()), sign=-self.sign)

    def __eq__(self, other):
        return (
            isinstance(other, FermionKet)
            and self.sign == other.sign
            and len(self.state) == len(other.state)
            and all([
                s == o
                for s, o in zip(self.state, other.state)
            ])
        )

    def copy(self):
        return FermionKet(*list(self.state.keys()), sign=self.sign)

    @classmethod
    def _order(cls, states: Tuple[List[Symbol]]) -> Tuple[List[Symbol], Sign]:
        result = []
        resulting_sign = Sign.POSITIVE

        while len(states) > 0:
            element = min(states)
            index = states.index(element)

            states = states[:index] + states[index+1:]

            index_sign = Sign.POSITIVE
            if index % 2 != 0:
                index_sign = Sign.NEGATIVE

            resulting_sign *= index_sign

            result.append(element)
        
        return result, resulting_sign

    def order(self) -> 'FermionKet':
        result, resulting_sign = FermionKet._order(tuple(self.state.keys()))
        return FermionKet(*result, sign=self.sign * resulting_sign)

    def create(self, state: Symbol) -> 'FermionKet':
        if state in self.state.keys():
            return Integer.ZERO()
        
        return (
            FermionKet(*([state] + list(self.state.keys())), sign=self.sign)
            .order()
        )
    
    @classmethod
    def _annihilate(cls, state: Symbol, states: List[Symbol]) -> Tuple[List[Symbol], Sign]:
        if state not in states:
            return Integer.ZERO(), Sign.POSITIVE
        
        index = states.index(state)

        new_states = states[:index] + states[index+1:]

        index_sign = Sign.POSITIVE
        if index % 2 != 0:
            index_sign = Sign.NEGATIVE

        return new_states, index_sign

    def annihilate(self, state: Symbol) -> 'FermionKet':
        result, resulting_sign = FermionKet._annihilate(state, list(self.state.keys()))

        if result == Integer.ZERO():
            return result
        return FermionKet(*result, sign=resulting_sign * self.sign).order()

    def __hash__(self) -> int:
        return hash((self.sign, *self.state))


class FermionBra(Bra):
    def __init__(self, *state: List[Symbol], sign=Sign.POSITIVE):
        ordered, order_sign = FermionKet._order(state)
        super().__init__(ordered, sign * order_sign)

    def __neg__(self):
        return FermionBra(*list(self.state.keys()), sign=-self.sign)

    def order(self) -> 'FermionBra':
        result, resulting_sign = FermionKet._order(tuple(self.state.keys()))
        return FermionBra(*result, sign=self.sign * resulting_sign)

    def copy(self):
        return FermionBra(*list(self.state.keys()), sign=self.sign)
    
    def create(self, state: Symbol) -> 'FermionKet':
        if state in self.state.keys():
            return Integer.ZERO()
        
        return (
            FermionBra(*([state] + list(self.state.keys())), sign=self.sign)
            .order()
        )
    
    def annihilate(self, state: Symbol) -> 'FermionKet':
        result, resulting_sign = FermionKet._annihilate(state, list(self.state.keys()))
        
        if result == Integer.ZERO():
            return result
        return FermionBra(*result, sign=resulting_sign * self.sign).order()

    def __eq__(self, other):
        return (
            isinstance(other, FermionBra)
            and self.sign == other.sign
            and len(self.state) == len(other.state)
            and all([
                s == o
                for s, o in zip(self.state, other.state)
            ])
        )

    def __hash__(self) -> int:
        return hash((self.sign, *self.state))

class Operator(Expression):
    def __init__(self, name: str, dagger: bool=False, sign: Sign=Sign.POSITIVE):
        self.name = name
        self._dagger = dagger
        super().__init__(sign)

    def copy(self):
        return Operator(self.name, self._dagger, self.sign)

    def __repr__(self):
        return f'{self.sign}{self.name}{"†" if self._dagger else ""}'

    def dagger(self):
        return Operator(self.name, ~self._dagger, self.sign)
    
    def apply(self, vec:Union[Ket, Bra]) -> Union[Ket, Bra, Integer]:
        raise NotImplementedError(f"apply not implemented for this operator {repr}")
    
    def __hash__(self) -> int:
        return hash((self.sign, self.name, self._dagger))

class FermionCreation(Operator):
    def __init__(self, state: Symbol, sign: Sign=Sign.POSITIVE):
        super().__init__(f'c_{state}', dagger=True, sign=sign)
        self.state = state.copy()

    def copy(self):
        return FermionCreation(self.state, self.sign)
    
    def dagger(self):
        return FermionAnnihilation(self.state, self.sign)
    
    def apply(self, vec:Union[FermionKet, FermionBra]) -> Union[FermionKet, FermionBra, Integer]:
        if isinstance(vec, FermionKet):
            return vec.create(self.state)
        elif isinstance(vec, FermionBra):
            return vec.annihilate(self.state)
        else:
            raise TypeError('Only FermionKet or FermionBra allowed.')

class FermionAnnihilation(Operator):
    def __init__(self, state: Symbol, sign: Sign=Sign.POSITIVE):
        super().__init__(f'c_{state}', dagger=False, sign=sign)
        self.state = state.copy() 

    def copy(self):
        return FermionAnnihilation(self.state, self.sign)
    
    def dagger(self):
        return FermionCreation(self.state, self.sign)
    
    def apply(self, vec:Union[FermionKet, FermionBra]) -> Union[FermionKet, FermionBra, Integer]:
        if isinstance(vec, FermionKet):
            return vec.annihilate(self.state)
        elif isinstance(vec, FermionBra):
            return vec.create(self.state)
        else:
            raise TypeError('Only FermionKet or FermionBra allowed.')

Fd = FermionCreation
F = FermionAnnihilation

def expand(expression: Expression) -> Expression:
    expression_hash = None

    while expression_hash != hash(expression):
        expression_hash = hash(expression)
        expression = expression.expand()

    return expression

def simplify(expression : Expression) -> Expression:
    expression_hash = None

    while expression_hash != hash(expression):
        expression_hash = hash(expression)
       # print(expression_string)
        expression = expression.simplify()

   # print(repr(expression))
    return expression



