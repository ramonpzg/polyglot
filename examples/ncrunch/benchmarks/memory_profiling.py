import tracemalloc
import numcrunch as nc


def run():
    tracemalloc.start()
    model = nc.AustralianMiningModel()
    model.load_pilbara_data("data/pilbara_geology.csv")
    geo = model.create_geology_model()
    engine = nc.MonteCarloEngine(seed=42)
    engine.run_geological_simulation(model=geo, num_iterations=1_000_00)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"Current: {current/1e6:.1f} MB, Peak: {peak/1e6:.1f} MB")


if __name__ == "__main__":
    run()

