# Промпты для ИИ в Specter

Схема Specter намеренно подробна — но писать спецификации вручную вы не должны. Задуманный процесс — сотрудничество: **вы даёте замысел, ваш ИИ-ассистент переводит его в полную спецификацию и тесты, вы проверяете и одобряете.**

Эти промпты можно вставлять в Claude, Cursor, Copilot или любой ИИ-ассистент для кода. Используйте их по порядку для новой функции или по отдельности, когда нужен конкретный шаг.

---

## 1. Замысел → Спецификация

Отправная точка каждой функции. Вы описываете, чего хотите; ИИ создаёт полный `.spec.yaml`.

```
I want to build [module name]. Here is my intent:

[2-3 sentences describing what it does]

Key constraints I care about:
- [constraint 1]
- [constraint 2]

Non-obvious decisions / trade-offs:
- [anything the AI shouldn't guess about]

Generate a complete `.spec.yaml` for this using Specter's schema.
- id: [kebab-case name]
- status: draft
- tier: [1 = security/money, 2 = business logic, 3 = utility]
- Use MUST / MUST NOT language for constraints
- Generate ACs that cover each constraint, including error cases
- Do not invent requirements I haven't mentioned
```

---

## 2. Ревью сгенерированной спецификации

Запускайте перед одобрением любой спецификации. Спецификация — шлюз одобрения: проблемы, найденные здесь, ничего не стоят. Проблемы, найденные после реализации, дороги.

```
Review this Specter spec before I approve it.

Check for:
- Are all constraints actually testable?
- Are there obvious missing edge cases in the ACs?
- Does the objective accurately match the constraints?
- Is the tier appropriate for this module's criticality?
- Are any constraints redundant or contradictory?
- Would anything here surprise a developer implementing it?

Be direct — flag problems, don't just validate.

[paste spec]
```

---

## 3. Спецификация → Тесты

Запускайте после ревью и одобрения спецификации. Тесты выводятся напрямую из AC. Никаких догадок, никакого расширения объёма.

Specter читает аннотации тестов из двух мест:

- **Комментарии к исходнику**: `// @spec <id>` и `// @ac AC-NN` над тестом. Читает `specter coverage`.
- **Заголовок теста или лог выполнения**: пара `<spec-id>/AC-NN`, видимая в выводе раннера тестов. Читает `specter ingest`. Требуется для `specter coverage --strict`.

Только комментарии к исходнику: `coverage` их учитывает, `--strict` понижает. Пишите обе формы.

Полные правила, примеры по раннерам, параметризованные тесты и устранение неполадок: см. [`TEST_ANNOTATION_REFERENCE.ru.md`](TEST_ANNOTATION_REFERENCE.ru.md).

```
Using this Specter spec as the contract, write [Go/Python/TypeScript] tests
for every acceptance criterion.

Rules:
- One test function per AC. No multi-AC tests — each test runner entry
  maps to one (spec, AC) pair under --strict.
- The test title carries [spec-id/AC-NN]:
    TypeScript:  it('[spec-id/AC-NN] brief description', () => { ... })
    Python:      def test_spec_id_AC_NN_brief_description(...): ...
    Go:          t.Run("spec-id/AC-NN brief description", func(t *testing.T) { ... })
  AC-NN is zero-padded: AC-01, not AC-1. Spec-id and AC-NN match the spec.
- Add source comments above the test function:
    // @spec [spec-id]
    // @ac [AC-NN]
- Tests are executable. No pseudocode, no TODOs.
- Cover happy path and error cases from the spec.
- Do not test anything outside the spec.

[paste spec]
```

**Альтернативная форма — лог выполнения.** Когда переименовать заголовки нельзя (общие соглашения об именовании, snapshot-тесты, внешние контракты), выводите пару во время выполнения из тела теста:

```typescript
test('rejects zero amount', () => {
  console.log('// @spec payment-charge');
  console.log('// @ac AC-03');
  // assertions
});
```
```go
func TestCharge_ZeroAmount(t *testing.T) {
    t.Log("// @spec payment-charge")
    t.Log("// @ac AC-03")
    // assertions
}
```

Выберите одну форму на файл. Не смешивайте формы «заголовок» и «лог выполнения» в одном файле.

---

## 4. Спецификация → Реализация

ИИ реализует по спецификации как по контракту. Тесты уже существуют и определяют, что значит «готово».

```
Implement [module name] using this Specter spec as the contract.

Rules:
- Every C-NN constraint must be satisfied — do not skip or soften any
- Do not add behavior not described in the spec
- If the spec is ambiguous on something, ask before assuming
- The tests already exist — your implementation must make them pass

[paste spec]
```

---

## 5. Очистка спецификации, полученной обратной компиляцией

После запуска `specter reverse` на существующей кодовой базе используйте это, чтобы превратить сырые извлечённые черновики в осмысленные спецификации, достойные одобрения.

```
I ran `specter reverse` on my codebase. These are draft specs extracted from
existing code. Improve them:

- Replace `gap: true` ACs with real descriptions based on the constraints
- Improve the objective summary to describe intent, not just structure
- Make constraint descriptions precise using MUST / MUST NOT language
- Suggest the correct tier (1/2/3) based on what the module does
- Remove placeholder text like "auto-generated placeholder"
- Keep status: draft — I will promote to approved after review

[paste specs]
```

---

## 6. Полный цикл (новая функция от начала до конца)

Когда вы хотите пройти весь процесс за одну сессию. Пауза после шага 1 не обсуждается — никогда не позволяйте ИИ писать тесты или код по непроверенной спецификации.

```
I want to build [feature]. My intent:

[brief description]
[key constraints]
[non-obvious decisions]

Do the following in order:
1. Write a complete `.spec.yaml` (status: draft).
2. Write [language] tests for every AC. One test per AC. Test title carries
   `[spec-id/AC-NN]`. Add `// @spec` and `// @ac` comments above the test.
   See section 3 for the exact form.
3. Implement the feature so the tests pass.

After step 1, pause and show me the spec. I will review it before you proceed
to step 2. Do not write tests or code until I approve the spec.
```

---

## Порядок важен

Эти промпты следуют циклу SDD последовательно:

```
Intent → Spec → [Review] → Tests → Implementation → specter sync
```

Пропуск этапа ревью уничтожает смысл. Спецификация — место, где зафиксирован ваш замысел; если ИИ что-то понял неверно, это самое дешёвое место, чтобы это поймать.

Запустите `specter sync` после этапа реализации. Если он проходит, функция готова. Если падает, спецификация точно говорит, чего не хватает.
