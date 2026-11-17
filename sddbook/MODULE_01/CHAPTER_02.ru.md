# Глава 2: Единый источник истины (SSOT)

## МОДУЛЬ 01 — Основы: мышление «контрактами»

---

### Вступление к лекции

*С возвращением. В прошлый раз мы говорили о том, почему естественный язык не годится как среда для спецификаций и как отрасль эволюционировала от vibe coding к разработке через спецификации. Сегодня мы займёмся тем, что я считаю самым важным архитектурным решением в SDD: утверждением спецификации в роли единого источника истины.*

*Поначалу эта концепция может показаться абстрактной. «Источник истины» — одна из тех фраз, которые так часто бросают в инженерии, что она отчасти потеряла смысл. Поэтому позвольте мне быть очень точным в том, что я имею в виду и почему это важно.*

*Доставайте тетради. Это глава, где философия становится архитектурой.*

---

## 2.1 Что на самом деле означает «источник истины»

В любой системе, где одна и та же информация существует в нескольких местах, есть потенциал конфликта. База данных говорит, что имя пользователя — «Alice». Кеш говорит «Alce» (устаревшая запись с опечаткой). UI показывает «Alice Smith», потому что соединил имя из кеша со свежей фамилией. Что верно?

Ответ зависит от того, что является **источником истины.** Если источник истины — база данных, то база всегда права, а всё остальное — производные, которые нужно обновлять под неё. Если кеш расходится с базой, кеш неверен.

Это фундаментальное понятие в архитектуре ПО, и оно напрямую применимо к отношению спецификаций и кода в SDD:

> **Файл `.spec` — источник истины. Файл `.code` — производная.**

Это значит:

- Когда спецификация и код расходятся, **права спецификация, а код неверен.**
- Когда вы хотите понять, что делает функция, **читайте спецификацию, а не код.**
- Когда вы хотите изменить функцию, **сначала меняйте спецификацию, затем перегенерируйте или обновите код.**
- Когда вы хотите проверить функцию, **сначала проверьте спецификацию на правильность замысла, затем код на правильность реализации.**

Это глубокий сдвиг в том, как большинство разработчиков думает о своей кодовой базе. Десятилетиями код был высшей инстанцией. «Читай исходники» — один из старейших советов в программировании. Документация вечно устарела. Комментарии лгут. Код — единственное, что говорит, что программа *на самом деле делает.*

SDD не спорит с тем, что код говорит, что программа делает. Он вводит различие:

- **Код говорит вам, ЧТО программа делает.** (реализация)
- **Спецификация говорит, что программа ДОЛЖНА делать.** (замысел)

Оба нужны. Ни одного не достаточно в одиночку. Но когда они конфликтуют, управляет замысел. Спецификация — авторитет.

> **Заметка профессора:** Я знаю, о чём думают некоторые: «Но ведь код — это то, что реально выполняется. Спецификация — просто документ. Как документ может быть авторитетнее работающего софта?» Вот как: код — *перевод* спецификации. Если перевод неверен, вы исправляете перевод, а не исходный текст. Если французский перевод романа меняет финал, вы не говорите: «Ну, французская версия — это то, что реально напечатали, значит, это и есть настоящий финал». Вы говорите, что переводчик ошибся. Спецификация — роман. Код — перевод.

---

## 2.2 Отношение спецификации и кода

Формализую отношение между спецификациями и кодом. Понимание этого отношения необходимо для всего остального в SDD.

### Спецификация — это «что и почему»

Спецификация отвечает на вопросы:

- **Что** должен делать этот компонент/функция/модуль?
- **Почему** он существует? Какую проблему решает?
- **Каковы** ограничения и границы?
- **Каковы** критерии приёмки?
- **Каков** контекст, в котором он работает?

Спецификация намеренно НЕ отвечает:

- **Как** должна быть реализована функция?
- Какие конкретные алгоритмы использовать?
- Какие имена переменных выбрать?
- Как код должен быть устроен внутри?

### Код — это «как»

Код отвечает на вопросы:

- **Как** достигается заданное поведение?
- Какие структуры данных используются?
- Каков поток управления?
- Как обрабатываются крайние случаи на уровне реализации?

Код НЕ должен содержать:

- Информацию о том, *почему* были приняты проектные решения
- Бизнес-контекст, не очевидный из самого кода
- Ограничения, которые не обеспечиваются механически

### Конкретный пример

Покажу это отношение на реальном примере. Вот спецификация функции поиска:

```yaml
# search-bar.spec.yaml
kind: Component
metadata:
  name: SearchBar
  module: search
  version: 1.2.0

context:
  description: >
    The application has a product catalog with ~50,000 items.
    The existing search API is at GET /api/search?q={query}&limit={n}.
    The API supports debouncing on the server side but we want
    client-side debouncing to reduce unnecessary network requests.
    Current implementation has no search — users browse by category only.

objective:
  summary: >
    Add a search bar to the main navigation that provides real-time
    search suggestions as the user types.
  acceptance_criteria:
    - Search input is always visible in the top navigation bar
    - Suggestions appear after the user has typed at least 2 characters
    - Suggestions are debounced at 300ms to avoid excessive API calls
    - Maximum of 8 suggestions displayed at a time
    - Each suggestion shows product name and category
    - Clicking a suggestion navigates to the product detail page
    - Pressing Enter searches with the full query text
    - Pressing Escape closes the suggestion dropdown
    - The search bar is accessible (ARIA combobox pattern)

constraints:
  - MUST debounce on the client side at 300ms minimum
  - MUST NOT make API calls for queries shorter than 2 characters
  - MUST NOT display more than 8 suggestions
  - MUST cancel in-flight requests when a new query is typed
  - MUST handle API errors gracefully (no uncaught exceptions)
  - MUST NOT block the main thread during search
```

А вот как может выглядеть сгенерированный код (упрощённо):

```typescript
// SearchBar.tsx — Generated from search-bar.spec.yaml v1.2.0

import { useState, useCallback, useRef, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useDebounce } from "@/hooks/useDebounce";
import { searchProducts } from "@/api/search";

interface SearchSuggestion {
  id: string;
  name: string;
  category: string;
}

export function SearchBar() {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  // Debounce at 300ms per spec constraint
  const debouncedQuery = useDebounce(query, 300);

  // Only search when query is 2+ characters per spec constraint
  const shouldSearch = debouncedQuery.length >= 2;

  const { data: suggestions = [], isError } = useQuery({
    queryKey: ["search", debouncedQuery],
    queryFn: () => searchProducts(debouncedQuery, 8), // max 8 per spec
    enabled: shouldSearch,
    staleTime: 60_000,
  });

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      switch (e.key) {
        case "Escape":
          setIsOpen(false);
          inputRef.current?.blur();
          break;
        case "Enter":
          if (activeIndex >= 0 && suggestions[activeIndex]) {
            navigate(`/products/${suggestions[activeIndex].id}`);
          } else if (query.length >= 2) {
            navigate(`/search?q=${encodeURIComponent(query)}`);
          }
          setIsOpen(false);
          break;
        case "ArrowDown":
          e.preventDefault();
          setActiveIndex((prev) =>
            prev < suggestions.length - 1 ? prev + 1 : prev
          );
          break;
        case "ArrowUp":
          e.preventDefault();
          setActiveIndex((prev) => (prev > 0 ? prev - 1 : -1));
          break;
      }
    },
    [activeIndex, suggestions, query, navigate]
  );

  return (
    <div role="combobox" aria-expanded={isOpen} aria-haspopup="listbox">
      <input
        ref={inputRef}
        type="search"
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setIsOpen(true);
          setActiveIndex(-1);
        }}
        onFocus={() => shouldSearch && setIsOpen(true)}
        onKeyDown={handleKeyDown}
        aria-autocomplete="list"
        aria-controls="search-suggestions"
        aria-activedescendant={
          activeIndex >= 0 ? `suggestion-${activeIndex}` : undefined
        }
        placeholder="Search products..."
      />
      {isOpen && shouldSearch && !isError && suggestions.length > 0 && (
        <ul id="search-suggestions" role="listbox">
          {suggestions.map((item, index) => (
            <li
              key={item.id}
              id={`suggestion-${index}`}
              role="option"
              aria-selected={index === activeIndex}
              onClick={() => {
                navigate(`/products/${item.id}`);
                setIsOpen(false);
              }}
            >
              <span>{item.name}</span>
              <span>{item.category}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

Теперь посмотрите на отношение спецификации и кода:

| Спецификация говорит | Код реализует |
|---|---|
| «debounced at 300ms» | `useDebounce(query, 300)` |
| «at least 2 characters» | `debouncedQuery.length >= 2` |
| «Maximum of 8 suggestions» | `searchProducts(debouncedQuery, 8)` |
| «Pressing Escape closes» | `case "Escape": setIsOpen(false)` |
| «ARIA combobox pattern» | `role="combobox"`, `aria-expanded` и т.д. |
| «Cancel in-flight requests» | React Query делает это автоматически |

Каждая строка кода прослеживается к требованию спецификации. У каждого требования есть соответствующая реализация. Эта прослеживаемость — отличительная черта кода, управляемого спецификацией.

---

## 2.3 Почему не использовать код как источник истины?

Это самое частое возражение, которое я слышу от опытных разработчиков, и оно заслуживает обстоятельного ответа.

Аргумент звучит так: «Код уже точен. Код уже структурирован. Код уже версионируется. Зачем добавлять ещё один слой? Почему не использовать сам код как источник истины?»

Вот пять причин.

### Причина 1: код фиксирует «как», а не «почему»

Посмотрите на эту строку:

```typescript
const debouncedQuery = useDebounce(query, 300);
```

Код говорит, что интервал дебаунса — 300 мс. Но он не говорит, *почему* 300 мс. Потому что это UX-стандарт? Потому что бэкенд не выдерживает больше 3 запросов в секунду? Потому что тестирование показало, что короткие интервалы ощущаются «дёргаными»? Потому что у API есть ограничение частоты?

Спецификация фиксирует этот контекст:

```yaml
constraints:
  - MUST debounce on the client side at 300ms minimum
  # Rationale: Our API rate limit is 10 req/s per user.
  # With 300ms debounce, even fast typists generate at most
  # ~3 req/s, leaving headroom for other API calls.
```

Когда будущий разработчик задастся вопросом «могу ли я уменьшить до 100 мс?», код не даст ответа. Спецификация скажет точно, почему выбрано это значение и что сломается, если его изменить.

### Причина 2: код не может выразить замысел о том, чего НЕТ

Одна из самых мощных возможностей спецификации — выражать то, чего не должно происходить и что не входит в объём. Код этого не может. Код может выразить только то, что ЕСТЬ.

Рассмотрим такой раздел:

```yaml
constraints:
  - MUST NOT store search queries in localStorage
  - MUST NOT send search queries to analytics without user consent
  - MUST NOT cache search results across sessions

scope:
  excludes:
    - Search history / recent searches feature
    - Voice search
    - Image search
    - Search filters / faceted search
```

Ни одна из этих сведений не может существовать в коде. Невозможно написать код, который говорит: «Я намеренно решил не реализовывать историю поиска». Отсутствие функции в коде неотличимо от того, что функцию не рассматривали.

> **Заметка профессора:** Этот момент тонок, но глубок. В коде отсутствие неоднозначно. Функции может не быть потому, что её намеренно исключили, потому что забыли, потому что планируют позже, или потому что ИИ не попросили её включить. В спецификации отсутствие в `includes` и присутствие в `excludes` *значимо*. Оно сообщает: «мы подумали об этом и решили не делать». Это информация, которую код буквально не может выразить.

### Причина 3: код слишком детален для проверки замысла

Представьте, что вы рецензируете pull request с новой функцией. В PR 500 строк TypeScript. Чтобы понять замысел разработчика, нужно:

1. Прочитать все 500 строк
2. Построить мысленную модель того, что делает код
3. Вывести замысел разработчика из реализации
4. Определить, соответствует ли реализация вашему пониманию требований
5. Выявить, не упущено ли что-то (самая трудная часть)

Теперь представьте, что в том же PR есть спецификация на 50 строк. Вы читаете спецификацию первой. Понимаете замысел за две минуты. Теперь, читая код, вы *проверяете реализацию на соответствие замыслу* — гораздо более простая когнитивная задача, чем выводить замысел из реализации.

Спецификации делают код-ревью быстрее и эффективнее, разделяя вопрос «это правильная вещь?» и вопрос «это сделано правильно?».

### Причина 4: код зависит от модели; спецификации не зависят

Практическое соображение. Если вы сгенерировали код с Claude 3.5 Sonnet, а завтра хотите использовать GPT-4o, Gemini 2 Flash или последнюю модель Llama, ваш код привязан к шаблонам и конвенциям, которые выбрал Claude. А спецификация — нет.

Спецификация — не зависящее от модели описание того, что вы хотите. Вы можете передать ту же спецификацию любой модели ИИ (или человеку-разработчику) и получить соответствующую реализацию. Спецификация отделяет ваш *замысел* от конкретного *инструмента реализации.*

Это не теория. Команды регулярно переключаются между моделями ИИ с выходом новых версий. Команды со спецификациями переключаются легко — просто перегенерируют из спецификации. Команды без спецификаций застряли с тем, что выдала предыдущая модель.

### Причина 5: код не может управлять валидацией

Спецификация содержит проверяемые критерии приёмки:

```yaml
acceptance_criteria:
  - Suggestions appear after the user has typed at least 2 characters
  - Suggestions are debounced at 300ms
  - Maximum of 8 suggestions displayed
```

Эти критерии можно механически превратить в тесты. Более того, один из самых мощных процессов SDD — заставить ИИ сгенерировать тесты *из спецификации* до генерации реализации, гарантируя, что тесты управляются замыслом, а не реализацией.

Сам по себе код можно тестировать только против самого себя. Вы можете проверить, что функции возвращают то, что возвращают. Но вы не можете проверить, что они возвращают то, что *должны*, без внешнего определения «должны». Спецификация даёт это внешнее определение.

---

## 2.4 Принцип SSOT в отрасли

Идея, что структурированные авторитетные документы должны управлять кодом, не нова. SDD опирается на долгую линию инженерных практик. Проследим ключевые влияния.

### Проектные документы Google

Инженерная культура Google давно требует дизайн-документов до реализации. Дизайн-документ Google обычно содержит:

- **Контекст:** какую проблему решаем? Каково текущее состояние?
- **Цели и не-цели:** чего достигнет проект и что явно вне объёма?
- **Дизайн:** как система будет работать на высоком уровне?
- **Рассмотренные альтернативы:** какие подходы оценивались и почему отвергнуты?
- **Соображения безопасности/приватности:** каковы последствия?

Знакомо? Структура дизайн-документа Google почти напрямую отображается на спецификацию SDD:

| Дизайн-документ Google | Спецификация SDD |
|---|---|
| Контекст | раздел `context` |
| Цели | `objective.acceptance_criteria` |
| Не-цели | `scope.excludes`, `constraints` |
| Дизайн | Намеренно опущен (оставлен реализации) |
| Рассмотренные альтернативы | Необязательный раздел `rationale` |

Ключевое различие: дизайн-документ Google — одноразовый артефакт: его пишут, рецензируют, а затем он часто устаревает по мере расхождения с реализацией. Спецификация SDD — *живой* артефакт: она поддерживается вместе с кодом и обновляется при изменении требований.

Команда Gemini и DeepMind в Google, по сообщениям, распространили концепцию дизайн-документа на процессы ИИ-разработки, используя структурированные документы для управления генерацией кода внутренними инструментами. Шаблон ясен: когда ИИ генерирует код, нужен формальный документ, управляющий тем, что генерируется.

### Конституционный ИИ Anthropic

Подход Anthropic к безопасности ИИ даёт увлекательную параллель. В конституционном ИИ поведение модели управляется набором явных принципов — «конституцией», — которая определяет, что модель должна и не должна делать. Модель обучается следовать этим принципам, и принципы служат источником истины для оценки правильности поведения модели.

Это структурно идентично тому, как спецификация управляет кодом в SDD:

| Конституционный ИИ | SDD |
|---|---|
| Конституция | Спецификация |
| Поведение модели | Сгенерированный код |
| Оценка принципов | Валидация критериев приёмки |
| Red-teaming | Тестирование ограничений |

Конституция — источник истины для поведения модели, как спецификация — источник истины для поведения кода. Когда модель нарушает конституционный принцип, конституция не ошибается — ошибается модель. Когда сгенерированный код нарушает ограничение спецификации, спецификация не ошибается — ошибается код.

Системные промпты Claude от Anthropic — ещё одно проявление этого принципа. Системный промпт — спецификация того, как модель должна вести себя в данном контексте. Он источник истины для этого взаимодействия. Ответы модели — производные от системного промпта, оцениваемые против него.

> **Заметка профессора:** Оцените элегантность этой параллели. Anthropic использует спецификации (конституции, системные промпты) для управления поведением ИИ. Мы используем спецификации (SDD-спеки) для управления сгенерированным ИИ кодом. Принцип одинаков на обоих уровнях: явные структурированные декларации замысла дают более надёжные результаты, чем неявные ожидания.

### API OpenAI на основе схем

Эволюция OpenAI к структурированным выводам — ещё одно проявление принципа SSOT. Когда вы определяете JSON Schema для структурированных выводов:

```typescript
const schema = {
  type: "object",
  properties: {
    name: { type: "string" },
    age: { type: "number", minimum: 0 },
    email: { type: "string", format: "email" }
  },
  required: ["name", "email"],
  additionalProperties: false
};
```

Схема — источник истины. Вывод модели должен ей соответствовать. Если вывод не соответствует схеме, неверен вывод, а не схема.

Определения вызова функций OpenAI работают так же. Схема функции — источник истины для того, как модель должна вызывать функцию. Вызов функции моделью — производная от схемы. Если вызов не соответствует схеме, неверен вызов.

Это SSOT на уровне API. SDD распространяет тот же принцип на уровень приложения.

---

## 2.5 Файл спецификации и файл кода: практическая архитектура

Конкретизирую, как спецификации и код сосуществуют в проекте.

### Структура файлов

Типичный SDD-проект имеет параллельную структуру, где у каждого файла кода есть соответствующий файл спецификации:

```
project/
  specs/
    system.spec.yaml           # Global system context
    features/
      auth/
        login.spec.yaml        # Spec for login feature
        signup.spec.yaml       # Spec for signup feature
        password-reset.spec.yaml
      search/
        search-bar.spec.yaml   # Spec for search bar
        search-results.spec.yaml
      users/
        user-list.spec.yaml
        user-profile.spec.yaml
  src/
    features/
      auth/
        components/
          LoginForm.tsx         # Code generated from login.spec.yaml
          SignupForm.tsx
          PasswordResetForm.tsx
        hooks/
          useLogin.ts
          useSignup.ts
      search/
        components/
          SearchBar.tsx         # Code generated from search-bar.spec.yaml
          SearchResults.tsx
        hooks/
          useSearch.ts
      users/
        components/
          UserList.tsx
          UserProfile.tsx
```

### Системная спецификация

`system.spec.yaml` — особая спецификация, дающая глобальный контекст. Она не генерирует код напрямую. Вместо этого на неё ссылается каждая спецификация функции. Думайте о ней как о «конституции» всего приложения:

```yaml
# system.spec.yaml
kind: SystemContext
metadata:
  name: acme-saas
  version: 3.1.0
  updated: 2026-02-15

technology:
  language: TypeScript 5.4
  runtime: Node.js 22 LTS
  framework: React 19
  styling: Tailwind CSS 4.0
  state:
    global: Zustand 5
    server: "@tanstack/react-query v5"
    forms: "React Hook Form v7"
  routing: "React Router v7"
  testing:
    unit: Vitest 2
    component: React Testing Library
    e2e: Playwright

architecture:
  pattern: Feature-based modules
  api_style: REST with OpenAPI 3.1 schemas
  authentication: JWT with httpOnly cookies
  authorization: Role-based (RBAC)

conventions:
  naming:
    components: PascalCase
    hooks: camelCase with "use" prefix
    files: kebab-case
    types: PascalCase with no "I" prefix
  error_handling: >
    All API errors are caught by React Query.
    Components display ErrorBanner for fetch failures.
    Form validation errors are handled by React Hook Form.
    Unexpected errors are caught by ErrorBoundary at route level.
  data_fetching: >
    All server data access goes through React Query hooks.
    Custom hooks are in /features/{domain}/hooks/.
    No direct fetch() calls in components.
  accessibility: >
    All interactive components meet WCAG 2.1 AA.
    Use semantic HTML elements. No div-based buttons.
    All images have alt text. All form inputs have labels.

security:
  - All user input is sanitized before rendering (DOMPurify)
  - No dangerouslySetInnerHTML without explicit spec approval
  - All API calls include CSRF token from cookie
  - No sensitive data in localStorage (use httpOnly cookies)
  - No console.log in production builds
```

Эта системная спецификация отвечает на вопросы, которые иначе пришлось бы повторять в каждой спецификации функции: каков технологический стек? Каковы конвенции? Каковы глобальные ограничения? Вынеся это в общий документ, мы обеспечиваем согласованность всего приложения.

### Спецификация функции

Спецификация функции ссылается на системную спецификацию и добавляет контекст, цели и ограничения конкретной функции:

```yaml
# login.spec.yaml
kind: Feature
metadata:
  name: Login
  module: auth
  version: 2.0.0
  system_spec: system.spec.yaml@3.1.0

context:
  description: >
    The application currently has a JWT-based authentication system.
    The login API endpoint is POST /api/auth/login, which accepts
    { email, password } and returns { accessToken, refreshToken }.
    Tokens are set as httpOnly cookies by the API (not returned in body).
    The current login page is a basic form with no OAuth support.
    This spec adds OAuth support while maintaining email/password login.
  related_specs:
    - signup.spec.yaml  # Signup flow shares the auth layout
    - password-reset.spec.yaml  # Linked from login form

objective:
  summary: >
    Enhance the login page to support OAuth (Google, GitHub) alongside
    existing email/password authentication.
  acceptance_criteria:
    - Email/password login continues to work as before
    - Google OAuth button initiates Google OAuth flow
    - GitHub OAuth button initiates GitHub OAuth flow
    - OAuth callback handles success and error states
    - Failed login shows specific error message (not generic)
    - Successful login redirects to the page the user came from
    - Login form validates email format and password presence
    - Rate limiting feedback shown after 5 failed attempts

constraints:
  - MUST NOT store OAuth tokens on the client
  - MUST NOT send credentials over non-HTTPS connections
  - MUST NOT expose error details that reveal whether email exists
  - MUST use the existing AuthLayout component for page structure
  - MUST use React Hook Form for form handling (per system spec)
  - OAuth popup MUST close automatically after callback

testing:
  unit:
    - Email/password form validates required fields
    - Form submits correctly formatted data to API
    - Error messages display for invalid credentials
    - Rate limit message appears after 5 failures
  integration:
    - Google OAuth flow completes successfully
    - GitHub OAuth flow completes successfully
    - Redirect after login goes to original destination
  accessibility:
    - Form navigable by keyboard alone
    - Error messages announced by screen readers
    - OAuth buttons have descriptive labels
```

Обратите внимание, как спецификация функции ссылается на системную спецификацию (`system_spec: system.spec.yaml@3.1.0`). Это создаёт формальную цепочку зависимостей. ИИ, генерируя код из этой спецификации, должен также прочитать системную спецификацию, чтобы понять глобальные конвенции.

---

## 2.6 Контроль версий спецификаций и контроль версий кода

Один вопрос возникает сразу, как только вы начинаете относиться к спецификациям как к инженерным артефактам: как их версионировать?

Ответ: так же, как код. Спецификации живут в том же репозитории, что и код, которым управляют. Их коммитят, ветвят, сливают и рецензируют в том же Git-процессе.

Но есть важные нюансы.

### Изменения спецификации предшествуют изменениям кода

В типичном процессе SDD изменение начинается с правки спецификации:

```
1. Developer modifies the spec (e.g., adds a new acceptance criterion)
2. Spec change is reviewed (PR review)
3. After spec is approved, code is regenerated or updated
4. Code change is reviewed (PR review)
5. Both spec and code changes are merged together
```

Это значит, что изменения спецификации и кода обычно в одном коммите или PR. Вы видите diff спецификации рядом с diff кода, и ясно, *почему* код изменился.

### У спецификации своя версия

Каждая спецификация включает номер версии в метаданных:

```yaml
metadata:
  name: SearchBar
  version: 1.2.0
```

Эта версия не зависит от хеша Git-коммита. Она представляет *семантическую версию* самой спецификации:

- **Мажорная версия** (1.x.x → 2.0.0): ломающее изменение поведения или API функции
- **Минорная версия** (1.2.x → 1.3.0): новая возможность функции
- **Патч** (1.2.0 → 1.2.1): уточнение или исправление, не меняющее поведение

Сгенерированный код должен ссылаться на версию спецификации, из которой он создан:

```typescript
// SearchBar.tsx — Generated from search-bar.spec.yaml v1.2.0
```

Это создаёт прослеживаемость. Если вы найдёте баг, можно проверить, из какой версии спецификации сгенерирован код и обновлялась ли спецификация с тех пор.

### Diff спецификаций

Один из самых мощных аспектов версионируемых спецификаций — возможность их *сравнивать*. Diff спецификации говорит вам человекочитаемо, что именно изменилось в требованиях к функции:

```diff
  acceptance_criteria:
    - Search input is always visible in the top navigation bar
    - Suggestions appear after the user has typed at least 2 characters
-   - Suggestions are debounced at 300ms
+   - Suggestions are debounced at 200ms
    - Maximum of 8 suggestions displayed at a time
+   - Suggestions are grouped by category
+   - Each group shows a maximum of 3 suggestions
    - Each suggestion shows product name and category
```

Сравните это с попыткой понять diff кода, который меняет интервал дебаунса, перестраивает отрисовку подсказок, добавляет группировку по категориям и меняет вызов API — всё в 200-строчном diff на TypeScript. Diff спецификации немедленно передаёт *замысел* изменения. Diff кода показывает *реализацию* изменения.

> **Заметка профессора:** Это одна из вещей, которые я люблю в SDD на практике. Diff спецификаций *читаем.* Он рассказывает историю. «Мы уменьшили дебаунс до 200 мс и добавили группировку по категориям». Вы можете прочитать diff спецификации и понять изменение за секунды. Diff кода, напротив, часто требует глубокого чтения, чтобы понять, что и почему изменилось. Diff спецификации — исполнительное резюме; diff кода — подробный отчёт.

---

## 2.7 Что происходит, когда спецификация и код расходятся

Расхождение — рак SSOT. Оно случается, когда код перестаёт соответствовать спецификации. И оно будет случаться. Вот частые причины и как с ними справляться.

### Причина 1: кто-то правит код, не обновляя спецификацию

Самая частая причина расхождения, и обычно по понятным причинам. Разработчик находит баг. Исправление простое — изменить одну строку. Он правит код, коммитит и идёт дальше. Спецификацию не обновляет.

Теперь код делает то, чего спецификация не описывает. Спецификация говорит, дебаунс 300 мс. Код говорит 250 мс, потому что кто-то обнаружил, что 300 мс на мобильном ощущаются вяло. Спецификация теперь неточна.

**Предотвращение:**

1. **Дисциплина код-ревью.** Каждый PR, меняющий код под управлением спецификации, должен также менять спецификацию, если поведение меняется. Это должен быть обязательный пункт чек-листа в шаблоне PR.

2. **Проверки синхронизации спецификации и кода.** Автоматические проверки в CI, сравнивающие версию спецификации, указанную в коде, с последней версией спецификации. Если они расходятся, проверка падает.

3. **Комментарии в сгенерированном коде.** Включайте в файлы сгенерированного кода комментарий с версией спецификации:

```typescript
/**
 * @generated from search-bar.spec.yaml v1.2.0
 * @warning Manual edits to this file will diverge from the spec.
 * Update the spec and regenerate instead.
 */
```

### Причина 2: спецификация обновлена, но код не перегенерирован

Продакт-менеджер обновляет спецификацию, добавляя новое требование. Спецификация слита. Но никто не перегенерировал код и не обновил реализацию.

**Предотвращение:**

1. **Изменение спецификации порождает задачу на код.** В вашем процессе управления проектом изменение спецификации автоматически создаёт задачу обновить соответствующий код.

2. **Валидация в CI.** Шаг CI, сравнивающий версию спецификации с версией, встроенной в сгенерированный код. Если спецификация новее, сборка предупреждает (или падает).

3. **Автоматизация процесса.** Некоторые команды автоматизируют это: когда файл спецификации меняется в PR, задача CI перегенерирует код и добавляет его в PR автоматически.

### Причина 3: ИИ генерирует код, не соответствующий спецификации

Иногда ИИ ошибается. Несмотря на ясную спецификацию, сгенерированный код не выполняет все критерии приёмки. Может, упускает крайний случай. Может, использует не ту библиотеку. Может, частично реализует ограничение.

**Предотвращение:**

1. **Тесты из спецификации.** Генерируйте тесты из спецификации *до* генерации реализации. Тесты кодифицируют требования как исполняемые проверки. Если сгенерированный код не проходит тесты, вы сразу об этом узнаете.

2. **Критерии приёмки как чек-лист.** После генерации кода механически пройдитесь по каждому критерию и проверьте, что код его покрывает.

3. **Проверка ограничений.** Для каждого ограничения в спецификации проверьте, что код либо обеспечивает его, либо делает его обеспечиваемым через конфигурацию.

Вот как тестирование из спецификации выглядит на практике:

```typescript
// SearchBar.test.tsx — Generated from search-bar.spec.yaml v1.2.0

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SearchBar } from "./SearchBar";
import { server } from "@/test/mocks/server";
import { http, HttpResponse } from "msw";

// Acceptance Criterion: "Suggestions appear after the user has
// typed at least 2 characters"
describe("minimum query length", () => {
  it("does not show suggestions for single character input", async () => {
    const user = userEvent.setup();
    render(<SearchBar />);

    await user.type(screen.getByRole("searchbox"), "a");

    await waitFor(() => {
      expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
    });
  });

  it("shows suggestions for two character input", async () => {
    const user = userEvent.setup();
    render(<SearchBar />);

    await user.type(screen.getByRole("searchbox"), "ab");

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument();
    });
  });
});

// Constraint: "MUST NOT display more than 8 suggestions"
describe("suggestion limit", () => {
  it("displays at most 8 suggestions even when API returns more", async () => {
    server.use(
      http.get("/api/search", () => {
        return HttpResponse.json({
          results: Array.from({ length: 15 }, (_, i) => ({
            id: String(i),
            name: `Product ${i}`,
            category: "Test",
          })),
        });
      })
    );

    const user = userEvent.setup();
    render(<SearchBar />);

    await user.type(screen.getByRole("searchbox"), "test");

    await waitFor(() => {
      const options = screen.getAllByRole("option");
      expect(options.length).toBeLessThanOrEqual(8);
    });
  });
});

// Constraint: "MUST NOT make API calls for queries shorter
// than 2 characters"
describe("API call prevention", () => {
  it("does not call search API for single character queries", async () => {
    let apiCallCount = 0;
    server.use(
      http.get("/api/search", () => {
        apiCallCount++;
        return HttpResponse.json({ results: [] });
      })
    );

    const user = userEvent.setup();
    render(<SearchBar />);

    await user.type(screen.getByRole("searchbox"), "a");

    // Wait enough time for a debounced request to fire
    await new Promise((r) => setTimeout(r, 500));

    expect(apiCallCount).toBe(0);
  });
});
```

Обратите внимание, как каждый тест аннотирован требованием спецификации, которое проверяет. Это создаёт прямую прослеживаемую связь «спецификация → тест → код». Если тест падает, вы точно знаете, какое требование не выполнено. Если требование меняется, вы точно знаете, какие тесты обновить.

---

## 2.8 Спецификация как слой коммуникации

Хочу отойти назад и поговорить о роли спецификации в коммуникации команды.

В традиционной разработке цепочка коммуникации выглядит так:

```
Product Manager → (conversation/ticket) → Developer → (code) → Reviewer
```

На шаге «разговор/тикет» теряется замысел. Тикеты Jira пишутся прозой. Разговоры эфемерны. К моменту, когда рецензент видит код, исходный замысел прошёл через два перевода (PM → разработчик, разработчик → код).

В SDD цепочка выглядит так:

```
Product Manager → Spec ← Developer → Code ← Reviewer
```

Спецификация — *общий артефакт*, в который вносят вклад и PM, и разработчик. PM определяет цели и ограничения. Разработчик добавляет технический контекст и критерии проверки. Рецензент читает спецификацию, чтобы понять замысел, и код, чтобы проверить реализацию.

У этого несколько преимуществ:

### Преимущество 1: PM может рецензировать спецификации

Продакт-менеджеры обычно не квалифицированы рецензировать код TypeScript. Но вполне квалифицированы рецензировать спецификацию. Они могут проверить, что критерии приёмки соответствуют их замыслу. Могут проверить правильность ограничений. Могут валидировать объём.

```yaml
# A PM can read this and verify it matches their intent:
acceptance_criteria:
  - Search input is always visible in the top navigation bar
  - Suggestions appear after the user has typed at least 2 characters
  - Maximum of 8 suggestions displayed at a time
```

Это огромное улучшение по сравнению с традиционным процессом, где PM пишет тикет, разработчик его интерпретирует, а PM видит результат в staging через дни или недели.

### Преимущество 2: новые члены команды быстрее входят в курс

Когда новый разработчик приходит в команду, он может прочитать спецификации, чтобы понять, что делает каждая функция и почему. Спецификации читабельнее кода, актуальнее документации (потому что поддерживаются как часть процесса разработки) и структурированнее историй чатов или заметок встреч.

### Преимущество 3: ИИ становится членом команды

Тонкий, но важный момент: спецификация делает ИИ предсказуемым членом команды.

Без спецификаций ИИ — как блестящий, но непредсказуемый подрядчик, который может построить ровно то, что вы хотите, а может уйти в сторону. Вы никогда не знаете, что получите. Каждое взаимодействие — переговоры.

Со спецификациями ИИ — как надёжный подрядчик, работающий по чертежам. Чертёж (спецификация) определяет, что строится. Подрядчик (ИИ) реализует чертёж. Если результат не совпадает с чертежом, вы уточняете чертёж и пробуете снова. Процесс предсказуем, воспроизводим и отлаживаем.

### Преимущество 4: координация между командами

Когда функции A нужно интегрироваться с функцией B, команды могут обмениваться спецификациями, а не кодом. Команда A читает спецификацию команды B, чтобы понять интерфейс. Ей не нужно понимать реализацию команды B.

Это тот же принцип, что и документация API, но применённый ко всей поверхности функции. Спецификация — *контракт* между командами, как схема API — контракт между сервисами.

---

## 2.9 Живая спецификация против мёртвого документа

Хочу ответить на возражение, которое опытные разработчики сейчас кричат про себя:

*«Мы уже это проходили. Это называлось "документы требований". Они всегда были устаревшими. Никто их не поддерживал. Будет то же самое».*

Это закономерная тревога, и её стоит разобрать напрямую.

Традиционные документы требований умерли, потому что существовали *вне* процесса разработки. Их писали в Word или Confluence, отдельно от кода. Обновление требовало переключения инструментов, перехода в другое место, редактирования другого артефакта. Это было трение, и разработчики рационально его избегали.

Спецификации SDD отличаются по нескольким причинам:

### Причина 1: спецификации живут в репозитории

Спецификации в том же Git-репозитории, что и код. В том же PR. Их diff рядом с diff кода. Обновить спецификацию — тот же процесс, что обновить код: отредактировать файл, закоммитить, запушить.

### Причина 2: спецификации функциональны, а не документальны

Документ требований описателен — он описывает, что должно быть построено. Спецификация SDD *функциональна* — она вход для генератора кода ИИ. Если её не поддерживать, из неё нельзя генерировать код. Это создаёт естественный стимул держать её актуальной.

Представьте Dockerfile. Никто не пишет Dockerfile, а потом игнорирует его, потому что Dockerfile — это то, как вы собираете контейнер. Если Dockerfile неверен, сборка падает. Аналогично, если спецификация неверна, генерация кода неверна. У спецификации есть функциональные последствия.

### Причина 3: спецификации валидируются

У традиционных документов требований не было механизма валидации. Никто не мог сказать, точно ли документ описывает систему. У спецификаций, напротив, есть проверяемые критерии приёмки. Вы можете механически проверить, соответствует ли код спецификации.

### Причина 4: спецификации минимальны

Документ требований пытается зафиксировать всё о функции прозой. Спецификация SDD структурирована и сфокусирована: контекст, цель, ограничения, тесты. В ней нет повествования, обоснований, заметок встреч или исторических обсуждений. Она лаконична. Написание занимает минуты, а не часы.

### Причина 5: петля «спецификация — код» короткая

В традиционной разработке петля обратной связи от «изменились требования» до «изменился код» могла составлять недели. В SDD петля — минуты. Вы обновляете спецификацию, перегенерируете код, валидируете. Короткая петля делает практичным поддержание синхронизации.

> **Заметка профессора:** Я видел команды, которые принимали SDD и сначала относились к спецификациям как к «дополнительной работе». Через две недели они единодушно сообщали, что спецификации *экономят* время. Вложения в написание спецификации возвращаются многократно: меньше повторных промптов, меньше времени на код-ревью, меньше времени на онбординг, меньше времени на отладку. Спецификация — не накладные расходы. Это артефакт с максимальным рычагом в вашем процессе разработки.

---

## 2.10 Контракт SSOT: правила взаимодействия

Формализую правила, управляющие отношением SSOT между спецификацией и кодом. Это «правила взаимодействия» для любой SDD-команды.

### Правило 1: спецификация пишется первой

Никакой код не пишется (и не генерируется) без спецификации. Спецификация не обязана быть идеальной — можно начать с черновика и уточнять. Но она должна существовать до начала генерации кода.

### Правило 2: код ссылается на спецификацию

Каждый файл сгенерированного кода включает ссылку на спецификацию, из которой он создан, включая версию:

```typescript
/**
 * @spec search-bar.spec.yaml
 * @spec-version 1.2.0
 * @generated 2026-02-24
 */
```

### Правило 3: изменения спецификации вызывают обновление кода

Когда спецификация изменена, соответствующий код должен быть обновлён. Это можно автоматизировать (перегенерация) или делать вручную (точечные правки), но код должен отражать текущую спецификацию.

### Правило 4: изменения кода могут вызывать обновление спецификации

Если разработчик во время реализации обнаруживает, что спецификация неполна или неверна, он обновляет спецификацию *первой*, затем код. Код не управляет спецификацией, но код может её *информировать.*

### Правило 5: расхождение — это баг

Если код не соответствует спецификации, это баг — независимо от того, «работает» ли код. Функция, которая работает, но не соответствует спецификации, неверна. Правильность определяется спецификацией, а не наблюдаемым поведением.

### Правило 6: тесты валидируют соответствие спецификации

Набор тестов проверяет, что код соответствует спецификации. Тесты выводятся из критериев приёмки и ограничений. Проходящие тесты означают соответствие. Падающие — расхождение.

### Правило 7: спецификации рецензируются

Спецификации проходят ревью так же, как код. PR спецификации рецензируется на ясность, полноту, правильность и согласованность с системной спецификацией. В ревью спецификаций должны участвовать и технические, и продуктовые заинтересованные стороны.

---

## 2.11 Практический процесс: день из жизни

Проведу вас через реалистичный день SDD-разработки, чтобы это стало конкретным.

### Утро: запрос новой функции

PM создаёт черновик спецификации новой функции «избранное». Спецификация включает бизнес-контекст, критерии приёмки и объём:

```yaml
# favorites.spec.yaml (draft)
kind: Feature
metadata:
  name: Favorites
  module: catalog
  version: 0.1.0
  status: draft
  system_spec: system.spec.yaml@3.1.0

context:
  description: >
    Users have been requesting the ability to save products
    for later. Analytics show 60% of users visit the same
    product pages multiple times before purchasing. A favorites
    feature would reduce friction in the purchase funnel.

objective:
  summary: >
    Allow users to mark products as favorites and view a
    list of their favorite products.
  acceptance_criteria:
    - Heart icon on each product card toggles favorite status
    - Favorites are persisted to the user's account
    - A "My Favorites" page shows all favorited products
    - Favorites count shown in the navigation bar
    - Removing a favorite from the list updates immediately (optimistic)
```

### Середина утра: ревью спецификации

Разработчик рецензирует черновик и добавляет технический контекст и ограничения:

```yaml
# favorites.spec.yaml (reviewed)
# ... (previous sections unchanged)

context:
  description: >
    Users have been requesting the ability to save products
    for later. Analytics show 60% of users visit the same
    product pages multiple times before purchasing. A favorites
    feature would reduce friction in the purchase funnel.
  technical_context: >
    The favorites API is being built by the backend team and will
    be available at:
      POST /api/favorites/:productId (add favorite)
      DELETE /api/favorites/:productId (remove favorite)
      GET /api/favorites (list all favorites)
    The API uses the standard auth middleware (JWT from cookie).
    Product cards are rendered by the existing ProductCard component.

constraints:
  - MUST use optimistic updates for toggle (immediate UI feedback)
  - MUST invalidate product list queries when favorites change
  - MUST handle offline/network error gracefully (revert optimistic update)
  - MUST NOT allow unauthenticated users to favorite (show login prompt)
  - MUST limit favorites display to 50 per page with pagination
  - MUST NOT refetch all favorites on every toggle (surgical cache update)

scope:
  excludes:
    - Sharing favorites with other users
    - Organizing favorites into collections/folders
    - Favorites import/export
    - Favorite notifications (e.g., price drop alerts)

testing:
  unit:
    - Heart icon toggles visual state immediately
    - Optimistic update reverts on API error
    - Unauthenticated users see login prompt on toggle
    - Favorites count in nav updates on toggle
  integration:
    - Full add/remove/list cycle works end-to-end
    - Pagination works for users with many favorites
```

### День: генерация кода

Разработчик передаёт вычитанную спецификацию ИИ. ИИ генерирует:

- `FavoriteButton.tsx` — компонент переключения сердечка
- `FavoritesList.tsx` — компонент страницы избранного
- `useFavorites.ts` — хуки React Query для API избранного
- `FavoriteButton.test.tsx` — тесты из спецификации
- `FavoritesList.test.tsx` — тесты из спецификации

Разработчик проверяет сгенерированный код по каждому критерию приёмки и ограничению. Обнаруживает, что ИИ не обработал случай «неаутентифицированный пользователь». Добавляет уточнение в спецификацию и перегенерирует соответствующий компонент.

### Ближе к вечеру: PR и ревью

Разработчик создаёт PR, включающий и спецификацию, и сгенерированный код. Рецензент сначала читает спецификацию, затем рецензирует код. Ревью сосредоточено на:

1. Точно ли спецификация отражает требования?
2. Правильно ли код реализует спецификацию?
3. Достаточно ли тесты полны для проверки соответствия?

Рецензент предлагает дополнительное ограничение: «MUST animate the heart icon on toggle». Разработчик добавляет его в спецификацию, перегенерирует компонент и обновляет PR.

### Конец дня: слияние

Спецификация и код сливаются вместе. Версия спецификации обновляется с 0.1.0 до 1.0.0. В кодовой базе теперь есть ясная, версионированная, рецензируемая запись о том, что делает функция избранного и почему.

---

## 2.12 Распространённые антишаблоны

Закончу главу антишаблонами — вещами, которые я вижу у команд и которые подрывают принцип SSOT.

### Антишаблон 1: ретроспективная спецификация

Написание спецификации *после* написания кода. Это как писать чертёж после постройки здания. Спецификация становится документацией, а не источником истины. Она описывает, что было построено, а не управляет тем, что должно быть построено.

**Исправление:** Спецификация первой, всегда. Даже если черновая. Даже если она изменится во время реализации. Основная ценность — в самом акте продумывания спецификации до написания кода.

### Антишаблон 2: сиротская спецификация

Спецификация, которая существует, но на неё никогда не ссылаются. Никакой код на неё не ссылается. Никакие тесты из неё не выводятся. Она лежит в каталоге и медленно устаревает.

**Исправление:** Сгенерированный код должен ссылаться на свою спецификацию. Проверки CI должны убеждаться, что у каждой спецификации есть соответствующий код и версии совпадают.

### Антишаблон 3: спецификация «на всё сразу»

Спецификация, которая пытается зафиксировать всё — детали реализации, попиксельные спецификации UI, схемы БД, форматы ответов API, конфигурацию развёртывания. Излишне подробная спецификация так же плоха, как отсутствие спецификации, потому что её написание и поддержка занимают столько времени, что команда её бросает.

**Исправление:** Спецификации фиксируют *что* и *почему*, а не *как*. Если вы начали указывать имена переменных или пиксельные значения CSS, вы зашли слишком далеко. Спецификация должна быть на уровне абстракции, где компетентный разработчик (человек или ИИ) может реализовать её без дополнительных указаний.

### Антишаблон 4: неизменяемая спецификация

Отношение к спецификации как к священному документу, который нельзя менять после написания. Требования меняются. Понимание углубляется. Спецификация должна эволюционировать.

**Исправление:** Спецификации — живые документы. У них есть номера версий именно потому, что они меняются. Цель — не идеальность с первого черновика, а документ, всегда отражающий текущий замысел.

### Антишаблон 5: игнорируемая спецификация

Все пишут спецификации, но никто их не читает. Код генерируется без обращения к спецификации. Ревью проводится без ссылок на неё. Спецификация существует, но не имеет авторитета.

**Исправление:** Это культурная проблема, а не техническая. Команда должна принять принцип, что спецификация — источник истины. Это значит: ревью спецификации обязательно, расхождение спецификации и кода считается багом, ссылки на спецификацию в коде обязательны.

---

## Итоги главы

| Понятие | Ключевой вывод |
|---|---|
| Источник истины | Файл спецификации — высшая инстанция. Когда спецификация и код расходятся, права спецификация. |
| Спецификация = что + почему | Спецификация фиксирует замысел и ограничения. Код фиксирует реализацию. |
| Отраслевые параллели | Дизайн-документы Google, конституционный ИИ Anthropic и структурированные выводы OpenAI — все воплощают принцип SSOT. |
| Контроль версий | Спецификации версионируются вместе с кодом. Diff спецификации передаёт изменения замысла; diff кода — изменения реализации. |
| Предотвращение расхождений | Код-ревью, проверки CI, тесты из спецификации и культурная дисциплина предотвращают расхождение. |
| Слой коммуникации | Спецификации — общий артефакт для PM, разработчиков, рецензентов и ИИ. |
| Живой документ | В отличие от традиционных документов требований, спецификации функциональны, минимальны, валидируемы и тесно связаны с кодом. |

---

## Вопросы для обсуждения

1. Ваша команда сейчас использует тикеты Jira для требований. Как бы вы ввели спецификации рядом с тикетами (или вместо них)? Какого сопротивления ожидаете?

2. Рассмотрите спор «код управляет спецификацией» против «спецификация управляет кодом». Есть ли ситуации, где код разумно сделать источником истины? Когда?

3. Как бы вы поступили, если старший разработчик не согласен со спецификацией? У кого авторитет — у автора спецификации, автора кода или команды?

4. Подумайте о концепции системной спецификации. Как выглядела бы системная спецификация вашего текущего проекта? Какие шаблоны и конвенции она бы фиксировала?

5. Глава утверждает, что расхождение спецификации и кода — «баг». Вы согласны? Насколько строго это должно быть на практике?

---

*Далее: глава 3 — «Анатомия микро-спецификации»*
