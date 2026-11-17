# Глава 3: Анатомия микро-спецификации

## МОДУЛЬ 01 — Основы: мышление «контрактами»

---

### Вступление к лекции

*Сегодня мы препарируем. В главе 1 мы узнали, почему спецификации важны. В главе 2 узнали, что спецификация — источник истины. Теперь узнаем, как спецификация на самом деле выглядит — часть за частью, раздел за разделом.*

*Я называю фундаментальную единицу SDD «микро-спецификацией». Не потому что она маленькая — некоторые микро-спецификации довольно подробны, — а потому что она сфокусирована. Микро-спецификация описывает один компонент, одну функцию, одну конечную точку, одну ограниченную единицу работы. Это атом разработки через спецификации. Всё более крупное составляется из микро-спецификаций.*

*К концу главы вы сможете взять любую микро-спецификацию, сразу опознать её части, оценить качество и понять, как она будет направлять ИИ. Что важнее — вы сможете написать её с нуля.*

*Открывайте редакторы. Сегодня мы строим спецификации.*

---

## 3.1 Три столпа

Каждая эффективная микро-спецификация строится на трёх столпах:

1. **Контекст** — что существует сейчас?
2. **Цель** — какое конкретное изменение нужно сделать?
3. **Ограничения** — чего НЕ должно произойти?

Эти три столпа соответствуют трём фундаментальным вопросам, на которые должен получить ответ любой разумный агент — человек или ИИ, — прежде чем сделать полезную работу:

- **Где я?** (Контекст)
- **Куда я иду?** (Цель)
- **Каких мин избегать?** (Ограничения)

Упустите любой из них — и результат предсказуемо ухудшится:

| Пропущенный столп | Результат |
|---|---|
| Нет контекста | ИИ делает предположения о текущем состоянии системы, технологическом стеке и существующих шаблонах. Эти предположения обычно неверны. |
| Нет цели | ИИ не знает, когда закончил. Он либо недоделывает (упускает требования), либо переделывает (добавляет функции, которых вы не просили). |
| Нет ограничений | ИИ идёт по пути наименьшего сопротивления, что часто включает небезопасные умолчания, неподходящие зависимости или шаблоны, конфликтующие с существующей кодовой базой. |

Разберём каждый столп подробно.

---

## 3.2 Столп 1: контекст

Контекст отвечает на вопрос: **каково текущее состояние мира?**

Модель ИИ, какой бы способной она ни была, начинает каждое взаимодействие с нулевым знанием о вашем конкретном проекте. Она не знает, какой фреймворк вы используете. Не знает, какая у вас база данных. Не знает, какие существуют API. Не знает, каким шаблонам следует ваша команда. Не знает, какая у вас версия React.

Без контекста ИИ откатывается к обучающим данным — статистическому среднему всего кода, который он когда-либо видел. Это значит, что он сгенерирует код, в целом разумный, но конкретно неверный для вашего проекта.

У контекста несколько подкомпонентов. Разберём каждый.

### 3.2.1 Контекст системы

Системный контекст — глобальная информация, применимая ко всему проекту. Обычно он живёт в системной спецификации (которую мы обсуждали в главе 2) и на него ссылается каждая микро-спецификация. Он включает:

**Технологический стек:**

```yaml
context:
  system:
    language: TypeScript 5.4
    runtime: Node.js 22
    framework: React 19
    styling: Tailwind CSS 4.0
    state_management: Zustand 5
    data_fetching: "@tanstack/react-query v5"
    testing: Vitest + React Testing Library
    package_manager: pnpm
```

Почему это важно? Рассмотрим, что происходит без явного контекста стека. Вы просите ИИ «создать компонент, который получает данные пользователя». ИИ может:

- Использовать JavaScript вместо TypeScript
- Использовать классовые компоненты вместо функциональных
- Использовать `axios` вместо предпочитаемого вами HTTP-клиента
- Использовать Redux вместо Zustand
- Использовать Jest вместо Vitest
- Использовать синтаксис `npm` в инструкциях вместо `pnpm`

Каждое из этого — разумное умолчание. Каждое — неверно для вашего проекта. Явный контекст стека устраняет эти несоответствия.

**Существующие шаблоны:**

```yaml
context:
  patterns:
    data_fetching: >
      All data fetching is done through custom React Query hooks
      located in /features/{domain}/hooks/. Hooks follow the
      naming convention use{Domain}{Action}, e.g., useUsersFetch,
      useUsersCreate. Each hook returns the React Query result
      object directly.
    error_handling: >
      API errors are handled by React Query's error state.
      Components check query.isError and display the shared
      ErrorBanner component. No try/catch blocks in components.
      Unexpected errors are caught by the ErrorBoundary at the
      route level.
    component_structure: >
      Components are functional, using TypeScript interfaces for
      props. Props interfaces are defined in the same file as the
      component and exported. Components are in /features/{domain}/
      components/. One component per file.
```

Шаблоны критичны. Это *институциональное знание* вашей кодовой базы — конвенции, которые делают код согласованным и поддерживаемым. Без явных шаблонов ИИ сгенерирует код, который *работает*, но не *вписывается.* Он будет белой вороной: компонентом, обрабатывающим ошибки иначе; хуком, устроенным иначе; файлом не на своём месте.

> **Заметка профессора:** У меня есть правило: если новому члену команды нужно *сказать* о конвенции (потому что он не мог бы вывести её из кода), эта конвенция принадлежит разделу контекста. Примеры: «Мы используем barrel-экспорты из каждого каталога функции». «Мы добавляем префикс `data-testid` ко всем тестовым ID». «Мы не используем экспорт по умолчанию». Это те конвенции, которые модели ИИ сами не обнаружат.

**Существующая инфраструктура:**

```yaml
context:
  infrastructure:
    api_base: "https://api.acme.com/v2"
    auth_mechanism: "JWT in httpOnly cookies, auto-refreshed by interceptor"
    api_documentation: "OpenAPI spec at /docs/api/openapi.yaml"
    existing_endpoints:
      - "GET /api/users — List all users (paginated)"
      - "GET /api/users/:id — Get single user"
      - "POST /api/users — Create user"
      - "PUT /api/users/:id — Update user"
      - "DELETE /api/users/:id — Soft-delete user"
```

Это говорит ИИ, что уже существует в системе. Без этого ИИ может создать новые конечные точки API, дублирующие существующие, или сгенерировать мок-API, конфликтующие с реальными.

### 3.2.2 Контекст функции

Контекст функции специфичен для конкретной микро-спецификации. Он описывает, что существует в непосредственной области строящейся функции:

```yaml
context:
  feature:
    description: >
      The product catalog currently displays products in a grid view
      using the ProductCard component. Each ProductCard shows the
      product image, name, price, and an "Add to Cart" button.
      There is no search functionality — users browse by category
      using the sidebar navigation.
    current_state:
      - ProductCard component exists at /features/catalog/components/ProductCard.tsx
      - Category sidebar exists at /features/catalog/components/CategorySidebar.tsx
      - Product data is fetched by useProductsFetch hook
      - Product type is defined in /features/catalog/types/Product.ts
    related_features:
      - "Cart feature (cart.spec.yaml) — ProductCard's 'Add to Cart' button
         dispatches addToCart action"
      - "Category feature (categories.spec.yaml) — Sidebar navigation
         filters products by category"
```

Контекст функции говорит ИИ, рядом с чем он работает. Так вы предотвращаете дублирование существующей работы, конфликты со смежными функциями и неверные предположения о том, что доступно, а что нет.

### 3.2.3 Тест полноты контекста

Как понять, достаточно ли контекста? Примените этот тест:

**Смог бы компетентный разработчик, никогда не видевший вашу кодовую базу, правильно реализовать эту функцию, используя только информацию из спецификации?**

Если ответ «нет» — если ему пришлось бы исследовать кодовую базу, спрашивать коллегу или делать предположения, — контекст неполон.

Это не значит, что контекст должен быть исчерпывающим. Не нужно описывать каждый файл в репозитории. Нужно описать:

1. Технологический стек (чтобы он знал, какие инструменты использовать)
2. Существующие шаблоны (чтобы он знал, как структурировать код)
3. Непосредственное окружение (чтобы он знал, что уже существует)
4. Точки интеграции (чтобы он знал, к чему подключаться)

Представьте, что объясняете дорогу. Не нужно описывать каждое здание в городе. Нужно описать начальную точку, пункт назначения, основные ориентиры по пути и дороги, которых следует избегать.

---

## 3.3 Столп 2: цель

Цель отвечает на вопрос: **какое конкретное изменение нужно сделать?**

Обратите внимание на слово «конкретное». Цель — не миссия. Не пользовательская история. Не расплывчатое описание желаемой функциональности. Это точное, проверяемое описание *дельты* — различия между текущим состоянием (описанным в контексте) и желаемым будущим.

### 3.3.1 Краткое описание

Каждая цель начинается с краткого описания — одного-трёх предложений об изменении:

```yaml
objective:
  summary: >
    Add a search bar to the main navigation that provides real-time
    search suggestions as the user types. When a suggestion is selected,
    navigate to the product detail page.
```

Краткое описание должно быть понятно любому — PM, разработчику, дизайнеру, QA. Это «презентация в лифте» для функции.

### 3.3.2 Критерии приёмки

Критерии приёмки — сердце цели. Это конкретные проверяемые условия, которые должны быть истинны, когда функция завершена:

```yaml
objective:
  acceptance_criteria:
    - Search input is visible in the top navigation bar on all pages
    - Typing in the search input triggers a search after 2+ characters
    - Search results appear in a dropdown below the input
    - Each result shows the product name and category
    - Results are limited to 8 items maximum
    - Clicking a result navigates to /products/:id
    - Pressing Enter with text submits a full search to /search?q=...
    - Pressing Escape closes the dropdown
    - The dropdown closes when clicking outside it
    - The search input is cleared after navigating to a result
```

Хорошие критерии приёмки обладают следующими свойствами:

**Проверяемость:** каждый критерий можно проверить механически. «Строка поиска выглядит хорошо» непроверяемо. «Строка поиска видна в верхней панели навигации на всех страницах» проверяемо.

**Независимость:** каждый критерий стоит сам по себе. Любой критерий можно протестировать, не полагаясь на порядок перечисления.

**Полнота:** вместе критерии полностью описывают функцию. Если все критерии проходят, функция готова. Не должно быть «подразумеваемых» требований, которых нет в списке.

**Однозначность:** у каждого критерия только одна возможная интерпретация. «Результаты ограничены» неоднозначно (ограничены как? по времени? по количеству? по размеру?). «Результаты ограничены максимум 8 элементами» однозначно.

> **Заметка профессора:** Написание хороших критериев приёмки — навык, и, как все навыки, он улучшается с практикой. Полезное упражнение: напишите критерии, затем попросите коллегу прочитать их без другого контекста. Если он сможет точно сказать, что делает функция, только по критериям, они хороши. Если у него есть вопросы, критерии неполны или неоднозначны.

### 3.3.3 Определение объёма

Раздел объёма явно определяет, что включено и что не включено в функцию:

```yaml
objective:
  scope:
    includes:
      - Search bar component in the navigation
      - Search suggestions dropdown
      - Navigation to product detail on selection
      - Navigation to search results page on Enter
      - Keyboard navigation within suggestions
    excludes:
      - Search results page (separate spec)
      - Advanced search / filters
      - Search history / recent searches
      - Voice search
      - Search analytics tracking
```

Раздел `excludes` — не пустая формальность. Это одна из важнейших частей спецификации. Вспомните провал 3 из главы 1 — расползание объёма системы уведомлений? Разработчик хотел тост-сообщение, а получил 15 000-строчную платформу уведомлений. Явный раздел `excludes` это предотвращает.

Когда ИИ видит `excludes: Search history / recent searches`, он знает, что не нужно добавлять «недавние поиски», хотя его обучающие данные содержат тысячи реализаций строки поиска с такой функцией. Раздел исключений — *граница*, а границы необходимы для контролируемой генерации кода.

### 3.3.4 Принцип дельты

Хочу подчеркнуть концепцию, которую называю **принципом дельты**: микро-спецификация описывает *изменение*, а не *состояние.*

Неправильно (описывает состояние):

```yaml
objective:
  summary: The application has a search feature that...
```

Правильно (описывает изменение):

```yaml
objective:
  summary: Add a search bar to the existing navigation bar that...
```

Формулировка через дельту важна, потому что говорит ИИ, что *создавать*, а что уже *существует.* Если вы описываете состояние, ИИ может попытаться перегенерировать уже существующее. Если описываете дельту, ИИ знает, что создавать только новые части и интегрировать с существующими.

Это особенно важно в больших кодовых базах. Вы не хотите, чтобы ИИ перегенерировал всю панель навигации, когда вам нужно лишь добавить в неё поле поиска. Формулировка через дельту вместе с контекстом о существующем держит объём узким.

---

## 3.4 Столп 3: ограничения

Ограничения отвечают на вопрос: **чего НЕ должно произойти?**

Если цель — акселератор, ограничения — тормоза. Они очерчивают пространство решений. Не дают ИИ срезать углы, принимать небезопасные решения или отклоняться от стандартов проекта.

Я называю ограничения «никогда-никогда», потому что они выражают незыблемые правила. Это не предпочтения и не предложения. Это жёсткие границы.

### 3.4.1 Типы ограничений

Ограничения делятся на несколько категорий:

**Технические ограничения:**

```yaml
constraints:
  technical:
    - MUST use React Query for data fetching (no raw fetch in components)
    - MUST NOT introduce new npm dependencies
    - MUST NOT use inline styles (Tailwind only)
    - MUST be compatible with React 19 strict mode
    - MUST NOT use deprecated React APIs (no componentWillMount, etc.)
```

Технические ограничения гарантируют, что сгенерированный код вписывается в существующую кодовую базу. Без них ИИ с радостью импортирует `lodash`, чтобы использовать `_.debounce`, хотя в проекте есть собственный хук `useDebounce`, или применит `styled-components`, когда проект использует Tailwind.

**Ограничения безопасности:**

```yaml
constraints:
  security:
    - MUST NOT store tokens in localStorage or sessionStorage
    - MUST NOT use dangerouslySetInnerHTML
    - MUST sanitize all user input before rendering
    - MUST NOT log sensitive data (tokens, passwords, PII)
    - MUST NOT expose internal API paths in client-side code
    - MUST include CSRF token in all mutating API calls
```

Ограничения безопасности, пожалуй, самые важные в любой спецификации. У моделей ИИ есть склонность генерировать *функциональный* код, который *небезопасен*, потому что их обучающие данные содержат смесь безопасных и небезопасных шаблонов, а оптимизируются они под «работает», а не «безопасно».

Галлюцинация аутентификации из главы 1 — где ИИ захардкодил `"secret"` как ключ JWT — была бы предотвращена одним ограничением: «MUST load JWT secret from environment variable».

**Ограничения производительности:**

```yaml
constraints:
  performance:
    - MUST debounce search input at 300ms minimum
    - MUST NOT re-render the entire product list on search input change
    - MUST cancel in-flight requests when new search query is entered
    - MUST lazy-load the search suggestions component
    - MUST NOT block the main thread during search processing
```

Ограничения производительности не дают ИИ сгенерировать код, который работает, но плохо себя ведёт. Без них ИИ может создать поиск, отправляющий API-запрос на каждое нажатие клавиши, или список, перерисовывающий все 1000 элементов при изменении одного.

**Ограничения доступности:**

```yaml
constraints:
  accessibility:
    - MUST implement ARIA combobox pattern for search
    - MUST support keyboard navigation (arrow keys, Enter, Escape)
    - MUST announce search results to screen readers via aria-live
    - MUST NOT rely solely on color to communicate state
    - MUST have minimum 4.5:1 color contrast ratio
    - MUST have visible focus indicators on all interactive elements
```

Доступность — область, где модели ИИ особенно непоследовательны. Некоторые модели по умолчанию генерируют разумно доступный код; другие — совершенно недоступный. Явные ограничения доступности обеспечивают согласованный доступный результат независимо от используемой модели.

**Бизнес-ограничения:**

```yaml
constraints:
  business:
    - MUST NOT show product prices to unauthenticated users
    - MUST NOT display out-of-stock products in search results
    - MUST respect user's region for currency formatting
    - MUST comply with GDPR (no tracking without consent)
```

Бизнес-ограничения кодируют правила из продуктовых, юридических или комплаенс-требований. Это правила, которые ИИ никогда не смог бы вывести только из технического контекста.

### 3.4.2 Конвенция MUST / MUST NOT

Вы заметите, что каждое ограничение начинается с `MUST` или `MUST NOT`. Это намеренно. Это идёт из RFC 2119, определяющего ключевые слова для спецификаций:

- **MUST (ДОЛЖЕН):** абсолютное требование. Нарушение — дефект.
- **MUST NOT (НЕ ДОЛЖЕН):** абсолютный запрет. Нарушение — дефект.
- **SHOULD (СЛЕДУЕТ):** сильная рекомендация. Нарушение требует обоснования.
- **SHOULD NOT (НЕ СЛЕДУЕТ):** сильное неодобрение. Нарушение требует обоснования.
- **MAY (МОЖЕТ):** действительно необязательно.

В SDD мы в основном используем MUST и MUST NOT для ограничений. SHOULD и MAY используются редко, обычно в разделе цели для приятных дополнений.

У этого словаря два преимущества:

1. **Ясность для ИИ.** Модели обучены на RFC и технических спецификациях. Они понимают вес MUST против SHOULD. Использование этого словаря повышает вероятность, что ИИ будет считать ограничения незыблемыми.

2. **Ясность для людей.** Во время ревью спецификации MUST и MUST NOT выделяются визуально и семантически. Рецензент может быстро просмотреть раздел ограничений и понять жёсткие границы.

### 3.4.3 Тест полноты ограничений

Как понять, достаточно ли ограничений? Спросите себя:

**Если ИИ выдаст код, который технически выполняет все критерии приёмки, но делает это худшим возможным способом, что пойдёт не так?**

Например, критерии приёмки говорят «получает данные пользователей». Без ограничений ИИ может:

- Получить всех 50 000 пользователей сразу (без пагинации)
- Хранить пользователей в глобальной переменной (без управления состоянием)
- Кешировать пользователей бессрочно (устаревшие данные)
- Получать пользователей при каждом рендере (катастрофа производительности)
- Логировать ответ API в консоль (утечка данных)

Каждый из этих «худших» сценариев подсказывает ограничение:

```yaml
constraints:
  - MUST paginate results (maximum 50 per request)
  - MUST use React Query for state management
  - MUST set staleTime to 5 minutes maximum
  - MUST deduplicate requests (React Query handles this)
  - MUST NOT log API responses containing user data
```

> **Заметка профессора:** Иногда я называю это тестом «злонамеренного соответствия». Представьте, что ИИ — злой джинн, который исполнит ваше желание худшим возможным способом, если вы не ограничите его точно. Какие ограничители нужны? Эта мысленная модель полезна, потому что заставляет думать о крайних случаях и режимах отказа *до* генерации кода, а не после.

---

## 3.5 Полная микро-спецификация: аннотированный разбор

Покажу полную микро-спецификацию с подробными аннотациями, объясняющими, зачем существует каждый раздел и что он сообщает ИИ.

```yaml
# ============================================================
# METADATA
# ============================================================
# Metadata identifies the spec. It answers: What is this spec
# for, and where does it fit in the system?
# ============================================================
kind: Component                          # [1]
metadata:
  name: NotificationBell                 # [2]
  module: notifications                  # [3]
  version: 1.0.0                         # [4]
  status: approved                       # [5]
  owner: team-engagement                 # [6]
  system_spec: system.spec.yaml@3.1.0    # [7]
  created: 2026-02-20                    # [8]
  updated: 2026-02-24                    # [8]

# [1] kind: What type of thing is this? Component, Feature,
#     Endpoint, Migration, etc. Tells the AI what kind of
#     code to generate.
# [2] name: The specific name. Will be used for the component/
#     function/class name in generated code.
# [3] module: Which feature domain this belongs to. Determines
#     file placement.
# [4] version: Semantic version of this spec. Incremented
#     when the spec changes.
# [5] status: draft | review | approved | deprecated.
#     Only approved specs should drive code generation.
# [6] owner: Which team is responsible. Useful for review
#     routing and ownership.
# [7] system_spec: Reference to the global system spec,
#     pinned to a specific version.
# [8] Timestamps for auditability.


# ============================================================
# CONTEXT
# ============================================================
# Context answers: What is the current state of the world?
# This is the AI's "briefing" before it starts work.
# ============================================================
context:
  description: >                         # [9]
    The application currently has no notification system.
    The backend team has built a notifications API that
    provides unread notification count and notification
    list. We need a UI component that shows the count
    and allows the user to view their notifications.

  technical_context: >                   # [10]
    Notifications API:
      GET /api/notifications/count → { count: number }
      GET /api/notifications → { notifications: Notification[], total: number }
      PUT /api/notifications/:id/read → { success: boolean }

    Notification type (from backend):
      { id: string, title: string, body: string,
        type: "info" | "warning" | "error",
        read: boolean, createdAt: string }

    The app header is rendered by the HeaderBar component at
    /features/layout/components/HeaderBar.tsx. It has a
    designated slot for notification UI (a div with
    id="notification-slot").

  related_specs:                         # [11]
    - notification-panel.spec.yaml  # Full notification list panel
    - notification-settings.spec.yaml  # User notification preferences

  assumptions:                           # [12]
    - Backend API is stable and deployed
    - Notification count endpoint is lightweight (< 50ms response)
    - Maximum 99+ notifications displayed in badge


# [9]  description: Plain-language overview of why this spec
#      exists. Provides business context.
# [10] technical_context: Detailed technical information the AI
#      needs — API endpoints, data types, existing components.
# [11] related_specs: Other specs that interact with this one.
#      Helps the AI understand the boundaries.
# [12] assumptions: Things we are taking as given. If an
#      assumption is wrong, the spec may need revision.


# ============================================================
# OBJECTIVE
# ============================================================
# Objective answers: What specific change should be made?
# This is the AI's "mission brief."
# ============================================================
objective:
  summary: >                             # [13]
    Create a notification bell icon component for the app
    header that shows the unread notification count and
    opens a notification dropdown when clicked.

  acceptance_criteria:                   # [14]
    - Bell icon is rendered inside the #notification-slot in HeaderBar
    - Badge shows unread count (number) when count > 0
    - Badge shows "99+" when count exceeds 99
    - Badge is hidden when count is 0
    - Clicking the bell toggles a dropdown panel
    - Dropdown shows the 5 most recent notifications
    - Each notification shows title, body preview (50 chars), and time ago
    - Clicking a notification marks it as read and navigates to its target
    - "Mark all as read" button at the bottom of the dropdown
    - Unread count refreshes every 30 seconds via polling
    - Dropdown closes when clicking outside it

  scope:                                 # [15]
    includes:
      - Bell icon with badge
      - Notification dropdown (compact, 5 items)
      - Mark-as-read functionality
      - Polling for count updates
    excludes:
      - Full notification list/page (see notification-panel.spec)
      - Notification settings (see notification-settings.spec)
      - Push notifications / WebSocket real-time updates
      - Notification sounds or browser notifications
      - Notification grouping or categorization


# [13] summary: One clear sentence describing the delta.
#      "Create a..." tells the AI this is new, not a modification.
# [14] acceptance_criteria: Testable conditions. Each one maps
#      to at least one test case.
# [15] scope: Explicit boundaries. The excludes section prevents
#      the AI from building adjacent features.


# ============================================================
# CONSTRAINTS
# ============================================================
# Constraints answer: What must NOT happen?
# These are the guardrails that prevent bad AI decisions.
# ============================================================
constraints:                             # [16]
  # Technical
  - MUST use React Query for fetching notification count and list
  - MUST use the existing usePolling hook for count refresh
  - MUST NOT introduce new npm dependencies
  - MUST NOT use CSS animations (use Tailwind transition utilities)
  - MUST use React Portal for the dropdown (to escape header overflow)

  # Performance
  - MUST NOT fetch full notification list until dropdown is opened
  - MUST NOT re-render HeaderBar when notification count changes
  - Polling interval MUST be 30 seconds (not shorter)
  - MUST abort in-flight requests when dropdown closes

  # Security
  - MUST NOT include notification content in document.title
  - MUST NOT store notification data in localStorage
  - MUST sanitize notification body before rendering (DOMPurify)

  # Accessibility
  - Bell button MUST have aria-label "Notifications"
  - Badge count MUST be announced to screen readers via aria-live="polite"
  - Dropdown MUST trap focus when open
  - MUST support Escape key to close dropdown
  - Notifications MUST be navigable by keyboard (arrow keys)

  # UX
  - Dropdown MUST NOT cover more than 50% of viewport on mobile
  - MUST show loading skeleton in dropdown while fetching
  - MUST show "No notifications" message when list is empty


# [16] Constraints are organized by category for readability.
#      Each constraint uses MUST or MUST NOT for unambiguous
#      requirement level.


# ============================================================
# TESTING
# ============================================================
# Testing defines how we validate that code matches the spec.
# These are the spec's "teeth" — without tests, constraints
# are just suggestions.
# ============================================================
testing:                                 # [17]
  unit:
    - Bell icon renders without errors
    - Badge shows correct count for counts 1-99
    - Badge shows "99+" for counts > 99
    - Badge is hidden when count is 0
    - Dropdown opens on bell click
    - Dropdown closes on outside click
    - Dropdown closes on Escape key
    - Notifications render with title and truncated body
    - "Mark all as read" calls PUT endpoint for each notification
    - Clicking notification triggers navigation

  integration:
    - Count polling updates badge every 30 seconds
    - Opening dropdown fetches notification list
    - Marking notification as read decrements badge count
    - Dropdown position is correct in various viewport sizes

  accessibility:
    - Bell button has aria-label "Notifications"
    - Badge count is announced via aria-live
    - Dropdown traps focus when open
    - All notifications reachable via keyboard
    - Focus returns to bell button when dropdown closes


# [17] Tests are organized by type. Unit tests validate individual
#      behaviors. Integration tests validate interactions between
#      parts. Accessibility tests validate WCAG compliance.
#      Each test maps to one or more acceptance criteria or
#      constraints.
```

Это полная микро-спецификация. Подчеркну ключевые свойства:

1. **Самодостаточность.** Всё, что нужно ИИ для генерации этого компонента, есть в документе (плюс указанная системная спецификация). Никакой неоднозначности, никаких подразумеваемых требований, никаких «вы понимаете, что я имею в виду».

2. **Структурированность.** У каждого раздела ясная цель. Рецензент может перейти к нужному разделу: PM читает цель, инженеры по безопасности — ограничения, QA — раздел тестирования.

3. **Прослеживаемость.** Каждый критерий приёмки прослеживается к тесту. Каждое ограничение проверяемо. Каждая часть контекста валидируема по реальной кодовой базе.

4. **Ограниченность.** Раздел объёма явно говорит, что включено, а что нет. ИИ не может добавить push-уведомления или звуки уведомлений, потому что спецификация их явно исключает.

---

## 3.6 Как каждый раздел отображается на поведение ИИ

Объясню явно, что каждый раздел микро-спецификации делает с поведением ИИ. Понимание этого отображения поможет писать лучшие спецификации.

### Контекст → снижает галлюцинации

Без контекста ИИ заполняет пробелы из обучающих данных. С контекстом у него есть конкретная, заземлённая информация.

**Без контекста:**

```
Create a notification bell component.
```

ИИ может:
- Изобрести собственные конечные точки API
- Использовать Socket.io для обновлений в реальном времени
- Создать полную модель уведомлений с нуля
- Выбрать случайную библиотеку иконок
- Угадывать структуру данных

**С контекстом:**

```yaml
context:
  technical_context: >
    GET /api/notifications/count → { count: number }
    GET /api/notifications → { notifications: Notification[], total: number }
    Notification: { id: string, title: string, body: string, ... }
```

Теперь ИИ использует точно указанные вами конечные точки и типы данных. Изобретать не нужно.

Вот пример на TypeScript того, что ИИ генерирует при правильном контексте:

```typescript
// With context: AI uses the exact API and types from the spec

interface Notification {
  id: string;
  title: string;
  body: string;
  type: "info" | "warning" | "error";
  read: boolean;
  createdAt: string;
}

interface NotificationCountResponse {
  count: number;
}

interface NotificationListResponse {
  notifications: Notification[];
  total: number;
}

function useNotificationCount() {
  return useQuery({
    queryKey: ["notifications", "count"],
    queryFn: async (): Promise<NotificationCountResponse> => {
      const response = await fetch("/api/notifications/count");
      return response.json();
    },
    refetchInterval: 30_000, // 30 seconds per spec
  });
}
```

Сравните с тем, что ИИ может сгенерировать без контекста:

```typescript
// Without context: AI invents everything

interface Notification {
  _id: string;          // MongoDB-style ID (your project uses UUID)
  message: string;      // Different field name than your API
  isRead: boolean;      // Different naming convention
  timestamp: number;    // Unix timestamp, but your API sends ISO string
  priority: number;     // Field that does not exist in your API
}

// Uses axios (not in your project's dependencies)
const fetchNotifications = async () => {
  const { data } = await axios.get("/notifications");  // Wrong URL path
  return data;
};
```

Разница резкая. Контекст не просто «помогает». Он фундаментально меняет качество вывода.

### Цель → определяет полноту

Критерии приёмки говорят ИИ, *когда он закончил.* Без них ИИ судит сам, что входит в «колокольчик уведомлений». С ними у него есть чек-лист.

Это важно, потому что у моделей ИИ есть смещение к полноте — они склонны генерировать больше, а не меньше. Подробный набор критериев приёмки *фокусирует* ИИ ровно на нужном:

```typescript
// The AI generates exactly these behaviors, no more, no less:

export function NotificationBell() {
  const { data: countData } = useNotificationCount();
  const [isOpen, setIsOpen] = useState(false);
  const count = countData?.count ?? 0;

  return (
    <div id="notification-slot">
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Notifications"
      >
        <BellIcon />
        {/* Criterion: Badge shows count when > 0 */}
        {/* Criterion: Badge shows "99+" when count > 99 */}
        {/* Criterion: Badge is hidden when count is 0 */}
        {count > 0 && (
          <span aria-live="polite">
            {count > 99 ? "99+" : count}
          </span>
        )}
      </button>

      {/* Criterion: Clicking the bell toggles dropdown */}
      {isOpen && (
        <NotificationDropdown
          onClose={() => setIsOpen(false)}
        />
      )}
    </div>
  );
}
```

Каждый кусок сгенерированного кода прослеживается к конкретному критерию приёмки. Ничего лишнего. Ничего пропущенного.

### Ограничения → предотвращают плохие решения

Ограничения — самая прямая форма контроля ИИ. Это явные запреты и требования, переопределяющие поведение ИИ по умолчанию.

Покажу разницу на реальном примере:

**Без ограничений безопасности:**

```typescript
// AI's default: functional but insecure
function NotificationDropdown({ notifications }) {
  return (
    <div>
      {notifications.map((n) => (
        <div
          key={n.id}
          // DANGER: renders raw HTML from API without sanitization
          dangerouslySetInnerHTML={{ __html: n.body }}
        />
      ))}
    </div>
  );
}
```

**С ограничением «MUST sanitize notification body before rendering»:**

```typescript
// AI respects the constraint: sanitized input, safe preview
import DOMPurify from "dompurify";

function NotificationDropdown({ notifications }) {
  return (
    <div>
      {notifications.map((n) => {
        // Strip all tags to derive a plain-text preview, then truncate.
        // React then auto-escapes when rendering the preview as text.
        const preview = DOMPurify.sanitize(n.body, { ALLOWED_TAGS: [] }).slice(0, 50);
        return (
          <div key={n.id}>
            <p>{n.title}</p>
            <p>{preview}</p>
          </div>
        );
      })}
    </div>
  );
}
```

Ограничение превратило вывод из небезопасного в безопасный. Одна строка в спецификации — `MUST sanitize notification body before rendering` — предотвратила потенциальную XSS-уязвимость.

В исправленной версии стоит отметить две вещи. Во-первых, DOMPurify должен сделать реальную работу: нарезка санированной *HTML*-строки так, будто это текст, может разрезать внутри тега и вернуть проблему, поэтому мы удаляем теги (`ALLOWED_TAGS: []`) *до* обрезки — нарезать простой текст безопасно. Во-вторых, превью рендерится внутри `{...}`, а не через `dangerouslySetInnerHTML`, поэтому встроенное экранирование React — последняя линия защиты. «Плохое» умолчание ИИ было структурно небезопасным; «хорошая» версия безопасна по построению.

---

## 3.7 Частые ошибки: избыточная и недостаточная спецификация

У детализации спецификации есть золотая середина. Слишком мало — ИИ неверно заполнит пробелы. Слишком много — спецификация станет такой же сложной, как код, и цель будет потеряна.

### Недостаточная спецификация

```yaml
# BAD: Under-specified
kind: Component
metadata:
  name: NotificationBell

objective:
  summary: Show notifications to the user.
```

Это даёт ИИ почти ничего. Он примет десятки неявных решений об API, структурах данных, поведении, стилизации, доступности и объёме. Результат будет функциональным, но почти наверняка не совпадёт с вашим замыслом.

### Избыточная спецификация

```yaml
# BAD: Over-specified
kind: Component
metadata:
  name: NotificationBell

objective:
  acceptance_criteria:
    - Bell icon MUST be 24x24 pixels
    - Bell icon MUST use SVG path "M12 22c1.1 0 2-.9 2-2h-4c0..."
    - Badge MUST be positioned top: -4px, right: -4px
    - Badge MUST use background-color: #EF4444
    - Badge MUST use font-size: 10px
    - Badge MUST use border-radius: 9999px
    - Dropdown MUST be positioned 8px below the bell
    - Dropdown MUST have width: 320px
    - Dropdown MUST have max-height: 400px
    - Dropdown MUST have box-shadow: 0 4px 6px rgba(0,0,0,0.1)
    - Each notification row MUST have padding: 12px 16px
    - Each notification title MUST use font-weight: 600
    - Each notification body MUST use font-size: 14px
    - Each notification body MUST use color: #6B7280
    - Time ago MUST use font-size: 12px
    - Time ago MUST use color: #9CA3AF
    - Use useState for isOpen with initial value false
    - Use useQuery with queryKey ["notifications", "count"]
    - Use useQuery with queryFn that calls fetch("/api/notifications/count")
    - Set refetchInterval to 30000
    ...
```

Эта спецификация подробнее самого кода. Она микроменеджит ИИ, указывая пиксели, цвета, CSS-свойства и даже имена переменных. Если вы собираетесь быть настолько конкретным, проще написать код самому.

### Золотая середина

```yaml
# GOOD: Right level of detail
kind: Component
metadata:
  name: NotificationBell

context:
  technical_context: >
    API: GET /api/notifications/count → { count: number }
    API: GET /api/notifications → { notifications: Notification[] }
    Place in #notification-slot in HeaderBar component.

objective:
  summary: >
    Create a notification bell icon with unread count badge
    that opens a dropdown showing recent notifications.
  acceptance_criteria:
    - Badge shows count when > 0, "99+" when > 99, hidden when 0
    - Clicking bell toggles a dropdown with 5 most recent notifications
    - Each notification shows title, body preview, and time ago
    - Clicking a notification marks it as read
    - Count refreshes via polling every 30 seconds

constraints:
  - MUST use React Query for all data fetching
  - MUST sanitize notification body with DOMPurify
  - MUST support keyboard navigation and screen readers
  - MUST NOT fetch notifications until dropdown opens
  - MUST NOT introduce new dependencies
```

Эта спецификация говорит ИИ, *что строить* (цель), *в каком контексте* (контекст) и *какие ограничители соблюдать* (ограничения). Она не говорит ИИ, *как строить* — имена переменных, значения CSS, структуру компонента. Это решения реализации, которые ИИ вполне способен принять.

> **Заметка профессора:** Хорошее правило: если изменение детали в спецификации НЕ изменит видимое пользователю поведение или архитектурные качества функции (безопасность, производительность, доступность), эта деталь, вероятно, слишком конкретна. Бейдж `#EF4444` против `#DC2626` не меняет поведение. Дебаунс 300 мс против 100 мс МЕНЯЕТ характеристики производительности. Специфицируйте второе, а не первое.

---

## 3.8 Микро-спецификация и отраслевые параллели

Структура микро-спецификации, которую я описал, — контекст, цель, ограничения — не произвольное изобретение. Она отражает шаблоны, независимо возникшие в ИИ-индустрии.

### Схема вызова функций OpenAI

Когда вы определяете функцию для API OpenAI, вы предоставляете:

```typescript
{
  name: "search_products",                    // Identity (metadata)
  description: "Search the product catalog",  // Objective (what it does)
  parameters: {                               // Constraints (valid inputs)
    type: "object",
    properties: {
      query: { type: "string", minLength: 2 },    // Constraint
      category: { type: "string", enum: [...] },   // Constraint
      maxResults: { type: "integer", maximum: 50 } // Constraint
    },
    required: ["query"]                             // Constraint
  }
}
```

Это микро-спецификация функции. У неё есть идентичность (имя), цель (описание) и ограничения (схема параметров с типами, перечислениями, min/max и обязательными полями). Структура другая, но столпы те же.

### Определения инструментов Anthropic

Формат инструментов Claude от Anthropic следует тому же шаблону:

```typescript
{
  name: "get_stock_price",                    // Identity
  description:                                 // Objective + Context
    "Get the current stock price for a given ticker symbol. " +
    "Returns price in USD. Only works for US-listed stocks.",
  input_schema: {                             // Constraints
    type: "object",
    properties: {
      ticker: {
        type: "string",
        description: "Stock ticker symbol (e.g., 'AAPL', 'GOOGL')",
        pattern: "^[A-Z]{1,5}$"              // Constraint: format
      }
    },
    required: ["ticker"]                      // Constraint: required
  }
}
```

Снова: идентичность, цель, ограничения. Описание даёт контекст («only works for US-listed stocks») и цель («get the current stock price»). Схема даёт ограничения (тип, шаблон, обязательность).

### Объявления функций Google Vertex AI

Подход Google с Gemini и Vertex AI структурно идентичен:

```typescript
{
  name: "control_light",                      // Identity
  description:                                 // Objective
    "Set the brightness and color of a room light.",
  parameters: {                               // Constraints
    type: "object",
    properties: {
      brightness: {
        type: "number",
        description: "Light level from 0 to 100",
        minimum: 0,                           // Constraint
        maximum: 100                          // Constraint
      },
      colorTemperature: {
        type: "string",
        enum: ["daylight", "cool", "warm"],   // Constraint
        description: "Color temperature of the light"
      }
    },
    required: ["brightness"]                  // Constraint
  }
}
```

### Шаблон универсален

Схождение поразительно. Три разные компании, строящие три разные ИИ-системы, независимо пришли к одному шаблону: **структурированная идентичность + структурированная цель + структурированные ограничения дают надёжное поведение ИИ.**

SDD берёт этот шаблон — который эти компании применяют на уровне функции/инструмента — и применяет его на уровне функции (feature). Микро-спецификация — определение функции для функции продукта. Она говорит ИИ, что это за функция (идентичность/метаданные), что она должна делать (цель/критерии приёмки) и какие ограничители действуют (ограничения).

Причина, по которой шаблон работает, не специфична для реализации какой-либо компании. Он работает, потому что отображается на фундаментальную структуру разумного исполнения задач: знай, где ты, знай, куда идёшь, знай, чего избегать. Это верно для моделей ИИ, для людей-разработчиков и для любого агента, действующего в сложной среде.

---

## 3.9 Построение микро-спецификации: шаг за шагом

Проведу вас через процесс создания микро-спецификации с нуля. Возьмём реальный запрос функции и методично построим спецификацию.

**Запрос функции (от PM, в Slack):**

> «Нам нужно добавить в приложение переключатель тёмной темы. Пользователи просят.»

### Шаг 1: определить вид

Что это за вещь? Переключатель тёмной темы — UI-компонент, но он также включает управление состоянием темы и изменения CSS. Опишем это как Feature (которая может породить несколько компонентов).

```yaml
kind: Feature
metadata:
  name: DarkMode
  module: theme
  version: 1.0.0
```

### Шаг 2: собрать контекст

Прежде чем писать спецификацию, нужно понять текущее состояние. Спросите себя (или исследуйте кодовую базу):

- Какую систему стилизации использует приложение? (Tailwind CSS 4.0)
- Есть ли существующая система тем? (Нет)
- Как управляется глобальное состояние? (Zustand)
- Где должен быть переключатель? (HeaderBar, рядом с аватаром пользователя)
- Как хранятся предпочтения? (API предпочтений по /api/preferences)

```yaml
context:
  description: >
    Users have requested dark mode support. The app currently has
    no theme system — all styles use Tailwind's default (light) theme.
    User preferences are stored via the preferences API.
  technical_context: >
    Styling: Tailwind CSS 4.0 with dark mode class strategy,
    configured in CSS via @custom-variant dark (&:where(.dark, .dark *)).
    State: Zustand for global state.
    Preferences API:
      GET /api/preferences → { theme: "light" | "dark" | "system", ... }
      PUT /api/preferences → updates preference
    The toggle should go in the HeaderBar component, next to
    the existing UserAvatar component.
    Tailwind's dark: variant is already available but unused.
```

### Шаг 3: определить цель

Каково конкретное изменение? Будьте точны насчёт дельты.

```yaml
objective:
  summary: >
    Add dark mode support with a toggle in the header bar that
    allows users to switch between light, dark, and system-default
    themes. Persist the preference to the user's account.
  acceptance_criteria:
    - Toggle in HeaderBar shows current theme mode (icon changes)
    - Three options: Light, Dark, System (follows OS preference)
    - Selecting a theme immediately applies it (no page reload)
    - Theme preference is persisted to the user's account via API
    - On first load, theme is read from user preference (or system default)
    - Dark mode applies appropriate Tailwind dark: styles globally
    - System mode responds to OS theme changes in real-time
    - Unauthenticated users can use the toggle (stored in localStorage)
    - When user logs in, localStorage preference syncs to account
  scope:
    includes:
      - Theme toggle component in header
      - Theme state management (Zustand store)
      - Theme persistence (API for authenticated, localStorage for anonymous)
      - Dark class management on document root
      - OS theme detection via matchMedia
    excludes:
      - Redesigning existing components for dark mode (separate task)
      - Custom theme colors (only light/dark, using Tailwind defaults)
      - Theme scheduling (auto-switch at certain times)
      - Per-page or per-component theme overrides
```

### Шаг 4: определить ограничения

Что может пойти не так? Чего не должно произойти?

```yaml
constraints:
  - MUST NOT cause flash of unstyled content (FOUC) on page load
  - MUST apply theme class to <html> element before React hydration
  - MUST use Tailwind's dark: variant (no custom CSS variables for theme)
  - MUST NOT store theme preference in cookies (use API or localStorage)
  - MUST debounce theme toggle to prevent rapid API calls
  - MUST handle API failure gracefully (apply theme locally even if save fails)
  - MUST NOT introduce new dependencies (no theme libraries)
  - MUST respect prefers-reduced-motion for theme transitions
  - MUST ensure all existing Tailwind classes work correctly in dark mode
  - Toggle MUST be accessible (keyboard operable, screen reader labels)
```

### Шаг 5: определить тестирование

Какие тесты проверяют, что реализация соответствует спецификации?

```yaml
testing:
  unit:
    - Toggle renders with correct icon for current theme
    - Toggle cycles through light → dark → system options
    - Theme class is applied to document.documentElement
    - System theme matches OS preference via matchMedia
    - Preference is saved to API on change (authenticated user)
    - Preference is saved to localStorage on change (anonymous user)
  integration:
    - Full cycle: change theme → reload page → theme persists
    - System mode responds to OS theme change
    - Login syncs localStorage preference to API
  visual:
    - No FOUC on initial page load
    - Smooth transition between themes (if motion allowed)
  accessibility:
    - Toggle is keyboard operable
    - Current theme is announced to screen readers
```

### Полная спецификация

Собирая всё вместе, мы получаем всеобъемлющую микро-спецификацию, которую любая модель ИИ может использовать для генерации согласованной качественной реализации тёмной темы. Спецификация — около 80 строк. Сгенерированный код может быть 200–400 строк. Но эти 80 строк гарантируют, что 200–400 строк кода *верны* — соответствуют замыслу команды, соблюдают конвенции проекта и избегают частых ловушек.

---

## 3.10 Оценка качества спецификации

Как понять, хороша ли спецификация? Вот рубрика для оценки любой микро-спецификации:

### Полнота (0–10)

- Включает ли контекст технологический стек?
- Описывает ли контекст существующие шаблоны и конвенции?
- Определяет ли контекст точки интеграции?
- Есть ли у цели ясное краткое описание?
- Есть ли у цели проверяемые критерии приёмки?
- Явно ли указаны включаемые И исключаемые элементы объёма?
- Есть ли технические ограничения?
- Есть ли ограничения безопасности?
- Есть ли ограничения доступности?
- Определены ли тесты для каждого критерия приёмки?

### Ясность (0–5)

- Однозначен ли каждый критерий приёмки?
- Используют ли ограничения словарь MUST/MUST NOT?
- Смог бы разработчик, никогда не видевший кодовую базу, реализовать это только по спецификации?
- Есть ли расплывчатые термины («быстро», «хорошо», «современно», «чисто»)?
- Ясна ли граница объёма?

### Уместность детализации (0–5)

- Избегает ли спецификация деталей реализации (имена переменных, значения CSS)?
- Сосредоточена ли спецификация на поведении, а не структуре?
- Значительно ли спецификация короче ожидаемого кода?
- Может ли реализация измениться без изменения спецификации?
- Сосредоточены ли ограничения на качествах (безопасность, производительность), а не на реализации?

Оценка 15+ из 20 указывает на высококачественную спецификацию. Ниже 10 — спецификацию нужно доработать перед генерацией кода.

---

## 3.11 Шаблоны и отправные точки

Чтобы написание спецификаций стало практичным, вот шаблоны для распространённых типов.

### Шаблон спецификации компонента

```yaml
kind: Component
metadata:
  name: [ComponentName]
  module: [feature-domain]
  version: 1.0.0
  system_spec: system.spec.yaml@[version]

context:
  description: >
    [Why does this component need to exist? What problem does it solve?]
  technical_context: >
    [What APIs, types, and existing components does it interact with?]

objective:
  summary: >
    [One sentence: Create/Add/Modify [what] that [purpose].]
  acceptance_criteria:
    - [Testable criterion 1]
    - [Testable criterion 2]
    - [...]
  scope:
    includes:
      - [Explicit capability 1]
    excludes:
      - [Explicit exclusion 1]

constraints:
  - MUST [technical requirement]
  - MUST NOT [technical prohibition]
  - MUST [security requirement]
  - MUST [accessibility requirement]

testing:
  unit:
    - [Test case derived from acceptance criterion]
  accessibility:
    - [Accessibility test case]
```

### Шаблон спецификации конечной точки API

```yaml
kind: Endpoint
metadata:
  name: [EndpointName]
  module: [feature-domain]
  version: 1.0.0
  system_spec: system.spec.yaml@[version]

context:
  description: >
    [Why does this endpoint need to exist?]
  technical_context: >
    [Database tables, existing services, authentication requirements]

endpoint:
  method: [GET|POST|PUT|DELETE|PATCH]
  path: /api/[resource]
  authentication: [required|optional|none]
  authorization: [roles that can access]

request:
  params:
    - name: [param]
      type: [string|number|boolean]
      required: [true|false]
      description: [what it is]
      validation: [rules]
  body:
    type: object
    properties:
      [field]:
        type: [type]
        required: [true|false]
        validation: [rules]

response:
  success:
    status: [200|201|204]
    body:
      type: object
      properties:
        [field]:
          type: [type]
  errors:
    - status: 400
      condition: [when this error occurs]
      body: { error: "[message]" }
    - status: 401
      condition: Unauthenticated request
    - status: 403
      condition: Insufficient permissions
    - status: 404
      condition: Resource not found

constraints:
  - MUST validate all input before processing
  - MUST NOT expose internal error details
  - MUST [rate limiting requirement]
  - MUST [data access constraint]

testing:
  unit:
    - [Test case for success path]
    - [Test case for each error condition]
  integration:
    - [Test case for database interaction]
  security:
    - [Test for authentication requirement]
    - [Test for authorization requirement]
    - [Test for input validation]
```

Эти шаблоны — отправные точки, а не жёсткие формы. Адаптируйте их под нужды проекта. Важно, чтобы каждая спецификация покрывала три столпа — контекст, цель, ограничения — и каждый столп был достаточно подробен, чтобы направлять генерацию кода ИИ.

---

## Итоги главы

| Понятие | Ключевой вывод |
|---|---|
| Три столпа | В каждой микро-спецификации есть контекст (что существует), цель (что должно измениться) и ограничения (чего не должно произойти). |
| Контекст снижает галлюцинации | Явный контекст даёт ИИ заземлённую информацию вместо средних значений из обучающих данных. |
| Цель определяет полноту | Критерии приёмки говорят ИИ, когда он закончил. Объём определяет границы. |
| Ограничения предотвращают плохие решения | Правила MUST/MUST NOT переопределяют поведение ИИ по умолчанию и предотвращают проблемы безопасности, производительности и согласованности. |
| Принцип дельты | Спецификации описывают изменения, а не состояния. Это держит ИИ сфокусированным на новом. |
| Золотая середина | Специфицируйте что и почему, а не как. Избегайте и недостаточной (слишком расплывчатой), и избыточной (слишком подробной) спецификации. |
| Отраслевые параллели | Схемы функций OpenAI, определения инструментов Anthropic и объявления функций Google следуют шаблону «контекст — цель — ограничения». |
| Рубрика качества | Оценивайте спецификации по полноте (0–10), ясности (0–5) и уместности детализации (0–5). |

---

## Вопросы для обсуждения

1. Возьмите функцию, которую вы недавно построили, и напишите раздел «Контекст» её микро-спецификации. Какую информацию понадобилось бы ИИ, которую вы считаете само собой разумеющейся, потому что знакомы с кодовой базой?

2. Посмотрите на пример «избыточной спецификации» в разделе 3.7. Почему указание пиксельных значений CSS в спецификации — проблема? Где должны жить детали визуального дизайна, если не в спецификации?

3. Глава утверждает, что ограничения — «самая важная часть спецификации». Вы согласны? Можете ли вспомнить ограничение, отсутствие которого привело бы к серьёзному дефекту?

4. Сравните структуру микро-спецификации (контекст, цель, ограничения) с тикетом Jira. Что фиксирует микро-спецификация, чего обычно не фиксирует тикет? Что фиксирует тикет, чего обычно не фиксирует микро-спецификация?

---

*Далее: глава 4 — «Практика: от вайба к спецификации»*
