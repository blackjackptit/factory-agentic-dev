# Gold Price Monitor Skill

Monitor real-time gold prices automatically every 30 seconds with automatic data logging and analysis.

## Activation

This skill is activated when the user runs `/gold-price` or asks to check gold prices.

## Features

- Real-time gold price monitoring with 30-second updates
- Automatic price data logging to JSON files (organized by date)
- Historical price analysis with statistics and trends
- Price change indicators and percentage calculations

## Instructions

When this skill is activated, run the gold price monitor script to display live gold prices. All prices are automatically saved to the `output/` folder for later analysis.

### Usage

Run the monitor with a specified duration (default 5 minutes):

```bash
python3 .claude/skills/gold-price/monitor.py --duration 5
```

### Options

- `--duration [minutes]` - How long to run the monitor (default: 5 minutes)
- `--once` - Get a single price check instead of continuous monitoring
- `--analyze` - Analyze all saved price data and display statistics

### Examples

1. **Start monitoring for 5 minutes (default):**
   ```bash
   python3 .claude/skills/gold-price/monitor.py
   ```

2. **Monitor for 10 minutes:**
   ```bash
   python3 .claude/skills/gold-price/monitor.py --duration 10
   ```

3. **Single price check:**
   ```bash
   python3 .claude/skills/gold-price/monitor.py --once
   ```

4. **Analyze saved price data:**
   ```bash
   python3 .claude/skills/gold-price/monitor.py --analyze
   ```

### Data Storage

All fetched prices are automatically saved to:
```
.claude/skills/gold-price/output/gold_prices_YYYY-MM-DD.json
```

Each file contains all price data for that specific day, making it easy to track historical trends.

### Analysis Features

The `--analyze` option provides:
- Total data points and date range
- Price statistics (current, average, highest, lowest, range)
- Overall price movement with percentage change
- Recent trend analysis (last 10 readings)
- Data source breakdown

Run the appropriate command based on user request. Use `--once` for single checks, `--analyze` to view historical data, or start the continuous monitor with `--duration`.
