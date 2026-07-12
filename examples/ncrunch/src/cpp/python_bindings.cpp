#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <chrono>
#include <sstream>

#include "monte_carlo.hpp"

namespace py = pybind11;
using namespace numcrunch;

namespace {

py::dict to_dict(const simulation_results &r) {
  py::dict d;
  d["mean_grade"] = r.mean_grade;
  d["p10"] = r.p10;
  d["p50"] = r.p50;
  d["p90"] = r.p90;
  d["iterations"] = r.iterations;
  return d;
}

py::dict to_dict(const financial_distribution &r) {
  py::dict d;
  d["mean"] = r.mean;
  d["p10"] = r.p10;
  d["p50"] = r.p50;
  d["p90"] = r.p90;
  return d;
}

py::dict to_dict(const environmental_impact &r) {
  py::dict d;
  d["expected_contaminated_volume"] = r.expected_contaminated_volume;
  d["max_concentration"] = r.max_concentration;
  return d;
}

}  // namespace

PYBIND11_MODULE(_cpp_core, m) {
  m.doc() = "NumCrunch: High-performance mining risk calculations";

  py::class_<cash_flow>(m, "CashFlow")
      .def(py::init<double, double>(), py::arg("revenue"), py::arg("cost"))
      .def_readwrite("revenue", &cash_flow::revenue)
      .def_readwrite("cost", &cash_flow::cost);

  py::class_<market_parameters>(m, "MarketParameters")
      .def(py::init<double, double, double>(), py::arg("base_price"), py::arg("price_vol"),
           py::arg("discount_rate"))
      .def_readwrite("base_price", &market_parameters::base_price)
      .def_readwrite("price_vol", &market_parameters::price_vol)
      .def_readwrite("discount_rate", &market_parameters::discount_rate);

  py::class_<geology_model>(m, "GeologyModel")
      .def_property_readonly("shape", [](const geology_model &g) {
        return py::make_tuple(g.nx, g.ny, g.nz);
      });

  py::class_<monte_carlo_engine>(m, "MonteCarloEngine")
      .def(py::init<std::uint32_t>(), py::arg("seed") = 0)
      .def("run_geological_simulation",
           [](const monte_carlo_engine &self, const geology_model &model,
              std::size_t num_iterations) {
             auto r = self.run_geological_simulation(model, num_iterations);
             if (!r) throw std::runtime_error("invalid geological model input");
             return to_dict(*r);
           },
           py::arg("model"), py::arg("num_iterations") = 1'000'000)
      .def("calculate_project_npv",
           [](const monte_carlo_engine &self, const std::vector<cash_flow> &flows,
              const market_parameters &market) {
             auto r = self.calculate_project_npv(flows, market);
             if (!r) throw std::runtime_error("invalid NPV inputs");
             return to_dict(*r);
           },
           py::arg("flows"), py::arg("market"));

  py::class_<australian_mining_model>(m, "AustralianMiningModel")
      .def(py::init<>())
      .def("load_pilbara_data", &australian_mining_model::load_pilbara_data,
           py::arg("data_file"))
      .def("create_geology_model", &australian_mining_model::create_geology_model)
      .def("simulate_water_contamination",
           [](const australian_mining_model &self, py::object source, int years) {
             std::tuple<double, double, double> src{0.0, 0.0, 0.0};
             if (!source.is_none()) {
               try {
                 auto t = source.cast<std::tuple<double, double, double>>();
                 src = t;
               } catch (...) {
                 // ignore and use default
               }
             }
             auto r = self.simulate_water_contamination(src, std::chrono::years{years});
             if (!r) throw std::runtime_error("invalid contamination inputs");
             return to_dict(*r);
           },
           py::arg("source"), py::arg("years"));
}

