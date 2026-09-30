use crate::{Options, OutputFormat, value::MQValue};

use pyo3::prelude::*;

#[pyclass]
pub struct MQResult {
    pub values: Vec<MQValue>,
    pub nodes: Vec<mq_markdown::Node>,
    pub options: Options,
}

#[pymethods]
impl MQResult {
    #[getter]
    pub fn text(&self) -> String {
        self.values().join("\n")
    }

    #[getter]
    pub fn values(&self) -> Vec<String> {
        self.values
            .iter()
            .filter_map(|value| {
                if value.__len__() == 0 {
                    None
                } else {
                    Some(value.text())
                }
            })
            .collect::<Vec<String>>()
    }

    /// Render the result in the given output format.
    ///
    /// If `output_format` is omitted, the `output_format` of the `Options`
    /// passed to `run` is used (Markdown by default). The rendering options
    /// (`list_style`, `link_title_style`, `link_url_style`) are applied.
    #[pyo3(signature = (output_format=None))]
    pub fn render(&self, output_format: Option<OutputFormat>) -> String {
        let format = output_format
            .or(self.options.output_format)
            .unwrap_or_default();
        let mut markdown = mq_markdown::Markdown::new(self.nodes.clone());
        markdown.set_options(self.options.render_options());

        match format {
            OutputFormat::Markdown => markdown.to_string(),
            OutputFormat::Html => markdown.to_html(),
            OutputFormat::Text => markdown.to_text(),
        }
    }

    pub fn __len__(&self) -> usize {
        self.values.len()
    }

    pub fn __contains__(&self, value: &MQValue) -> PyResult<bool> {
        Ok(self.values.iter().any(|v| v == value))
    }

    pub fn __getitem__(&self, idx: usize) -> PyResult<MQValue> {
        if idx < self.values.len() {
            Ok(self.values[idx].clone())
        } else {
            Err(pyo3::exceptions::PyIndexError::new_err(format!(
                "Index {} out of range for MQResult with length {}",
                idx,
                self.values.len()
            )))
        }
    }

    fn __repr__(&self) -> String {
        format!("MQResult({} items)", self.values.len())
    }

    fn __str__(&self) -> String {
        self.text()
    }

    fn __eq__(&self, other: &Self) -> bool {
        if self.values.len() != other.values.len() {
            return false;
        }

        self.values
            .iter()
            .zip(other.values.iter())
            .all(|(a, b)| a.__eq__(b))
    }

    fn __ne__(&self, other: &Self) -> bool {
        !self.__eq__(other)
    }

    fn __lt__(&self, other: &Self) -> bool {
        if self.values.len() != other.values.len() {
            return self.values.len() < other.values.len();
        }

        self.values
            .iter()
            .zip(other.values.iter())
            .all(|(a, b)| a.__lt__(b))
    }

    fn __gt__(&self, other: &Self) -> bool {
        if self.values.len() != other.values.len() {
            return self.values.len() > other.values.len();
        }

        self.values
            .iter()
            .zip(other.values.iter())
            .all(|(a, b)| a.__gt__(b))
    }
}

impl From<Vec<MQValue>> for MQResult {
    fn from(values: Vec<MQValue>) -> Self {
        Self {
            values,
            nodes: Vec::new(),
            options: Options::default(),
        }
    }
}
