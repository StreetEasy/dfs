
`dfschema` is also available as a command line interface, via `dfshema` alias.


### Usage
```dfschema [OPTIONS] COMMAND [ARGS]...
```
### Commands
#### 1. Generate
Generate Schema from given dataset.
Usage: `dfschema generate [OPTIONS] FILE`
Will Print Schema to stdout. To write to the file, use piping.

##### Example
```bash
dfschema generate data.csv > schema.dfs.json
```

##### Arguments
- `FILE`  data file to generate schema from  [required]
##### Options
  - `--format [yaml|json]`, output format, either `json` or `yaml`  [default:
                        json]
  - `--help`, Show this message and exit.

#### 2. Validate
Validate data from file against given schema

Usage: `dfschema validate [OPTIONS] FILE SCHEMA`

##### Example
```
dfschema validate data.csv schema.dfs.json --read-kwargs-json '{"delimiter":"|"}' --summary
```
##### Arguments
  `FILE`    Data file to validate  [required]
  `SCHEMA`  Schema file to validate against  [required]

##### Options
  - `--read-kwargs-json TEXT`, Extra read options to be passed to pandas method, as a json object.
  - `--summary / --no-summary`,  Print summary of validation results. If `no-summary`, will stop at first violation (faster)  [default: summary]
  - `--help`, Show this message and exit.

#### 3. Misc:
  - `--install-completion [bash|zsh|fish|powershell|pwsh]`, Install completion for the specified shell.
  - `--show-completion [bash|zsh|fish|powershell|pwsh]`, Show completion for the specified shell, to copy it or customize the installation.
  - `--help`, Show this message and exit.
