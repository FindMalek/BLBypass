# BlackLight License Bypass (BLBypass)

![](github.png)

A lightweight CLI tool to automate the generation and injection of [BlackLight 3](https://michelf.ca/projects/black-light/) trial extension requests. This tool allows you to bypass the trial period by programmatically generating and injecting license codes, so you can use BlackLight 3 indefinitely without purchasing a license.

## Features

- **Automated License Generation**: Generates license codes by simulating trial extension requests
- **Auto Mode**: Automatically generates fake names/emails and copies information step-by-step
- **Proxy Support**: Built-in proxy rotation to avoid IP bans and rate limits
- **Smart Rate Limit Handling**: Automatic retry with exponential backoff when rate limited
- **Browser Fingerprinting**: Realistic browser headers to avoid detection
- **CLI Integration**: Copy and paste name, email, and license code directly from the terminal
- **Batch Generation**: Generate multiple licenses at once
- **Beautiful Output**: Rich terminal formatting with tables and panels
- **Clipboard Integration**: Automatically copy license information to clipboard
- **Debug Mode**: Detailed logging for troubleshooting
- **Open Source**: Free to use, modify, and contribute

## Installation

### From Source

```bash
git clone https://github.com/findmalek/BLBypass.git
cd BLBypass
pip install -e .
```

### Development Setup

```bash
git clone https://github.com/findmalek/BLBypass.git
cd BLBypass

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Usage

### Basic Usage (Interactive)

```bash
blbypass generate
```

Follow the prompts to enter your name and email. The license will be displayed and optionally copied to clipboard.

### Auto Mode (Recommended)

The easiest way to use BLBypass - automatically generates fake data and copies each field step-by-step:

```bash
blbypass generate --auto
```

This will:
1. Generate a random fake name and email
2. Request the license
3. Copy name → email → license code to clipboard one by one
4. Display clear instructions for each step

### Direct Mode

```bash
blbypass generate --name "John Doe" --email "john@example.com" --copy
```

### Using Proxies (Avoid IP Bans)

**Auto-fetch proxies** (recommended):
```bash
blbypass generate --auto --auto-proxy
```

**Manual proxy**:
```bash
blbypass generate --name "John Doe" --email "john@example.com" --proxy "http://proxy.example.com:8080"
```

**Choose proxy source**:
```bash
blbypass generate --auto --auto-proxy --proxy-source proxyscrape  # Default
blbypass generate --auto --auto-proxy --proxy-source pubproxy     # Alternative
```

### Rate Limit Protection

If you're getting rate limited, increase delays and use proxies:

```bash
# Safe mode: longer delays + auto-proxy
blbypass generate --auto --auto-proxy --delay 10.0

# More retries with longer delays
blbypass generate --name "John Doe" --email "john@example.com" --retries 5 --retry-delay 15.0
```

### Batch Generation

```bash
blbypass batch --count 5 --output licenses.json --format json
```

### Save to File

```bash
blbypass generate --name "John Doe" --email "john@example.com" --output license.json
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
blbypass --debug generate --name "John Doe" --email "john@example.com"
```

### Experimental: Full License Research

```bash
blbypass full --name "John Doe" --email "john@example.com" --pi "pi_xxx" --pics "pi_xxx_secret_xxx" --ps "session_xxx"
```

**Note**: The full license endpoint requires valid Stripe payment intents and is provided for research purposes only.

## Options

### Global Options

- `--debug`: Enable debug logging for troubleshooting
- `--version`: Show version information

### `generate` command

**Basic Options:**
- `--name, -n`: Name for the license
- `--email, -e`: Email address for the license
- `--lang, -l`: Language code (default: en)
- `--copy, -c`: Copy license code to clipboard
- `--output, -o`: Save license to file (JSON format)
- `--quiet, -q`: Minimal output

**Auto Mode:**
- `--auto`: Auto-generate fake name/email and copy step-by-step

**Rate Limit Protection:**
- `--delay, -d`: Delay between requests in seconds (default: 5.0, recommended: 10+ for safety)
- `--retries, -r`: Number of retry attempts (default: 3)
- `--retry-delay`: Delay between retries in seconds (default: 5.0)

**Proxy Options:**
- `--proxy`: Manual proxy URL (e.g., `http://proxy.example.com:8080`)
- `--auto-proxy`: Automatically fetch and use proxies from public sources
- `--proxy-source`: Proxy source for auto-proxy (`proxyscrape` or `pubproxy`, default: `proxyscrape`)

### `batch` command

- `--count, -c`: Number of licenses to generate (default: 1)
- `--lang, -l`: Language code (default: en)
- `--output, -o`: Output file path (required)
- `--format, -f`: Output format: json or csv (default: json)

### `full` command

- `--name, -n`: Name for the license (required)
- `--email, -e`: Email address (required)
- `--pi`: Payment Intent ID (experimental)
- `--pics`: Payment Intent Client Secret (experimental)
- `--ps`: Payment Session ID (experimental)

## How It Works

1. Run the CLI tool with your name and email (or use `--auto` for automatic generation)
2. The tool makes a POST request to BlackLight's trial endpoint with realistic browser headers
3. If rate limited, the tool automatically retries with exponential backoff
4. The response HTML is parsed to extract the license code
5. License information is displayed and optionally copied to clipboard
6. Paste the information into BlackLight 3 to extend your trial

## Examples

### Quick Start (Easiest)

```bash
# Auto mode with proxy protection
blbypass generate --auto --auto-proxy
```

### Generate and Copy to Clipboard

```bash
blbypass generate -n "Jane Doe" -e "jane@example.com" -c
```

### Generate Quietly and Save to File

```bash
blbypass generate -n "Jane Doe" -e "jane@example.com" -o license.json -q
```

### Safe Mode (Avoid Rate Limits)

```bash
# Long delays + auto-proxy + more retries
blbypass generate --auto --auto-proxy --delay 15.0 --retries 5 --retry-delay 20.0
```

### Generate 10 Licenses

```bash
blbypass batch -c 10 -o licenses.json
```

### Debug a Failed Request

```bash
blbypass --debug generate --name "Test" --email "test@example.com" --auto-proxy
```

## Rate Limiting & IP Bans

If you encounter rate limiting or IP bans:

1. **Use Proxies**: Always use `--auto-proxy` to avoid IP bans
   ```bash
   blbypass generate --auto --auto-proxy
   ```

2. **Increase Delays**: Use longer delays between requests
   ```bash
   blbypass generate --auto --delay 15.0
   ```

3. **Wait**: If your IP is banned, wait 5-10 minutes before retrying

4. **Use Different Network**: Try from a different network (mobile hotspot, VPN, etc.)

The tool automatically:
- Detects rate limits and retries with exponential backoff
- Rotates browser fingerprints to avoid detection
- Falls back to direct connection if proxies fail
- Provides clear error messages and suggestions

## Proxy Sources

### ProxyScrape (Default)
- Free, no API key required
- Up to 2000 proxies per request
- Good for bulk operations

### PubProxy
- Free tier: 50 requests/day
- Premium: $12/month for unlimited
- Returns random proxies per request

## Project Structure

```
blbypass/
├── app/
│   ├── cli.py              # Main CLI entry point
│   ├── core/               # Core business logic
│   │   ├── api.py          # API client
│   │   └── parser.py       # HTML parsing
│   ├── commands/           # CLI commands
│   │   ├── generate.py     # Generate command
│   │   ├── batch.py        # Batch command
│   │   └── full.py         # Full license command
│   └── utils/              # Utilities
│       ├── clipboard.py    # Clipboard operations
│       ├── display.py      # Display formatting
│       ├── file_ops.py     # File operations
│       ├── fake_data.py    # Fake data generation
│       └── proxy_manager.py # Proxy management
├── README.md
├── requirements.txt
└── pyproject.toml
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT

## Disclaimer

This tool is for educational and research purposes only. Use responsibly and in accordance with BlackLight's terms of service. The tool includes rate limiting protection and proxy support to minimize impact on the service, but users should still use it responsibly.