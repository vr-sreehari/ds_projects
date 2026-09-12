# Global Seismic Trends - 30 MySQL Analytical Queries

This directory contains 30 analytical SQL queries designed for **MySQL 8.0+** to extract seismological insights from the `earthquakes` table.

---

## File Structure

| File | Description | Notes / Dependencies |
| :--- | :--- | :--- |
| `00_all_30_queries.sql` | Consolidated script with all 30 queries in one file | Full project master script |
| `01_top_10_strongest_earthquakes.sql` | Top 10 highest magnitude earthquakes | |
| `02_top_10_deepest_earthquakes.sql` | Top 10 deepest earthquakes by focal depth | |
| `03_shallow_strong_earthquakes.sql` | Shallow events (< 50 km) with magnitude > 7.5 | |
| `04_avg_depth_per_continent.sql` | Average depth and volume per continent | Requires `continent` column |
| `05_avg_mag_by_magtype.sql` | Average magnitude and count across `magType` | |
| `06_year_with_most_earthquakes.sql` | Calendar year with highest earthquake activity | |
| `07_month_with_highest_earthquake_count.sql` | Peak seasonal month across all recorded years | |
| `08_day_of_week_most_earthquakes.sql` | Weekly seismic event frequency | |
| `09_earthquakes_per_hour.sql` | Diurnal hourly distribution across 24 UTC hours | |
| `10_most_active_reporting_network.sql` | Most active contributing network code (`net`) | |
| `11_top_5_places_highest_casualties.sql` | Top 5 locations with highest human casualties | Requires external `casualties` column |
| `12_total_economic_loss_by_continent.sql` | Total economic loss aggregated by continent | Requires external `economic_loss_usd` and `continent` |
| `13_avg_economic_loss_by_alert.sql` | Average monetary loss by PAGER alert level | Requires `economic_loss_usd` and `alert` |
| `14_reviewed_vs_automatic_events.sql` | Human-reviewed vs automated station detection count | |
| `15_earthquake_count_by_event_type.sql` | Event counts by phenomenon type (`earthquake`, `blast`, etc.) | Backticks on `` `type` `` |
| `16_earthquakes_by_associated_data_type.sql` | Recursive CTE parsing comma-separated `types` products | MySQL 8.0 `WITH RECURSIVE` |
| `17_avg_rms_and_gap_per_continent.sql` | Average station gap and travel time RMS by continent | Requires `continent` column |
| `18_events_with_high_station_coverage.sql` | High-station coverage events (`nst > threshold`) | Uses user session variable `@nst_threshold` |
| `19_tsunami_earthquakes_by_year.sql` | Annual count of tsunami-flagged earthquakes | |
| `20_earthquake_count_by_alert_level.sql` | Event counts across PAGER color levels | Requires `alert` column from API |
| `21_top_5_countries_highest_avg_mag_5yrs.sql` | Top 5 countries with highest avg magnitude (past 5 yrs) | Enforces `HAVING COUNT(*) >= 10` |
| `22_countries_shallow_and_deep_same_month.sql` | Countries having both shallow & deep events in same month | Subduction zone activity indicator |
| `23_year_over_year_growth_rate.sql` | Annual percentage growth rate in global seismic volume | Uses `LAG()` window function |
| `24_top_3_active_regions_freq_and_mag.sql` | Composite seismic activity ranking (50% freq + 50% mag) | Min-max normalization |
| `25_avg_depth_equatorial_region.sql` | Average depth for countries in equatorial band (±5° lat) | |
| `26_countries_highest_shallow_deep_ratio.sql` | Countries with highest shallow-to-deep focal depth ratio | |
| `27_magnitude_diff_tsunami_vs_non_tsunami.sql` | Magnitude difference between tsunami and non-tsunami events | |
| `28_lowest_data_reliability_gap_rms.sql` | Unreliability score combining normalized `gap` and `rms` | Higher score = poorer quality |
| `29_consecutive_earthquakes_50km_1hr.sql` | Successive events within 50 km and 1 hour | `LAG()` + Haversine formula |
| `30_regions_most_deep_focus_earthquakes.sql` | Countries with the most deep-focus (> 300 km) events | |

---

## Dataset & Column Prerequisites

1. **Native USGS Fields**:
   - `id`, `time`, `place`, `mag`, `depth_km`, `magType`, `net`, `nst`, `gap`, `rms`, `tsunami`, `latitude`, `longitude`, `status`, `types`, `` `type` ``
2. **Derived Fields** (present in cleaned schema):
   - `country`, `year`, `month`, `day`, `day_of_week`, `depth_category`, `strong_flag`, `destructive_flag`
3. **External / Supplemental Fields**:
   - `continent` (Used in queries 04, 12, 17): Needs to be derived/mapped from country.
   - `alert` (Used in queries 13, 20): Available from USGS API if preserved during ingestion.
   - `casualties` (Used in query 11) & `economic_loss_usd` (Used in queries 12, 13): Require external disaster-impact datasets (e.g. EM-DAT, NOAA NCEI, or USGS PAGER economic tables).
