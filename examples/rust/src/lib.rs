use pyo3::prelude::*;
use rayon::prelude::*;

#[pyfunction]
fn process_frame(data: Vec<u8>, width: usize, height: usize, scale: usize) -> PyResult<String> {
    // ASCII characters from dark to light
    const ASCII_CHARS: &[char] = &[' ', '.', ':', '-', '=', '+', '*', '#', '%', '@'];

    // Process in chunks for each character position
    let chars_per_row = width / scale;
    let rows = height / scale;

    let mut result = String::with_capacity(rows * (chars_per_row + 1));

    for y in 0..rows {
        for x in 0..chars_per_row {
            let mut brightness_sum = 0u32;
            let mut pixel_count = 0u32;

            // Average the brightness of the pixel block
            for dy in 0..scale {
                for dx in 0..scale {
                    let py = y * scale + dy;
                    let px = x * scale + dx;

                    if py < height && px < width {
                        let idx = (py * width + px) * 3;
                        if idx + 2 < data.len() {
                            // Average RGB values for brightness
                            brightness_sum +=
                                (data[idx] as u32 + data[idx + 1] as u32 + data[idx + 2] as u32)
                                    / 3;
                            pixel_count += 1;
                        }
                    }
                }
            }

            if pixel_count > 0 {
                let avg_brightness = brightness_sum / pixel_count;
                let char_idx = (avg_brightness * ASCII_CHARS.len() as u32 / 256) as usize;
                result.push(ASCII_CHARS[char_idx.min(ASCII_CHARS.len() - 1)]);
            } else {
                result.push(' ');
            }
        }
        result.push('\n');
    }

    Ok(result)
}

#[pyfunction]
fn process_frame_parallel(
    data: Vec<u8>,
    width: usize,
    height: usize,
    scale: usize,
) -> PyResult<String> {
    const ASCII_CHARS: &str = " .:-=+*#%@";

    let chars_per_row = width / scale;
    let rows = height / scale;

    // Parallel processing
    let ascii_rows: Vec<String> = (0..rows)
        .into_par_iter()
        .map(|y| {
            (0..chars_per_row)
                .map(|x| {
                    let mut brightness_sum = 0u32;
                    let mut pixel_count = 0u32;

                    for dy in 0..scale {
                        for dx in 0..scale {
                            let py = y * scale + dy;
                            let px = x * scale + dx;

                            if py < height && px < width {
                                let idx = (py * width + px) * 3;
                                if idx + 2 < data.len() {
                                    brightness_sum += (data[idx] as u32
                                        + data[idx + 1] as u32
                                        + data[idx + 2] as u32)
                                        / 3;
                                    pixel_count += 1;
                                }
                            }
                        }
                    }

                    if pixel_count > 0 {
                        let avg_brightness = brightness_sum / pixel_count;
                        let char_idx = (avg_brightness * 10 / 256) as usize;
                        ASCII_CHARS.chars().nth(char_idx.min(9)).unwrap_or(' ')
                    } else {
                        ' '
                    }
                })
                .collect::<String>()
        })
        .collect();

    Ok(ascii_rows.join("\n"))
}

#[pymodule]
fn video_filters(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process_frame, m)?)?;
    m.add_function(wrap_pyfunction!(process_frame_parallel, m)?)?;
    Ok(())
}
