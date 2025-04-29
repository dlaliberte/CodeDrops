# CodeDrops

CodeDrops is a methodology and toolset for creating self-contained code units that include requirements, design, documentation, implementation, and testing in a single file.

## What is a CodeDrop?

A CodeDrop is a single file that contains everything needed to understand, use, and verify a code component:

- **Requirements**: What the code should do
- **Design**: How the code is structured
- **Documentation**: How to use the code
- **Implementation**: The actual code
- **Testing**: Verification that the code works

## Benefits

- **Self-contained**: Everything in one place
- **Documentation proximity**: Requirements and design right next to the code
- **Easy to share**: A single file is simpler to share than a multi-file project
- **Immediate testability**: Tests are included and can be run directly

## Getting Started

### Installation

```bash
pip install -r requirements.txt
pip install codedrops
```

### Basic Usage

```bash
# Extract sections from a CodeDrop
python -m codedrops.extractor my_code_drop.md

# Run tests from a CodeDrop
python -m codedrops.runner my_code_drop.md
```

## Examples

See the [examples](examples/) directory for sample CodeDrops.

## Documentation

Full documentation is available in the [docs](docs/) directory.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
