# Analysis methodology

## Source and units

The project uses FRED series `LTOTALNSA`, Light Weight Vehicle Sales, sourced from the U.S. Bureau of Economic Analysis. Observations are monthly, in thousands of units, and not seasonally adjusted. Values are revised by the source over time.

## Resampling

The source is already monthly. Month-end resampling preserves each monthly observation and standardizes its timestamp. Quarterly totals sum the three monthly observations within each quarter. Missing bins use `min_count=1`, so an empty period stays missing rather than becoming a false zero.

## Changes and rolling mean

- Monthly change is the current value minus the prior observation.
- Year-over-year change compares the current observation with the value 12 monthly periods earlier.
- Percent changes are relative changes and can be undefined when the comparison value is zero.
- Rolling means are trailing windows that require all observations in the configured window.

## Seasonal summary and gaps

The seasonal summary groups observed values by calendar month across all years. It reports observation count, mean, median, minimum, and maximum. It does not adjust for long-term trends or inflation, so differences can reflect both seasonality and changes over time.

The missing-month report lists calendar months absent between the first and last observation. Missing values are not filled or interpolated. A quarterly sum may therefore be partial when one or more source months are missing; inspect `missing_months.csv` before interpreting it.
