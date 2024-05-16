from dataclasses import dataclass


@dataclass(frozen=True)
class A:
    a: str 

@dataclass(frozen=True)
class B(A):
    b: int