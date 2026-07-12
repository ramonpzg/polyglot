#pragma once

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <expected>
#include <filesystem>
#include <fstream>
#if __has_include(<mdspan>)
  #include <mdspan>
#else
  #include <experimental/mdspan>
  namespace std { using std::experimental::mdspan; using std::experimental::dextents; }
#endif
#include <numeric>
#include <optional>
#include <random>
#include <ranges>
#include <span>
#include <sstream>
#include <string>
#include <string_view>
#include <tuple>
#include <utility>
#include <vector>

namespace numcrunch {

// Basic PODs exposed to Python
struct cash_flow {
  double revenue{};
  double cost{};
};

struct market_parameters {
  double base_price{};     // nominal base price level
  double price_vol{};      // annualized volatility
  double discount_rate{};  // rate used for NPV discounting
};

// Simple result containers we can convert to dict in bindings
struct simulation_results {
  double mean_grade{};
  double p10{};
  double p50{};
  double p90{};
  std::uint64_t iterations{};
};

struct financial_distribution {
  double mean{};
  double p10{};
  double p50{};
  double p90{};
};

struct environmental_impact {
  double expected_contaminated_volume{};
  double max_concentration{};
};

enum class simulation_error { invalid_input };
enum class calculation_error { invalid_input };
enum class modeling_error { invalid_input };

struct geology_model {
  std::vector<double> grid;  // flattened [x*y*z]
  std::size_t nx{}, ny{}, nz{};
};

// constexpr LUT example
constexpr auto risk_calculation_lut = []() {
  std::array<double, 1024> lut{};
  for (std::size_t i = 0; i < lut.size(); ++i) {
    double x = static_cast<double>(i) / static_cast<double>(lut.size() - 1);
    lut[i] = std::sqrt(1.0 + x) / (1.0 + x * x * 0.1);
  }
  return lut;
}();

class monte_carlo_engine {
 public:
  explicit monte_carlo_engine(std::random_device::result_type seed)
      : seed_(seed == 0 ? std::random_device{}() : seed) {}

  [[nodiscard]] std::expected<simulation_results, simulation_error>
  run_geological_simulation(const geology_model &model,
                            std::size_t num_iterations = 1'000'000) const {
    if (model.grid.empty() || model.nx == 0 || model.ny == 0 || model.nz == 0) {
      return std::unexpected(simulation_error::invalid_input);
    }

    // Create an mdspan over the data
    std::mdspan<const double, std::dextents<std::size_t, 3>> grid(
        model.grid.data(), model.nx, model.ny, model.nz);

    std::mt19937_64 rng(seed_);
    std::uniform_int_distribution<std::size_t> dx(0, model.nx - 1),
        dy(0, model.ny - 1), dz(0, model.nz - 1);

    double sum = 0.0;
    std::vector<double> samples;
    samples.reserve(num_iterations);

    for (std::size_t i = 0; i < num_iterations; ++i) {
      auto x = dx(rng), y = dy(rng), z = dz(rng);
      double grade = grid(x, y, z);
      // Light transformation using LUT for demo
      auto idx = static_cast<std::size_t>((grade - 0.0) * 1023.0);
      idx = std::min<std::size_t>(std::max<std::size_t>(idx, 0), 1023);
      double adjusted = grade * risk_calculation_lut[idx];
      samples.push_back(adjusted);
      sum += adjusted;
    }

    std::ranges::sort(samples);
    auto pct = [&](double p) {
      auto pos = static_cast<std::size_t>(p * (samples.size() - 1));
      return samples[pos];
    };

    simulation_results res{};
    res.mean_grade = sum / static_cast<double>(num_iterations);
    res.p10 = pct(0.10);
    res.p50 = pct(0.50);
    res.p90 = pct(0.90);
    res.iterations = static_cast<std::uint64_t>(num_iterations);
    return res;
  }

  [[nodiscard]] std::expected<financial_distribution, calculation_error>
  calculate_project_npv(std::span<const cash_flow> flows,
                        const market_parameters &market) const {
    if (flows.empty()) return std::unexpected(calculation_error::invalid_input);

    std::mt19937 rng(static_cast<unsigned>(seed_));
    std::lognormal_distribution<double> price_shock(0.0, market.price_vol);

    constexpr std::size_t trials = 100'000;  // fixed Monte Carlo for NPV
    std::vector<double> npvs;
    npvs.reserve(trials);

    for (std::size_t t = 0; t < trials; ++t) {
      double price = market.base_price * price_shock(rng);
      double npv = 0.0;
      for (std::size_t i = 0; i < flows.size(); ++i) {
        double cf = (flows[i].revenue * price) - flows[i].cost;
        double disc = std::pow(1.0 + market.discount_rate, static_cast<double>(i + 1));
        npv += cf / disc;
      }
      npvs.push_back(npv);
    }

    std::ranges::sort(npvs);
    auto pct = [&](double p) {
      auto pos = static_cast<std::size_t>(p * (npvs.size() - 1));
      return npvs[pos];
    };

    financial_distribution dist{};
    dist.mean = std::accumulate(npvs.begin(), npvs.end(), 0.0) / static_cast<double>(npvs.size());
    dist.p10 = pct(0.10);
    dist.p50 = pct(0.50);
    dist.p90 = pct(0.90);
    return dist;
  }

 private:
  std::random_device::result_type seed_;
};

class australian_mining_model {
 public:
  void load_pilbara_data(const std::filesystem::path &data_file) {
    // Expect CSV rows: x,y,z,grade
    std::ifstream f(data_file);
    if (!f) return;  // no-throw; model remains empty
    std::string line;
    std::vector<std::tuple<std::size_t, std::size_t, std::size_t, double>> rows;
    std::size_t maxx = 0, maxy = 0, maxz = 0;
    // skip header if present
    std::getline(f, line);
    auto looks_header = line.find("x") != std::string::npos;
    if (!looks_header) {
      f.seekg(0);
    }
    while (std::getline(f, line)) {
      if (line.empty()) continue;
      std::size_t x = 0, y = 0, z = 0;
      double g = 0.0;
      char sep;
      std::istringstream ss(line);
      if (!(ss >> x >> sep >> y >> sep >> z >> sep >> g)) continue;
      rows.emplace_back(x, y, z, g);
      maxx = std::max(maxx, x);
      maxy = std::max(maxy, y);
      maxz = std::max(maxz, z);
    }
    nx_ = maxx + 1; ny_ = maxy + 1; nz_ = maxz + 1;
    grid_.assign(nx_ * ny_ * nz_, 0.0);
    auto idx = [&](std::size_t x, std::size_t y, std::size_t z) { return (x * ny_ + y) * nz_ + z; };
    for (auto [x, y, z, g] : rows) {
      grid_[idx(x, y, z)] = g;
    }
  }

  [[nodiscard]] geology_model create_geology_model() const {
    return geology_model{grid_, nx_, ny_, nz_};
  }

  [[nodiscard]] std::expected<environmental_impact, modeling_error>
  simulate_water_contamination([[maybe_unused]] const std::tuple<double, double, double> &source,
                               std::chrono::years years) const {
    // Toy diffusion-like growth with saturation
    double t = static_cast<double>(years.count());
    double expected_volume = (nx_ * ny_) * (1.0 - std::exp(-0.1 * t));
    double max_conc = 1.0 / (1.0 + 0.05 * t);
    return environmental_impact{expected_volume, max_conc};
  }

 private:
  std::vector<double> grid_{};
  std::size_t nx_{0}, ny_{0}, nz_{0};
};

}  // namespace numcrunch
