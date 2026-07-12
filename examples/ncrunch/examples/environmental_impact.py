import numcrunch as nc


def main():
    model = nc.AustralianMiningModel()
    model.load_pilbara_data("data/pilbara_geology.csv")

    # Source: x,y,intensity (toy)
    src = (0.0, 0.0, 1.0)
    env = model.simulate_water_contamination(src, years=10)
    print("Environmental impact (10y):", env)


if __name__ == "__main__":
    main()

