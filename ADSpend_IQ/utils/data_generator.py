import numpy as np
import pandas as pd

from config.settings import (
    PLATFORMS,
    CAMPAIGNS,
    CITIES,
    DEVICES,
    GENDERS,
    RANDOM_SEED
)


def generate_ad_data(
    n_records=10000,
    seed=RANDOM_SEED
):
    """
    Generate reproducible synthetic advertising records.

    Each row represents one simulated campaign/audience
    delivery segment, not an individual customer.

    Data is suitable for analytics demonstrations.
    It does not represent actual advertising results.
    """

    n_records = int(n_records)

    if n_records < 1:
        raise ValueError("n_records must be positive")

    rng = np.random.default_rng(seed)

    platform = rng.choice(
        PLATFORMS,
        size=n_records,
        p=[0.23, 0.24, 0.25, 0.15, 0.13]
    )

    campaign = rng.choice(
        CAMPAIGNS,
        size=n_records
    )

    city = rng.choice(
        CITIES,
        size=n_records
    )

    device = rng.choice(
        DEVICES,
        size=n_records,
        p=[0.52, 0.32, 0.13, 0.03]
    )

    gender = rng.choice(
        GENDERS,
        size=n_records,
        p=[0.48, 0.49, 0.03]
    )

    age = rng.integers(
        18, 61, size=n_records
    )

    start_date = pd.Timestamp("2025-01-01")

    date_offsets = rng.integers(
        0, 365, size=n_records
    )

    dates = start_date + pd.to_timedelta(
        date_offsets, unit="D"
    )

    # Simulated performance assumptions per platform
    ctr_base = {
        "Facebook": 0.026,
        "Instagram": 0.033,
        "Google": 0.050,
        "TikTok": 0.037,
        "YouTube": 0.020
    }

    conversion_base = {
        "Facebook": 0.035,
        "Instagram": 0.039,
        "Google": 0.065,
        "TikTok": 0.026,
        "YouTube": 0.029
    }

    cpc_base = {
        "Facebook": 22.0,
        "Instagram": 27.0,
        "Google": 34.0,
        "TikTok": 15.0,
        "YouTube": 20.0
    }

    impressions = rng.integers(
        500, 50001, size=n_records
    )

    ctr = np.array([
        ctr_base[p] for p in platform
    ])

    ctr *= rng.lognormal(
        mean=0, sigma=0.23, size=n_records
    )

    ctr = np.clip(ctr, 0.002, 0.25)

    clicks = rng.binomial(
        impressions, ctr
    )

    conversion_rate = np.array([
        conversion_base[p] for p in platform
    ])

    conversion_rate *= rng.lognormal(
        mean=0, sigma=0.25, size=n_records
    )

    conversion_rate = np.clip(
        conversion_rate, 0.001, 0.30
    )

    conversions = rng.binomial(
        clicks, conversion_rate
    )

    cpc = np.array([
        cpc_base[p] for p in platform
    ])

    cpc *= rng.lognormal(
        mean=0, sigma=0.18, size=n_records
    )

    # Spend includes a small impression-based charge
    spend = (
        clicks * cpc
        + impressions * rng.uniform(
            0.001, 0.006, size=n_records
        )
    )

    # Average simulated order value varies per campaign
    order_value = rng.lognormal(
        mean=np.log(2200),
        sigma=0.40,
        size=n_records
    )

    revenue = conversions * order_value

    df = pd.DataFrame({
        "date": dates,
        "campaign": campaign,
        "platform": platform,
        "impressions": impressions,
        "clicks": clicks,
        "spend": np.round(spend, 2),
        "conversions": conversions,
        "revenue": np.round(revenue, 2),
        "age": age,
        "gender": gender,
        "city": city,
        "device": device
    })

    return df


if __name__ == "__main__":
    data = generate_ad_data(10000)

    print("Generated records:", len(data))
    print(data.head())

    data.to_csv(
        "data/raw/sample_ads.csv",
        index=False
    )

    print("Sample dataset saved successfully.")
