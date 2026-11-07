# Contributing

Thanks for helping improve this time-series learning project.

## Local workflow

1. Create a virtual environment and install `requirements.txt`.
2. Run `python download_data.py` to retrieve the FRED CSV locally.
3. Run `python time_series.py` or open `pandas_time_series.ipynb`.

## Analysis conventions

- Keep the source series in its original units: thousands of light vehicle sales, not seasonally adjusted.
- Use month-end (`ME`) and quarter-end (`QE`) resampling aliases supported by current Pandas.
- Do not interpolate missing observations silently. Report gaps or explain any chosen treatment.
- Distinguish monthly changes, year-over-year changes, and rolling averages in labels.
- Cite the FRED series and its source agency in user-facing reports.
- Do not commit downloaded datasets, virtual environments, or generated outputs.

## Pull requests

Describe the change, how to run it, and how it affects the interpretation of the series. Update the README or methodology guide when adding an output or changing an analysis assumption.
