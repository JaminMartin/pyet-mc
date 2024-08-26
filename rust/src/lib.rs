use pyo3::prelude::*;
use rayon::prelude::*;


#[pyfunction]
pub fn general_energy_transfer(time: Vec<f64>, radial_data: Vec<f64>, amp: f64, cr: f64, rad: f64, offset: f64) -> PyResult<Vec<f64>> {
    let n = radial_data.len() as f64;

    let mut result = Vec::with_capacity(time.len());

    for t in &time {
        let mut sum = 0.0;
        for r in &radial_data {
            sum += (-t * (cr * r + rad)).exp();
        }
        result.push(amp / n * sum + offset);
    }

    Ok(result)
}

#[pyfunction]
pub fn general_energy_transfer_para(time: Vec<f64>, radial_data: Vec<f64>, amp: f64, cr: f64, rad: f64, offset: f64) -> PyResult<Vec<f64>> {
    let n = radial_data.len() as f64;


    let result = time.par_iter().map(|t| {
        let sum: f64 = radial_data.iter().map(|r| (-t * (cr * r + rad)).exp()).sum();
        amp / n * sum + offset
    }).collect();

    Ok(result)
}



#[pymodule]
fn _pyet_mc(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(general_energy_transfer, m)?)?;
    m.add_function(wrap_pyfunction!(general_energy_transfer_para, m)?)?;
    Ok(())
}
