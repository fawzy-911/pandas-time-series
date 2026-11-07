"""Download monthly light vehicle sales from FRED as a CSV."""

from pathlib import Path
from urllib.request import Request, urlopen


SERIES_ID = "LTOTALNSA"
DATA_URL = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES_ID}"
DATA_DIR = Path(__file__).parent / "data"
CSV_FILE = DATA_DIR / "light_vehicle_sales.csv"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    request = Request(DATA_URL, headers={"User-Agent": "pandas-time-series-project/1.0"})
    print(f"Downloading FRED series {SERIES_ID}...")
    with urlopen(request, timeout=30) as response:
        content = response.read()
    if b"observation_date" not in content or SERIES_ID.encode() not in content.splitlines()[0]:
        raise RuntimeError("FRED returned an unexpected CSV format.")
    temp_file = CSV_FILE.with_suffix(".csv.tmp")
    temp_file.write_bytes(content)
    temp_file.replace(CSV_FILE)
    print(f"Saved {len(content):,} bytes to {CSV_FILE}")


if __name__ == "__main__":
    main()
