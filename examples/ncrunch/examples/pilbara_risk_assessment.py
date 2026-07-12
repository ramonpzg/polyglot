import numcrunch as nc


def main():
    model = nc.AustralianMiningModel()
    model.load_pilbara_data("data/pilbara_geology.csv")
    geo = model.create_geology_model()

    engine = nc.MonteCarloEngine(seed=42)
    res = engine.run_geological_simulation(model=geo, num_iterations=2_000_000)
    print("Geology:", res)

    from numcrunch.mining import make_cash_flows, make_market

    flows = make_cash_flows([150, 170, 180, 200], [120, 130, 140, 150])
    market = make_market(base_price=100.0, price_vol=0.25, discount_rate=0.08)
    npv = engine.calculate_project_npv(flows=flows, market=market)
    print("NPV:", npv)


if __name__ == "__main__":
    main()

