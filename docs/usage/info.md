# Get information about softwares versions

`ardl` comes with a tool to get version information from Arista website. It is valid for both __CloudVision__ and __EOS__ packages.

## Get information about available versions

```bash
ardl info versions --help
Usage: ardl info versions [OPTIONS]

  List available versions of Arista packages (eos or CVP) packages

Options:
  --format [json|text|fancy]  Output format
  --package [eos|cvp]
  -b, --branch TEXT
  --release-type TEXT
  --help                      Show this message and exit.
```

## Usage example

With this CLI, you can specify either a branch or a release type when applicable to filter information:

### Fancy format (default)

```bash
# Get F version in branch 4.29 using default fancy mode
ardl info versions --branch 4.29 --release-type F

╭──────────────────────────── Available versions ──────────────────────────────╮
│                                                                              │
│   - version: 4.29.2F                                                         │
│   - version: 4.29.1F                                                         │
│   - version: 4.29.0.2F                                                       │
│   - version: 4.29.2F                                                         │
│   - version: 4.29.1F                                                         │
│   - version: 4.29.0.2F                                                       │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Text Format

```bash
# Get M version in branch 4.29 using text output
❯ ardl info versions --branch 4.29 --release-type M --format text
Listing versions
  - version: 4.29.10M
  - version: 4.29.9.1M
  - version: 4.29.9M
  - version: 4.29.8M
  - version: 4.29.7.1M
  ...
```

### JSON format

You can also specify JSON as output format:

```bash
ardl info versions --branch 4.29 --release-type F --format json
[
  {
    "version": "4.29.2F",
    "branch": "4.29"
  },
  {
    "version": "4.29.1F",
    "branch": "4.29"
  },
  {
    "version": "4.29.0.2F",
    "branch": "4.29"
  },
  {
    "version": "4.29.2F",
    "branch": "4.29"
  },
  {
    "version": "4.29.1F",
    "branch": "4.29"
  },
  {
    "version": "4.29.0.2F",
    "branch": "4.29"
  }
]
```
