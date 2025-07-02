# Get information about software mapping

`ardl` comes with a tool to get all supoprted package format for both CVP and EOS softwares. It helps to know which format to use for a specific file extension.

## Get information about available versions

```bash
$ ardl info mapping --help
Usage: ardl info mapping [OPTIONS]

  List available flavors of Arista packages (eos or CVP) packages.

Options:
  --package [eos|cvp]
  --format [json|text|fancy]  Output format
  --details                   Show details for each flavor
  --help                      Show this message and exit.
```

## Usage example

With this CLI, you can specify either a branch or a release type when applicable to filter information:


```bash
# Get list of supported packages for EOS.
$ ardl info mapping --package eos
Log Level is: error

╭─────────────────────────── Flavors ───────────────╮
│                                                   │
│    * Flavor: 64                                   │
│    * Flavor: INT                                  │
│    * Flavor: 2GB-INT                              │
│    * Flavor: cEOS                                 │
│    * Flavor: cEOS64                               │
│    * Flavor: cEOSarm                              │
│    * Flavor: vEOS                                 │
│    * Flavor: vEOS-lab                             │
│    * Flavor: EOS-2GB                              │
│    * Flavor: RN                                   │
│    * Flavor: SOURCE                               │
│    * Flavor: default                              │
│                                                   │
╰───────────────────────────────────────────────────╯

# Get list of supported packages for EOS with filename information
$ ardl info mapping --package eos --details
Log Level is: error

╭─────────────────────────────────────────────────── Flavors ─────────╮
│                                                                     │
│    * Flavor: 64                                                     │
│      - Information: extension='.swi' prepend='EOS64'                │
│    * Flavor: INT                                                    │
│      - Information: extension='-INT.swi' prepend='EOS'              │
│    * Flavor: 2GB-INT                                                │
│      - Information: extension='-INT.swi' prepend='EOS-2GB'          │
│    * Flavor: cEOS                                                   │
│      - Information: extension='.tar.xz' prepend='cEOS-lab'          │
│    * Flavor: cEOS64                                                 │
│      - Information: extension='.tar.xz' prepend='cEOS64-lab'        │
│    * Flavor: cEOSarm                                                │
│      - Information: extension='.tar.xz' prepend='cEOSarm-lab'       │
│    * Flavor: vEOS                                                   │
│      - Information: extension='.vmdk' prepend='vEOS'                │
│    * Flavor: vEOS-lab                                               │
│      - Information: extension='.vmdk' prepend='vEOS-lab'            │
│    * Flavor: EOS-2GB                                                │
│      - Information: extension='.swi' prepend='EOS-2GB'              │
│    * Flavor: RN                                                     │
│      - Information: extension='-' prepend='RN'                      │
│    * Flavor: SOURCE                                                 │
│      - Information: extension='-source.tar' prepend='EOS'           │
│    * Flavor: default                                                │
│      - Information: extension='.swi' prepend='EOS'                  │
│                                                                     │
╰─────────────────────────────────────────────────────────────────────╯

```