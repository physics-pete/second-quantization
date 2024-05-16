use std::{fmt::Display, iter::Sum, ops::{Add, Mul, Neg, Sub}};

enum StateChangeResult {
    SignPositive,
    SignNegative,
    StateIsZero
}

#[derive(Clone, PartialEq)]
pub struct StateContainer {
    states: Vec<String>
}

impl StateContainer {
    fn new(states: Vec<&str>) -> (StateChangeResult, StateContainer) {
        let mut state_container = StateContainer {
            states: Vec::with_capacity(states.len())
        };

        let mut change_result = StateChangeResult::SignPositive;

        for state in states.into_iter().rev() {
            change_result = match state_container.create(String::from(state)) {
                StateChangeResult::SignPositive => match change_result {
                    StateChangeResult::SignPositive => StateChangeResult::SignPositive,
                    StateChangeResult::SignNegative => StateChangeResult::SignNegative,
                    StateChangeResult::StateIsZero => StateChangeResult::StateIsZero,
                },
                StateChangeResult::SignNegative => match change_result {
                    StateChangeResult::SignPositive => StateChangeResult::SignNegative,
                    StateChangeResult::SignNegative => StateChangeResult::SignPositive,
                    StateChangeResult::StateIsZero => StateChangeResult::StateIsZero,
                },
                StateChangeResult::StateIsZero => StateChangeResult::StateIsZero
            };
        }

        (change_result, state_container)
    }

    #[allow(unused)]
    fn create(&mut self, state: String) -> StateChangeResult {
        match self.states.binary_search(&state) {
            Ok(_) => {
                self.states.clear();
                StateChangeResult::StateIsZero
            },
            Err(pos) => {
                self.states.insert(pos, state);

                if pos % 2 == 0 {
                    StateChangeResult::SignPositive
                } else {
                    StateChangeResult::SignNegative
                }
            },
        }
    }

    #[allow(unused)]
    fn annihilate(&mut self, state: String) -> StateChangeResult {
        match self.states.binary_search(&state) {
            Ok(pos) => {
                self.states.remove(pos);
                if pos % 2 == 0 {
                    StateChangeResult::SignPositive
                } else {
                    StateChangeResult::SignNegative
                }
            },
            Err(_) => {
                self.states.clear();
                StateChangeResult::StateIsZero
            },
        }
    }
}

impl Display for StateContainer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.states.join(", "))
    }
}


#[allow(dead_code)]
#[derive(Clone, PartialEq)]
pub enum Term {
    Integer(u64),
    Symbol(String),
    Addition(Box<Term>, Box<Term>),
    Multiplication(Box<Term>, Box<Term>),
    Negation(Box<Term>),
    FermionKet(StateContainer),
    FermionBra(StateContainer),
    Creation(String),
    Annihilation(String)
}

impl Term {
    pub fn new_symbol(name: &str) -> Term {
        Term::Symbol(String::from(name))
    }

    pub fn f(name: &str) -> Term {
        Term::Annihilation(String::from(name))
    }

    pub fn fd(name: &str) -> Term {
        Term::Creation(String::from(name))
    }

    pub fn new_ket(states: Vec<&str>) -> Term {
        let (result, container) = StateContainer::new(states);

        match result {
            StateChangeResult::SignPositive => Term::FermionKet(container),
            StateChangeResult::SignNegative => -Term::FermionKet(container),
            StateChangeResult::StateIsZero =>  Term::Integer(0),
        }
    }

    pub fn new_bra(states: Vec<&str>) -> Term {
        let (result, container) = StateContainer::new(states);

        match result {
            StateChangeResult::SignPositive => Term::FermionBra(container),
            StateChangeResult::SignNegative => -Term::FermionBra(container),
            StateChangeResult::StateIsZero =>  Term::Integer(0),
        }
    }

    pub fn expand(self) -> Term {
        match self {
            Term::Addition(lhs, rhs) => {
                if let Term::Integer(0) = *lhs {
                    return *rhs
                }else if let Term::Integer(0) = *rhs {
                    return *lhs
                }
                
                return lhs.expand() + rhs.expand()
            },
            Term::Multiplication(lhs, rhs) => Term::expand_multiplication(lhs, rhs),
            Term::Negation(inner) => {-inner.expand()},
            _ => self
        }
    }

    fn expand_multiplication(lhs: Box<Term>, rhs: Box<Term>) -> Term {
        if let Term::Integer(0) = *rhs {
            return Term::Integer(0)
        } 
        else if let Term::Integer(1) = *rhs {
            return *lhs
        }

        return match *lhs {
            Term::Integer(0) => Term::Integer(0),
            Term::Integer(1) => *rhs,
            Term::Integer(_) => match *rhs {
                Term::Addition(add_lhs, add_rhs) => (*lhs).clone() * add_lhs.expand() + (*lhs) * add_rhs.expand(),
                _=> (*lhs) * rhs.expand()
            },
            Term::Symbol(_) => match *rhs {
                Term::Integer(_) => (*rhs) * (*lhs),
                Term::Negation(term) => match *term {
                    Term::Integer(_) => -(*term) * (*lhs),
                    _ => (*lhs) * -(*term)
                }
                Term::Addition(add_lhs, add_rhs) => (*lhs).clone() * add_lhs.expand() + (*lhs) * add_rhs.expand(),
                _=> (*lhs) * rhs.expand()
            },
            Term::Addition(lhs_lhs, lhs_rhs) => {
                let expanded_rhs =  (*rhs).expand();
                lhs_lhs.expand() * expanded_rhs.clone() + lhs_rhs.expand() * expanded_rhs
            },
            Term::Multiplication(lhs_lhs, lhs_rhs) => Term::expand_multiplication(lhs_lhs, Box::new(Term::expand_multiplication(lhs_rhs, rhs))),
            Term::Negation(lhs) => -(lhs.expand() * rhs.expand()),
            Term::FermionKet(_) =>  match *rhs {
                Term::Integer(_) | Term::Symbol(_) => (*rhs) * (*lhs),
                Term::Addition(add_lhs, add_rhs) => (*lhs).clone() * add_lhs.expand() + (*lhs) * add_rhs.expand(),
                _=> (*lhs) * rhs.expand()
            },
            Term::FermionBra(bra_state) =>  match *rhs {
                Term::Integer(_) | Term::Symbol(_) => (*rhs) * Term::FermionBra(bra_state),
                Term::Addition(add_lhs, add_rhs) => Term::FermionBra(bra_state.clone()) * add_lhs.expand() + Term::FermionBra(bra_state) * add_rhs.expand(),
                Term::FermionKet(ket_state) => Term::inner_product(bra_state, ket_state),
                Term::Multiplication(mul_lhs, mul_rhs) => match *mul_lhs {
                    Term::Integer(_) | Term::Symbol(_) => (*mul_lhs) * Term::expand_multiplication(Box::new(Term::FermionBra(bra_state)), mul_rhs),
                    _ => Term::FermionBra(bra_state) * Term::expand_multiplication(mul_lhs, mul_rhs)
                }
                _=> Term::FermionBra(bra_state) * rhs.expand()
            }
            Term::Creation(_) | Term::Annihilation(_) => match *rhs {
                Term::Addition(add_lhs, add_rhs) => {
                    Term::expand_multiplication(lhs.clone(), add_lhs) + Term::expand_multiplication(lhs, add_rhs)
                },
                Term::Multiplication(mul_lhs, mul_rhs) => match *mul_lhs {
                    Term::Integer(_) | Term::Symbol(_) => (*mul_lhs) * Term::expand_multiplication(lhs, mul_rhs),
                    _ => (*lhs) * Term::expand_multiplication(mul_lhs, mul_rhs)
                },
                Term::Negation(inner) => -Term::expand_multiplication(lhs, inner),
                Term::FermionKet(mut states) => {
                    match *lhs {
                        Term::Creation(state) => match states.create(state) {
                            StateChangeResult::SignPositive => Term::FermionKet(states),
                            StateChangeResult::SignNegative => -Term::FermionKet(states),
                            StateChangeResult::StateIsZero => Term::Integer(0),
                        },
                        Term::Annihilation(state) => match states.annihilate(state) {
                            StateChangeResult::SignPositive => Term::FermionKet(states),
                            StateChangeResult::SignNegative => -Term::FermionKet(states),
                            StateChangeResult::StateIsZero => Term::Integer(0),
                        },
                        _ => panic!("lhs should be creation or annihilation - something went wrong")
                    }

                },
                Term::FermionBra(_) | Term::Creation(_) | Term::Annihilation(_) => (*lhs) * (*rhs),
                _ => Term::expand_multiplication(rhs, lhs)
            },
        }
    }
    
    fn inner_product(bra_state: StateContainer, ket_state: StateContainer) -> Term {
        if bra_state == ket_state {
            Term::Integer(1)
        } else {
            Term::Integer(0)
        }
    }

}



impl Display for Term {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Term::Integer(number) => write!(f, "{}", number),
            Term::Symbol(name) => write!(f, "{}", name),
            Term::Addition(lhs, rhs) => match **rhs {
                Term::Negation(ref rhs) => write!(f, "({} - {})", lhs, rhs),
                _ => write!(f, "({} + {})", lhs, rhs)
            },
            Term::Multiplication(lhs, rhs) => write!(f, "[{}⋅{}]", lhs, rhs),
            Term::Negation(term) => write!(f, "-{}", term),
            Term::FermionKet(container) => write!(f, "|{}⟩", container),
            Term::FermionBra(container) => write!(f, "⟨{}|", container),
            Term::Creation(state) => write!(f, "c_{}†", state),
            Term::Annihilation(state) => write!(f, "c_{}", state),
        }
    }
}


impl Add for Term {
    type Output = Term;

    fn add(self, rhs: Self) -> Self::Output {
        match self {
            Term::Negation(lhs) => match rhs {
                Term::Negation(rhs) => Term::Negation(Box::new(Term::Addition(lhs, rhs))), // -(a + b)
                _ => Term::Negation(
                    Box::new(Term::Addition(
                        lhs, 
                        Box::new(Term::Negation(Box::new(rhs)))
                    )))  // -(a - b)
            },
            _ => Term::Addition(Box::new(self), Box::new(rhs))
        }
    }
}

impl Sum for Term {
    fn sum<I: Iterator<Item = Self>>(iter: I) -> Self {
        iter.fold(Term::Integer(0), |acc, term| acc + term).expand()
    }
}

impl Sub for Term {
    type Output = Term;

    fn sub(self, rhs: Self) -> Self::Output {
        match self {
            Term::Negation(lhs) => match rhs {
                Term::Negation(rhs) => Term::Negation(
                    Box::new(Term::Addition(
                        lhs, 
                        Box::new(Term::Negation(rhs))
                    ))), // -(a - b)
                _ => Term::Negation(
                    Box::new(Term::Addition(
                        lhs, 
                        Box::new(rhs)
                    )))  // -(a + b)
            },
            _ => match rhs {
                Term::Negation(rhs) => Term::Addition(Box::new(self), rhs),
                _ => Term::Addition(Box::new(self), Box::new(Term::Negation(Box::new(rhs))))
            }
                
        }
    }
}

impl Neg for Term {
    type Output = Term;

    fn neg(self) -> Self::Output {
        match self {
            Term::Integer(0) => self,
            Term::Negation(inner) => *inner,
            _ => Term::Negation(Box::new(self))
        }
        
    }
}

impl Mul for Term {
    type Output = Term;

    fn mul(self, rhs: Self) -> Self::Output {
        match self {
            Term::Negation(inner_lhs) => match rhs {
                Term::Negation(inner_rhs) => Term::Multiplication(inner_lhs, inner_rhs),
                _ => Term::Negation(
                    Box::new(Term::Multiplication(inner_lhs, Box::new(rhs)))
                )
            },
            _ => match rhs {
                Term::Negation(inner_rhs) => Term::Negation(
                    Box::new(Term::Multiplication(Box::new(self),  inner_rhs))
                ),
                _ => Term::Multiplication(Box::new(self), Box::new(rhs)),
            }
        }
    }
}