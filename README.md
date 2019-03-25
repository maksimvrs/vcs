# Install
```bash
pip install -e .
```

# Usage

## Init repository
```bash
python3 -m vcs init
```

## Add file to indexing
```bash
python3 -m vcs add REDME.md
```

## Commit changes
```bash
python3 -m vcs commit -m 'Initial commit' -t 'v0.1'
```

## Go to commit
```bash
python3 -m vcs reset 52d667d1365da92ee85a380950aaaf2bf0e8b12e
```

## Create new branch
```bash
python3 -m vcs branch develop
```

## Switch to a branch
```bash
python3 -m vcs checkout develop
```

## Merge
```bash
python3 -m vcs merge develop
```

## Get log
```bash
python3 -m vcs log
```
