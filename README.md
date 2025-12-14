# BlackLight License Bypass (BLBypass)

![](github.png)

A lightweight CLI tool to automate the generation and injection of [BlackLight 3](https://michelf.ca/projects/black-light/) trial extension requests. This tool allows you to bypass the trial period by programmatically generating and injecting license codes, so you can use BlackLight 3 indefinitely without purchasing a license.

## Features

- **Automated License Generation**: Generates license codes by simulating trial extension requests
- **CLI Integration**: Copy and paste name, email, and license code directly from the terminal
- **Batch Generation**: Generate multiple licenses at once
- **Beautiful Output**: Rich terminal formatting with tables and panels
- **Clipboard Integration**: Automatically copy license information to clipboard
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
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Usage

### Basic Usage (Interactive)

```bash
blbypass generate
```

Follow the prompts to enter your name and email. The license will be displayed and optionally copied to clipboard.

### Direct Mode

```bash
blbypass generate --name "John Doe" --email "john@example.com" --copy
```

### Batch Generation

```bash
blbypass batch --count 5 --output licenses.json --format json
```

### Save to File

```bash
blbypass generate --name "John Doe" --email "john@example.com" --output license.json
```

### Experimental: Full License Research

```bash
blbypass full --name "John Doe" --email "john@example.com" --pi "pi_xxx" --pics "pi_xxx_secret_xxx" --ps "session_xxx"
```

**Note**: The full license endpoint requires valid Stripe payment intents and is provided for research purposes only.

## Options

### `generate` command

- `--name, -n`: Name for the license
- `--email, -e`: Email address for the license
- `--lang, -l`: Language code (default: en)
- `--copy, -c`: Copy license code to clipboard
- `--output, -o`: Save license to file (JSON format)
- `--quiet, -q`: Minimal output

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

1. Run the CLI tool with your name and email
2. The tool makes a POST request to BlackLight's trial endpoint
3. The response HTML is parsed to extract the license code
4. License information is displayed and optionally copied to clipboard
5. Paste the information into BlackLight 3 to extend your trial

## Examples

### Generate and copy to clipboard

```bash
blbypass generate -n "Jane Doe" -e "jane@example.com" -c
```

### Generate quietly and save to file

```bash
blbypass generate -n "Jane Doe" -e "jane@example.com" -o license.json -q
```

### Generate 10 licenses

```bash
blbypass batch -c 10 -o licenses.json## Contributing
```

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Disclaimer

This tool is for educational and research purposes only. Use responsibly and in accordance with BlackLight's terms of service.
