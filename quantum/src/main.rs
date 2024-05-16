mod quant;

use quant::Term;

fn calculate_matrix_element(bra_state: Vec<&str>, ket_state: Vec<&str>, hamiltonian: Term) -> Term{
    let mut old_term = Term::Integer(0);
    let mut term = Term::new_bra(bra_state) * hamiltonian * Term::new_ket(ket_state);

    while old_term != term {
        old_term = term.clone();
        term = term.expand();
    }

    return term;
}

fn prepare_hamiltonian(upstates: Vec<&str>, downstates: Vec<&str>, energies: Vec<Term>) -> Result<Term, String> {

        if upstates.len() != downstates.len() {
            return Result::Err(String::from("Upstate must have same amount of elements as Downstates"));
        }

        if upstates.len() != energies.len() {
            return Result::Err(String::from("Upstate must have same amount of elements as Energies"));
        }

        let e = Term::new_symbol("E");
        let j = Term::new_symbol("J");

        let h_up: Term = energies.iter().zip(&upstates).map(|(ei, &s)| e.clone() * ei.clone() * Term::fd(s) * Term::f(s)).sum();
        let h_down: Term = energies.iter().zip(&downstates).map(|(ei, &s)| e.clone() * ei.clone() * Term::fd(s) * Term::f(s)).sum();

        let h_ww_up: Term = upstates.iter().flat_map(
            |&x| upstates.iter().map(move |&y| Term::fd(x) * Term::f(y))
        ).sum();

        let h_ww_down: Term = downstates.iter().flat_map(
            |&x| downstates.iter().map(move |&y| Term::fd(x) * Term::f(y))
        ).sum();

        return Result::Ok(h_up + h_down + j.clone() * h_ww_up - j * h_ww_down);

}


fn main() {

    let states = vec!["111", "211", "121", "112", "221", "212", "122", "311", "131", "113", "222"];
    let energies: Vec<u64> = vec![3, 6, 6, 6, 9, 9, 9, 11, 11, 11, 12];

    let up_states_strings: Vec<String> = states.iter().map(|&x| format!("{}↑", x)).collect();
    let up_states: Vec<&str> = up_states_strings.iter().map(|x| x.as_str()).collect();

    let down_states_strings: Vec<String> = states.iter().map(|&x| format!("{}↓", x)).collect();
    let down_states: Vec<&str> = down_states_strings.iter().map(|x| x.as_str()).collect();

    let energy_terms = energies.iter().map(|&x| Term::Integer(x)).collect();

    let h = prepare_hamiltonian(
        up_states.clone(), 
        down_states.clone(), 
        energy_terms
    ).unwrap();

    let all_single_states = [up_states, down_states].concat();


    // let all_states: Vec<Vec<&str>>  = all_single_states.iter().enumerate().flat_map(
    //     |(i, &s)| all_single_states.iter().skip(i + 1).map(move |&r| vec![s, r])
    // ).collect();

    let all_states: Vec<Vec<&str>> = all_single_states.iter().map(|&x|vec![x]).collect();
    let all_states_string : Vec<String> = all_states.iter().map(|x| x.join(",")).collect();
    println!("{}", all_states_string.join("; "));

    println!("---");

    for left_state in all_states.iter() {
        let mut res: Vec<Term> = Vec::with_capacity(all_states.len());

        for right_state in all_states.iter() {
            res.push(
                calculate_matrix_element(left_state.clone(), right_state.clone(), h.clone())
            );
        }

        let res_string: Vec<String> = res.iter().map(|x| format!("{x}")).collect();
        println!("{}", res_string.join(","));
    }
}
