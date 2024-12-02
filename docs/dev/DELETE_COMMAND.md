# 🗑️ Data Deletion Command Documentation

## Overview

The `delete_data` command provides a flexible way to delete records from the Environmental Data Dashboard database based on various conditions and filters.

## Basic Usage

```bash
python manage.py delete_data --model [model_type] [options]
```

## Required Arguments

- `--model`: Specify which type of data to delete
  - `metric`: Delete only metric records
  - `aqi`: Delete only AQI records
  - `all`: Delete both metric and AQI records

## Optional Arguments

### Location Filters

- `--city [city_name]`: Filter by city name (case-insensitive)
- `--country [country_name]`: Filter by country name (case-insensitive)

### Time Filters

- `--future`: Delete all records with future dates
- `--before [YYYY-MM-DD]`: Delete records before specified date
- `--after [YYYY-MM-DD]`: Delete records after specified date

### Other Options

- `--force`: Skip confirmation prompt and delete immediately

## Examples

1. Delete all future records:

```bash
python manage.py delete_data --model all --future
```

2. Delete metrics for a specific city:

```bash
python manage.py delete_data --model metric --city "Beijing"
```

3. Delete AQI records before a certain date:

```bash
python manage.py delete_data --model aqi --before 2024-01-01
```

4. Delete all records for a country within a date range:

```bash
python manage.py delete_data --model all --country "Japan" --after 2023-12-01 --before 2024-01-01
```

5. Force delete without confirmation:

```bash
python manage.py delete_data --model metric --city "London" --force
```

6. Delete all future records for a specific city:

```bash
python manage.py delete_data --model all --city "Tokyo" --future --force
```

## Safety Features

1. Confirmation Prompt
   - By default, the command shows how many records will be deleted and asks for confirmation
   - Use `--force` to skip the confirmation prompt

2. Preview Count
   - Before deletion, displays the number of records that will be affected
   - Gives you a chance to abort if the count seems incorrect

## Common Use Cases

### Cleaning Up Test Data

```bash
# Delete all test city records
python manage.py delete_data --model all --city "Test"
```

### Removing Outdated Data

```bash
# Delete records older than a specific date
python manage.py delete_data --model all --before 2023-01-01
```

### Fixing Wrong Data

```bash
# Delete specific timeframe for a city
python manage.py delete_data --model metric --city "Paris" --after 2024-01-01 --before 2024-02-01
```

### Database Maintenance

```bash
# Delete all future records (data integrity)
python manage.py delete_data --model all --future --force
```

## Error Handling

1. Invalid Date Format
   - Dates must be in YYYY-MM-DD format
   - Command will show error message for invalid dates

2. Non-existent Data
   - If no records match the criteria, shows count of 0
   - No deletion performed if no matching records

## Best Practices

1. Always run without `--force` first to preview the deletion
2. Use specific filters to avoid unintended deletions
3. Consider backing up data before large deletions
4. Use date ranges when possible to be more precise
5. Double-check city and country names

## Notes

- All deletions are permanent and cannot be undone
- Deletions are performed in a single transaction
- Time-based filters use the database timezone
- City and country filters are case-insensitive partial matches
- Multiple filters can be combined for precise control
