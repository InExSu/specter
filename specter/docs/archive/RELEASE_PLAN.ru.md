> **⚠ Архив — устаревшее содержимое.** Этот документ написан до v0.3.0 и после этой версии не поддерживался. Текущий статус релизов — в [CHANGELOG.md](../../CHANGELOG.ru.md). Оставлен только для исторической справки.

---

# Specter: план открытого релиза

## 1. Чек-лист перед релизом

### Готовность кода

- [x] MVP завершён (M1–M5): parse, resolve, check, coverage, sync
- [x] 41 тест, 33 AC, 100% покрытие спецификаций
- [x] Все проверки проходят: typecheck, lint, format, test, build
- [x] Specter валидирует собственные спецификации (доказательство догфудинга)
- [x] Цель Go 1.22+, go vet, go test
- [ ] Аудит безопасности: `go vet ./...` и `govulncheck ./...` проходят с 0 уязвимостей
- [x] Файл лицензии (MIT) в корне репозитория
- [x] CONTRIBUTING.md с правилами участия
- [ ] CODE_OF_CONDUCT.md
- [x] Шаблоны issue (отчёт об ошибке, запрос функции)
- [x] Шаблон PR

### Готовность документации

- [x] README.md с быстрым стартом, примерами и обзором CLI
- [x] docs/GETTING_STARTED.md
- [x] docs/SPEC_SCHEMA_REFERENCE.md
- [x] docs/CLI_REFERENCE.md
- [x] docs/FAQ.md
- [x] docs/MVP_VALUE_PROPOSITION.md
- [x] CHANGELOG.md
- [ ] docs/CONTRIBUTING_SPECS.md (как писать спецификации для вкладов)

### Настройка репозитория

- [ ] Описание и темы репозитория GitHub (`sdd`, `spec-driven-development`, `yaml`, `validation`, `cli`, `golang`)
- [ ] Workflow GitHub Actions CI проверен на GitHub (не только локально)
- [ ] Защита ветки `main` (требовать прохождение CI, требовать ревью)
- [x] Файл `.github/CODEOWNERS`
- [x] Конфигурация goreleaser для сборок бинарников под разные платформы

---

## 2. Стратегия версионирования

### Семантическое версионирование (SemVer)

Specter следует строгому semver:

- **MAJOR** (1.0.0 -> 2.0.0): ломающие изменения схемы спецификации, интерфейса CLI или основного API
- **MINOR** (1.0.0 -> 1.1.0): новые функции, новые правила проверки, новые команды CLI
- **PATCH** (1.0.0 -> 1.0.1): исправления ошибок, обновления документации, улучшения производительности

### Вехи версий

| Версия | Что означает |
|---------|-------------------|
| `0.1.0` | Текущий MVP (M1–M5). Предрелиз. Схема может меняться. |
| `0.2.0` | M6 (обратный компилятор). Кандидат на стабильную схему. |
| `0.3.0` | Проверки с помощью ИИ (семантические конфликты, обнаружение пробелов). |
| `1.0.0` | Стабильный релиз. Схема заморожена. Публичный API гарантирован. |
| `1.x.x` | Функции после 1.0 без ломающих изменений. |

### Что считается ломающим изменением

**Изменения схемы (касаются всех пользователей):**
- Удаление обязательного поля из `spec-schema.json`
- Изменение типов полей или паттернов валидации
- Изменение смысла существующих полей
- Удаление значения перечисления из `status`, `tier` и т.п.

**Изменения CLI (касаются интеграций CI):**
- Удаление команды или опции
- Изменение семантики кодов выхода
- Изменение формата вывода режима `--json`

**НЕ ломающие:**
- Добавление новых необязательных полей в схему
- Добавление новых правил проверки (новых предупреждений/ошибок)
- Добавление новых команд CLI
- Добавление новых форматов вывода

---

## 3. Автоверсионирование через Conventional Commits

### Соглашение о коммитах

Все коммиты следуют [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Типы:**

| Тип | Повышение версии | Пример |
|------|-------------|---------|
| `feat` | MINOR | `feat(check): add duplicate constraint ID detection` |
| `fix` | PATCH | `fix(parse): handle YAML tabs correctly` |
| `feat!` или `BREAKING CHANGE:` | MAJOR | `feat!(schema): remove deprecated trust_level field` |
| `docs` | нет | `docs: update CLI reference for resolve --dot` |
| `chore` | нет | `chore: update dependencies` |
| `test` | нет | `test(coverage): add edge case for empty test files` |
| `refactor` | нет | `refactor(resolver): simplify cycle detection` |
| `ci` | нет | `ci: add Go 1.22 to test matrix` |
| `perf` | PATCH | `perf(parse): cache compiled JSON Schema validator` |

### Области

| Область | Что покрывает |
|-------|---------------|
| `schema` | Изменения `spec-schema.json` или типов схемы |
| `parse` | spec-parse (M1) |
| `resolve` | spec-resolve (M2) |
| `check` | spec-check (M3) |
| `coverage` | spec-coverage (M4) |
| `sync` | spec-sync (M5) |
| `reverse` | Обратный компилятор (M6) |
| `cli` | Команды CLI и форматирование вывода |
| `docs` | Документация |
| `deps` | Обновления зависимостей |

### Инструментарий: release-please (отложен)

> **Примечание:** для альфа-релизов Specter использует ручную разметку через goreleaser. release-please будет принят после альфы, когда темп релизов оправдает автоматизацию.

[release-please](https://github.com/googleapis/release-please) (автоматизация релизов от Google) планируется для будущего автоверсионирования:

1. Разбирает сообщения conventional commit с прошлого релиза
2. Определяет повышение версии (major/minor/patch)
3. Генерирует записи CHANGELOG.md
4. Создаёт релизный PR с повышением версии
5. При мерже: создаёт GitHub Release + git tag
6. Запускает goreleaser для сборки и публикации бинарников

**Почему release-please, а не альтернативы:**
- `semantic-release`: более догматичен, сложнее настраивать для монорепозитория
- `changesets`: требует ручных файлов changeset на каждый PR
- `release-please`: полностью автоматизирован по сообщениям коммитов, поддерживает монорепозиторий, поддерживается Google

### GitHub Actions: workflow релиза

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  release-please:
    runs-on: ubuntu-latest
    outputs:
      release_created: ${{ steps.release.outputs.release_created }}
      tag_name: ${{ steps.release.outputs.tag_name }}
    steps:
      - uses: googleapis/release-please-action@v4
        id: release
        with:
          release-type: go
          path: specter
          package-name: specter

  goreleaser:
    needs: release-please
    if: ${{ needs.release-please.outputs.release_created }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'

      - uses: goreleaser/goreleaser-action@v6
        with:
          distribution: goreleaser
          version: latest
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Конфигурация: release-please-config.json

```json
{
  "$schema": "https://raw.githubusercontent.com/googleapis/release-please/main/schemas/config.json",
  "packages": {
    "specter": {
      "release-type": "go",
      "package-name": "specter",
      "changelog-path": "CHANGELOG.md",
      "bump-minor-pre-major": true,
      "bump-patch-for-minor-pre-major": true,
      "draft": false,
      "prerelease": false
    }
  }
}
```

**`bump-minor-pre-major: true`**: пока версия 0.x.x, коммиты `feat` повышают patch, а не minor (избегает быстрой инфляции версий 0.x во время разработки до 1.0).

---

## 4. Стратегия распространения бинарников

### Каналы распространения

Specter распространяется как один статический бинарник без зависимостей времени выполнения.

**Homebrew (macOS и Linux):**
```bash
brew install hanalyx/tap/specter
```

**Пакет DEB (Debian/Ubuntu):**
```bash
# Скачайте из GitHub Releases, затем:
sudo dpkg -i specter_*.deb
```

**GitHub Releases (все платформы):**

Скачайте готовые бинарники для Linux, macOS (Intel и Apple Silicon) и Windows со страницы [GitHub Releases](https://github.com/Hanalyx/specter/releases). goreleaser создаёт архивы для каждой платформы при каждом тегированном релизе.

> **Примечание:** `go install github.com/Hanalyx/specter/cmd/specter@latest` сейчас не работает, потому что `go.mod` лежит в подкаталоге `specter/`, а не в корне репозитория. Используйте скачивание бинарников или пакеты DEB. Это будет решено при будущей реструктуризации репозитория.

### Конфигурация сборки

Файл `go.mod` в корне репозитория определяет путь модуля и зависимости. `Makefile` предоставляет цели сборки:

```bash
make build       # Build for current platform -> bin/specter
make build-all   # Cross-compile for linux/darwin/windows
make clean       # Remove built binaries
```

### Опыт установки (цель)

```bash
# Homebrew
brew install hanalyx/tap/specter
specter sync

# Go install
go install github.com/Hanalyx/specter/cmd/specter@latest
specter sync

# Direct download (example for Linux amd64)
curl -Lo specter.tar.gz https://github.com/Hanalyx/specter/releases/latest/download/specter_Linux_x86_64.tar.gz
tar xzf specter.tar.gz
./specter sync
```

---

## 5. Фазы релиза

### Фаза 1: мягкий запуск (v0.1.0)

**Цель:** получить раннюю обратную связь от практиков SDD.

- [ ] Запушить на GitHub как публичный репозиторий
- [ ] Написать анонс (dev.to, Reddit r/programming, HN)
- [ ] Поделиться с сообществом SDD (пользователи GitHub Spec Kit, Kiro, OpenSpec)
- [ ] Опубликовать бинарники через goreleaser как `v0.1.0-beta.1`
- [ ] Собирать обратную связь через GitHub Issues

**Метрика успеха:** 10+ звёзд GitHub, 3+ внешних заведённых issue.

### Фаза 2: стабилизация схемы (v0.2.0)

**Цель:** зафиксировать схему спецификации по реальному использованию.

- [ ] Выходит M6 (обратный компилятор) — решает проблему холодного старта
- [ ] Учтены изменения схемы по обратной связи пользователей
- [ ] Руководство по миграции для любых изменений схемы
- [ ] Опубликовать `0.2.0`

**Метрика успеха:** 3+ внешних проекта используют спецификации Specter.

### Фаза 3: стабильный релиз (v1.0.0)

**Цель:** схема спецификации заморожена. Публичный API гарантирован.

- [ ] Схема объявлена стабильной (без ломающих изменений без major-bump)
- [ ] Интерфейс CLI объявлен стабильным
- [ ] Полный обзор документации
- [ ] Опубликовать `1.0.0`

**Метрика успеха:** скачивания релизов GitHub > 100/неделю. Звёзды GitHub > 500.

---

## 6. Общественная инфраструктура

### Шаблоны GitHub

**Отчёт об ошибке:**
```markdown
**Specter version:** (output of `specter --version`)
**Go version:** (output of `go version`)
**OS:**

**Steps to reproduce:**
1.
2.

**Expected behavior:**

**Actual behavior:**

**Spec file (if relevant):**
```yaml
```
```

**Запрос функции:**
```markdown
**Is this related to a problem?**

**Proposed solution:**

**Spec (if you've written one):**
```yaml
```

**Alternatives considered:**
```

**Предложение спецификации (для новых правил проверки, полей схемы и т.п.):**
```markdown
**What should Specter detect/validate?**

**Example of a spec that should PASS:**
```yaml
```

**Example of a spec that should FAIL:**
```yaml
```

**Which tier(s) should this affect?**

**Proposed severity:** error / warning / info
```

### Метки

| Метка | Цвет | Использование |
|-------|-------|-------|
| `schema` | red | Изменения spec-schema.json |
| `check-rule` | blue | Новые или изменённые правила проверки |
| `cli` | green | Изменения интерфейса CLI |
| `docs` | grey | Документация |
| `good-first-issue` | purple | Лёгкая точка входа для участников |
| `breaking` | red | Потребует повышения major-версии |
| `reverse-compiler` | orange | Функции M6 |

---

## 7. Немедленные следующие шаги

1. **Создать файл LICENSE** (MIT)
2. **Создать CONTRIBUTING.md** (fork, ветка, сначала спецификация, PR)
3. **Настроить release-please** (GitHub Action + конфиг)
4. **Настроить goreleaser** (`.goreleaser.yaml` с целями кросс-компиляции)
5. **Запушить в Hanalyx/specter и проверить CI**
6. **Поставить тег v0.1.0**
