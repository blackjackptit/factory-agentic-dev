# Gold Price Monitor Skill

Monitor real-time gold prices automatically every 30 seconds.

## Activation

This skill is activated when the user runs `/gold-price` or asks to check gold prices.

## Instructions

When this skill is activated, run the gold price monitor script in the background to display live gold prices every 30 seconds.

### Usage

Run the monitor with a specified duration (default 5 minutes):

```bash
python3 .claude/skills/gold-price/monitor.py --duration 5
```

### Options

- `--duration [minutes]` - How long to run the monitor (default: 5 minutes)
- `--once` - Get a single price check instead of continuous monitoring

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

Run the appropriate command based on user request. Use `--once` for single checks, otherwise start the continuous monitor.
