/*
 * Bush Ears - Real-time Australian wildlife audio identification
 * Modern C++ implementation for high-performance audio processing and ML inference
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <pybind11/chrono.h>

#include <vector>
#include <array>
#include <string>
#include <unordered_map>
#include <algorithm>
#include <numeric>
#include <execution>
#include <cmath>
#include <complex>
#include <chrono>
#include <memory>
#include <random>
#include <optional>

namespace py = pybind11;

// Australian wildlife species database
enum class AustralianSpecies : uint8_t {
    Unknown = 0,
    Kookaburra = 1,
    Magpie = 2,
    Galah = 3,
    Cockatoo = 4,
    Lorikeet = 5,
    Butcherbird = 6,
    WattleBird = 7,
    Koala = 8,
    PossumBrushtail = 9,
    Dingo = 10,
    FruitBat = 11
};

// Species data with call characteristics
struct SpeciesProfile {
    AustralianSpecies species;
    std::string common_name;
    std::string scientific_name;
    double min_frequency;    // Hz
    double max_frequency;    // Hz
    double typical_duration; // seconds
    double conservation_weight; // ecosystem importance (0-1)
    std::vector<double> call_pattern; // frequency signature
};

// Audio processing utilities
class AudioProcessor {
private:
    static constexpr size_t SAMPLE_RATE = 44100;
    static constexpr size_t FFT_SIZE = 1024;
    static constexpr size_t HOP_SIZE = 512;
    
    std::vector<std::complex<double>> fft_buffer_;
    std::vector<double> window_;
    std::vector<double> magnitude_spectrum_;
    
public:
    AudioProcessor() : fft_buffer_(FFT_SIZE), 
                      window_(FFT_SIZE), 
                      magnitude_spectrum_(FFT_SIZE / 2 + 1) {
        // Initialize Hann window for audio analysis
        for (size_t i = 0; i < FFT_SIZE; ++i) {
            window_[i] = 0.5 * (1.0 - std::cos(2.0 * M_PI * i / (FFT_SIZE - 1)));
        }
    }
    
    // Extract audio features for wildlife identification
    std::vector<double> extract_features(const std::vector<double>& audio_data) {
        
        if (audio_data.size() < FFT_SIZE) {
            throw std::runtime_error("Audio segment too short for analysis");
        }
        
        // Apply window and compute FFT
        for (size_t i = 0; i < FFT_SIZE; ++i) {
            fft_buffer_[i] = std::complex<double>(audio_data[i] * window_[i], 0.0);
        }
        
        // Simple DFT (in production, use FFTW or similar)
        compute_dft();
        
        // Extract magnitude spectrum
        for (size_t i = 0; i < FFT_SIZE / 2 + 1; ++i) {
            magnitude_spectrum_[i] = std::abs(fft_buffer_[i]);
        }
        
        // Extract key features for wildlife identification
        std::vector<double> features;
        features.reserve(8);
        
        // Spectral features
        features.push_back(compute_spectral_centroid());
        features.push_back(compute_spectral_bandwidth());
        features.push_back(compute_spectral_rolloff());
        features.push_back(compute_zero_crossing_rate(audio_data));
        
        // Energy in frequency bands (important for bird call identification)
        features.push_back(compute_band_energy(0, 1000));     // Low frequency
        features.push_back(compute_band_energy(1000, 4000));  // Mid frequency  
        features.push_back(compute_band_energy(4000, 8000));  // High frequency
        features.push_back(compute_band_energy(8000, 22050)); // Very high frequency
        
        return features;
    }
    
    // Real-time spectrogram computation for visualization
    py::array_t<double> compute_spectrogram(py::array_t<double> audio) {
        auto buf = audio.request();
        auto* ptr = static_cast<double*>(buf.ptr);
        size_t length = buf.shape[0];
        
        size_t num_frames = (length - FFT_SIZE) / HOP_SIZE + 1;
        size_t freq_bins = FFT_SIZE / 2 + 1;
        
        auto result = py::array_t<double>({num_frames, freq_bins});
        auto result_buf = result.request();
        auto* result_ptr = static_cast<double*>(result_buf.ptr);
        
        // Process audio in overlapping windows
        for (size_t frame = 0; frame < num_frames; ++frame) {
            size_t start_idx = frame * HOP_SIZE;
            std::vector<double> segment(ptr + start_idx, ptr + start_idx + FFT_SIZE);
            
            try {
                auto features = extract_features(segment);
                // Copy magnitude spectrum to result
                std::copy(magnitude_spectrum_.begin(), magnitude_spectrum_.end(),
                         result_ptr + frame * freq_bins);
            } catch (const std::exception&) {
                // Fill with zeros on error
                std::fill(result_ptr + frame * freq_bins, 
                         result_ptr + (frame + 1) * freq_bins, 0.0);
            }
        }
        
        return result;
    }

private:
    void compute_dft() {
        // Simplified DFT (use FFTW in production for better performance)
        std::vector<std::complex<double>> temp(FFT_SIZE);
        
        for (size_t k = 0; k < FFT_SIZE; ++k) {
            std::complex<double> sum(0.0, 0.0);
            for (size_t n = 0; n < FFT_SIZE; ++n) {
                double angle = -2.0 * M_PI * k * n / FFT_SIZE;
                sum += fft_buffer_[n] * std::complex<double>(std::cos(angle), std::sin(angle));
            }
            temp[k] = sum;
        }
        
        fft_buffer_ = std::move(temp);
    }
    
    double compute_spectral_centroid() {
        double weighted_sum = 0.0;
        double magnitude_sum = 0.0;
        
        for (size_t i = 0; i < magnitude_spectrum_.size(); ++i) {
            double freq = i * SAMPLE_RATE / (2.0 * (magnitude_spectrum_.size() - 1));
            weighted_sum += freq * magnitude_spectrum_[i];
            magnitude_sum += magnitude_spectrum_[i];
        }
        
        return magnitude_sum > 0 ? weighted_sum / magnitude_sum : 0.0;
    }
    
    double compute_spectral_bandwidth() {
        double centroid = compute_spectral_centroid();
        double weighted_deviation = 0.0;
        double magnitude_sum = 0.0;
        
        for (size_t i = 0; i < magnitude_spectrum_.size(); ++i) {
            double freq = i * SAMPLE_RATE / (2.0 * (magnitude_spectrum_.size() - 1));
            double deviation = freq - centroid;
            weighted_deviation += deviation * deviation * magnitude_spectrum_[i];
            magnitude_sum += magnitude_spectrum_[i];
        }
        
        return magnitude_sum > 0 ? std::sqrt(weighted_deviation / magnitude_sum) : 0.0;
    }
    
    double compute_spectral_rolloff(double threshold = 0.85) {
        double total_energy = std::accumulate(magnitude_spectrum_.begin(), 
                                            magnitude_spectrum_.end(), 0.0);
        double cumulative_energy = 0.0;
        double target_energy = total_energy * threshold;
        
        for (size_t i = 0; i < magnitude_spectrum_.size(); ++i) {
            cumulative_energy += magnitude_spectrum_[i];
            if (cumulative_energy >= target_energy) {
                return i * SAMPLE_RATE / (2.0 * (magnitude_spectrum_.size() - 1));
            }
        }
        
        return SAMPLE_RATE / 2.0;  // Nyquist frequency
    }
    
    double compute_zero_crossing_rate(const std::vector<double>& audio_data) {
        size_t crossings = 0;
        for (size_t i = 1; i < audio_data.size(); ++i) {
            if ((audio_data[i-1] >= 0.0) != (audio_data[i] >= 0.0)) {
                crossings++;
            }
        }
        return static_cast<double>(crossings) / audio_data.size();
    }
    
    double compute_band_energy(double min_freq, double max_freq) {
        size_t start_bin = static_cast<size_t>(min_freq * 2 * magnitude_spectrum_.size() / SAMPLE_RATE);
        size_t end_bin = static_cast<size_t>(max_freq * 2 * magnitude_spectrum_.size() / SAMPLE_RATE);
        
        start_bin = std::min(start_bin, magnitude_spectrum_.size() - 1);
        end_bin = std::min(end_bin, magnitude_spectrum_.size());
        
        return std::accumulate(magnitude_spectrum_.begin() + start_bin,
                             magnitude_spectrum_.begin() + end_bin, 0.0);
    }
};

// Lightweight ML inference engine for species classification
class WildlifeClassifier {
private:
    std::unordered_map<AustralianSpecies, SpeciesProfile> species_database_;
    std::vector<std::vector<double>> model_weights_; // Simple neural network weights
    
public:
    WildlifeClassifier() {
        initialize_species_database();
        initialize_classifier_model();
    }
    
    // Classify audio features
    AustralianSpecies classify_audio_features(const std::vector<double>& features) {
        
        if (features.size() != 8) {
            return AustralianSpecies::Unknown;
        }
        
        // Simple neural network inference (1 hidden layer)
        std::vector<double> hidden_layer = compute_hidden_layer(features);
        std::vector<double> output_layer = compute_output_layer(hidden_layer);
        
        // Find species with highest probability
        auto max_iter = std::max_element(output_layer.begin(), output_layer.end());
        size_t predicted_class = std::distance(output_layer.begin(), max_iter);
        
        double confidence = *max_iter;
        
        if (confidence < 0.3) {
            return AustralianSpecies::Unknown;
        }
        
        return static_cast<AustralianSpecies>(predicted_class + 1);
    }
    
    // Get species information
    std::optional<SpeciesProfile> get_species_info(AustralianSpecies species) const {
        auto it = species_database_.find(species);
        return it != species_database_.end() ? 
               std::make_optional(it->second) : 
               std::nullopt;
    }
    
    // Batch processing for performance testing
    std::vector<AustralianSpecies> classify_batch(const std::vector<std::vector<double>>& feature_batch) {
        std::vector<AustralianSpecies> results;
        results.reserve(feature_batch.size());
        
        // Process each feature vector
        for (const auto& features : feature_batch) {
            results.push_back(classify_audio_features(features));
        }
        
        return results;
    }

private:
    void initialize_species_database() {
        // Australian wildlife with realistic call characteristics
        species_database_ = {
            {AustralianSpecies::Kookaburra, {
                AustralianSpecies::Kookaburra,
                "Laughing Kookaburra",
                "Dacelo novaeguineae", 
                200.0, 2000.0, 3.0, 0.8,
                {0.1, 0.3, 0.8, 0.4, 0.2, 0.1, 0.05, 0.02}
            }},
            {AustralianSpecies::Magpie, {
                AustralianSpecies::Magpie,
                "Australian Magpie",
                "Gymnorhina tibicen",
                400.0, 4000.0, 2.5, 0.9,
                {0.05, 0.2, 0.6, 0.7, 0.3, 0.15, 0.08, 0.03}
            }},
            {AustralianSpecies::Galah, {
                AustralianSpecies::Galah,
                "Galah",
                "Eolophus roseicapilla",
                800.0, 3500.0, 1.5, 0.7,
                {0.02, 0.1, 0.4, 0.8, 0.5, 0.2, 0.1, 0.05}
            }},
            {AustralianSpecies::Koala, {
                AustralianSpecies::Koala,
                "Koala",
                "Phascolarctos cinereus",
                100.0, 1200.0, 4.0, 1.0,
                {0.3, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005}
            }},
            {AustralianSpecies::Dingo, {
                AustralianSpecies::Dingo,
                "Dingo",
                "Canis dingo",
                150.0, 1500.0, 2.0, 0.95,
                {0.2, 0.4, 0.3, 0.15, 0.08, 0.04, 0.02, 0.01}
            }}
        };
    }
    
    void initialize_classifier_model() {
        // Simple neural network: 8 inputs -> 16 hidden -> 12 outputs (species)
        // In production, load from trained model file
        
        // Hidden layer weights (8x16)
        model_weights_.resize(2);
        model_weights_[0].resize(8 * 16);
        model_weights_[1].resize(16 * 12);
        
        // Initialize with small random values
        std::random_device rd;
        std::mt19937 gen(rd());
        std::normal_distribution<double> dist(0.0, 0.1);
        
        for (auto& weight : model_weights_[0]) {
            weight = dist(gen);
        }
        for (auto& weight : model_weights_[1]) {
            weight = dist(gen);
        }
    }
    
    std::vector<double> compute_hidden_layer(const std::vector<double>& features) {
        std::vector<double> hidden(16, 0.0);
        
        for (size_t h = 0; h < 16; ++h) {
            for (size_t i = 0; i < 8; ++i) {
                hidden[h] += features[i] * model_weights_[0][i * 16 + h];
            }
            hidden[h] = std::tanh(hidden[h]); // Activation function
        }
        
        return hidden;
    }
    
    std::vector<double> compute_output_layer(const std::vector<double>& hidden) {
        std::vector<double> output(12, 0.0);
        
        for (size_t o = 0; o < 12; ++o) {
            for (size_t h = 0; h < 16; ++h) {
                output[o] += hidden[h] * model_weights_[1][h * 12 + o];
            }
        }
        
        // Softmax activation
        double max_val = *std::max_element(output.begin(), output.end());
        for (auto& x : output) {
            x = std::exp(x - max_val);
        }
        
        double sum = std::accumulate(output.begin(), output.end(), 0.0);
        for (auto& x : output) {
            x = x / sum;
        }
        
        return output;
    }
};

// Real-time ecosystem monitoring system
class EcosystemMonitor {
private:
    AudioProcessor processor_;
    WildlifeClassifier classifier_;
    
    // Ecosystem health metrics
    struct EcosystemMetrics {
        std::unordered_map<AustralianSpecies, size_t> species_counts;
        double biodiversity_index;
        double conservation_score;
        std::chrono::time_point<std::chrono::steady_clock> last_update;
        size_t total_detections;
    };
    
    EcosystemMetrics metrics_;
    
public:
    EcosystemMonitor() : metrics_{} {
        metrics_.last_update = std::chrono::steady_clock::now();
    }
    
    // Process real-time audio stream
    py::dict process_audio_stream(py::array_t<double> audio_chunk) {
        auto buf = audio_chunk.request();
        std::vector<double> audio_data(static_cast<double*>(buf.ptr), 
                                      static_cast<double*>(buf.ptr) + buf.shape[0]);
        
        py::dict result;
        
        try {
            // Extract features
            auto features = processor_.extract_features(audio_data);
            
            // Classify species
            auto species = classifier_.classify_audio_features(features);
            
            if (species != AustralianSpecies::Unknown) {
                // Update ecosystem metrics
                update_ecosystem_metrics(species);
                
                // Get species information
                if (auto species_info = classifier_.get_species_info(species)) {
                    result["species_detected"] = true;
                    result["species_id"] = static_cast<int>(species);
                    result["common_name"] = species_info->common_name;
                    result["scientific_name"] = species_info->scientific_name;
                    result["conservation_weight"] = species_info->conservation_weight;
                }
            } else {
                result["species_detected"] = false;
            }
            
            // Add audio features for visualization
            py::list feature_list;
            for (double feature : features) {
                feature_list.append(feature);
            }
            result["audio_features"] = feature_list;
            
        } catch (const std::exception& e) {
            result["error"] = e.what();
            result["species_detected"] = false;
        }
        
        // Add current ecosystem metrics
        result["ecosystem_health"] = get_ecosystem_health_score();
        result["biodiversity_index"] = metrics_.biodiversity_index;
        result["total_detections"] = metrics_.total_detections;
        
        return result;
    }
    
    // Batch processing for performance comparison
    std::vector<int> classify_audio_batch(const std::vector<std::vector<double>>& audio_segments) {
        std::vector<std::vector<double>> all_features;
        all_features.reserve(audio_segments.size());
        
        // Extract features for all segments
        for (const auto& segment : audio_segments) {
            try {
                auto features = processor_.extract_features(segment);
                all_features.push_back(features);
            } catch (const std::exception&) {
                all_features.push_back(std::vector<double>(8, 0.0));
            }
        }
        
        // Classify all at once
        auto species_results = classifier_.classify_batch(all_features);
        
        // Convert to int for Python
        std::vector<int> int_results;
        int_results.reserve(species_results.size());
        for (AustralianSpecies s : species_results) {
            int_results.push_back(static_cast<int>(s));
        }
        
        return int_results;
    }
    
    py::dict get_ecosystem_report() {
        py::dict report;
        
        // Species diversity
        py::dict species_counts;
        for (const auto& [species, count] : metrics_.species_counts) {
            if (auto info = classifier_.get_species_info(species)) {
                species_counts[info->common_name.c_str()] = count;
            }
        }
        report["species_counts"] = species_counts;
        
        // Health metrics
        report["biodiversity_index"] = metrics_.biodiversity_index;
        report["conservation_score"] = metrics_.conservation_score;
        report["total_detections"] = metrics_.total_detections;
        
        auto now = std::chrono::steady_clock::now();
        auto monitoring_duration = std::chrono::duration_cast<std::chrono::seconds>(
            now - metrics_.last_update).count();
        report["monitoring_duration_seconds"] = monitoring_duration;
        
        return report;
    }
    
    void reset_metrics() {
        metrics_ = EcosystemMetrics{};
        metrics_.last_update = std::chrono::steady_clock::now();
    }

private:
    void update_ecosystem_metrics(AustralianSpecies species) {
        metrics_.species_counts[species]++;
        metrics_.total_detections++;
        
        // Calculate Shannon biodiversity index
        size_t total = metrics_.total_detections;
        double shannon_index = 0.0;
        
        for (const auto& [sp, count] : metrics_.species_counts) {
            double proportion = static_cast<double>(count) / total;
            if (proportion > 0) {
                shannon_index -= proportion * std::log(proportion);
            }
        }
        
        metrics_.biodiversity_index = shannon_index;
        
        // Calculate conservation score (weighted by species importance)
        double conservation_sum = 0.0;
        for (const auto& [sp, count] : metrics_.species_counts) {
            if (auto info = classifier_.get_species_info(sp)) {
                conservation_sum += count * info->conservation_weight;
            }
        }
        metrics_.conservation_score = conservation_sum / total;
    }
    
    double get_ecosystem_health_score() {
        // Combine biodiversity and conservation metrics
        double diversity_score = std::min(metrics_.biodiversity_index / 2.0, 1.0); // Normalize
        return (diversity_score + metrics_.conservation_score) / 2.0;
    }
};

// Synthetic audio generator for testing and demos
class AudioSimulator {
private:
    static constexpr double SAMPLE_RATE = 44100.0;
    
public:
    // Generate synthetic bird call with specific characteristics
    py::array_t<double> generate_bird_call(AustralianSpecies species, double duration = 2.0) {
        size_t samples = static_cast<size_t>(duration * SAMPLE_RATE);
        auto result = py::array_t<double>(samples);
        auto buf = result.request();
        auto* data = static_cast<double*>(buf.ptr);
        
        // Get species profile for call characteristics
        WildlifeClassifier classifier;
        auto species_info = classifier.get_species_info(species);
        
        if (!species_info) {
            // Generate silence for unknown species
            std::fill(data, data + samples, 0.0);
            return result;
        }
        
        // Generate synthetic call based on species characteristics
        double freq_center = (species_info->min_frequency + species_info->max_frequency) / 2.0;
        double freq_range = species_info->max_frequency - species_info->min_frequency;
        
        // Generate audio samples
        for (size_t i = 0; i < samples; ++i) {
            double t = static_cast<double>(i) / SAMPLE_RATE;
            
            // Frequency modulation for natural sound
            double freq_mod = freq_center + 
                            freq_range * 0.3 * std::sin(2.0 * M_PI * 5.0 * t);
            
            // Amplitude envelope (attack-decay-sustain-release)
            double envelope = compute_envelope(t, duration);
            
            // Generate waveform
            data[i] = envelope * std::sin(2.0 * M_PI * freq_mod * t);
        }
        
        return result;
    }
    
    // Generate ambient bush sounds with multiple species
    py::array_t<double> generate_ecosystem_audio(const std::vector<int>& species_list, 
                                                  double duration = 10.0) {
        size_t samples = static_cast<size_t>(duration * SAMPLE_RATE);
        std::vector<double> mixed_audio(samples, 0.0);
        
        // Generate calls for each species at random times
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<double> time_dist(0.0, duration - 2.0);
        
        for (int species_int : species_list) {
            auto species = static_cast<AustralianSpecies>(species_int);
            double start_time = time_dist(gen);
            auto call_audio = generate_bird_call(species, 2.0);
            
            // Mix into main audio
            auto call_buf = call_audio.request();
            auto* call_data = static_cast<double*>(call_buf.ptr);
            size_t call_samples = call_buf.shape[0];
            size_t start_sample = static_cast<size_t>(start_time * SAMPLE_RATE);
            
            for (size_t i = 0; i < call_samples && start_sample + i < samples; ++i) {
                mixed_audio[start_sample + i] += call_data[i] * 0.3; // Mix at reduced volume
            }
        }
        
        // Add ambient noise
        std::uniform_real_distribution<double> noise_dist(-0.01, 0.01);
        for (auto& sample : mixed_audio) {
            sample += noise_dist(gen);
        }
        
        auto result = py::array_t<double>(samples);
        auto buf = result.request();
        std::copy(mixed_audio.begin(), mixed_audio.end(), static_cast<double*>(buf.ptr));
        
        return result;
    }

private:
    double compute_envelope(double t, double duration) {
        double attack_time = 0.1;
        double release_time = 0.3;
        
        if (t < attack_time) {
            return t / attack_time; // Linear attack
        } else if (t > duration - release_time) {
            return (duration - t) / release_time; // Linear release
        } else {
            return 1.0; // Sustain
        }
    }
};

// Performance benchmarking utilities
class PerformanceBenchmark {
public:
    static py::dict compare_cpp_vs_python(size_t num_samples, size_t num_iterations) {
        // C++ processing
        AudioProcessor processor;
        std::vector<double> test_audio(num_samples);
        std::iota(test_audio.begin(), test_audio.end(), 0.0);
        
        auto start_time = std::chrono::high_resolution_clock::now();
        
        for (size_t i = 0; i < num_iterations; ++i) {
            try {
                auto features = processor.extract_features(test_audio);
            } catch (const std::exception&) {
                // Ignore errors in benchmark
            }
        }
        
        auto end_time = std::chrono::high_resolution_clock::now();
        auto cpp_duration = std::chrono::duration<double>(end_time - start_time).count();
        
        py::dict results;
        results["cpp_time"] = cpp_duration;
        results["samples_processed"] = num_samples * num_iterations;
        results["samples_per_second"] = (num_samples * num_iterations) / cpp_duration;
        
        return results;
    }
};

// Python module definition
PYBIND11_MODULE(_core, m) {
    m.doc() = "Bush Ears - High-performance wildlife audio identification";
    
    // Enums
    py::enum_<AustralianSpecies>(m, "AustralianSpecies")
        .value("Unknown", AustralianSpecies::Unknown)
        .value("Kookaburra", AustralianSpecies::Kookaburra)
        .value("Magpie", AustralianSpecies::Magpie)
        .value("Galah", AustralianSpecies::Galah)
        .value("Cockatoo", AustralianSpecies::Cockatoo)
        .value("Lorikeet", AustralianSpecies::Lorikeet)
        .value("Koala", AustralianSpecies::Koala)
        .value("Dingo", AustralianSpecies::Dingo);
    
    // Classes
    py::class_<AudioProcessor>(m, "AudioProcessor")
        .def(py::init<>())
        .def("extract_features", [](AudioProcessor& self, py::array_t<double> audio) {
            auto buf = audio.request();
            std::vector<double> audio_vec(static_cast<double*>(buf.ptr), 
                                         static_cast<double*>(buf.ptr) + buf.shape[0]);
            return self.extract_features(audio_vec);
        })
        .def("compute_spectrogram", &AudioProcessor::compute_spectrogram);
    
    py::class_<WildlifeClassifier>(m, "WildlifeClassifier")
        .def(py::init<>())
        .def("classify_audio_features", [](WildlifeClassifier& self, const std::vector<double>& features) {
            auto result = self.classify_audio_features(features);
            return static_cast<int>(result);
        })
        .def("classify_batch", &WildlifeClassifier::classify_batch);
    
    py::class_<EcosystemMonitor>(m, "EcosystemMonitor")
        .def(py::init<>())
        .def("process_audio_stream", &EcosystemMonitor::process_audio_stream)
        .def("classify_audio_batch", &EcosystemMonitor::classify_audio_batch)
        .def("get_ecosystem_report", &EcosystemMonitor::get_ecosystem_report)
        .def("reset_metrics", &EcosystemMonitor::reset_metrics);
    
    py::class_<AudioSimulator>(m, "AudioSimulator")
        .def(py::init<>())
        .def("generate_bird_call", &AudioSimulator::generate_bird_call)
        .def("generate_ecosystem_audio", &AudioSimulator::generate_ecosystem_audio);
    
    // Utility functions
    m.def("benchmark_performance", &PerformanceBenchmark::compare_cpp_vs_python,
          "Compare C++ vs Python audio processing performance");
}
