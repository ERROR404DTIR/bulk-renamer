# bulk-renamer

<p align="center"><img src="assets/readme-banner.svg" alt="Animated Bulk Renamer banner" width="100%"></p>

Safe, dry-run-first CLI for bulk renaming files. Zero dependencies, pure Python 3.8+.

## Features

- Dry run by default — nothing changes until you pass `--apply`
- Regex find/replace on names
- Sequential numbering with padding
- Case conversion (lower, upper, title, snake, kebab)
- Prefix / suffix, extension change
- Collision detection and undo log

## Install

```bash
pip install .
```

or just run `python bulk_renamer.py`.

## Usage

```bash
# preview: replace spaces with underscores
bulk-renamer ./photos --replace " " "_"

# regex + apply
bulk-renamer ./photos --regex "IMG_(\d+)" "holiday_\1" --apply

# numbering
bulk-renamer ./photos --number --start 1 --pad 3 --prefix "trip_" --apply

# kebab case, only .txt files, recursive
bulk-renamer ./docs --case kebab --glob "*.txt" -r --apply

# undo the last run
bulk-renamer --undo
```

## Options

| Option | Description |
|---|---|
| `--replace OLD NEW` | Plain text replace |
| `--regex PATTERN REPL` | Regex replace |
| `--case MODE` | `lower`, `upper`, `title`, `snake`, `kebab` |
| `--prefix / --suffix` | Add text around the stem |
| `--ext EXT` | Change extension |
| `--number` | Rename to sequential numbers (`--start`, `--pad`) |
| `--glob PATTERN` | Only match files (default `*`) |
| `-r` | Recurse into subfolders |
| `--apply` | Actually rename |
| `--undo` | Revert last applied run |

## License

MIT