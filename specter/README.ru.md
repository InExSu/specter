# Specter

**Система типов для спецификаций.** Проверяет, связывает и типизирует `.spec.yaml` так же, как `tsc` проверяет `.ts`.

Спецификации без проверки — просто документы. Они могут противоречить друг другу, ссылаться на несуществующие зависимости, содержать ограничения, которые не покрывает ни один тест, и тихо гнить по мере развития кода. Specter трактует спецификации как типизированные артефакты в графе зависимостей, подверженные тому же статическому анализу, что и код.

Specter не зависит от содержания. `.spec.yaml` может описывать поведение во время выполнения, инварианты данных, политику безопасности, контракты схем, архитектурные правила или любой другой контракт компонента. Конвейер проверяет форму (ограничения, AC, прослеживаемость), а не категорию правила, которое вы кодируете.

```
$ specter sync
Specter Sync

  PASS parse: 15 spec(s) parsed successfully
  PASS resolve: 15 specs, 23 dependencies resolved
  PASS check: 0 warning(s), 0 info
  PASS coverage: 15 spec(s) meet coverage thresholds


All checks passed.
```

---

## Замысел человека, исполнение ИИ

Схема Specter намеренно подробна: ограничения, критерии приёмки, tiers, происхождение, пороги покрытия. Писать всё это вручную для каждого модуля было бы непрактично, и это никогда не было замыслом.

Задуманный процесс — сотрудничество между вами и вашим ИИ-ассистентом:

1. **Вы даёте замысел:** краткое описание того, что должен делать модуль, его ключевые ограничения и любые неочевидные суждения или компромиссы
2. **ИИ пишет спецификацию:** переводя ваш замысел в полностью структурированный файл `.spec.yaml` с ограничениями, AC и назначением tier
3. **ИИ пишет тесты:** выведенные напрямую из AC в спецификации
4. **Вы проверяете:** спецификация и тесты — шлюз одобрения; вы подтверждаете, что ИИ правильно зафиксировал ваш замысел, до начала любой реализации
5. **ИИ реализует:** спецификация как контракт, тесты как проверка

Specter проверяет артефакты перед собой, а не порядок, в котором вы их писали. Он проверяет, что каждая спецификация парсится и разрешается. Он измеряет покрытие по аннотациям `@spec` и `@ac` в ваших тестах. По умолчанию он засчитывает аннотированный критерий, только если его тест прошёл, в результатах, которые вы загружаете через `specter ingest`. Он валит `specter sync`, когда спецификация ниже своего порогового tier. Это делает правила инфраструктурой, а не пожеланием.

**Основная миссия: провести ваш ИИ-ассистент через спецификацию, тесты, реализацию и оценку в правильном порядке, каждый раз, с сохранением вашего замысла на всём пути.**

---

## Установка

### Расширение VS Code (рекомендуется большинству пользователей)

Найдите **Specter SDD** в панели Extensions. Расширение использует CLI, уже находящийся в PATH, если его версия поддерживается расширением, иначе скачивает собственную копию в `~/.specter/cli/`. Оно никогда не заменяет установленный вами CLI. Чтобы вызывать `specter` из терминала, один раз выполните **Specter: Add CLI to Shell PATH** из командной палитры; оно положит копию в `~/.specter/bin/specter`, если там ничего нет.

### CLI, Linux / macOS (tar.gz)

Имена ассетов следуют соглашениям Go `GOOS`/`GOARCH` (строчные `linux`/`darwin`, `amd64`/`arm64`), а не `Linux`/`x86_64` из `uname`. Этот фрагмент переводит их и автоматически выбирает последнюю версию:

```bash
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m); case "$ARCH" in x86_64) ARCH=amd64 ;; aarch64) ARCH=arm64 ;; esac
VERSION=$(curl -sL https://api.github.com/repos/Hanalyx/specter/releases/latest | grep '"tag_name"' | head -n1 | cut -d'"' -f4 | sed 's/^v//')
curl -LO "https://github.com/Hanalyx/specter/releases/download/v${VERSION}/specter_${VERSION}_${OS}_${ARCH}.tar.gz"
tar xzf "specter_${VERSION}_${OS}_${ARCH}.tar.gz"
sudo mv specter /usr/local/bin/
specter --version
```

### CLI, Debian / Ubuntu (.deb)

```bash
ARCH=$(dpkg --print-architecture)   # amd64 or arm64
VERSION=$(curl -sL https://api.github.com/repos/Hanalyx/specter/releases/latest | grep '"tag_name"' | head -n1 | cut -d'"' -f4 | sed 's/^v//')
curl -LO "https://github.com/Hanalyx/specter/releases/download/v${VERSION}/specter_${VERSION}_linux_${ARCH}.deb"
sudo dpkg -i "specter_${VERSION}_linux_${ARCH}.deb"
```

### CLI, Fedora / RHEL / openSUSE (.rpm)

```bash
ARCH=$(uname -m); case "$ARCH" in x86_64) ARCH=amd64 ;; aarch64) ARCH=arm64 ;; esac
VERSION=$(curl -sL https://api.github.com/repos/Hanalyx/specter/releases/latest | grep '"tag_name"' | head -n1 | cut -d'"' -f4 | sed 's/^v//')
curl -LO "https://github.com/Hanalyx/specter/releases/download/v${VERSION}/specter_${VERSION}_linux_${ARCH}.rpm"
sudo rpm -i "specter_${VERSION}_linux_${ARCH}.rpm"
```

### CLI, Windows (PowerShell)

```powershell
$version = (Invoke-RestMethod https://api.github.com/repos/Hanalyx/specter/releases/latest).tag_name -replace '^v',''
$asset = "specter_${version}_windows_amd64.zip"
Invoke-WebRequest -Uri "https://github.com/Hanalyx/specter/releases/download/v${version}/${asset}" -OutFile specter.zip
Expand-Archive specter.zip -DestinationPath "$env:USERPROFILE\.specter\bin"
[Environment]::SetEnvironmentVariable("Path", "$env:Path;$env:USERPROFILE\.specter\bin", "User")
specter --version  # restart terminal first, or reload $env:Path
```

### Сборка из исходников

```bash
git clone https://github.com/Hanalyx/specter.git
cd specter/specter
make build
./bin/specter --version
```

### Ручная загрузка

Если предпочитаете кликать, все ассеты перечислены на [странице Releases](https://github.com/Hanalyx/specter/releases/latest). Шаблон имени: `specter_<version>_<os>_<arch>.<ext>`, ОС в нижнем регистре, архитектура `amd64`/`arm64`.

---

## Конвейер

Specter выполняет четыре этапа последовательно, и `specter sync` запускает все четыре за вас. Каждый этап ловит свой класс проблем:

```
.spec.yaml files
      │
   [parse]      Schema validation: missing fields, invalid IDs, wrong types
      │
  [resolve]     Dependency graph: cycles, dangling refs, version mismatches
      │
   [check]      Structural analysis: orphan constraints, spec conflicts
      │
  [coverage]    Traceability: ACs without tests, below-threshold tiers

  specter sync  Runs all four in this order. Exits non-zero on any failure.
```

### Что ловит каждый этап

**`specter parse`.** Ловит некорректные спецификации до запуска чего-либо ещё. Отсутствующие обязательные поля, ID, не соответствующие допустимому шаблону, недопустимые значения перечислений, неверные типы. Как компилятор, ловящий синтаксические ошибки.

```bash
specter parse

# FAIL specs/auth.spec.yaml
#   error [required] spec: Missing required field 'acceptance_criteria'. Add at least one AC with id (AC-01 format) and description
#   error [pattern] spec.constraints[0].id: Constraint ID must match the C-NN pattern (e.g. C-01, C-02). Use uppercase C followed by a dash and two digits
```

**`specter resolve`.** Строит граф зависимостей по всем спецификациям и проверяет его. Ловит циклические зависимости и ссылки на несуществующие спецификации. Строки `did you mean` и `fix`, следующие за висячей ссылкой, в этом примере опущены.

```bash
specter resolve

# Spec Graph: 3 specs, 2 dependencies
#
# error [dangling_reference] Spec "spec-auth" depends on "spec-session" which does not exist
# error [circular_dependency] Circular dependency detected: spec-a -> spec-b -> spec-a
```

**`specter check`.** Находит структурные проблемы внутри и между спецификациями. Осиротевшее ограничение — то, на которое не ссылается ни один критерий приёмки, — это ограничение, которое никогда нельзя проверить. Конфликт tier ловит спецификацию, чей объявленный `tier:` расходится с устаревшим `settings.tier_overrides`. Управляет объявленный tier, переопределение не применяется. Предупреждение не косметическое: `--strict` повышает его до ошибки, поэтому расхождение валит строгую сборку.

```bash
specter check

# warn: settings.tier_overrides is deprecated and resolves no tier. Its value is still compared: one that disagrees with a spec's declared tier warns, and --strict makes that an error. Set tier: in each .spec.yaml file. It is removed at v1.0.0.
# error [orphan_constraint] spec-auth C-04 (security): Constraint C-04 in "spec-auth" is not referenced by any acceptance criterion
# warn [tier_conflict] spec-payments: spec "spec-payments" declares tier: 2 but specter.yaml tier_overrides assigns tier: 1. The declared tier governs; tier_overrides is not applied.
#
# 1 error(s), 1 warning(s), 0 info
```

**`specter coverage`.** Читает аннотации `@spec` и `@ac` из ваших тестовых файлов и строит матрицу прослеживаемости. Применяет пороги покрытия по tier.

Строгость по умолчанию — `threshold`, проверяемая по результатам: она требует
`.specter-results.json` и отказывает без него. В новом рабочем пространстве сначала выполните
`specter ingest` или передайте `--strictness annotation`, чтобы считать только аннотации.

```bash
specter coverage --strictness annotation

# Spec ID                                   Tier   ACs      Covered   Coverage   Status
# ----------------------------------------------------------------------------------
# spec-auth                                 T1     6        4         66%        FAIL
#   uncovered: AC-05, AC-06
# spec-payments                             T2     5        5         100%       PASS
```

**`specter sync`.** Запускает все четыре этапа и выходит с 0, только когда всё проходит. Поместите это в CI.

---

## Напишите спецификацию

```yaml
spec:
  id: user-registration
  version: "1.0.0"
  status: approved
  tier: 1

  context:
    system: Auth service
    description: >
      Handles new user account creation. Email is the primary identifier.
      Passwords are hashed with bcrypt before storage, never stored in plaintext.

  objective:
    summary: >
      Register a new user with email and password.
      Return a session token on success.
    scope:
      excludes:
        - "Social login (OAuth), separate spec"
        - "Email verification, handled post-registration"

  constraints:
    - id: C-01
      description: "Email MUST be a valid RFC 5322 address"
      type: technical
      enforcement: error
    - id: C-02
      description: "Password MUST be at least 12 characters"
      type: security
      enforcement: error
    - id: C-03
      description: "Passwords MUST be hashed with bcrypt, cost factor ≥ 12"
      type: security
      enforcement: error

  acceptance_criteria:
    - id: AC-01
      description: "Returns 201 with session token when registration succeeds"
      references_constraints: ["C-01", "C-02", "C-03"]
    - id: AC-02
      description: "Returns 422 when email format is invalid"
      references_constraints: ["C-01"]
    - id: AC-03
      description: "Returns 422 when password is shorter than 12 characters"
      references_constraints: ["C-02"]
    - id: AC-04
      description: "Returns 409 when email is already registered"
      references_constraints: ["C-01"]
```

Проверьте её:

```bash
specter parse user-registration.spec.yaml
# PASS user-registration.spec.yaml — user-registration@1.0.0
```

---

## Аннотируйте тесты

Связывайте тестовые функции с критериями приёмки через комментарии к исходнику. `specter coverage` читает эти комментарии и строит матрицу прослеживаемости.

```go
// @spec user-registration
// @ac AC-01
func TestRegistration_ValidEmailAndPassword_Returns201(t *testing.T) {
    // ...
}

// @spec user-registration
// @ac AC-02
func TestRegistration_InvalidEmail_Returns422(t *testing.T) {
    // ...
}
```

Для `coverage --strict` раннер тестов также должен показать ту же пару `(spec_id, ac_id)` в своём выводе. Поместите `spec-id/AC-NN` в заголовок теста или напечатайте `// @spec` и `// @ac` из тела теста перед запуском `specter ingest`.

---

## Принуждение по tier

Пороги покрытия масштабируются с риском:

| Tier | Примеры | Требуемое покрытие по умолчанию |
|---|---|---|
| **T1**, безопасность и деньги | Аутентификация, платежи, шифрование | 100% |
| **T2**, бизнес-логика | Поток бронирования, правила ценообразования | 80% |
| **T3**, утилиты | Форматтеры, помощники | 50% |

Спецификация ниже своего порога валится на каждом tier. Tier задаёт, сколько покрытия требуется, а не то, как трактуется дефицит: строка читается FAIL независимо от того, Tier 1 это или Tier 3. Сам шлюз порога выходит с 1, но он работает после шлюзов аннотаций, нулевой терпимости и одобрения. Прогон, задевший один из них, выходит с 2 или 3. [Справочник кодов выхода](docs/EXIT_CODES.ru.md) содержит полный порядок.

Эти пороги — значения по умолчанию. `settings.coverage.tier1` … `tier3` меняют их для рабочего пространства, а `coverage_threshold` у спецификации переопределяет её tier.

---

## Аналогия с системой типов

Спецификации отображаются в концепции типов программирования один к одному:

| Система типов | Эквивалент в Specter |
|---|---|
| Определение типа | Ограничение. Определяет, что допустимо |
| Сигнатура функции | Критерий приёмки. Вход и ожидаемый выход |
| Инструкция импорта | `depends_on`. Формальный контракт между спецификациями |
| Ошибка типа | Конфликт спецификаций. Ловится до запуска кода |
| Неиспользуемая переменная | Осиротевшее ограничение. На него не ссылается ни один AC |
| Отсутствующая проверка null | Пробел покрытия. AC без теста |

---

## Структура проекта

```
specter/
  cmd/specter/       CLI entry point (Cobra)
  internal/
    parser/          M1: YAML to validated SpecAST
    resolver/        M2: Dependency graph, cycle detection
    checker/         M3: Orphan constraints, structural conflicts
    coverage/        M4: Spec-to-test traceability matrix
    sync/            M5: CI pipeline orchestrator
    reverse/         M6: Reverse-compile specs from existing code
    ingest/          Test-runner output to .specter-results.json
    diff/            Semantic diff between two specs
    explain/         Read-only reference surfaces
    manifest/        specter.yaml parsing and validation
    migrate/         Schema migration paths
    schema/          Canonical types + embedded JSON Schema
  specs/             Specter's own specs (dogfooding)
  testdata/          Test fixtures
  docs/              User documentation
```

---

## Разработка

```bash
make check           # gofmt-check, go vet, golangci-lint, go test, go build. The CI gate
make dogfood         # run specter against its own specs (annotation-counting gate)
make dogfood-strict  # mechanical eval gate: go test -json + jest, then specter ingest, then coverage --strict
make build-all       # cross-compile for linux/darwin/windows
```

Ни один пакет в `internal/` не импортирует CLI-фреймворк; `cmd/specter/` владеет разбором флагов и завершением процесса. Большинство — чистые: `internal/ingest` — исключение, потому что чтение артефакта раннера тестов и запись `.specter-results.json` и есть его назначение.

---

## Dogfooding

Specter проверяет собственные спецификации. Набор dogfood покрывает конвейер CLI и расширение VS Code. Строгий шлюз проверяет результаты тестов через `go test -json`, вывод Jest JUnit, `specter ingest` и `coverage --strict`.

Эти цифры проверены по результатам: они получены из `make dogfood-strict`, который
запускает тесты, подаёт результаты через `specter ingest` и шлюзует по ним. Число
покрытия ничего не значит без уровня строгости, потому что одно и то же
рабочее пространство отчитывается по-разному при каждом из них.

Три строки `hint:` об аннотациях без соответствующего результата предшествуют отчёту
и опущены ниже, как и некоторые строки таблицы, помеченные `...`.

```
$ specter coverage --strict

Spec Coverage Report — 15 specs · 99% avg coverage
  Tier 1: 4/4 passing (100%)
  Tier 2: 9/9 passing (100%)
  Tier 3: 2/2 passing (100%)

Spec ID                                   Tier   ACs      Covered   Coverage   Status
----------------------------------------------------------------------------------
spec-diff                                 T2     19       18        94%        PASS
  uncovered: AC-11
  no test: AC-11
spec-manifest                             T2     72       71        98%        PASS
  uncovered: AC-29
  no test: AC-29
...
spec-check                                T1     46       46        100%       PASS
spec-ingest                               T1     18       18        100%       PASS
...

15 specs: 15 passing, 0 failing
warn: 3 acceptance criterion(s) have no test. settings.annotation.permissive is true, so this does not fail the run
```

---

## Документация

| | |
|---|---|
| [Начало работы](docs/GETTING_STARTED.ru.md) | Напишите и проверьте первую спецификацию |
| [Промпты для ИИ](docs/AI_PROMPTS.ru.md) | Готовые промпты для каждого этапа цикла SDD |
| [Справочник схемы спецификации](docs/SPEC_SCHEMA_REFERENCE.ru.md) | Каждое поле формата `.spec.yaml` |
| [Справочник CLI](docs/CLI_REFERENCE.ru.md) | Все команды, флаги и коды выхода |
| [FAQ](docs/FAQ.ru.md) | Частые вопросы о SDD и Specter |

---

## Лицензия

MIT
