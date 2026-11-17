# Начало работы со Specter

Это руководство ведёт вас от **нуля спецификаций до полного покрытия** шаг за шагом, с каждой командой, каждым промптом для ИИ и полным разбором рабочего пространства VS Code.

Если вы просто хотите увидеть, как это работает, за 5 минут — начните с [QuickStart](QUICKSTART.ru.md).

---

## Перед началом

### Что такое Specter

Specter — **система типов для спецификаций**. Он проверяет, связывает и типизирует `.spec.yaml` так же, как `tsc` проверяет `.ts`. Основная идея: ваша спецификация — источник истины, а не код, не тесты и не вывод ИИ. Specter это обеспечивает.

### Чем Specter не является

Specter — **не** универсальный читатель форматов спецификаций. Если вы уже используете спецификации (файлы Gherkin/Cucumber `.feature`, OpenAPI `.yaml`, документы Notion, страницы Confluence), Specter не читает эти форматы. Он использует собственную структурированную схему (см. [Справочник по схеме](SPEC_SCHEMA_REFERENCE.ru.md)).

**Если у вас есть спецификации в другом формате**, есть два варианта:

| Вариант | Когда использовать |
|--------|-------------|
| **Запустить `specter reverse`** по исходному коду, затем отказаться от старых спецификаций | Ваши существующие спецификации высокоуровневые или неформальные, а код — реальный источник истины |
| **Мигрировать существующие спецификации** в схему Specter вручную или с помощью ИИ | Ваши существующие спецификации подробны и авторитетны, и вы хотите их сохранить |

Для миграции используйте этот промпт:

```
I have specifications in [Gherkin / OpenAPI / plain text / other format].
I want to migrate them to Specter's .spec.yaml format.

Specter's schema requires these top-level fields:
  spec.id — lowercase letters, digits, hyphens only, must start with a letter
            (e.g. "user-create", "payment-process"). No uppercase, no underscores.
  spec.version — quoted semver string: "1.0.0" (must be quoted or YAML parsing fails)
  spec.status — one of: draft | review | approved | deprecated | removed
  spec.tier — integer only, no quotes: 1 (Security/Money), 2 (Core Business), 3 (Utility)
  spec.context.system — string (name of the system or service)
  spec.objective.summary — string inside an objective object, not a bare string
  spec.constraints — array of objects. Required fields per item: id (format: C-01, C-02...),
                     description. Optional fields: type (technical | security | performance |
                     accessibility | business), enforcement (error | warning | info).
                     No other fields are allowed.
  spec.acceptance_criteria — array of objects. Required fields per item: id (format: AC-01,
                     AC-02...), description. Optional fields: references_constraints (array
                     of C-XX strings), inputs, expected_output, priority (critical | high |
                     medium | low). No other fields are allowed.

Here is my existing spec:
[paste your spec]

Please convert it to Specter's .spec.yaml format. Keep all the intent,
rewrite constraints to use MUST/MUST NOT/SHOULD language (RFC 2119),
and break acceptance criteria into individually testable AC-XX items.
```

---

## Фаза 1: Установка

### CLI

Релизные ассеты следуют соглашению goreleaser `specter_<version>_<os>_<arch>.<ext>`: строчные `linux`/`darwin`/`windows`, `amd64`/`arm64` из Go (а не `x86_64`/`aarch64` из `uname`). Каждый фрагмент ниже переводит их и автоматически выбирает последнюю версию.

**macOS / Linux (tar.gz):**
```bash
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m); case "$ARCH" in x86_64) ARCH=amd64 ;; aarch64) ARCH=arm64 ;; esac
VERSION=$(curl -sL https://api.github.com/repos/Hanalyx/specter/releases/latest | grep '"tag_name"' | head -n1 | cut -d'"' -f4 | sed 's/^v//')
curl -LO "https://github.com/Hanalyx/specter/releases/download/v${VERSION}/specter_${VERSION}_${OS}_${ARCH}.tar.gz"
tar xzf "specter_${VERSION}_${OS}_${ARCH}.tar.gz" && sudo mv specter /usr/local/bin/
specter --version
```

**DEB-пакет (Ubuntu/Debian):**
```bash
ARCH=$(dpkg --print-architecture)
VERSION=$(curl -sL https://api.github.com/repos/Hanalyx/specter/releases/latest | grep '"tag_name"' | head -n1 | cut -d'"' -f4 | sed 's/^v//')
curl -LO "https://github.com/Hanalyx/specter/releases/download/v${VERSION}/specter_${VERSION}_linux_${ARCH}.deb"
sudo dpkg -i "specter_${VERSION}_linux_${ARCH}.deb"
```

**RPM-пакет (Fedora/RHEL):**
```bash
ARCH=$(uname -m); case "$ARCH" in x86_64) ARCH=amd64 ;; aarch64) ARCH=arm64 ;; esac
VERSION=$(curl -sL https://api.github.com/repos/Hanalyx/specter/releases/latest | grep '"tag_name"' | head -n1 | cut -d'"' -f4 | sed 's/^v//')
curl -LO "https://github.com/Hanalyx/specter/releases/download/v${VERSION}/specter_${VERSION}_linux_${ARCH}.rpm"
sudo rpm -i "specter_${VERSION}_linux_${ARCH}.rpm"
```

**Windows (PowerShell):**
```powershell
$v = (Invoke-RestMethod https://api.github.com/repos/Hanalyx/specter/releases/latest).tag_name -replace '^v',''
Invoke-WebRequest -Uri "https://github.com/Hanalyx/specter/releases/download/v${v}/specter_${v}_windows_amd64.zip" -OutFile specter.zip
Expand-Archive specter.zip -DestinationPath "$env:USERPROFILE\.specter\bin"
[Environment]::SetEnvironmentVariable("Path", "$env:Path;$env:USERPROFILE\.specter\bin", "User")
```

**Сборка из исходников (Go 1.27.3+):**
```bash
git clone https://github.com/Hanalyx/specter.git
cd specter/specter && make build
sudo mv bin/specter /usr/local/bin/
```

Проверьте (в Windows сначала перезапустите терминал, чтобы PATH подхватился):
```bash
specter --version
specter --help
```

### Расширение VS Code

1. Откройте VS Code
2. Нажмите `Ctrl+Shift+X` (панель Extensions)
3. Найдите `Specter SDD`
4. Нажмите **Install**

Расширение активируется автоматически, как только в рабочем пространстве появится `specter.yaml` (фаза 2, шаг 3).

---

## Фаза 2: Загрузка спецификаций

### Шаг 1: Запустите обратный компилятор

Направьте Specter на каталог с исходниками. Он анализирует код и автоматически генерирует черновики спецификаций:

```bash
specter reverse src/        # TypeScript / JavaScript / Next.js
specter reverse app/        # Python / Django / FastAPI
specter reverse ./          # Go
specter reverse packages/   # monorepo — point at the package root
```

Что создаётся:
```
specs/
  user-create.spec.yaml
  payment-process.spec.yaml
  auth-jwt.spec.yaml
  ...
```

Каждая спецификация отражает структуру, которую Specter нашёл в коде: маршруты, модели, правила валидации и ограничения. У некоторых критериев приёмки на этом этапе может быть `gap: true`. Это ожидаемо.

> **`gap: true` означает:** Specter извлёк структуру, но не смог вывести *замысел*. Человек (или ИИ) должен завершить её, прежде чем она станет авторитетной.

### Шаг 2: Инициализируйте манифест рабочего пространства

```bash
specter init
```

Создаёт `specter.yaml` и создаёт каталог `specs/`, который он называет, если этого каталога ещё нет:
```yaml
schema_version: 1
system:
  name: my-project
domains:
  default:
    description: Add spec IDs here as you create them. See the spec-manifest spec for the schema.
settings:
  specs_dir: specs
  coverage:
    tier1: 100
    tier2: 80
    tier3: 50
  exclude:
    - node_modules
    - dist
    - .git
    - vendor
```

Этот файл нужен, чтобы:
- Активировалось расширение VS Code
- `specter sync` знал, где искать
- Работали настройки обнаружения и пороги покрытия

Закоммитьте этот файл. Ему место в системе контроля версий.

### Шаг 3: Проверьте, что расширение VS Code активировалось

Откройте VS Code в папке проекта. Посмотрите на панель активности (левая боковая панель) — там значок **Sp**. Нажмите его. Вы должны увидеть панель **Specter: Coverage** со списком ваших спецификаций и текущими процентами покрытия.

Если видите `Specter: no specter.yaml found in this workspace`, сначала запустите `specter init` (шаг 2).

---

## Фаза 3: Закройте пробелы

Это самая важная фаза. Вы превращаете извлечённые ИИ черновики в авторитетные спецификации.

### Шаг 1: Запустите `specter check`, чтобы увидеть картину

```bash
specter check
```

Он сообщает о структурных проблемах: осиротевшие ограничения (на них не ссылается ни один AC), битые зависимости, отсутствующие обязательные поля. Исправьте каждую `error` перед продолжением. Пункты `warn` можно закрывать постепенно.

### Шаг 2: Проверьте каждую спецификацию с ИИ

Откройте сгенерированную спецификацию. Она выглядит так:

```yaml
spec:
  id: user-create
  version: "1.0.0"
  status: draft
  tier: 2
  context:
    system: User service
    description: "Handles user account creation"
  objective:
    summary: "Create a new user account"
  constraints:
    - id: C-01
      description: "POST /users accepts email and password"
  acceptance_criteria:
    - id: AC-01
      description: ""
      gap: true
    - id: AC-02
      description: ""
      gap: true
```

**Промпт для ИИ, чтобы закрыть пробелы:**

```
Here is a draft spec generated by Specter's reverse compiler for my [language/framework] codebase.

[paste the spec]

Please complete this spec:
1. Fill each empty acceptance_criteria description with a specific, testable behavior
   (e.g., "Valid email + password creates user and returns 201 with JWT token")
2. Add any obviously missing constraints based on the context
3. Add `references_constraints` arrays to each AC linking back to the C-XX IDs it validates
4. Set `status: draft` (leave it; we'll promote later)
5. Remove `gap: true` once all gaps are filled
6. Keep all existing IDs (C-01, AC-01, etc.) unchanged. Do not renumber
7. Use MUST/MUST NOT/SHOULD language in constraint descriptions (RFC 2119)

Return only the completed YAML.
```

**Промпт для ИИ, чтобы добавить недостающие ограничения:**

```
Review this Specter spec for [feature name]. Based on the context and objective,
what constraints are likely missing?

[paste the spec]

For each gap you identify, add a new constraint with:
- Sequential ID (next after the last C-XX)
- A MUST/MUST NOT description
- type: technical | security | performance | business
- enforcement: error | warning

Also add a corresponding AC that references it.
Return the updated YAML only.
```

### Шаг 3: Проверьте каждую спецификацию

После правок ИИ проверяйте перед продолжением:

```bash
specter parse specs/user-create.spec.yaml
```

```
PASS specs/user-create.spec.yaml — user-create@1.0.0
```

Если не проходит, Specter точно скажет, что не так:

```
FAIL specs/user-create.spec.yaml
  error [pattern] spec/constraints/0/id: must match "^C-\d{2,}$"
```

Частые исправления:
- ID должны быть `C-01`, а не `c1`, `C1` или `constraint-1`
- Версия должна быть в кавычках: `"1.0.0"`, а не `1.0.0`
- `tier` должен быть целым числом: `2`, а не `"2"`
- `status` должен быть одним из: `draft`, `review`, `approved`, `deprecated`, `removed`

### Шаг 4: Повторите для всех спецификаций

```bash
specter parse    # validates all specs at once
specter check    # checks structural relationships
```

Когда обе команды завершаются чисто без ошибок, фаза 3 завершена.

---

## Фаза 4: Пишите тесты по спецификациям

Specter читает аннотации тестов из двух мест. Оба важны.

1. **Комментарии к исходнику**: `// @spec <spec-id>` и `// @ac AC-NN` над тестовой функцией. Читает `specter coverage`.
2. **Аннотация, видимая раннеру**: пара `<spec-id>/AC-NN` в заголовке теста или `console.log('// @spec ...')` в теле теста. Читает `specter ingest` в `.specter-results.json`. Требуется для `specter coverage --strict`.

Только комментарии к исходнику: `coverage` их учитывает, `--strict` понижает. Пишите обе формы, чтобы работали обе команды.

Полные правила, примеры по языкам, параметризованные тесты, рецепт миграции и устранение неполадок: см. [`TEST_ANNOTATION_REFERENCE.ru.md`](TEST_ANNOTATION_REFERENCE.ru.md).

### Шаг 1: Посмотрите, что не покрыто

```bash
specter coverage
```

```
Spec Coverage Report

Spec ID        Tier   ACs   Covered   Coverage   Status
------------------------------------------------------------
user-create    T2     4     0         0%         PASS
payment        T1     6     0         0%         FAIL  ← tier 1 needs 100%
auth-jwt       T2     5     0         0%         PASS
```

### Шаг 2: Попросите ИИ написать аннотированные тесты

Используйте `specter explain`, чтобы получить готовый к копированию пример аннотации для любого AC:

```bash
specter explain user-create
```

Затем передайте спецификацию ИИ-ассистенту:

**Промпт для ИИ, чтобы написать тесты по спецификации:**

```
Here is a Specter spec:

[paste the spec]

Write tests in [TypeScript/Jest | Python/pytest | Go testing].

Rules:
1. One test per AC.
2. The test title carries [spec-id/AC-NN]:
   TypeScript:  it('[spec-id/AC-NN] brief description', () => { ... })
   Python:      use a runtime print/log form; pytest function names do not
                contain the `/` or `:` separator that ingest requires
   Go:          t.Run("spec-id/AC-NN brief description", ...)
   AC-NN is zero-padded: AC-01, not AC-1.
3. Above each test, add:
   // @spec [spec-id]
   // @ac [AC-NN]
4. Use [your test framework/mocks].
5. Tests are runnable. Use realistic inputs from the spec's `inputs` fields.

Return only the test code.
```

**TypeScript/Jest:**
```typescript
// @spec user-create
// @ac AC-01
test('[user-create/AC-01] valid email and password creates user and returns 201 with JWT', async () => {
  const res = await request(app).post('/users').send({
    email: 'alice@example.com',
    password: 'correct-horse-battery',
  });
  expect(res.status).toBe(201);
  expect(res.body).toHaveProperty('token');
});

// @spec user-create
// @ac AC-02
test('[user-create/AC-02] invalid email format returns 400', async () => {
  const res = await request(app).post('/users').send({
    email: 'not-an-email',
    password: 'correct-horse-battery',
  });
  expect(res.status).toBe(400);
  expect(res.body.error).toContain('email');
});
```

**Python/pytest**: имена функций Python не могут содержать `/` или `:`. Используйте вывод во время выполнения, чтобы `specter ingest` мог прочитать пару из JUnit `<system-out>`.
```python
# @spec user-create
# @ac AC-01
def test_valid_registration_returns_201(client):
    print('// @spec user-create')
    print('// @ac AC-01')
    response = client.post('/users', json={
        'email': 'alice@example.com',
        'password': 'correct-horse-battery'
    })
    assert response.status_code == 201
    assert 'token' in response.json()

# @spec user-create
# @ac AC-02
def test_invalid_email_returns_400(client):
    print('// @spec user-create')
    print('// @ac AC-02')
    response = client.post('/users', json={
        'email': 'not-an-email',
        'password': 'correct-horse-battery'
    })
    assert response.status_code == 400
```

Запускайте pytest с включённым логированием JUnit:

```bash
pytest --junitxml=test-results.xml -o junit_logging=all -o junit_log_passing_tests=True
```

**Go**: используйте `t.Run`, чтобы у каждого AC был собственный заголовок подтеста, видимый раннеру. `specter ingest` читает имена подтестов из вывода `go test -json`.
```go
// @spec user-create
// @ac AC-01
// @ac AC-02
func TestCreateUser(t *testing.T) {
    t.Run("user-create/AC-01 valid credentials returns 201 with JWT", func(t *testing.T) {
        body := `{"email":"alice@example.com","password":"correct-horse-battery"}`
        rec := httptest.NewRecorder()
        req := httptest.NewRequest(http.MethodPost, "/users", strings.NewReader(body))
        handler.ServeHTTP(rec, req)
        assert.Equal(t, http.StatusCreated, rec.Code)
        assert.Contains(t, rec.Body.String(), "token")
    })

    t.Run("user-create/AC-02 invalid email returns 400", func(t *testing.T) {
        body := `{"email":"not-an-email","password":"correct-horse-battery"}`
        rec := httptest.NewRecorder()
        req := httptest.NewRequest(http.MethodPost, "/users", strings.NewReader(body))
        handler.ServeHTTP(rec, req)
        assert.Equal(t, http.StatusBadRequest, rec.Code)
    })
}
```

### Шаг 3: Проверяйте покрытие после каждого тестового файла

```bash
specter coverage
```

```
user-create    T2    4 ACs    2 covered    50%    PASS
```

Повторяйте, пока все спецификации tier 1 не достигнут 100%, а tier 2 — 80%.

---

## Фаза 5: Разбор рабочего пространства VS Code

Когда `specter.yaml` на месте, а спецификации аннотированы, расширение VS Code даёт обратную связь в реальном времени по мере написания кода.

### Панель покрытия

Нажмите значок **Sp** в панели активности. Панель **Specter: Coverage** показывает каждую спецификацию с текущим процентом покрытия. Красный — ниже порога. Нажмите на спецификацию, чтобы открыть её.

### Встроенная диагностика

Расширение подчёркивает аннотации `@ac` в тестовых файлах, когда указанный AC не существует ни в одной спецификации. Это ловит опечатки и устаревшие ссылки сразу, до CI.

### Запуск Sync из VS Code

Откройте командную палитру (`Ctrl+Shift+P`), введите **Specter: Run Sync**. Это запускает полный конвейер `specter sync` и сообщает результаты в панели Output, не покидая VS Code.

### Обнаружение дрейфа

Когда спецификация меняется (вы правите ограничение или описание AC), расширение подсвечивает тестовые файлы, ссылающиеся на эту спецификацию. Это предупреждение о **дрейфе замысла**: ваши тесты могут больше не соответствовать обновлённой спецификации.

---

## Фаза 6: Закрепите в CI

Когда `specter sync` проходит локально, добавьте его в CI-конвейер. Это шлюз, не дающий спецификациям и тестам разъезжаться на каждом PR.

**GitHub Actions (композитный action, закреплённая версия, предпочтительно):**
```yaml
- uses: Hanalyx/specter/specter/.github/actions/specter-sync@v0.15.3
  with:
    version: 0.15.3
```

Action живёт в подкаталоге `specter/` репозитория `Hanalyx/specter`, поэтому путь
повторяет `specter`. Тег после `@` выбирает код самого action. Вход `version` выбирает
бинарник, который он скачивает. Закрепляйте оба.

Action версии `v0.15.3` и новее проверяет sha256 архива по `checksums.txt` релиза
перед извлечением бинарника. При несовпадении или отсутствии файла шаг падает. Теги до
v0.15.3 эту проверку не выполняют.

**Или inline-загрузка (если не можете использовать композитный action):**
```yaml
- name: Install specter
  shell: bash
  run: |
    set -euo pipefail
    case "${{ runner.os }}" in Linux) OS=linux ;; macOS) OS=darwin ;; *) echo "Unsupported OS: ${{ runner.os }}. Linux and macOS only." >&2; exit 1 ;; esac
    case "${{ runner.arch }}" in X64) ARCH=amd64 ;; ARM64) ARCH=arm64 ;; esac
    VERSION=0.15.3   # pin a version; don't rely on "latest" in CI
    FILE="specter_${VERSION}_${OS}_${ARCH}.tar.gz"
    BASE="https://github.com/Hanalyx/specter/releases/download/v${VERSION}"
    curl -fsSLO "${BASE}/${FILE}"
    curl -fsSLO "${BASE}/checksums.txt"
    grep " ${FILE}\$" checksums.txt | shasum -a 256 -c -   # fails on a mismatch or a missing entry
    tar xzf "${FILE}" specter && sudo mv specter /usr/local/bin/   # extract only the binary
    rm -f "${FILE}" checksums.txt
- name: Specter sync
  run: specter sync
```

---

## Фаза 7: Переведите спецификации в approved

Когда спецификация полностью покрыта и проверена вашей командой, переведите её:

```yaml
spec:
  id: user-create
  status: approved    # ← was draft
```

`approved` означает, что команда приняла спецификацию как авторитетную. Specter по умолчанию проверяет и спецификации `draft`, и `review`. Для релизных шлюзов установите `settings.warn_on_draft: true` и `settings.strict: true`, чтобы черновики и предупреждения блокировали конвейер.

**Промпт для ИИ, чтобы проверить спецификацию перед переводом:**

```
Review this Specter spec before we promote it from draft to approved:

[paste the spec]

Check for:
1. All constraints use RFC 2119 language (MUST/MUST NOT/SHOULD/MAY)
2. Every constraint is referenced by at least one AC
3. Every AC has a specific, testable description (not vague)
4. The objective scope clearly states what is excluded
5. Tier assignment is appropriate (1=Security/Money, 2=Core Business, 3=Utility)

Flag any issues. If it looks good, say so and I'll promote it.
```

---

## Устранение неполадок

| Проблема | Причина | Решение |
|---------|-------|-----|
| `Specter: no specter.yaml found` | Манифест отсутствует | Запустите `specter init` |
| `error [required] spec/id` | Отсутствует обязательное поле | Добавьте поле; см. [Справочник по схеме](SPEC_SCHEMA_REFERENCE.ru.md) |
| `error [pattern] spec/constraints/0/id` | Неверный формат ID | Должно быть `C-01`, `C-02` и т.д. |
| AC показывает 0% после аннотирования тестов | Аннотация не найдена | Проверьте, что ID в `@spec` точно совпадает с `spec.id`; проверьте `settings.tests_glob` или передайте `--tests <glob>` |
| `specter reverse` генерирует слишком много спецификаций | Большая кодовая база | Используйте флаг `--exclude` или добавьте шаблоны в `specter.yaml` |
| Покрытие падает после рефакторинга | Тесты удалены | Переаннотируйте новые тесты; запустите `specter coverage`, чтобы найти пробел |

---

## Справочник

- **[QuickStart](QUICKSTART.ru.md)**: 5-минутный путь, если хотите просто увидеть, как это работает
- **[Справочник схемы спецификации](SPEC_SCHEMA_REFERENCE.ru.md)**: каждое поле, тип и правило валидации
- **[Справочник CLI](CLI_REFERENCE.ru.md)**: все команды и флаги
- **[Промпты для ИИ](AI_PROMPTS.ru.md)**: готовые промпты для полного цикла SDD
- **[Собственные спецификации Specter](../specs/)**: продакшн-спецификации самого Specter
- **[FAQ](FAQ.ru.md)**: частые вопросы о SDD и Specter
