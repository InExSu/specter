# Аннотируйте тесты и проверьте покрытие

## Добавьте аннотации в тесты

Аннотируйте каждый тест двумя вещами:

1. **Комментарии к исходнику** над тестом: `// @spec <id>` и `// @ac AC-NN`. Их считает `specter coverage`.
2. **`<spec-id>/AC-NN` в заголовке теста**. Это читает `specter ingest`. Этого требует `specter coverage --strict`.

Пишите оба. `coverage` работает только с комментариями к исходнику; `--strict` — нет.

```typescript
// @spec user-create
// @ac AC-01
test('[user-create/AC-01] valid email and password creates user and returns 201', async () => {
  // ...
});
```

```python
# @spec user-create
# @ac AC-01
def test_user_create_AC_01_valid_registration_returns_201(client):
    # ...
```

```go
// @spec user-create
// @ac AC-01
func TestCreateUser(t *testing.T) {
    t.Run("user-create/AC-01 valid credentials returns 201", func(t *testing.T) {
        // ...
    })
}
```

Номера AC дополняются нулями: `AC-01`, а не `AC-1`. Один тест на AC. Полные правила — в `docs/TEST_ANNOTATION_REFERENCE.md`.

**Автодополнение работает автоматически** — наберите `// @spec `, и Specter предложит ID; наберите `// @ac `, и варианты будут ограничены спецификацией выше.

## Проверьте покрытие

```bash
specter coverage
```

```
user-create    T2    4 ACs    1 covered    25%    PASS
```

Каждая добавленная аннотация `@ac` повышает процент. Спецификациям Tier 1 нужно 100%. Спецификациям Tier 2 нужно 80%.

## Запустите весь конвейер

```bash
specter sync
```

```
PASS parse:    all specs valid
PASS resolve:  no dependency issues
PASS check:    0 errors
PASS coverage: thresholds met

All checks passed.
```

**Добавьте это в CI** — команда завершается с ненулевым кодом, если какая-либо спецификация Tier 1 или Tier 2 опускается ниже своего порога покрытия.

```yaml
# GitHub Actions
- name: Specter sync
  run: specter sync
```

> **Готово.** Панель Coverage в боковой панели показывает статус в реальном времени. Значки на полях становятся зелёными по мере аннотирования. Строка состояния всегда показывает суммарное покрытие.
