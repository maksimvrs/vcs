# Install
```bash
pip install -e .
```

# Usage

## Init repository
Создать репозитории с текущей папке
```bash
python3 -m vcs init
```

## Add file to indexing
Сделать файлы отслеживаемыми для следующего коммита (пути к файлам через пробел)
```bash
python3 -m vcs add REDME.md
```

## Commit changes
Зафиксировать коммит индексируемых файлов
```bash
python3 -m vcs commit -m 'Initial commit' -t 'v0.1'
```

## Go to commit
Перейти к коммиту 
```bash
python3 -m vcs reset 52d667d1365da92ee85a380950aaaf2bf0e8b12e
```

## Create new branch
Создать новую ветку. Ответвление от текущего коммита текущей ветки. 
```bash
python3 -m vcs branch develop
```

## Switch to a branch
Переключить на ветку (текщий коммит ветки)
```bash
python3 -m vcs checkout develop
```

## Merge
Объединить ветку с текущей (текущим коммитом указаной ветки) и создать в настоящей ветке коммит с объединенным состоянием. История ветки сохраняется.
```bash
python3 -m vcs merge develop
```

## Rebase
Переместить все изменения ветки в новый коммит текущей ветки. История ветки не сохраняется.
```bash
python3 -m vcs rebase develop
```

## Cherry-pick
Переместить коммит ветки в новый коммит текущей ветки. Ветка остаетс яв рабочем состоянии.
```bash
python3 -m vcs cherry-pick develop 52d667d1365da92ee85a380950aaaf2bf0e8b12e
```

## Get log
```bash
python3 -m vcs log
```
