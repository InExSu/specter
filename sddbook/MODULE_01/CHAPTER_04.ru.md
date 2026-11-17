# Глава 4: Практика — от вайба к спецификации

## МОДУЛЬ 01 — Основы: мышление «контрактами»

> [Оглавление курса](../INDEX.ru.md) · [Модуль 01](../INDEX.ru.md#модуль-01--основы-мышление-контрактами)

---

### Вступление к лекции

*Хорошо. Хватит теории. Сегодня день практикума.*

*Последние три главы я рассказывал, почему спецификации важны, что делает спецификацию хорошей и как спецификации вписываются в процесс разработки. Сегодня вы будете это делать. Мы возьмём реальные «вайб-промпты» — то, что разработчики на самом деле печатают в ИИ-ассистентах каждый день, — и превратим их в структурированные спецификации.*

*Здесь теория встречается с практикой. Знать теорию спецификаций — как знать теорию плавания: полезно, но в первый раз в бассейне вы всё равно наглотаетесь воды. Так что заходим в бассейн.*

*Я проведу вас через три упражнения, каждое сложнее предыдущего. Для каждого покажу вайб-промпт, разберу, почему он проблематичен, и затем вместе с вами построю спецификацию шаг за шагом. После упражнений разберём частые антишаблоны и построим чек-лист качества, который вы сможете применять к своим спецификациям.*

*Открывайте редакторы. Это практическая глава.*

---

## 4.1 Анатомия вайб-промпта

Прежде чем начать рефакторинг, поймём, *из чего* мы рефакторим. У «вайб-промпта» есть узнаваемые черты:

1. **Разговорный тон.** Он читается как то, что вы сказали бы коллеге, а не как то, что вы поместили бы в технический документ.

2. **Неявные допущения.** Он предполагает, что ИИ знает ваш проект, ваш стек, ваши конвенции и ваши предпочтения.

3. **Расплывчатый объём.** Он описывает общую область работы, но не точные границы.

4. **Отсутствующие ограничения.** Он говорит, что строить, но не чего избегать.

5. **Нет критериев успеха.** Объективно определить правильность вывода невозможно.

6. **Эфемерность.** Он существует в окне чата и будет потерян после сессии.

Классический вайб-промпт:

```
Hey, can you build me a todo list app with React? I want to be able to
add, edit, and delete todos. Make it look nice.
```

В этом промпте примерно 25 слов и примерно 200 неявных решений. Посчитаем некоторые:

- «React» — какая версия? С TypeScript? Какой сборщик?
- «todo list app» — полное приложение или компонент? Какой роутинг?
- «add» — какие поля? Только заголовок? Заголовок + описание? Срок? Приоритет?
- «edit» — редактирование на месте? Модальное окно? Отдельная страница?
- «delete» — мягкое удаление? Жёсткое? Диалог подтверждения?
- «look nice» — какая дизайн-система? Какая цветовая схема? Адаптивность?
- (Не упомянуто) — сохранение? localStorage? База данных? API?
- (Не упомянуто) — аутентификация? Мультипользовательность?
- (Не упомянуто) — тестирование? Доступность? Обработка ошибок?

Разработчик знает ответы на большинство этих вопросов. Он просто их не набрал. И ИИ ответит на каждый из них молча, вероятностно, на основе обучающих данных.

---

## 4.2 Упражнение 1: простая CRUD-функция

### Вайб-промпт

```
I need a user management page. It should show all users in a table,
let me add new users, edit existing ones, and delete them. We're using
React and TypeScript. The API is at /api/users.
```

Это, вообще-то, промпт лучше среднего. Он упоминает стек и API. Но в нём всё ещё значительные пробелы. Разберём их.

### Анализ пробелов

| Что сказано | Что отсутствует |
|---|---|
| «user management page» | Какие поля у пользователя? Какова модель данных? |
| «show all users in a table» | Какие колонки? Пагинация? Сортировка? Фильтрация? |
| «add new users» | Какие поля формы? Правила валидации? Модальное окно или страница? |
| «edit existing ones» | Редактирование на месте или отдельная форма? Какие поля редактируемы? |
| «delete them» | Мягкое или жёсткое удаление? Подтверждение? Авторизация? |
| «React and TypeScript» | Какие версии? Какие ещё библиотеки? |
| «API at /api/users» | Какие HTTP-методы? Какие формы запроса/ответа? |
| (Не упомянуто) | Состояния загрузки, ошибки, пустые состояния |
| (Не упомянуто) | Доступность, адаптивный дизайн |
| (Не упомянуто) | Авторизация (кто может CRUD пользователей?) |
| (Не упомянуто) | Существующие шаблоны и конвенции кодовой базы |

### Построение спецификации

Превратим это в полноценную микро-спецификацию. Буду строить по разделам.

**Шаг 1: метаданные**

```yaml
kind: Feature
metadata:
  name: UserManagement
  module: admin
  version: 1.0.0
  system_spec: system.spec.yaml@3.1.0
```

Уже мы приняли решение, которое вайб-промпт оставил неявным: это функция *администратора*. Это влияет на авторизацию, размещение в приложении и дизайн UI.

**Шаг 2: контекст**

```yaml
context:
  description: >
    The admin section of the application currently has a dashboard
    and a settings page but no user management. Administrators need
    to view, create, edit, and deactivate user accounts. The backend
    API for user CRUD operations has been built and deployed.

  technical_context: >
    User API:
      GET    /api/users         → { users: User[], total: number, page: number }
      GET    /api/users/:id     → User
      POST   /api/users         → User (created)
      PUT    /api/users/:id     → User (updated)
      DELETE /api/users/:id     → { success: boolean } (soft-delete)

    User type:
      {
        id: string (UUID),
        email: string,
        name: string,
        role: "admin" | "editor" | "viewer",
        status: "active" | "inactive",
        createdAt: string (ISO 8601),
        lastLoginAt: string | null (ISO 8601)
      }

    Pagination: API supports ?page=N&limit=N (default limit 20, max 100)
    Sorting: API supports ?sort=field&order=asc|desc
    Filtering: API supports ?status=active|inactive&role=admin|editor|viewer

    Existing admin layout: AdminLayout component with sidebar navigation.
    Existing components: DataTable, Modal, FormField, ErrorBanner, Skeleton.

  related_specs:
    - auth.spec.yaml  # Role-based access control
    - admin-layout.spec.yaml  # Admin section layout and navigation
```

Обратите внимание, насколько это богаче вайб-промпта. Мы указали:

- Точный контракт API (конечные точки, методы, формы запроса/ответа)
- Полную модель данных с типами
- Возможности пагинации, сортировки и фильтрации
- Существующие компоненты для переиспользования
- Контекст вёрстки
- Связанные спецификации для сквозных задач

**Шаг 3: цель**

```yaml
objective:
  summary: >
    Create a user management interface in the admin section that allows
    administrators to list, create, edit, and deactivate user accounts.

  acceptance_criteria:
    # List View
    - User table displays columns: Name, Email, Role, Status, Last Login
    - Table is paginated with 20 users per page
    - Table supports sorting by any column (click column header)
    - Table supports filtering by Status and Role (dropdown filters)
    - Table shows total user count and current page
    - Empty state shows "No users found" message with appropriate context

    # Create User
    - "Create User" button opens a modal form
    - Form fields: Name (required), Email (required), Role (required, dropdown)
    - Email field validates email format
    - Name field requires minimum 2 characters
    - Form shows validation errors inline
    - Successful creation closes modal and refreshes table
    - Duplicate email shows specific error message from API

    # Edit User
    - Clicking a table row opens an edit modal pre-filled with user data
    - Edit form has same fields as create, plus Status toggle
    - Email field is read-only in edit mode (cannot change email)
    - Changes are saved on form submission
    - Successful save closes modal and refreshes table row

    # Deactivate User
    - Each row has a "Deactivate" action (visible on hover or in menu)
    - Deactivating shows a confirmation dialog with user's name
    - Confirmation dialog requires typing "DEACTIVATE" to proceed
    - Deactivation calls DELETE endpoint (soft-delete)
    - Deactivated users show "Inactive" status in table
    - Already inactive users show a "Reactivate" action instead

    # States
    - Loading state shows Skeleton component in table area
    - Error state shows ErrorBanner with retry button
    - Optimistic updates for status changes

  scope:
    includes:
      - User list table with pagination, sorting, filtering
      - Create user modal form
      - Edit user modal form
      - Deactivate/reactivate user action
      - Input validation (client-side)
    excludes:
      - User profile detail page (separate spec)
      - Password reset for users
      - Bulk operations (multi-select, bulk delete)
      - CSV import/export of users
      - User activity log / audit trail
      - Email notifications on user changes
```

Сравните с «add, edit, and delete» из вайб-промпта. Критерии приёмки делают каждое поведение явным и проверяемым. Раздел объёма не даёт ИИ построить функции вроде CSV-экспорта или массового удаления, которые «страница управления пользователями» могла бы разумно включать.

**Шаг 4: ограничения**

```yaml
constraints:
  # Technical
  - MUST use existing DataTable component for the table
  - MUST use existing Modal component for create/edit forms
  - MUST use existing FormField component for form inputs
  - MUST use React Query for all API interactions
  - MUST NOT introduce new dependencies
  - MUST use Zod for form validation schema

  # Security
  - MUST require "admin" role to access this page (redirect others)
  - MUST NOT display user passwords or password hashes
  - MUST NOT allow an admin to deactivate their own account
  - MUST NOT allow changing a user's email (immutable after creation)
  - MUST sanitize all user-provided text before rendering

  # Performance
  - MUST NOT fetch all users at once (use pagination)
  - MUST debounce filter changes at 300ms
  - MUST cancel in-flight requests when filters change
  - Table MUST use virtualization if more than 100 visible rows

  # Accessibility
  - Table MUST have proper ARIA table roles
  - Sort buttons MUST announce sort direction to screen readers
  - Modal focus MUST be trapped when open
  - Form errors MUST be associated with inputs via aria-describedby
  - Confirmation dialog MUST be announced to screen readers
```

**Шаг 5: тестирование**

```yaml
testing:
  unit:
    # List
    - Table renders with correct columns
    - Pagination navigates between pages
    - Sorting toggles on column header click
    - Filters update the query parameters
    - Empty state renders when no users match
    - Loading state renders Skeleton component
    - Error state renders ErrorBanner with retry

    # Create
    - Create modal opens on button click
    - Form validates required fields
    - Form validates email format
    - Form validates name minimum length
    - Successful creation closes modal
    - API error shows error message

    # Edit
    - Edit modal opens with pre-filled data
    - Email field is read-only
    - Changes are submitted on save
    - Successful save closes modal

    # Deactivate
    - Confirmation dialog appears on deactivate click
    - Typing "DEACTIVATE" enables confirm button
    - Confirmation calls DELETE endpoint
    - Status updates in table after deactivation

  integration:
    - Full create → appear in list cycle
    - Full edit → see changes in list cycle
    - Deactivate → status change in list cycle
    - Filter and sort persist across pagination

  accessibility:
    - Page is navigable by keyboard alone
    - Screen reader announces table content correctly
    - Modal trap focus works correctly
    - Form validation errors are announced
```

### Полное превращение

Поставим исходный вайб-промпт рядом со спецификацией и оценим разницу:

**Вайб-промпт:** 32 слова, ~200 неявных решений, эфемерный, без критериев проверки.

**Спецификация:** ~150 строк, каждое значимое решение явно, версионируется, тестируема, рецензируема.

Написание спецификации заняло, возможно, 20 минут. Вайб-промпт — 15 секунд. Но спецификация сэкономит часы переделок, повторных промптов и отладки. Она даст согласованный код независимо от модели ИИ. Она послужит документацией для будущих разработчиков. И она не даст ИИ молча принять решения о безопасности, доступности, объёме и поведении, которые могут не совпасть с вашим замыслом.

> **Заметка профессора:** Хочу быть честным насчёт экономики. Двадцать минут на спецификацию функции, реализация которой займёт пару часов, кажется много. Но подумайте: без спецификации вы можете потратить 30 минут на повторные промпты, 20 минут на исправление решений ИИ по безопасности, 15 минут на корректировку объёма и 30 минут на выяснение, почему сгенерированный код не соответствует существующим шаблонам. Спецификация — не дополнительное время. Это время, *вложенное вперёд*, устраняющее боль в конце.

---

## 4.3 Упражнение 2: запрос UI-компонента

### Вайб-промпт

```
Build me a date picker component. It should look modern and work well on mobile.
```

Это обманчиво простой запрос, скрывающий огромную сложность. Выбор даты — один из самых сложных UI-компонентов в веб-разработке, затрагивающий интернационализацию, часовые пояса, доступность, совместимость браузеров и пользовательский опыт.

### Анализ пробелов

| Что сказано | Что отсутствует |
|---|---|
| «date picker component» | Одна дата? Диапазон? Несколько? |
| «look modern» | Совершенно неопределённый эстетический критерий |
| «work well on mobile» | Размеры целей касания? Нативный fallback? Адаптивная вёрстка? |
| (Не упомянуто) | Формат даты (ISO, американский, европейский?) |
| (Не упомянуто) | Ограничения min/max даты |
| (Не упомянуто) | Недоступные даты |
| (Не упомянуто) | Выбор времени? Только дата? |
| (Не упомянуто) | Локаль/интернационализация |
| (Не упомянуто) | Интеграция (библиотека форм? самостоятельный?) |
| (Не упомянуто) | Доступность (клавиатура, скринридер) |
| (Не упомянуто) | Существующие библиотеки дат в проекте |

«Look modern» особенно проблематично. Для ИИ это ничего не значит. Понятие «современного» у ИИ — то, что чаще всего встречалось в обучающих данных, статистическое среднее дизайнов 2020–2025 годов. Ваше понятие «современного» — то, что решила ваша команда дизайна, и оно может быть очень конкретным.

### Построение спецификации

```yaml
kind: Component
metadata:
  name: DatePicker
  module: shared
  version: 1.0.0
  system_spec: system.spec.yaml@3.1.0

context:
  description: >
    The application has several forms that require date input
    (event scheduling, report filtering, user profile birthday).
    Currently, these use native HTML date inputs, which have
    inconsistent UX across browsers and do not support our design
    system. We need a custom date picker that integrates with
    our existing form library and design tokens.

  technical_context: >
    Form handling: React Hook Form v7 with Controller component.
    Date library: date-fns v3 is already installed and used for
    date formatting throughout the app.
    Design tokens: Tailwind CSS with custom theme colors defined
    in tailwind.config.ts (colors.primary, colors.surface, etc.).
    Localization: The app supports en-US and es-MX locales via
    the existing i18n system (react-intl).
    Existing components:
      - Popover component at /shared/components/Popover.tsx
      - IconButton component at /shared/components/IconButton.tsx
      - FormField component at /shared/components/FormField.tsx
        (wraps inputs with label, error message, description)

  assumptions:
    - Only date selection needed (no time picker for v1)
    - Only single date selection (no range picker for v1)
    - Calendar starts on Sunday for en-US, Monday for es-MX
    - Minimum supported date: 1900-01-01
    - Maximum supported date: 2100-12-31

objective:
  summary: >
    Create a reusable DatePicker component that integrates with
    React Hook Form and the existing design system, replacing
    native HTML date inputs across the application.

  acceptance_criteria:
    # Core Interaction
    - Text input field displays the selected date in locale-appropriate format
    - Clicking the input (or calendar icon) opens a calendar popover
    - Calendar shows a month view with selectable day cells
    - Clicking a day selects it and closes the popover
    - Month/year navigation via previous/next arrow buttons
    - Year can be jumped to via a year dropdown (range: 1900-2100)
    - Selected date is highlighted in the calendar
    - Today's date has a distinct visual indicator
    - Clicking outside the popover closes it

    # Text Input
    - User can type a date directly in the input field
    - Typed dates are parsed on blur using date-fns parse
    - Invalid date input shows validation error
    - Input placeholder shows expected format (e.g., "MM/DD/YYYY")

    # Integration
    - Works as a controlled component with React Hook Form Controller
    - Exposes value as ISO 8601 date string (YYYY-MM-DD)
    - Supports min and max date props
    - Supports disabled dates via a predicate function
    - Supports required, disabled, and read-only states
    - Triggers onChange and onBlur callbacks

    # Mobile
    - On screens < 640px, calendar renders as a bottom sheet (not popover)
    - Touch targets are minimum 44x44px
    - Swipe gestures for month navigation on touch devices
    - No hover-dependent interactions

    # Locale
    - Date format adapts to current locale (MM/DD/YYYY vs DD/MM/YYYY)
    - Day names and month names are localized
    - Calendar start day adapts to locale

  scope:
    includes:
      - DatePicker component with calendar popover
      - Text input with date parsing
      - Month/year navigation
      - React Hook Form integration
      - Locale support (en-US, es-MX)
      - Mobile-responsive layout
    excludes:
      - Time picker (separate component for v2)
      - Date range picker (separate component for v2)
      - Multi-date selection
      - Week number display
      - Holiday/event indicators on calendar
      - Custom day cell rendering

constraints:
  # Technical
  - MUST use date-fns for all date operations (no moment.js, no dayjs)
  - MUST use existing Popover component for desktop calendar display
  - MUST NOT introduce new npm dependencies
  - MUST work with React Hook Form Controller pattern
  - MUST expose a ref for form registration
  - Value MUST always be ISO 8601 format (YYYY-MM-DD) or null

  # Performance
  - MUST lazy-load the calendar popover (not in initial bundle)
  - Calendar render MUST NOT cause layout shift in the form
  - MUST NOT re-render parent form on internal state changes
  - MUST memoize calendar day cells to prevent unnecessary re-renders

  # Accessibility
  - MUST implement ARIA date picker pattern (role="dialog" for calendar)
  - Calendar MUST be navigable by keyboard (arrow keys for days)
  - Month navigation MUST be accessible via keyboard (Page Up/Page Down)
  - Selected date MUST be announced to screen readers
  - Disabled dates MUST have aria-disabled and not be focusable
  - MUST support Escape to close calendar and return focus to input
  - MUST NOT trap focus when opened as popover (trap only in bottom sheet)
  - Input MUST have associated label (via FormField wrapper)
  - Error messages MUST be linked via aria-describedby

  # UX
  - MUST NOT allow selecting dates outside min/max range
  - MUST visually distinguish disabled dates from selectable dates
  - MUST show current month on open (or month containing selected date)
  - Calendar MUST NOT flash or shift when navigating months
  - MUST provide clear visual feedback for hover, focus, and selected states

testing:
  unit:
    - Renders with no selected date (shows placeholder)
    - Renders with pre-selected date (shows formatted date)
    - Calendar opens on input click
    - Calendar opens on icon button click
    - Day selection updates the input value
    - Day selection closes the calendar
    - Month navigation shows previous/next month
    - Year dropdown changes the displayed year
    - Today's date has visual indicator
    - Min date prevents selecting earlier dates
    - Max date prevents selecting later dates
    - Disabled dates cannot be selected
    - Invalid typed input shows error
    - Valid typed input updates the value
    - ESC closes the calendar
    - Outside click closes the calendar

  integration:
    - Works with React Hook Form validation
    - Form submission includes the date value
    - Form reset clears the date value
    - Locale change updates date format and calendar

  accessibility:
    - Calendar is keyboard navigable (arrow keys)
    - Month navigation works with Page Up/Down
    - Selected date is announced by screen reader
    - Disabled dates are announced as disabled
    - Focus returns to input after calendar closes
    - Error messages are associated with input

  responsive:
    - Desktop: calendar renders as popover
    - Mobile (< 640px): calendar renders as bottom sheet
    - Touch targets meet 44x44px minimum
```

### Что изменилось от вайба к спецификации

Вайб-промпт — 15 слов. Спецификация — примерно 170 строк. Вот что добавляет спецификация:

1. **Конкретные проектные решения** вместо «look modern»: конкретные шаблоны взаимодействия, визуальные состояния и мобильное поведение.

2. **Точки интеграции** вместо самостоятельного компонента: React Hook Form, date-fns, существующие Popover и FormField.

3. **Контракт данных** вместо неоднозначности: значения ISO 8601, форматирование по локали, ограничения min/max.

4. **Доступность** вместо ничего: полная навигация с клавиатуры, поддержка скринридеров, ARIA-шаблоны.

5. **Мобильная стратегия** вместо «work well on mobile»: bottom sheet на маленьких экранах, минимальные цели касания, свайпы.

6. **Явный объём** вместо открытого: только одна дата, без времени, без диапазона, без кастомного рендеринга.

> **Заметка профессора:** Выбор даты — мой любимый пример для обучения SDD, потому что это компонент, который *все* считают простым и *никто* не делает правильно с первого раза. Число реализаций выбора даты, которые я видел недоступными, не учитывающими локаль или сломанными на мобильных, ошеломляет. Хорошая спецификация заставляет встретить сложность лицом к лицу заранее, до того как вы увязли в коде.

---

## 4.4 Упражнение 3: запрос конечной точки API

### Вайб-промпт

```
Create an API endpoint for uploading files. Users should be able to
upload documents and images. Store them in S3.
```

Этот промпт особенно опасен, потому что загрузка файлов — функция с серьёзными последствиями для безопасности. ИИ, генерирующий конечную точку загрузки файлов из этого промпта, может создать нечто работающее, но уязвимое к вредоносным загрузкам, атакам обхода путей, отказам в обслуживании через большие файлы или подделке запросов на стороне сервера.

### Анализ пробелов

| Что сказано | Что отсутствует |
|---|---|
| «uploading files» | Механизм загрузки (multipart? presigned URL? чанками?) |
| «documents and images» | Конкретные типы файлов? Ограничения размера? |
| «Store them in S3» | Какой бакет? Какая структура путей? Правила жизненного цикла? |
| (Не упомянуто) | Аутентификация и авторизация |
| (Не упомянуто) | Валидация файлов (тип, размер, содержимое) |
| (Не упомянуто) | Сканирование на вредоносное ПО |
| (Не упомянуто) | Ограничение частоты |
| (Не упомянуто) | Хранение метаданных (запись в БД для каждого файла?) |
| (Не упомянуто) | Контроль доступа (кто может смотреть загруженные файлы?) |
| (Не упомянуто) | Обработка ошибок (частичная загрузка, сбой сети) |
| (Не упомянуто) | Миниатюры или превью |
| (Не упомянуто) | Стратегия именования файлов (оригинальное имя? UUID?) |

### Построение спецификации

```yaml
kind: Endpoint
metadata:
  name: FileUpload
  module: files
  version: 1.0.0
  system_spec: system.spec.yaml@3.1.0

context:
  description: >
    The application needs to allow authenticated users to upload
    documents and images as attachments to projects. Currently
    there is no file upload capability. Files will be stored in
    AWS S3 and metadata will be stored in the application database.

  technical_context: >
    Backend: Express.js with TypeScript.
    Database: PostgreSQL with Prisma ORM.
    Storage: AWS S3, bucket "acme-app-uploads-prod".
    Auth: JWT middleware (req.user.id, req.user.role available).
    File processing: sharp library is available for image processing.
    Virus scanning: ClamAV service running at clamav:3310.

    Existing database tables:
      - projects (id, name, ownerId, ...)
      - project_members (projectId, userId, role)

    New table needed:
      - files (id, projectId, uploadedBy, originalName, storagePath,
              mimeType, sizeBytes, status, createdAt, deletedAt)

    S3 path convention: {projectId}/{fileId}/{filename}
    Max project storage: 5 GB per project
    Presigned URL strategy: Upload directly from client to S3
    using presigned POST URL (server never handles file bytes).

  assumptions:
    - ClamAV service is available and healthy
    - S3 bucket exists with proper IAM permissions
    - Client will handle the actual S3 upload using the presigned URL

objective:
  summary: >
    Create a two-step file upload flow: (1) server generates a
    presigned S3 URL and creates a pending file record, (2) client
    uploads directly to S3 and confirms completion.

  endpoints:
    - name: Request Upload URL
      method: POST
      path: /api/projects/:projectId/files/upload-url
      description: >
        Validates the upload request and returns a presigned S3 URL
        for direct client-to-S3 upload.
      request:
        params:
          - name: projectId
            type: string
            required: true
            description: Project to attach the file to
        body:
          type: object
          properties:
            fileName:
              type: string
              required: true
              description: Original file name
              validation: "Max 255 chars, no path separators"
            mimeType:
              type: string
              required: true
              description: MIME type of the file
              validation: "Must be in allowed types list"
            sizeBytes:
              type: number
              required: true
              description: File size in bytes
              validation: "Must be > 0 and <= 50MB"
      response:
        success:
          status: 201
          body:
            fileId: string
            uploadUrl: string (presigned S3 POST URL)
            fields: object (form fields for S3 POST)
            expiresAt: string (ISO 8601, 15 min from now)
        errors:
          - status: 400
            conditions:
              - Invalid MIME type
              - File too large
              - File name invalid
          - status: 401
            condition: Not authenticated
          - status: 403
            conditions:
              - Not a member of the project
              - Project storage quota exceeded
          - status: 404
            condition: Project not found
          - status: 429
            condition: Upload rate limit exceeded

    - name: Confirm Upload
      method: POST
      path: /api/projects/:projectId/files/:fileId/confirm
      description: >
        Client calls this after successful S3 upload. Server
        verifies the file exists in S3, triggers virus scan,
        and marks the file as active.
      request:
        params:
          - name: projectId
            type: string
            required: true
          - name: fileId
            type: string
            required: true
      response:
        success:
          status: 200
          body:
            file:
              id: string
              name: string
              mimeType: string
              sizeBytes: number
              url: string (CDN URL for access)
              status: "active"
              createdAt: string
        errors:
          - status: 400
            condition: File not found in S3
          - status: 401
            condition: Not authenticated
          - status: 403
            condition: Not the user who requested the upload
          - status: 404
            condition: File record not found
          - status: 409
            condition: File already confirmed

  acceptance_criteria:
    # Upload URL Generation
    - Validates user is authenticated and is a project member
    - Validates file name (no path traversal characters)
    - Validates MIME type against allowed list
    - Validates file size against 50MB maximum
    - Checks project storage quota before generating URL
    - Creates a "pending" file record in database
    - Generates presigned S3 POST URL with 15-minute expiration
    - S3 path follows convention: {projectId}/{fileId}/{sanitized-name}

    # Upload Confirmation
    - Verifies file exists at expected S3 path
    - Verifies file size in S3 matches declared size (within 1%)
    - Triggers asynchronous virus scan via ClamAV
    - Updates file status from "pending" to "active"
    - Returns CDN URL for file access

    # Background Processing
    - Pending files not confirmed within 1 hour are cleaned up (cron job)
    - Files flagged by ClamAV are quarantined (status: "quarantined")
    - Quarantined files are deleted from S3 within 24 hours

    # Rate Limiting
    - Maximum 10 upload URL requests per user per minute
    - Maximum 100 uploads per project per day

  scope:
    includes:
      - Presigned URL generation endpoint
      - Upload confirmation endpoint
      - File metadata storage in database
      - MIME type validation
      - File size validation
      - Project storage quota check
      - Virus scan trigger
      - Pending file cleanup logic
    excludes:
      - File download/access endpoint (separate spec)
      - File deletion endpoint (separate spec)
      - Image thumbnail generation (separate spec)
      - File versioning
      - Bulk upload
      - Resumable/chunked uploads
      - File sharing outside the project

constraints:
  # Security (CRITICAL)
  - MUST validate MIME type against allowlist, not blocklist
  - Allowed MIME types: image/jpeg, image/png, image/gif, image/webp,
    application/pdf, application/msword,
    application/vnd.openxmlformats-officedocument.wordprocessingml.document,
    text/plain, text/csv
  - MUST NOT trust client-declared MIME type alone (verify via file magic bytes after upload)
  - MUST sanitize file names (remove path separators, null bytes, special characters)
  - MUST NOT include user input in S3 key without sanitization
  - MUST use a UUID for the file ID (not sequential, not guessable)
  - Presigned URL MUST expire in 15 minutes maximum
  - MUST NOT return the raw S3 URL (return CDN URL only)
  - MUST verify that the confirming user is the same user who requested the URL
  - MUST NOT allow overwriting existing files (unique path per upload)
  - MUST run ClamAV scan on every uploaded file without exception
  - Quarantined files MUST NOT be accessible via CDN

  # Performance
  - Server MUST NOT receive or buffer file bytes (presigned URL only)
  - Database queries MUST use indexes on projectId and uploadedBy
  - Presigned URL generation MUST complete in < 200ms
  - Storage quota check MUST use a cached/aggregated value (not SUM query)

  # Data Integrity
  - File record MUST be created before presigned URL is returned
  - MUST use database transaction for file record creation
  - Pending cleanup job MUST NOT delete files that are being confirmed
  - MUST log all file operations for audit trail

  # Error Handling
  - MUST return specific, actionable error messages
  - MUST NOT expose S3 bucket name or internal paths in error messages
  - MUST NOT expose ClamAV details in error messages
  - Failed virus scans MUST NOT silently pass (fail closed)

testing:
  unit:
    # Upload URL
    - Returns 401 for unauthenticated requests
    - Returns 403 for non-project-members
    - Returns 400 for disallowed MIME types
    - Returns 400 for files exceeding 50MB
    - Returns 400 for file names with path traversal characters
    - Returns 403 when project storage quota is exceeded
    - Returns 429 when rate limit is exceeded
    - Returns 201 with valid presigned URL for valid requests
    - File record is created with "pending" status
    - S3 path follows naming convention
    - Presigned URL expires in 15 minutes

    # Upload Confirmation
    - Returns 404 for non-existent file records
    - Returns 403 if confirming user is not the uploader
    - Returns 400 if file not found in S3
    - Returns 409 if file already confirmed
    - Returns 200 and updates status to "active"
    - Triggers ClamAV scan
    - Returns CDN URL (not S3 URL)

    # File Name Sanitization
    - Removes path separators (/, \\)
    - Removes null bytes
    - Truncates to 255 characters
    - Preserves file extension
    - Handles unicode characters correctly

  integration:
    - Full upload flow: request URL → upload to S3 → confirm
    - Quota enforcement across multiple uploads
    - Rate limiting across multiple requests
    - Pending file cleanup after expiration

  security:
    - Path traversal in file name does not affect S3 key
    - Disallowed MIME type is rejected even if extension is allowed
    - Expired presigned URL is rejected by S3
    - Quarantined file is not accessible via CDN
    - File ID is not sequential or predictable
```

### Почему эта спецификация критична

Вайб-промпт загрузки файла — 22 слова. Спецификация — примерно 230 строк. Но посмотрите, что фиксирует спецификация и чего нет в промпте:

1. **Архитектуру presigned URL**, полностью убирающую байты файлов с сервера. Вайб-промпт, вероятно, породил бы обработчик multipart-загрузки, буферизующий файлы в памяти сервера, — нагрузку на производительность и риск безопасности.

2. **Пятнадцать ограничений безопасности**, предотвращающих реальные векторы атак: обход путей, подмену MIME-типа, перезапись файлов, ограничение частоты, сканирование вирусов.

3. **Двухшаговый поток** (запрос URL, подтверждение загрузки), правильно обрабатывающий шаблон presigned URL с корректным управлением состоянием.

4. **Обработку ошибок для каждого режима отказа** с конкретными кодами и условиями.

5. **Фоновую обработку** для очистки незавершённых файлов и сканирования вирусов.

Без этой спецификации ИИ почти наверняка сгенерировал бы более простую и менее безопасную реализацию. Он, вероятно:

- Принимал бы файл напрямую (multipart-загрузка на сервер)
- Хранил бы его в S3 без сканирования вирусов
- Использовал бы оригинальное имя файла без санирования
- Не проверял бы квоты хранилища
- Не реализовал бы ограничение частоты
- Возвращал бы сырой S3 URL
- Не обрабатывал бы шаг подтверждения
- Не очищал бы брошенные загрузки

Каждое из этих упущений — реальная уязвимость или операционная проблема. Спецификация предотвращает их все.

> **Заметка профессора:** Загрузка файлов — одна из функций, где спецификации важнее всего, потому что поверхность безопасности огромна, а последствия ошибки серьёзны. Если студент вынесет из этой главы только одно, надеюсь, это будет: чем чувствительнее функция к безопасности, тем подробнее должен быть раздел ограничений. Раздел ограничений — ваша позиция по безопасности для этой функции.

---

## 4.5 Распространённые антишаблоны промптинга (и как их исправляют спецификации)

Теперь, когда мы прошли три упражнения, каталогизируем антишаблоны, которые видим в вайб-промптах снова и снова, и сопоставим каждый с элементом спецификации, который его исправляет.

### Антишаблон 1: магическое слово

```
Make it look good.
Make it modern.
Make it fast.
Make it secure.
```

Это слова, которые кажутся значимыми, но не сообщают ничего конкретного. «Хорошо», «современно», «быстро» и «безопасно» — относительные термины, означающие разное для разных людей и разных моделей ИИ.

**Исправление спецификацией:** замените магические слова измеримыми критериями.

```yaml
# Instead of "make it fast":
constraints:
  - Page load MUST complete in under 2 seconds on 3G connection
  - API response time MUST be under 200ms at p95
  - Component MUST NOT cause layout shift (CLS < 0.1)

# Instead of "make it secure":
constraints:
  - MUST sanitize all user input with DOMPurify
  - MUST use parameterized queries (no string concatenation in SQL)
  - MUST validate CSRF token on all mutating requests
  - MUST NOT log sensitive data (passwords, tokens, PII)
```

### Антишаблон 2: подразумеваемый стек

```
Build me a login page.
```

Это не говорит ИИ ничего о технологическом стеке. Он выберет один на основе распределения обучающих данных — возможно, React, Vue, Angular, Svelte, чистый JS или что-то совсем другое.

**Исправление спецификацией:** явный раздел контекста с технологическим стеком.

```yaml
context:
  technical_context: >
    React 19, TypeScript 5.4, Tailwind CSS 4.0,
    React Hook Form v7, React Router v7.
    Auth API: POST /api/auth/login
```

### Антишаблон 3: отсутствующая граница

```
Add a notification system.
```

Без границы объёма ИИ решает, что входит в «систему уведомлений». Как мы видели в главе 1, он может сгенерировать email, SMS, push, in-app, аналитику, настройки, шаблоны и планирование.

**Исправление спецификацией:** явный объём с includes И excludes.

```yaml
scope:
  includes:
    - In-app toast notification component
    - Integration with background task completion events
  excludes:
    - Email notifications
    - Push notifications
    - SMS notifications
    - Notification preferences
    - Notification history
```

### Антишаблон 4: пропущенное отрицание

```
Build a comment system for blog posts.
```

Это говорит, что строить, но не чего избегать. ИИ может сгенерировать комментарии без модерации, защиты от спама, ограничения частоты, защиты от XSS, ограничений длины и лимитов вложенности ответов.

**Исправление спецификацией:** раздел ограничений с правилами MUST NOT.

```yaml
constraints:
  - MUST NOT render user-generated HTML (sanitize all content)
  - MUST NOT allow more than 3 levels of nesting for replies
  - MUST NOT allow comments longer than 5000 characters
  - MUST NOT allow more than 5 comments per user per minute
  - MUST NOT display comments flagged as spam
  - MUST NOT allow editing comments older than 15 minutes
```

### Антишаблон 5: контекстный вакуум

```
Add a "Mark as Complete" button to the task card.
```

Это предполагает, что ИИ знает, что такое «карточка задачи» в вашем приложении, что значит «завершено» в вашей модели данных, как выглядят существующие стили кнопок, какое управление состоянием использует карточка и какая конечная точка API обрабатывает завершение задачи.

**Исправление спецификацией:** раздел контекста с техническими деталями.

```yaml
context:
  technical_context: >
    TaskCard component at /features/tasks/components/TaskCard.tsx.
    Task type: { id: string, title: string, status: "todo" | "in_progress" | "done" }
    Update API: PUT /api/tasks/:id with { status: "done" }
    Existing button style: Use the existing SecondaryButton component.
    State: Task list is managed by React Query, key ["tasks", projectId].
    Optimistic updates are used for all task mutations.
```

### Антишаблон 6: запрос без тестов

```
Build the feature I described and make sure it works.
```

«Убедись, что работает» — не стратегия тестирования. Это не определяет, что значит «работает». Не указывает крайние случаи. Не описывает режимы отказа.

**Исправление спецификацией:** раздел тестирования с конкретными тестовыми случаями.

```yaml
testing:
  unit:
    - Button renders in "todo" and "in_progress" states
    - Button does NOT render in "done" state
    - Clicking button calls PUT /api/tasks/:id with { status: "done" }
    - Optimistic update shows "done" state immediately
    - Failed API call reverts to previous state
    - Button is disabled while API call is in flight
```

### Антишаблон 7: разговорный цикл отладки

Это не один промпт, а шаблон взаимодействия:

```
User: Build me a user profile page.
AI: [generates code]
User: No, I meant with an avatar.
AI: [regenerates with avatar]
User: The avatar should be editable.
AI: [adds upload functionality]
User: It should use our S3 bucket.
AI: [adds S3 integration, but now the form validation is gone]
User: Wait, where did the validation go?
AI: [adds it back but breaks the avatar upload]
```

Каждая итерация исправляет одно и потенциально ломает другое. Разработчик строит спецификацию инкрементально через разговор, но у ИИ нет постоянной полной картины требований.

**Исправление спецификацией:** напишите полную спецификацию заранее. Спецификация фиксирует все требования в одном месте. ИИ генерирует из полной картины, а не из развивающегося разговора.

```yaml
# One document captures everything:
# - Avatar upload with S3 integration
# - Form validation
# - Profile fields
# - Accessibility
# - Constraints
# No iterative degradation. No lost context.
```

---

## 4.6 Чек-лист качества спецификации

Вот практический чек-лист для оценки любой спецификации перед передачей ИИ. Распечатайте его. Приклейте на монитор. Пользуйтесь, пока не станет второй натурой.

### Чек-лист контекста

```
[ ] Указан технологический стек (язык, фреймворк, ключевые библиотеки)
[ ] Указаны релевантные версии библиотек
[ ] Описаны существующие шаблоны и конвенции
[ ] Определены точки интеграции (API, компоненты, сервисы)
[ ] Определены модели данных/типы с именами полей и типами
[ ] Связанные функции или спецификации указаны
[ ] Описано текущее состояние системы (что существует сейчас)
```

### Чек-лист цели

```
[ ] Краткое описание — ясное одно предложение о дельте
[ ] Краткое описание начинается с глагола действия (Create, Add, Modify, Remove)
[ ] Каждый критерий приёмки проверяем (бинарно да/нет)
[ ] Каждый критерий приёмки однозначен (одна интерпретация)
[ ] Критерии приёмки покрывают успешный путь
[ ] Критерии приёмки покрывают состояния ошибки/сбоя
[ ] Критерии приёмки покрывают крайние случаи
[ ] Раздел includes перечисляет, что ВХОДИТ в объём
[ ] Раздел excludes перечисляет, что НЕ входит в объём
[ ] Нет «магических слов» (good, modern, fast, clean, nice)
```

### Чек-лист ограничений

```
[ ] Технические ограничения указывают, какие библиотеки/шаблоны использовать
[ ] Технические ограничения указывают, что НЕ использовать
[ ] Ограничения безопасности касаются валидации ввода
[ ] Ограничения безопасности касаются раскрытия данных
[ ] Ограничения безопасности касаются аутентификации/авторизации
[ ] Ограничения производительности указывают измеримые пределы
[ ] Ограничения доступности указывают поддержку клавиатуры
[ ] Ограничения доступности указывают поддержку скринридеров
[ ] Все ограничения используют словарь MUST или MUST NOT
[ ] Применён тест «злонамеренного соответствия»
```

### Чек-лист тестирования

```
[ ] У каждого критерия приёмки есть хотя бы один тест
[ ] У каждого ограничения MUST есть хотя бы один тест
[ ] У каждого ограничения MUST NOT есть хотя бы один тест
[ ] Пути ошибок/сбоев покрыты тестами
[ ] Крайние случаи покрыты тестами
[ ] Требования доступности покрыты тестами
[ ] Тесты организованы по типам (unit, integration, accessibility)
```

### Мета-чек-лист

```
[ ] У спецификации есть номер версии
[ ] Спецификация ссылается на системную спецификацию
[ ] Спецификация включает метаданные (имя, модуль, владелец)
[ ] Спецификация короче ожидаемого кода
[ ] Спецификация сосредоточена на ЧТО и ПОЧЕМУ, а не КАК
[ ] Разработчик, не знакомый с кодовой базой, смог бы реализовать по этой спецификации
[ ] Спецификацию просмотрел хотя бы один другой человек
```

---

## 4.7 Процесс написания спецификации

Формализую процесс написания спецификации в повторяемый рабочий процесс:

### Фаза 1: сбор (5–10 минут)

Прежде чем написать строку спецификации, соберите нужную информацию:

1. **Прочитайте запрос функции.** Поймите, что просят.
2. **Исследуйте кодовую базу.** Поймите текущее состояние: что существует, какие шаблоны используются, какие компоненты/API доступны.
3. **Определите модель данных.** Какие типы, схемы и таблицы БД задействованы?
4. **Определите точки интеграции.** С какими API, компонентами и сервисами будет взаимодействовать функция?
5. **Определите заинтересованные стороны.** Кому важна эта функция? PM, безопасность, дизайн, QA?

### Фаза 2: черновик (10–15 минут)

Напишите первый черновик спецификации:

1. **Начните с контекста.** Сюда попадёт большая часть собранной информации.
2. **Напишите цель.** Сосредоточьтесь на критериях приёмки — это самая важная часть.
3. **Определите объём.** Будьте явны насчёт исключений.
4. **Напишите ограничения.** Примените тест «злонамеренного соответствия».
5. **Определите тесты.** Один тест на критерий приёмки, один на ограничение.

### Фаза 3: ревью (5–10 минут)

Проверьте спецификацию перед использованием:

1. **Прочитайте её как посторонний.** Смог бы кто-то незнакомый с проектом это реализовать?
2. **Примените чек-лист.** Пройдите по чек-листу качества пункт за пунктом.
3. **Спросите коллегу.** Пусть кто-то прочитает критерии приёмки и скажет, что, по его мнению, делает функция. Если его понимание не совпадает с вашим, спецификация неоднозначна.
4. **Проверьте магические слова.** Найдите расплывчатые термины и замените измеримыми критериями.

### Фаза 4: генерация и валидация (зависит от задачи)

Используйте спецификацию для генерации кода, затем проверьте:

1. **Передайте спецификацию ИИ.** Включите и микро-спецификацию, и системную спецификацию.
2. **Пройдитесь по критериям приёмки.** Для каждого критерия проверьте, что сгенерированный код его покрывает.
3. **Пройдитесь по ограничениям.** Для каждого ограничения проверьте, что код его соблюдает.
4. **Запустите сгенерированные тесты.** Проходят ли они? Действительно ли проверяют то, что заявляют?
5. **Если что-то не так, доработайте спецификацию.** Не патчите код. Исправьте спецификацию и перегенерируйте.

> **Заметка профессора:** Последний пункт критичен и неинтуитивен. Когда сгенерированный код неверен, инстинкт — исправить код. Сопротивляйтесь. Вместо этого спросите: «Что было неясно или упущено в спецификации, что привело ИИ к неверному коду?» Исправьте спецификацию, перегенерируйте, проверьте. Это создаёт добродетельный цикл: спецификации со временем становятся лучше, и каждая генерация точнее предыдущей. Если исправлять код, не исправляя спецификацию, вы снова столкнётесь с той же проблемой при следующей генерации.

---

## 4.8 От спецификации обратно к промпту: формат передачи

Студенты часто спрашивают на этом этапе: «У меня есть YAML-спецификация. Как мне на самом деле дать её ИИ?»

Есть несколько подходов:

### Подход 1: прямое включение спецификации

Просто включите спецификацию как есть в промпт ИИ:

```
Generate the implementation for the following spec:

---
kind: Component
metadata:
  name: DatePicker
  module: shared
...
```

Большинство современных моделей ИИ (Claude, GPT-4, Gemini) работают с YAML нативно и понимают структуру. Структурированный формат фактически помогает модели организовать вывод.

### Подход 2: спецификация + системный контекст

Включите и микро-спецификацию, и системную спецификацию:

```
System context:
[contents of system.spec.yaml]

Generate the implementation for the following feature spec:
[contents of feature.spec.yaml]
```

Это даёт ИИ полную картину: глобальные конвенции плюс требования конкретной функции.

### Подход 3: спецификация + существующий код

При изменении существующей функции включите спецификацию И текущий код:

```
Here is the current implementation:
[contents of existing Component.tsx]

Here is the updated spec:
[contents of updated spec.yaml]

Update the implementation to match the new spec. The changes
from the previous version are:
[diff of spec changes]
```

Этот подход мощно работает для инкрементальных изменений, потому что ИИ видит, где код сейчас и куда ему нужно прийти.

### Подход 4: автоматизированный конвейер

В зрелых процессах SDD генерация из спецификации автоматизирована. Конвейер CI/CD обнаруживает изменения спецификаций, передаёт их ИИ через API, генерирует код, запускает тесты и создаёт PR:

```typescript
// Simplified SDD pipeline (conceptual)

import { readSpec, readSystemSpec } from "./spec-reader";
import { generateCode } from "./ai-client";
import { runTests } from "./test-runner";
import { createPullRequest } from "./git-client";

async function processSpecChange(specPath: string) {
  const spec = await readSpec(specPath);
  const systemSpec = await readSystemSpec(spec.metadata.system_spec);

  const generatedCode = await generateCode({
    spec,
    systemSpec,
    model: "claude-opus-4-6",
    temperature: 0,
  });

  const testResults = await runTests(generatedCode.testFiles);

  if (testResults.allPassed) {
    await createPullRequest({
      title: `feat(${spec.metadata.module}): implement ${spec.metadata.name} v${spec.metadata.version}`,
      files: generatedCode.allFiles,
      description: `Generated from ${specPath} v${spec.metadata.version}`,
    });
  } else {
    // Log failures for human review
    console.error("Generated code did not pass spec-derived tests.");
    console.error(testResults.failures);
  }
}
```

Это эндшпиль SDD: человек пишет спецификацию, машина пишет код, а тесты (тоже выведенные из спецификации) проверяют результат. Работа человека смещается от *написания кода* к *написанию замысла* — и проверке, что замысел исполнен правильно.

---

## 4.9 Домашнее задание: преобразуйте собственный промпт

Вот ваше домашнее задание. Оно обязательное. Вы получите больше от одного этого упражнения, чем от чтения всех четырёх глав.

### Задание

1. **Найдите прошлый промпт.** Пролистайте историю чата с любым ИИ-ассистентом, которым пользуетесь. Найдите промпт, результат которого оказался не совсем правильным — где пришлось повторять промпт, чинить код вручную или вы получили не то, что ожидали.

2. **Проанализируйте пробелы.** Методом анализа пробелов из этой главы определите, чего не хватало вашему промпту. Какие решения ИИ принял, которых вы не указывали? Какие допущения сделал?

3. **Напишите микро-спецификацию.** Превратите промпт в полную микро-спецификацию по структуре трёх столпов (контекст, цель, ограничения). Оцените спецификацию по чек-листу качества.

4. **Перегенерируйте.** Передайте микро-спецификацию той же модели ИИ, которую использовали изначально. Сравните вывод с тем, что получили из исходного вайб-промпта.

5. **Отрефлексируйте.** Напишите краткую рефлексию (3–5 предложений):
   - Какие решения спецификация сделала явными, а промпт оставлял неявными?
   - Как вывод из спецификации отличается от вывода из промпта?
   - Что вы узнали о собственных допущениях, написав спецификацию?

### Критерии оценки

Ваша спецификация будет оцениваться по:

- **Полнота:** покрыты ли все три столпа с достаточной детализацией?
- **Ясность:** проверяем ли и однозначен ли каждый критерий приёмки?
- **Уместная детализация:** указано ли что и почему без указания как?
- **Ограничения:** есть ли значимые ограничения (не только технические, но и безопасности и доступности)?
- **Объём:** есть ли явные includes И excludes?

---

## 4.10 Что дальше

Вы завершили модуль 1: основы. Вы понимаете:

1. **Почему** спецификации важны (глава 1: естественный язык слишком неоднозначен для продакшн-софта)
2. **Какова** роль спецификации (глава 2: единый источник истины, управляющий кодом)
3. **Как** устроены спецификации (глава 3: контекст, цель, ограничения)
4. **Как** писать спецификации (глава 4: практическое превращение вайб-промптов)

В модуле 2 мы построим на этом фундаменте **язык спецификаций** — формальный синтаксис и семантику SDD-спецификаций. Вы узнаете о типах спецификаций (Component, Feature, Endpoint, Migration, Integration), композиции спецификаций (как спецификации ссылаются друг на друга и строятся друг на друге) и валидации спецификаций (как механически проверить, что спецификация хорошо оформлена).

Но прежде чем мы туда попадём, оставлю вас с мыслью.

Сдвиг от вайб-кодинга к разработке через спецификации — не просто изменение процесса. Это изменение *мышления*. Сдвиг от «я пишу код с помощью ИИ» к «я пишу спецификации, которые, оказалось, реализует ИИ». Работа человека — ясно выражать замысел. Работа ИИ — переводить этот замысел в работающий код. А спецификация — контракт между ними.

Когда вы пишете спецификацию, вы не занимаетесь бумажной работой. Вы не добавляете накладные расходы. Вы делаете *трудную часть* разработки ПО — решаете, что строить и что не строить, определяете границы системы, кодируете требования безопасности и доступности, создаёте проверяемое определение успеха.

Код — просто лёгкая часть. Любой (или что угодно) может написать код. Определять, что код должен делать, — точно, полно и ясно — это ремесло.

Добро пожаловать в Spec-Driven Development. Трудная, приносящая удовлетворение и ценная работа начинается здесь.

---

## Итоги главы

| Понятие | Ключевой вывод |
|---|---|
| Анатомия вайб-промпта | Вайб-промпты разговорны, неявны, расплывчаты, без ограничений, непроверяемы и эфемерны. |
| Анализ пробелов | Первый шаг написания спецификации — определить, что вайб-промпт оставляет несказанным. |
| Спецификация CRUD | Даже «простые» CRUD-функции скрывают десятки решений о модели данных, валидации, авторизации, состояниях и объёме. |
| Спецификация UI-компонента | Сложные компоненты (выбор даты и т.п.) требуют подробных спецификаций взаимодействия, доступности, интернационализации и мобильности. |
| Спецификация конечной точки API | Чувствительные к безопасности функции требуют обширных ограничений, чтобы предотвратить уязвимости, которые ИИ иначе проигнорирует. |
| Антишаблоны | Магические слова, подразумеваемый стек, отсутствующие границы, пропущенные отрицания, контекстные вакуумы, запросы без тестов и разговорные циклы отладки. |
| Чек-лист качества | Систематический чек-лист для оценки полноты, ясности, ограничений, тестирования и метаинформации спецификации. |
| Процесс написания | Сбор, черновик, ревью, генерация и валидация — повторяемый четырёхфазный процесс. |

---

## Вопросы для обсуждения

1. Посмотрите на три спецификации упражнений в этой главе. Какая, по вашему мнению, даст наибольшую разницу между версией из вайб-промпта и версией из спецификации? Почему?

2. Глава утверждает, что «исправлять спецификацию лучше, чем исправлять код». Можете ли вспомнить ситуацию, где это неверно — где прямая правка кода лучше?

3. Рассмотрите спецификацию загрузки файлов (упражнение 3). Там пятнадцать ограничений безопасности. Если бы нужно было выбрать три самых критичных, какие и почему?

4. Процесс написания спецификации описан как вложение 20–30 минут. Оправдано ли это для функции, реализация которой занимает 2 часа? А для функции на 20 минут?

5. Домашнее задание просит превратить один из ваших прошлых промптов в спецификацию. Прежде чем делать, предскажите: сколько неявных решений, по вашему мнению, содержал исходный промпт?

---

## Итоги модуля 1

Поздравляю. Вы завершили первый модуль Mastering Spec-Driven Development. Вот итог того, что вы узнали:

| Глава | Главный урок |
|---|---|
| Глава 1: От прозы к протоколу | Естественный язык слишком неоднозначен для ИИ-разработки. Отрасль эволюционировала от vibe coding к структурированному промптингу и разработке через спецификации. Более способному ИИ нужно больше структуры, а не меньше. |
| Глава 2: Единый источник истины | Спецификация — высшая инстанция над кодом. Спецификация = что + почему. Код = как. Когда они расходятся, побеждает спецификация. |
| Глава 3: Анатомия микро-спецификации | У каждой спецификации три столпа: контекст (что существует), цель (что должно измениться) и ограничения (чего не должно произойти). |
| Глава 4: От вайба к спецификации | Превращайте вайб-промпты в спецификации, анализируя пробелы, записывая структурированные контекст/цель/ограничения и проверяя чек-листом качества. |

Теперь у вас есть концептуальный фундамент SDD. В модуле 2 мы превратим эти концепции в строгую практику с формальными языками спецификаций, шаблонами композиции и автоматической валидацией.

До встречи в следующем модуле.

---

*Конец модуля 01: Основы — мышление «контрактами»*

*Далее: модуль 02 — Язык спецификаций*

---

[← Оглавление курса](../INDEX.ru.md) · [← Глава 3: Анатомия микро-спецификации](CHAPTER_03.ru.md) · [Глава 1: Проектирование от схем →](../MODULE_02/CHAPTER_01.ru.md)
