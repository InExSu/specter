# Глава 3: Стратегия контекстного окна

## МОДУЛЬ 03 — Валидация и петля обратной связи (средний уровень)

> [Оглавление курса](../INDEX.ru.md) · [Модуль 03](../INDEX.ru.md#модуль-03--валидация-и-петля-обратной-связи)

---

## Вступление к лекции

*Профессор рисует на доске большой прямоугольник и подписывает его «Context Window». Внутри прямоугольника он начинает заполнять его меньшими блоками: «System Prompt», «Spec A», «Spec B», «Spec C», «Code File 1», «Code File 2», «Conversation History». Прямоугольник заполняется быстро. Профессор обводит оставшееся свободное место — тонкую полоску внизу.*

Итак, вот о чём вам не расскажут, когда вы начинаете строить настоящие приложения с помощью ИИ.

Ваша спецификация — 4000 строк. Ваша кодовая база — 50 000 строк. История разговора растёт с каждым сообщением. А контекстное окно ИИ — весь объём информации, который он может «видеть» одновременно, — конечно.

*Показывает на тонкую полоску свободного места на доске.*

Вот сколько места у ИИ осталось, чтобы действительно *думать* над вашим запросом. Всё остальное — просто… контекст. И вот контринтуитивная часть: **больше контекста часто ухудшает работу ИИ, а не улучшает её.**

Сегодня мы научимся стратегически подходить к тому, что попадает в это окно. Мы построим «реестр спецификаций», который позволяет дать ИИ ровно тот контекст, который ему нужен, — не больше и не меньше. Мы разберёмся, почему Google вложился в контекстное окно Gemini на миллион токенов и почему это не решает проблему так, как вы, возможно, думаете. И мы изучим приёмы, которыми Claude Code от Anthropic и другие инструменты разработки с ИИ управляют контекстом в реальных кодовых базах.

Эта глава — об инженерной дисциплине управления контекстом. Это не блестящая тема. Но именно она отличает ИИ, который делает хорошую работу, от ИИ, который тонет в нерелевантной информации.

Погнали.

---

## 3.1 Понимание контекстных окон

### Что такое контекстное окно?

Контекстное окно — это общий объём текста (в токенах), который большая языковая модель может обработать за одно взаимодействие. Думайте о нём как о рабочей памяти ИИ — всё, что он может «видеть» сразу.

Токен — это примерно 3/4 английского слова, или около 4 символов. Значит:

| Контекстное окно | Примерно слов | Примерно страниц |
|---------------|-------------------|-------------------|
| 8K токенов    | ~6 000 слов       | ~12 страниц       |
| 32K токенов   | ~24 000 слов      | ~48 страниц       |
| 128K токенов  | ~96 000 слов      | ~192 страницы     |
| 200K токенов  | ~150 000 слов     | ~300 страниц      |
| 1M токенов    | ~750 000 слов     | ~1500 страниц     |
| 2M токенов    | ~1 500 000 слов   | ~3000 страниц     |

### Текущий ландшафт (2025–2026)

| Провайдер | Модель | Контекстное окно | Заметки |
|----------|-------|---------------|-------|
| Anthropic | Claude (Opus, Sonnet) | 200K токенов | Сильное удержание по всему окну |
| Google | Gemini 1.5 Pro/2.0 | 1M-2M токенов | Самый большой публично доступный контекст |
| OpenAI | GPT-4o/o1/o3 | 128K токенов | Зависит от варианта модели |
| Meta | Llama 3.x | 128K токенов | Открытый исходный код, расширяется сообществом |
| Mistral | Mistral Large | 128K токенов | Модель европейской разработки |

### Что на самом деле занимает контекстное окно

Когда вы общаетесь с ИИ-ассистентом по коду, контекстное окно расходуется на:

```
+--------------------------------------------------+
|              CONTEXT WINDOW (200K)                |
|                                                   |
|  +--------------------------------------------+  |
|  | System Prompt / Instructions     (~2-5K)   |  |
|  +--------------------------------------------+  |
|  | Project Configuration            (~1-3K)   |  |
|  | (.cursorrules, CLAUDE.md, etc.)             |  |
|  +--------------------------------------------+  |
|  | Referenced Files                 (~5-50K)   |  |
|  | (specs, code files, configs)                |  |
|  +--------------------------------------------+  |
|  | Conversation History             (~5-100K)  |  |
|  | (all previous messages in session)          |  |
|  +--------------------------------------------+  |
|  | Current Request                  (~0.5-5K)  |  |
|  +--------------------------------------------+  |
|  | REMAINING SPACE FOR REASONING    (varies)   |  |
|  | AND RESPONSE GENERATION                     |  |
|  +--------------------------------------------+  |
+--------------------------------------------------+
```

> **Заметка профессора:** Тонкий, но критичный момент. «Оставшееся место» нужно не только для текста ответа. Это ещё и пространство, которое модель использует для *рассуждения* — чтобы понять, какой код писать, как его структурировать, какие паттерны применить. Забивая контекстное окно под завязку справочным материалом, вы буквально сжимаете способность ИИ думать. Это как экзамен с открытой книгой, на который вы принесли столько справочников, что некуда положить черновик.

---

## 3.2 Почему больше контекста — не всегда лучше

### Проблема «иголки в стоге сена»

Это одно из самых изученных явлений в исследованиях LLM. Основной результат: с ростом длины контекста способность модели находить и использовать конкретные фрагменты информации *падает* — иногда резко.

Метафора: представьте, что вам нужно найти конкретное предложение (иголку) в документе на 500 страниц (стоге сена). Даже если модель технически «видит» все 500 страниц, её механизм внимания может не сфокусироваться на нужном предложении, когда это важно.

Исследования разных лабораторий стабильно показывают:

1. **Информация из середины контекста воспроизводится менее надёжно**, чем информация в начале или в конце. Это называют эффектом «потерянного в середине» (lost in the middle).

2. **Релевантной информацией, окружённой нерелевантной, труднее пользоваться**, чем той же информацией в сфокусированном контексте.

3. **Модель может смешивать или путать похожие, но разные фрагменты информации**, когда их слишком много одновременно.

### Практические следствия для SDD

Это значит: если вывалите в контекстное окно всю спецификацию (все 4000 строк) вместе с 20 файлами кода и длинной историей разговора, ИИ может:

- **Упустить критичные ограничения**, погребённые в середине спецификации
- **Перепутать требования из спецификации A с требованиями из спецификации B**
- **Применить паттерны из одной части кодовой базы в неподходящем контексте**
- **Сгенерировать код, который удовлетворяет одним требованиям спецификации и нарушает другие**

### Парадокс Google Gemini

Модели Gemini от Google предлагают контекстные окна в миллион токенов и больше — достаточно, чтобы вместить всю кодовую базу. Это впечатляющая инженерия, и она действительно полезна для некоторых задач (например, анализа всего репозитория или ответов на вопросы по множеству файлов).

Но вот парадокс: **огромное контекстное окно не значит, что его нужно использовать целиком.**

Собственная документация Google по Gemini Code Assist рекомендует давать сфокусированный, релевантный контекст, а не вываливать целые репозитории. Их внутренние исследования показали, что точечный отбор контекста даёт лучшие результаты, чем включение всего подряд, даже когда модель *может* обработать весь ввод.

Аналогия: в библиотеке миллионы книг. Вы *могли бы* прочитать все перед тем, как писать эссе. Но опытный исследователь отбирает 5–10 самых релевантных источников и читает их внимательно. То же нужно делать с контекстом для ИИ.

### Подход Anthropic: контекст нужного размера

Claude Code от Anthropic использует интересный подход. Вместо того чтобы пытаться загрузить в контекст всё, он:

1. **Читает конкретные файлы по необходимости** — с помощью инструментов смотрит именно те файлы, которые нужны
2. **Использует конфигурацию уровня проекта** (CLAUDE.md) как постоянный лёгкий контекст
3. **Поддерживает сценарий поиска и извлечения файлов**, позволяя ИИ находить релевантные файлы, а не предзагружать их
4. **Сохраняет контекст разговора**, но поощряет сфокусированные, ориентированные на задачу взаимодействия

Это «вытягивающая» модель управления контекстом: ИИ подтягивает нужное, когда это нужно, а не получает всё в контекст заранее.

---

## 3.3 Паттерн реестра: главный индекс спецификаций

### Что такое реестр спецификаций?

Реестр спецификаций — это главный индексный файл, каталогизирующий все спецификации проекта. Это оглавление вашей системы разработки через спецификации. ИИ читает реестр, чтобы понять, какие спецификации существуют и какие относятся к текущей задаче.

### Структура реестра

```markdown
# SPEC_REGISTRY.md

## Project: SaaS Dashboard v2

## Last Updated: 2026-02-20

## How to Use This Registry
This file lists all active specifications for the project.
When implementing a feature, find the relevant spec(s) below and
read them before writing any code.

---

## System-Level Specs

| ID | Name | Path | Status | Last Updated |
|----|------|------|--------|--------------|
| SYS-001 | Architecture Overview | `/specs/system/architecture.md` | Active | 2026-01-15 |
| SYS-002 | Authentication & Authorization | `/specs/system/auth.md` | Active | 2026-02-01 |
| SYS-003 | Database Schema | `/specs/system/database.md` | Active | 2026-02-10 |
| SYS-004 | API Design Standards | `/specs/system/api-standards.md` | Active | 2026-01-20 |
| SYS-005 | Error Handling Strategy | `/specs/system/error-handling.md` | Active | 2026-01-25 |
| SYS-006 | Security Requirements | `/specs/system/security.md` | Active | 2026-02-05 |

## Module-Level Specs

### User Management Module
| ID | Name | Path | Status | Dependencies |
|----|------|------|--------|-------------|
| USR-001 | User Registration | `/specs/modules/user/registration.md` | Active | SYS-002, SYS-003 |
| USR-002 | User Profile | `/specs/modules/user/profile.md` | Active | SYS-002, SYS-003 |
| USR-003 | User Settings | `/specs/modules/user/settings.md` | Active | SYS-002 |
| USR-004 | Team Management | `/specs/modules/user/teams.md` | Draft | SYS-002, SYS-003 |

### Billing Module
| ID | Name | Path | Status | Dependencies |
|----|------|------|--------|-------------|
| BIL-001 | Subscription Plans | `/specs/modules/billing/plans.md` | Active | SYS-003, SYS-004 |
| BIL-002 | Payment Processing | `/specs/modules/billing/payments.md` | Active | SYS-003, SYS-006 |
| BIL-003 | Invoice Generation | `/specs/modules/billing/invoices.md` | Active | SYS-003, BIL-001 |
| BIL-004 | Usage Metering | `/specs/modules/billing/metering.md` | Draft | SYS-003, BIL-001 |

### Dashboard Module
| ID | Name | Path | Status | Dependencies |
|----|------|------|--------|-------------|
| DSH-001 | Dashboard Layout | `/specs/modules/dashboard/layout.md` | Active | SYS-001 |
| DSH-002 | Analytics Widgets | `/specs/modules/dashboard/widgets.md` | Active | SYS-001, SYS-004 |
| DSH-003 | Real-time Updates | `/specs/modules/dashboard/realtime.md` | Active | SYS-001, SYS-004 |
| DSH-004 | Export & Reporting | `/specs/modules/dashboard/export.md` | Draft | SYS-004 |

### Notification Module
| ID | Name | Path | Status | Dependencies |
|----|------|------|--------|-------------|
| NTF-001 | Email Notifications | `/specs/modules/notifications/email.md` | Active | SYS-002 |
| NTF-002 | In-App Notifications | `/specs/modules/notifications/in-app.md` | Active | SYS-002, SYS-004 |
| NTF-003 | Webhook Integrations | `/specs/modules/notifications/webhooks.md` | Draft | SYS-004, SYS-006 |

## Component-Level Specs

| ID | Name | Path | Status | Parent |
|----|------|------|--------|--------|
| CMP-001 | DataTable Component | `/specs/components/data-table.md` | Active | DSH-001 |
| CMP-002 | Modal System | `/specs/components/modal.md` | Active | SYS-001 |
| CMP-003 | Form Builder | `/specs/components/form-builder.md` | Active | SYS-001 |
| CMP-004 | Chart Components | `/specs/components/charts.md` | Active | DSH-002 |
| CMP-005 | File Upload | `/specs/components/file-upload.md` | Active | SYS-006 |

## Cross-Cutting Specs

| ID | Name | Path | Status | Affects |
|----|------|------|--------|---------|
| XCT-001 | Styling Standards (Tailwind) | `/specs/cross-cutting/styling.md` | Active | All modules |
| XCT-002 | State Management (Zustand) | `/specs/cross-cutting/state.md` | Active | All modules |
| XCT-003 | Testing Standards | `/specs/cross-cutting/testing.md` | Active | All modules |
| XCT-004 | Accessibility (WCAG 2.1 AA) | `/specs/cross-cutting/accessibility.md` | Active | All modules |
| XCT-005 | Internationalization | `/specs/cross-cutting/i18n.md` | Draft | All modules |
| XCT-006 | Performance Budgets | `/specs/cross-cutting/performance.md` | Active | All modules |

---

## Dependency Graph

```
SYS-001 (Architecture)
  ├── DSH-001 (Dashboard Layout)
  │   ├── CMP-001 (DataTable)
  │   └── DSH-002 (Analytics Widgets)
  │       └── CMP-004 (Charts)
  ├── CMP-002 (Modal System)
  └── CMP-003 (Form Builder)

SYS-002 (Auth)
  ├── USR-001 (Registration)
  ├── USR-002 (Profile)
  ├── USR-003 (Settings)
  ├── USR-004 (Teams)
  ├── NTF-001 (Email)
  └── NTF-002 (In-App)

SYS-003 (Database)
  ├── USR-001 (Registration)
  ├── USR-002 (Profile)
  ├── BIL-001 (Plans)
  ├── BIL-002 (Payments)
  └── BIL-003 (Invoices)
```
```

### Почему паттерн реестра работает

Реестр решает три задачи одновременно:

1. **Обнаружение:** ИИ (или новый разработчик) быстро находит, какая спецификация относится к данной задаче. Вместо поиска по десяткам файлов он читает реестр.

2. **Определение границ:** реестр содержит информацию о зависимостях, поэтому ИИ знает не только *какую* спецификацию читать, но и *какие ещё спецификации связаны*. Реализуя USR-001 (регистрация пользователя), ИИ видит, что нужны также SYS-002 (аутентификация) и SYS-003 (база данных).

3. **Минимальный контекст:** сам реестр лёгкий — может быть, 2–3K токенов. Он даёт карту территории, не загружая всю территорию в контекст.

---

## 3.4 Иерархические спецификации: система, модуль, компонент

### Трёхуровневая иерархия

Самый эффективный способ организовать спецификации для управления контекстом — трёхуровневая иерархия:

```
Level 1: SYSTEM-LEVEL SPECS
  - Architecture decisions that affect everything
  - Technology choices, patterns, standards
  - Cross-cutting concerns (auth, logging, error handling)
  - ~5-10 specs total
  - Read when: starting a new module or making architectural decisions

Level 2: MODULE-LEVEL SPECS
  - Feature-area specifications
  - Business logic and domain rules
  - API contracts and data models
  - ~15-30 specs total
  - Read when: implementing a feature within a specific module

Level 3: COMPONENT-LEVEL SPECS
  - Individual UI component behavior
  - Specific function or service specifications
  - Detailed interaction patterns
  - ~30-100 specs total
  - Read when: implementing a specific component or function
```

### Как иерархия сокращает контекст

Без иерархии реализация одной функции может потребовать чтения 20+ файлов спецификаций. С иерархией:

```
Task: "Implement the DataTable component for the dashboard"

Without hierarchy:
  Load: ALL specs (~80 files, ~200K tokens) -- context window full

With hierarchy:
  Load: SPEC_REGISTRY.md              (~2K tokens) -- find relevant specs
  Load: XCT-001 (Styling Standards)   (~3K tokens) -- cross-cutting
  Load: XCT-004 (Accessibility)       (~2K tokens) -- cross-cutting
  Load: DSH-001 (Dashboard Layout)    (~4K tokens) -- parent module
  Load: CMP-001 (DataTable Component) (~5K tokens) -- specific component
  Total: ~16K tokens                  -- plenty of room for reasoning
```

Это сокращение использования контекста в 12 раз — при этом предоставлена *вся* релевантная информация.

### Суммаризация спецификаций

Каждая спецификация должна содержать в начале раздел с резюме, укладывающий ключевые ограничения в 5–10 строк. Это позволяет работать в «два прохода»:

**Проход 1: только резюме** — загрузите реестр и резюме потенциально релевантных спецификаций (~500 токенов каждое). Определите, какие спецификации действительно нужны.

**Проход 2: полные спецификации** — загрузите полный текст только тех спецификаций, что выбраны в проходе 1.

```markdown
# Spec: CMP-001 -- DataTable Component

## Summary
<!-- 5-10 lines capturing the essential constraints -->
- Renders tabular data with sorting, filtering, and pagination
- Uses TanStack Table (v8) for table logic
- Server-side pagination with cursor-based API
- Columns are configurable via a schema object
- Supports row selection (single and multi-select)
- Must meet WCAG 2.1 AA accessibility requirements
- All styling via Tailwind utility classes
- Responsive: stacks to card layout below 768px

## Full Specification
[... detailed spec follows, ~200-300 lines ...]
```

---

## 3.5 Как решить, какой контекст нужен ИИ

### Фреймворк принятия решения о контексте

Прежде чем поручить ИИ что-то сделать, пройдите по этому дереву решений:

```
TASK: What am I asking the AI to do?
  |
  +-- Is it a NEW feature?
  |     |
  |     +-- Load: Registry, relevant module spec, relevant system specs
  |     +-- Load: Cross-cutting specs that apply (styling, testing, etc.)
  |     +-- Load: Similar existing implementations for pattern reference
  |
  +-- Is it a BUG FIX?
  |     |
  |     +-- Load: The specific spec section that defines correct behavior
  |     +-- Load: The existing implementation file
  |     +-- Load: The existing test file
  |     +-- DO NOT load: Unrelated specs or code
  |
  +-- Is it a REFACTORING?
  |     |
  |     +-- Load: Architecture spec (system-level)
  |     +-- Load: The files being refactored
  |     +-- Load: Tests for those files
  |     +-- DO NOT load: Business logic specs (behavior shouldn't change)
  |
  +-- Is it a TEST?
        |
        +-- Load: The relevant spec (this is what we're testing against)
        +-- Load: The implementation (this is what we're testing)
        +-- Load: Testing standards spec (cross-cutting)
        +-- DO NOT load: Other module specs
```

### Принцип «ровно достаточно контекста»

Это главный принцип управления контекстом в SDD:

> **Дайте ИИ ровно ту информацию, которая нужна для правильного выполнения текущей задачи, — не больше и не меньше.**

«Не больше» — потому что избыток контекста ухудшает работу.
«Не меньше» — потому что нехватка контекста ведёт к неверному результату.

Вот практическая эвристика:

| Тип контекста | Включать? | Бюджет размера |
|-------------|----------|-------------|
| Системный промпт / инструкции | Всегда | 2-5K токенов |
| Конфигурация проекта (.cursorrules) | Всегда | 1-3K токенов |
| Релевантные спецификации | Всегда | 3-15K токенов |
| Существующий связанный код | Обычно | 5-20K токенов |
| Существующие тесты | Для багфиксов и рефакторинга | 3-10K токенов |
| История разговора | Автоматически | Зависит |
| Нерелевантные спецификации | Никогда | 0 токенов |
| Вся кодовая база | Никогда | 0 токенов |

**Цель: держать общий контекст ниже 50% ёмкости окна.** Так остаётся место для рассуждений ИИ и генерации ответа.

> **Заметка профессора:** Я видел, как разработчики вставляли всю кодовую базу из 100 файлов в контекстное окно Claude на 200K, а потом удивлялись, почему качество вывода упало. Модель тратила весь свой «бюджет внимания» на 100 файлов, когда ей нужны были 3. Это как просить человека найти опечатку в предложении, одновременно читая ему вслух всю энциклопедию. Дайте ИИ фокус. В ответ он даст вам точность.

---

## 3.6 Техники управления контекстом

### Техника 1: суммаризация спецификаций

Создайте сжатые версии спецификаций, укладывающие существенные ограничения в минимум токенов:

```typescript
// tools/spec-summarizer.ts

/**
 * Generates condensed summaries of spec files for context optimization.
 * The summary captures key constraints while reducing token count by ~80%.
 */

import { readFileSync, writeFileSync } from 'fs';

interface SpecSummary {
  id: string;
  title: string;
  path: string;
  constraints: string[];
  dependencies: string[];
  tokenEstimate: number;
}

function summarizeSpec(specPath: string): SpecSummary {
  const content = readFileSync(specPath, 'utf-8');
  const lines = content.split('\n');

  const summary: SpecSummary = {
    id: '',
    title: '',
    path: specPath,
    constraints: [],
    dependencies: [],
    tokenEstimate: 0,
  };

  for (const line of lines) {
    // Extract ID
    const idMatch = line.match(/^#\s+Spec:\s+(\S+)/);
    if (idMatch) summary.id = idMatch[1];

    // Extract title
    const titleMatch = line.match(/^#\s+(.+)/);
    if (titleMatch && !summary.title) summary.title = titleMatch[1];

    // Extract SHALL/MUST requirements (these are the constraints)
    if (/\b(SHALL|MUST)\b/i.test(line) && !line.startsWith('#')) {
      summary.constraints.push(line.trim().replace(/^\d+\.\s*/, ''));
    }

    // Extract dependencies
    const depMatch = line.match(/Dependencies?:\s*(.+)/i);
    if (depMatch) {
      summary.dependencies = depMatch[1].split(',').map(d => d.trim());
    }
  }

  // Estimate tokens (rough: 1 token per 4 characters)
  const summaryText = JSON.stringify(summary);
  summary.tokenEstimate = Math.ceil(summaryText.length / 4);

  return summary;
}

function generateContextBundle(
  specPaths: string[],
  maxTokens: number = 15000
): string {
  const summaries = specPaths.map(summarizeSpec);
  let bundle = '# Relevant Spec Summaries\n\n';
  let tokenCount = 0;

  for (const summary of summaries) {
    const section = [
      `## ${summary.id}: ${summary.title}`,
      `Path: ${summary.path}`,
      `Dependencies: ${summary.dependencies.join(', ') || 'None'}`,
      '',
      '### Key Constraints:',
      ...summary.constraints.map((c, i) => `${i + 1}. ${c}`),
      '',
      '---',
      '',
    ].join('\n');

    const sectionTokens = Math.ceil(section.length / 4);

    if (tokenCount + sectionTokens > maxTokens) {
      bundle += `\n> Note: ${summaries.length - summaries.indexOf(summary)} specs omitted due to context budget.\n`;
      bundle += `> Load full specs individually if needed.\n`;
      break;
    }

    bundle += section;
    tokenCount += sectionTokens;
  }

  bundle += `\n<!-- Total estimated tokens: ${tokenCount} -->\n`;
  return bundle;
}

export { summarizeSpec, generateContextBundle };
```

### Техника 2: графы зависимостей для загрузки спецификаций

```typescript
// tools/spec-dependency-graph.ts

/**
 * Builds a dependency graph from the spec registry.
 * Given a target spec, returns the minimal set of specs
 * needed for full context.
 */

interface SpecNode {
  id: string;
  path: string;
  dependencies: string[];
}

class SpecDependencyGraph {
  private nodes: Map<string, SpecNode> = new Map();

  addSpec(id: string, path: string, dependencies: string[]): void {
    this.nodes.set(id, { id, path, dependencies });
  }

  /**
   * Returns the minimal set of specs needed for a given task.
   * Walks the dependency graph from the target spec(s) upward.
   */
  resolve(targetIds: string[]): SpecNode[] {
    const resolved = new Map<string, SpecNode>();
    const queue = [...targetIds];

    while (queue.length > 0) {
      const currentId = queue.shift()!;

      if (resolved.has(currentId)) continue;

      const node = this.nodes.get(currentId);
      if (!node) {
        console.warn(`Warning: Spec ${currentId} not found in registry.`);
        continue;
      }

      resolved.set(currentId, node);

      // Add dependencies to the queue
      for (const depId of node.dependencies) {
        if (!resolved.has(depId)) {
          queue.push(depId);
        }
      }
    }

    // Return in dependency order (dependencies first)
    return this.topologicalSort(resolved);
  }

  /**
   * Returns a topologically sorted list of specs.
   * Dependencies come before their dependents.
   */
  private topologicalSort(nodes: Map<string, SpecNode>): SpecNode[] {
    const sorted: SpecNode[] = [];
    const visited = new Set<string>();
    const visiting = new Set<string>();

    const visit = (id: string) => {
      if (visited.has(id)) return;
      if (visiting.has(id)) {
        throw new Error(`Circular dependency detected involving: ${id}`);
      }

      visiting.add(id);

      const node = nodes.get(id);
      if (node) {
        for (const dep of node.dependencies) {
          if (nodes.has(dep)) {
            visit(dep);
          }
        }
        visited.add(id);
        visiting.delete(id);
        sorted.push(node);
      }
    };

    for (const id of nodes.keys()) {
      visit(id);
    }

    return sorted;
  }

  /**
   * Suggests which specs to load for a given file path.
   * Uses heuristics based on file location and naming.
   */
  suggestSpecs(filePath: string): string[] {
    const suggestions: string[] = [];

    // Always include cross-cutting specs
    for (const [id] of this.nodes) {
      if (id.startsWith('XCT-')) {
        suggestions.push(id);
      }
    }

    // Match based on file path patterns
    if (filePath.includes('/components/')) {
      // Component files need the component spec + parent module spec
      const componentName = filePath.split('/').pop()?.replace(/\.(tsx?|jsx?)$/, '');
      for (const [id, node] of this.nodes) {
        if (id.startsWith('CMP-') && node.path.includes(componentName?.toLowerCase() || '')) {
          suggestions.push(id);
        }
      }
    }

    if (filePath.includes('/services/') || filePath.includes('/api/')) {
      // Service/API files need the module spec + system specs
      for (const [id] of this.nodes) {
        if (id.startsWith('SYS-')) {
          suggestions.push(id);
        }
      }
    }

    return [...new Set(suggestions)];
  }
}

// Build the graph from registry
function buildGraphFromRegistry(registryPath: string): SpecDependencyGraph {
  const content = readFileSync(registryPath, 'utf-8');
  const graph = new SpecDependencyGraph();

  // Parse the registry markdown table
  const lines = content.split('\n');
  for (const line of lines) {
    // Match table rows: | ID | Name | Path | Status | Dependencies |
    const match = line.match(
      /\|\s*(\S+)\s*\|\s*([^|]+)\s*\|\s*`([^`]+)`\s*\|\s*(\w+)\s*\|\s*([^|]*)\s*\|/
    );
    if (match) {
      const [, id, , path, status, depsStr] = match;
      if (status === 'Active' || status === 'Draft') {
        const deps = depsStr.trim()
          ? depsStr.split(',').map(d => d.trim())
          : [];
        graph.addSpec(id, path, deps);
      }
    }
  }

  return graph;
}

import { readFileSync } from 'fs';

export { SpecDependencyGraph, buildGraphFromRegistry };

// Example usage:
// const graph = buildGraphFromRegistry('SPEC_REGISTRY.md');
// const needed = graph.resolve(['USR-001']); // Returns USR-001 + SYS-002 + SYS-003
// console.log(needed.map(n => `${n.id}: ${n.path}`));
```

### Техника 3: инкрементальная загрузка контекста

Вместо того чтобы загружать весь контекст сразу, загружайте его порциями по мере необходимости:

```markdown
# Pattern: Incremental Context Loading

## Phase 1: Registry Only
Load SPEC_REGISTRY.md. Ask the AI to identify which specs are relevant.

## Phase 2: Summaries
Load summaries of the identified specs. Ask the AI to confirm
which ones it needs in full.

## Phase 3: Full Specs
Load the full text of only the confirmed specs.

## Phase 4: Implementation Context
Load existing code files that are directly related to the task.
```

Этот паттерн особенно хорошо работает с инструментами разработки с ИИ, поддерживающими чтение файлов через инструменты (как Claude Code), где ИИ может запрашивать файлы по необходимости, а не получать их предзагруженными.

### Техника 4: бюджетирование контекста

Назначьте бюджет токенов каждой категории контекста и соблюдайте его:

```typescript
// tools/context-budget.ts

interface ContextBudget {
  systemPrompt: number;
  projectConfig: number;
  specs: number;
  existingCode: number;
  conversationHistory: number;
  reserve: number;  // Reserved for AI reasoning and response
}

function createBudget(totalTokens: number): ContextBudget {
  return {
    systemPrompt: Math.floor(totalTokens * 0.02),      // 2%
    projectConfig: Math.floor(totalTokens * 0.02),      // 2%
    specs: Math.floor(totalTokens * 0.15),              // 15%
    existingCode: Math.floor(totalTokens * 0.15),       // 15%
    conversationHistory: Math.floor(totalTokens * 0.16),// 16%
    reserve: Math.floor(totalTokens * 0.50),            // 50% reserved
  };
}

// Example: Claude's 200K token window
const claudeBudget = createBudget(200_000);
// {
//   systemPrompt: 4000,
//   projectConfig: 4000,
//   specs: 30000,
//   existingCode: 30000,
//   conversationHistory: 32000,
//   reserve: 100000
// }

// Example: GPT-4's 128K token window
const gptBudget = createBudget(128_000);
// {
//   systemPrompt: 2560,
//   projectConfig: 2560,
//   specs: 19200,
//   existingCode: 19200,
//   conversationHistory: 20480,
//   reserve: 64000
// }

function estimateTokens(text: string): number {
  // Rough estimate: 1 token per 4 characters
  return Math.ceil(text.length / 4);
}

function checkBudget(
  budget: ContextBudget,
  category: keyof ContextBudget,
  content: string
): { fits: boolean; tokens: number; remaining: number } {
  const tokens = estimateTokens(content);
  const remaining = budget[category] - tokens;

  return {
    fits: remaining >= 0,
    tokens,
    remaining: Math.max(0, remaining),
  };
}
```

---

## 3.7 Как инструменты разработки с ИИ работают с большими кодовыми базами

### Claude Code от Anthropic

Claude Code прагматично подходит к управлению контекстом:

1. **CLAUDE.md как постоянный контекст:** файл `CLAUDE.md` в корне проекта автоматически загружается в каждое взаимодействие. Это ваш «всегда включённый» контекст — в нём должны быть самые критичные ограничения, а не всё подряд.

2. **Чтение файлов через инструменты:** Claude Code читает файлы по необходимости. Вместо предзагрузки всей кодовой базы он открывает конкретные файлы, когда они нужны. Это та «вытягивающая» модель, о которой мы говорили.

3. **Иерархия файлов CLAUDE.md:** файлы `CLAUDE.md` можно размещать в подкаталогах. Работая в конкретном каталоге, Claude Code загружает корневой `CLAUDE.md` плюс локальный. Это естественным образом реализует иерархический паттерн спецификаций.

```
project/
  CLAUDE.md              # System-level context (always loaded)
  src/
    modules/
      billing/
        CLAUDE.md        # Billing module context (loaded when working here)
      user/
        CLAUDE.md        # User module context (loaded when working here)
```

4. **Управление разговором:** Claude Code поощряет короткие, сфокусированные разговоры. У каждого разговора свой контекст, и для новых задач рекомендуется начинать новый разговор, а не продолжать бесконечно.

### Gemini Code Assist от Google

Подход Google использует массивное контекстное окно Gemini иначе:

1. **Индексация репозитория:** Gemini Code Assist индексирует весь репозиторий и строит семантическое понимание кодовой базы. Индекс существует отдельно от контекстного окна — это система извлечения, помогающая ИИ находить релевантный код.

2. **Умный отбор контекста:** исходя из текущего файла и задачи, Gemini выбирает релевантные фрагменты кода из репозитория и включает их в контекст. Это автоматическое управление контекстом — инструмент сам решает, что релевантно.

3. **Конфигурация уровня проекта:** подобно `.cursorrules`, Gemini Code Assist поддерживает инструкции уровня проекта, дающие постоянный контекст.

### IDE Cursor

IDE Cursor ввела несколько паттернов управления контекстом:

1. **Файл `.cursorrules`:** конфигурация уровня проекта, дающая ИИ постоянные ограничения спецификации.

2. **Ссылки `@`:** Cursor позволяет явно ссылаться в промпте на файлы, папки или документацию синтаксисом `@` (например, `@file:src/components/DataTable.tsx`). Это даёт точный контроль над тем, какой контекст видит ИИ.

3. **Индексация кодовой базы:** Cursor строит семантический индекс и автоматически включает релевантный контекст, когда вы задаёте вопрос или просите сгенерировать код.

4. **Интеграция с документацией:** Cursor умеет индексировать внешнюю документацию (фреймворков, библиотек) и автоматически подмешивать релевантные разделы в контекст.

### Общие паттерны у разных инструментов

Несмотря на разные подходы, у всех этих инструментов есть общие паттерны:

| Паттерн | Claude Code | Gemini Code Assist | Cursor |
|---------|-------------|-------------------|--------|
| Постоянный конфигурационный файл | CLAUDE.md | Конфигурация проекта | .cursorrules |
| Чтение файлов по требованию | Да (инструменты) | Да (индексация) | Да (ссылки @) |
| Автоматический отбор контекста | Минимальный | Агрессивный | Умеренный |
| Индексация репозитория | Нет | Да | Да |
| Иерархическая конфигурация | Да | Частично | Частично |

---

## 3.8 Промпт, осведомлённый о спецификации: собираем всё вместе

### Полная структура промпта для SDD с управлением контекстом

Когда вы просите ИИ реализовать функцию в SDD-процессе с управлением контекстом, ваш промпт (и контекст) должны следовать такой структуре:

```markdown
## Context

### Project Configuration
[Contents of .cursorrules or CLAUDE.md -- always included]

### Spec Registry (Summary)
[The relevant portion of SPEC_REGISTRY.md]

### Relevant Specs
[Full text of the 2-4 specs that apply to this task]

### Existing Code Context
[The existing files that the AI needs to reference -- files it will modify,
files it should follow the pattern of, test files to update]

## Task

Implement [specific feature] according to the spec [SPEC-ID].

### Constraints
- Follow all patterns defined in the project configuration
- Write tests first, then implementation (per Module 3, Chapter 1)
- Ensure all spec requirements have test coverage
- Do not introduce any dependencies not listed in the approved deps spec

### Deliverables
1. Test file: `src/[path]/[feature].test.ts`
2. Implementation file: `src/[path]/[feature].ts`
3. Spec coverage annotation: which spec lines are covered by which tests
```

### Пример: реализация функции с управлением контекстом

Разберём реальный пример. Задача: реализовать функцию `calculateInvoice` для модуля биллинга.

**Шаг 1: обращаемся к реестру**

```
AI reads SPEC_REGISTRY.md and identifies:
  - BIL-003 (Invoice Generation) -- the primary spec
  - BIL-001 (Subscription Plans) -- dependency (invoice needs plan info)
  - SYS-003 (Database Schema) -- dependency (data model)
  - SYS-004 (API Standards) -- dependency (response format)
  - XCT-001 (Styling Standards) -- cross-cutting (if there's a UI component)
  - XCT-003 (Testing Standards) -- cross-cutting (always relevant)
```

**Шаг 2: загружаем релевантные спецификации (сначала резюме)**

```
Load summaries of: BIL-003, BIL-001, SYS-003, SYS-004, XCT-003
Estimated tokens: 5 specs x ~500 tokens each = ~2,500 tokens
```

**Шаг 3: определяем, какие полные спецификации нужны**

```
After reading summaries, determine:
  - BIL-003: Need full spec (primary task)
  - BIL-001: Need full spec (invoice references plan data)
  - SYS-003: Only need the Invoice table schema (partial load)
  - SYS-004: Only need the response format section (partial load)
  - XCT-003: Already in .cursorrules, skip
```

**Шаг 4: загружаем полные спецификации и контекст кода**

```
Load:
  - BIL-003 full spec:            ~4K tokens
  - BIL-001 full spec:            ~3K tokens
  - SYS-003 (Invoice schema only): ~1K tokens
  - SYS-004 (response format only): ~1K tokens
  - Existing billing service:       ~3K tokens
  - Existing billing tests:         ~2K tokens
  - .cursorrules:                   ~2K tokens

Total context: ~16K tokens out of 200K available
```

Это 8% контекстного окна Claude. Оставшиеся 92% доступны для рассуждений и генерации ответа. Вот так и получают качественный вывод от ИИ — давая ему фокус.

---

## 3.9 Управление зависимостями спецификаций

### Когда спецификация A зависит от спецификации B

В любом нетривиальном проекте спецификации зависят друг от друга. Управление этими зависимостями критично и для понимания людьми, и для загрузки контекста в ИИ.

### Типы зависимостей спецификаций

**1. Зависимости по данным**

Спецификация A ссылается на структуры данных, определённые в спецификации B.

```markdown
# BIL-003: Invoice Generation

## Data Model
The invoice SHALL contain the following fields:
- planId: Reference to a SubscriptionPlan (see BIL-001, Section 3.2)
- userId: Reference to a User (see USR-001, Section 2.1)
```

**2. Поведенческие зависимости**

Поведение спецификации A зависит от поведения, определённого в спецификации B.

```markdown
# NTF-001: Email Notifications

## Trigger Conditions
An email notification SHALL be sent when:
- A user registers (USR-001, event: USER_REGISTERED)
- A payment fails (BIL-002, event: PAYMENT_FAILED)
- A subscription renews (BIL-001, event: SUBSCRIPTION_RENEWED)
```

**3. Зависимости по ограничениям**

Спецификация A наследует ограничения спецификации B.

```markdown
# DSH-002: Analytics Widgets

## API Constraints
All widget data endpoints SHALL follow the API standards defined in SYS-004,
including:
- Pagination format (SYS-004, Section 4)
- Error response format (SYS-004, Section 6)
- Authentication requirements (SYS-002, Section 2)
```

### Отслеживание зависимостей в реестре

Реестр должен содержать матрицу зависимостей:

```markdown
## Dependency Matrix

| Spec | Depends On | Depended On By |
|------|-----------|----------------|
| SYS-001 | (none) | DSH-001, CMP-002, CMP-003 |
| SYS-002 | (none) | USR-001, USR-002, USR-003, USR-004, NTF-001, NTF-002 |
| SYS-003 | (none) | USR-001, USR-002, BIL-001, BIL-002, BIL-003 |
| SYS-004 | (none) | BIL-001, BIL-002, BIL-003, DSH-002, DSH-003, DSH-004 |
| USR-001 | SYS-002, SYS-003 | NTF-001 |
| BIL-001 | SYS-003, SYS-004 | BIL-003, BIL-004 |
| BIL-003 | SYS-003, BIL-001 | (none) |
```

### Работа с циклическими зависимостями

Иногда у спецификаций возникают циклические зависимости. Это признак проблемы в дизайне: обычно он означает, что спецификации нужно переработать.

```
BIL-001 (Plans) depends on USR-001 (Registration) -- plans need user data
USR-001 (Registration) depends on BIL-001 (Plans) -- registration needs plan data

SOLUTION: Extract the shared concern into a new spec
  - SYS-007 (User-Plan Binding) -- defines the relationship between users and plans
  - BIL-001 depends on SYS-007
  - USR-001 depends on SYS-007
  - No more circular dependency
```

### Автоматическая валидация зависимостей

```typescript
// tools/validate-spec-deps.ts

import { readFileSync, existsSync } from 'fs';

interface DepValidation {
  valid: boolean;
  errors: string[];
  warnings: string[];
  circularDeps: string[][];
}

function validateSpecDependencies(registryPath: string): DepValidation {
  const result: DepValidation = {
    valid: true,
    errors: [],
    warnings: [],
    circularDeps: [],
  };

  // Parse registry and build adjacency list
  const deps = new Map<string, string[]>();
  const paths = new Map<string, string>();

  const content = readFileSync(registryPath, 'utf-8');
  const lines = content.split('\n');

  for (const line of lines) {
    const match = line.match(
      /\|\s*(\S+)\s*\|[^|]+\|\s*`([^`]+)`\s*\|[^|]+\|\s*([^|]*)\s*\|/
    );
    if (match) {
      const [, id, path, depsStr] = match;
      const specDeps = depsStr.trim()
        ? depsStr.split(',').map(d => d.trim()).filter(Boolean)
        : [];
      deps.set(id, specDeps);
      paths.set(id, path);
    }
  }

  // Check 1: All dependencies reference existing specs
  for (const [id, specDeps] of deps) {
    for (const dep of specDeps) {
      if (!deps.has(dep)) {
        result.errors.push(
          `Spec ${id} depends on ${dep}, but ${dep} is not in the registry.`
        );
        result.valid = false;
      }
    }
  }

  // Check 2: All spec files exist on disk
  for (const [id, path] of paths) {
    if (!existsSync(path)) {
      result.warnings.push(
        `Spec ${id} references path ${path}, but file does not exist.`
      );
    }
  }

  // Check 3: Detect circular dependencies
  const visited = new Set<string>();
  const inStack = new Set<string>();

  function detectCycle(id: string, path: string[]): boolean {
    if (inStack.has(id)) {
      const cycleStart = path.indexOf(id);
      result.circularDeps.push(path.slice(cycleStart).concat(id));
      return true;
    }
    if (visited.has(id)) return false;

    visited.add(id);
    inStack.add(id);

    for (const dep of deps.get(id) || []) {
      if (detectCycle(dep, [...path, id])) {
        result.valid = false;
      }
    }

    inStack.delete(id);
    return false;
  }

  for (const id of deps.keys()) {
    if (!visited.has(id)) {
      detectCycle(id, []);
    }
  }

  if (result.circularDeps.length > 0) {
    for (const cycle of result.circularDeps) {
      result.errors.push(
        `Circular dependency detected: ${cycle.join(' -> ')}`
      );
    }
  }

  return result;
}

// Run validation
const result = validateSpecDependencies('SPEC_REGISTRY.md');

if (result.warnings.length > 0) {
  console.warn('\nWarnings:');
  for (const w of result.warnings) {
    console.warn(`  - ${w}`);
  }
}

if (result.errors.length > 0) {
  console.error('\nErrors:');
  for (const e of result.errors) {
    console.error(`  - ${e}`);
  }
  process.exit(1);
}

console.log('Spec dependency validation passed.');
```

---

## 3.10 Практическое упражнение: проектируем реестр спецификаций

### Задача

Спроектируйте полный реестр спецификаций для SaaS-приложения среднего размера — **инструмента управления проектами** (что-то вроде упрощённых Linear, Jira или Asana).

### Объём приложения

В приложении есть такие возможности:

- **Аутентификация:** вход, регистрация, SSO, сброс пароля
- **Проекты:** создание, архивирование, настройка проектов
- **Задачи (issues):** создание, назначение, метки, приоритеты, закрытие
- **Доски:** канбан, список, таймлайн
- **Комментарии:** комментарии к задачам, упоминания пользователей, вложения
- **Уведомления:** email, в приложении, вебхуки
- **Интеграции:** GitHub, Slack, Discord
- **Аналитика:** скорость проекта, burndown-графики, метрики команды
- **Администрирование:** управление пользователями, ролевой доступ, биллинг

### Что нужно сдать

Создайте полный файл `SPEC_REGISTRY.md`, включающий:

1. **Спецификации уровня системы** (5–8 штук: архитектура, аутентификация, база данных, стандарты API, безопасность и т. п.)

2. **Спецификации уровня модулей** (15–20 штук, по каждой функциональной области)

3. **Спецификации уровня компонентов** (10–15 штук для ключевых UI-компонентов)

4. **Сквозные спецификации** (5–8 штук: стилизация, тестирование, доступность, производительность и т. п.)

5. **Граф зависимостей**, показывающий связи спецификаций

6. **Матрицу зависимостей** для быстрой справки

### Подсказки

Вот отправная точка:

```markdown
# SPEC_REGISTRY.md

## Project: ProjectFlow (Project Management Tool)

## System-Level Specs

| ID | Name | Path | Status | Last Updated |
|----|------|------|--------|--------------|
| SYS-001 | Architecture Overview | `/specs/system/architecture.md` | Active | 2026-02-01 |
| SYS-002 | Authentication & Authorization | `/specs/system/auth.md` | Active | 2026-02-01 |
| SYS-003 | Database Schema & Migrations | `/specs/system/database.md` | Active | 2026-02-01 |
| SYS-004 | REST API Design Standards | `/specs/system/api-standards.md` | Active | 2026-02-01 |
| ... | ... | ... | ... | ... |

## Module-Level Specs

### Project Management Module
| ID | Name | Path | Status | Dependencies |
|----|------|------|--------|-------------|
| PRJ-001 | Project CRUD | `/specs/modules/project/crud.md` | Active | SYS-002, SYS-003 |
| PRJ-002 | Project Configuration | `/specs/modules/project/config.md` | Active | SYS-002, PRJ-001 |
| ... | ... | ... | ... | ... |

### Issue Tracking Module
| ID | Name | Path | Status | Dependencies |
|----|------|------|--------|-------------|
| ISS-001 | Issue CRUD & Lifecycle | `/specs/modules/issues/lifecycle.md` | Active | SYS-002, SYS-003, PRJ-001 |
| ... | ... | ... | ... | ... |

[Continue for all modules...]
```

Дополните реестр всеми модулями, следя за тем, чтобы:
- у каждой спецификации был уникальный ID по соглашению об именовании
- зависимости были явно перечислены
- был указан статус (Active, Draft, Deprecated)
- граф зависимостей был ациклическим (без циклических зависимостей)

---

## 3.11 Продвинутая тема: стратегии контекстного окна для разных провайдеров моделей

### Адаптация стратегии под модель ИИ

У разных моделей разные сильные и слабые стороны в использовании контекста. Ваша стратегия должна это учитывать.

### Стратегия для Claude (контекст 200K)

```
Claude's strengths:
  - Strong recall across the full 200K window
  - Good at following detailed instructions
  - Excellent at working with structured specs

Recommended strategy:
  - Budget: 30% for specs and code, 20% for conversation, 50% reserve
  - Load full specs (not just summaries) when within budget
  - Use CLAUDE.md for persistent constraints
  - Leverage tool-based file reading for on-demand context
  - Keep conversations focused on single tasks
```

### Стратегия для Gemini (контекст 1M+)

```
Gemini's strengths:
  - Massive context window allows loading more material
  - Good at finding information across large contexts
  - Multimodal (can process images, diagrams alongside specs)

Recommended strategy:
  - Budget: 20% for specs and code, 10% for conversation, 70% reserve
  - Even with 1M tokens, don't load everything
  - Use the extra capacity for broader code context (more reference files)
  - Include diagrams and visual specs when available
  - Still prioritize relevant context over quantity
```

### Стратегия для GPT-4o (контекст 128K)

```
GPT-4o's strengths:
  - Well-tuned for code generation tasks
  - Good at following structured prompts
  - Strong reasoning with focused context

Recommended strategy:
  - Budget: 25% for specs and code, 15% for conversation, 60% reserve
  - Use spec summaries more aggressively (full specs may exceed budget)
  - Prioritize the most critical spec sections
  - Break large tasks into smaller, focused interactions
  - Use system prompt efficiently (keep it concise)
```

### Стратегия для открытых моделей (Llama, Mistral — 128K)

```
Open-source model considerations:
  - Context recall may be weaker than frontier models
  - Performance degrades more with context length
  - Best results with highly focused context

Recommended strategy:
  - Budget: 20% for specs and code, 10% for conversation, 70% reserve
  - Always use summaries, load full specs only when absolutely needed
  - Keep context under 50K tokens if possible
  - Use very explicit, structured prompts
  - Break tasks into smallest possible units
```

---

## 3.12 Реестр спецификаций на практике: разобранный пример

### Строим процесс с управлением контекстом

Соберём всё вместе на реальном сценарии. Вас попросили добавить в модуль трекинга задач функцию «срок выполнения» (due date).

**Шаг 1: начинаем с реестра**

Вы открываете `SPEC_REGISTRY.md` и находите:

```
ISS-001: Issue CRUD & Lifecycle -- Dependencies: SYS-002, SYS-003, PRJ-001
ISS-002: Issue Assignment -- Dependencies: SYS-002, USR-001
ISS-003: Issue Labels & Priorities -- Dependencies: ISS-001
```

«Срок выполнения» — часть жизненного цикла задачи, поэтому основная спецификация — ISS-001.

**Шаг 2: разрешаем зависимости**

По графу зависимостей:

```
ISS-001 depends on:
  - SYS-002 (Auth) -- need to know permission model
  - SYS-003 (Database) -- need the Issue table schema
  - PRJ-001 (Projects) -- issues belong to projects
```

**Шаг 3: загружаем контекст**

```markdown
## For the AI:

I'm adding a "due date" feature to issues. Here's the context:

### From SYS-003 (Database Schema):
The Issue table currently has:
- id (UUID)
- title (string, max 200)
- description (text, nullable)
- status (enum: open, in_progress, done, closed)
- priority (enum: none, low, medium, high, urgent)
- projectId (FK to Project)
- assigneeId (FK to User, nullable)
- createdAt, updatedAt (timestamps)

### From ISS-001 (Issue Lifecycle), Section 4 - Due Dates:
[If this section exists, load it. If not, we need to write it.]

### From SYS-004 (API Standards):
- All date fields use ISO 8601 format (UTC)
- Nullable fields return null, not undefined or empty string
- Validation errors return 400 with field-specific messages

### Task:
1. Update the spec ISS-001 to include due date requirements
2. Write tests for the due date feature
3. Implement the database migration
4. Implement the API changes
5. Update the existing tests
```

**Шаг 4: генерируем дополнение к спецификации**

```markdown
## ISS-001 Addendum: Due Dates (Section 4)

### Requirements
1. Each issue MAY have a dueDate field (nullable timestamp, UTC)
2. dueDate SHALL be settable at issue creation or via update
3. dueDate SHALL be in the future or null (past dates not allowed on creation)
4. dueDate SHALL be stored as ISO 8601 UTC timestamp
5. The API SHALL support filtering issues by dueDate range
6. The API SHALL support sorting issues by dueDate (nulls last)
7. Issues with dueDate in the past and status != done/closed SHALL be flagged as "overdue"

### Constraints
8. dueDate validation SHALL allow dates up to 5 years in the future
9. Updating dueDate to a past date IS allowed (for corrections)
10. Clearing dueDate (setting to null) IS always allowed
```

**Шаг 5: пишем тесты по дополнению к спецификации**

Теперь у ИИ сфокусированный контекст: конкретное дополнение к спецификации, существующая модель данных и стандарты API. Он может сгенерировать точные тесты, не задыхаясь от нерелевантной информации.

> **Заметка профессора:** Обратите внимание: мы загрузили ровно четыре сфокусированных фрагмента контекста, а не всю библиотеку спецификаций. У ИИ есть всё необходимое для этой конкретной задачи и ничего лишнего. Вот принцип «ровно достаточно контекста» в действии.

---

## 3.13 Типичные ошибки и как их избежать

### Ошибка 1: промпт «всё в одну кучу»

**Как выглядит:** в один промпт вставляют все спецификации, все файлы кода и длинную историю разговора.

**Почему не работает:** ИИ не отличает важное от шума. Критичные ограничения теряются в объёме.

**Решение:** используйте реестр и граф зависимостей, чтобы выбирать только релевантные спецификации. Бюджетируйте контекст.

### Ошибка 2: проблема «амнезии»

**Как выглядит:** для связанной задачи начинают новый разговор и забывают включить контекст, установленный в предыдущем.

**Почему не работает:** ИИ генерирует код, несовместимый с решениями из предыдущего разговора.

**Решение:** фиксируйте решения в файлах спецификаций (а не только в разговорах). Используйте постоянные конфигурационные файлы. Коммитьте обновления спецификаций между разговорами.

### Ошибка 3: проблема «устаревшего контекста»

**Как выглядит:** загружаются спецификации, не обновлённые под недавние изменения.

**Почему не работает:** ИИ реализует по устаревшей спецификации, а потом падает на тестах, написанных по текущей.

**Решение:** указывайте в реестре даты «последнего обновления». Настройте проверки CI, помечающие спецификации, не обновлявшиеся 90+ дней. Сделайте обновление спецификаций частью определения «готово» для каждой функции.

### Ошибка 4: допущение «неявного контекста»

**Как выглядит:** предполагается, что ИИ «знает» проект, потому что вы работаете с ним весь день.

**Почему не работает:** каждый новый разговор начинается с чистого листа. ИИ не помнит предыдущие сессии.

**Решение:** никогда не предполагайте. Всегда давайте явный контекст. Если ограничение важно, оно должно быть в файле, который попадает в контекст.

### Ошибка 5: проблема «монолитной спецификации»

**Как выглядит:** один огромный файл спецификации, покрывающий всё.

**Почему не работает:** нельзя загрузить только часть. Всё или ничего, а «всё» обычно чересчур.

**Решение:** разбейте спецификации по трёхуровневой иерархии. Держите каждый файл сфокусированным на одной теме. Идеально, если файл спецификации — 100–300 строк: достаточно подробно, чтобы быть полезным, и достаточно кратко, чтобы уложиться в бюджет контекста.

---

## 3.14 Упражнения

### Упражнение 1: расчёт бюджета контекста (начальный уровень)

По следующим параметрам проекта рассчитайте бюджет контекста и определите, помещается ли запрошенный контекст:

**Модель:** Claude (контекстное окно 200K токенов)
**Конфигурация проекта (.cursorrules):** 2500 токенов
**История разговора на данный момент:** 15 000 токенов

**Задача:** реализовать модуль обработки платежей

**Спецификации к загрузке:**
- BIL-002 (обработка платежей): 4200 токенов
- BIL-001 (тарифные планы): 3800 токенов
- SYS-003 (схема базы данных): 6500 токенов
- SYS-004 (стандарты API): 3200 токенов
- SYS-006 (требования безопасности): 5100 токенов
- XCT-003 (стандарты тестирования): 2800 токенов

**Файлы кода к загрузке:**
- Существующий сервис биллинга: 4500 токенов
- Существующие тесты биллинга: 3200 токенов
- Интеграция с платёжным шлюзом: 5800 токенов

**Вопросы:**
1. Каков общий объём загружаемого контекста?
2. Какой процент контекстного окна занят?
3. Достаточно ли остатка для рассуждений? (Цель: резерв 50%)
4. Если нет, какие спецификации стоит загрузить в виде резюме?

### Упражнение 2: декомпозиция спецификации (средний уровень)

У вас есть монолитный файл спецификации для системы оформления заказов в интернет-магазине (примерно 12 000 токенов). Разложите его в иерархический набор спецификаций:

**Монолитная спецификация покрывает:**
- операции с корзиной
- валидацию адреса
- выбор способа доставки
- расчёт налогов
- обработку платежей
- подтверждение заказа
- чеки по email
- резервирование товаров на складе

**Что нужно сдать:**
1. Список из 6–10 отдельных файлов спецификаций с оценкой их размера
2. Граф зависимостей, показывающий их связи
3. План загрузки контекста для трёх разных задач:
   - Задача A: исправить баг в расчёте налогов
   - Задача B: добавить новый способ доставки
   - Задача C: реализовать полный сценарий оформления заказа

### Упражнение 3: напишите загрузчик контекста (продвинутый уровень)

Реализуйте инструмент `context-loader.ts`, который:

1. Читает `SPEC_REGISTRY.md`
2. Принимает список ID целевых спецификаций
3. Разрешает зависимости (по графу зависимостей)
4. Оценивает общее число токенов
5. Если сумма превышает бюджет, автоматически переключается на резюме для менее критичных спецификаций
6. Выдаёт отформатированный пакет контекста, готовый к вставке в промпт ИИ

**Что нужно сдать:** полностью рабочий TypeScript-файл, который:
- разбирает markdown реестра
- строит граф зависимостей
- разрешает транзитивные зависимости
- оценивает число токенов
- генерирует пакет контекста в пределах заданного бюджета токенов
- переходит на резюме, когда полные спецификации превышают бюджет

### Упражнение 4: реестр для вашего проекта (итоговое)

Возьмите реальный или гипотетический проект, над которым работаете, и:

1. **Определите все спецификации**, которые вам нужны (даже если их пока нет)
2. **Организуйте их** в трёхуровневую иерархию (система, модуль, компонент)
3. **Составьте карту зависимостей** между спецификациями
4. **Создайте полный файл SPEC_REGISTRY.md**
5. **Создайте файл CLAUDE.md** (или .cursorrules), который ссылается на реестр
6. **Опишите три примера задач** и план загрузки контекста для каждой

**Что нужно сдать:** полный набор файлов, который можно добавить в реальный проект, чтобы включить SDD с управлением контекстом.

---

## Итоги

В этой главе мы разобрали инженерную дисциплину управления контекстом — один из самых практичных и значимых навыков в разработке через спецификации.

**Ключевые выводы:**

1. **Контекстные окна конечны и ценны.** Даже у моделей с 200K или 1M токенов заполнение окна ухудшает работу. Относитесь к контексту как к памяти: его мало и он дорог.

2. **Больше контекста — не значит лучше контекст.** Из-за проблемы «иголки в стоге сена» ИИ труднее использовать релевантную информацию в окружении нерелевантной. Фокус важнее объёма.

3. **Паттерн реестра необходим.** Главный индекс всех спецификаций с ID, путями, статусами и зависимостями позволяет и людям, и ИИ быстро выходить на нужный контекст.

4. **Иерархические спецификации (система, модуль, компонент) позволяют загружать гранулярно.** Вместо загрузки всего — только те уровни, что относятся к текущей задаче.

5. **Принцип «ровно достаточно контекста» управляет всеми решениями.** Давайте ровно то, что нужно ИИ, — не больше и не меньше. Бюджетируйте контекст, измеряйте его и оставляйте место для рассуждений.

6. **Постоянные конфигурационные файлы сокращают повторяющуюся загрузку контекста.** .cursorrules, CLAUDE.md и подобные файлы автоматически подмешивают критичные ограничения, освобождая бюджет для информации о задаче.

7. **Зависимости спецификаций должны быть явными и управляемыми.** Когда спецификация A зависит от B, загрузчик контекста должен об этом знать. Отслеживайте зависимости в реестре и валидируйте их автоматически.

8. **Разным моделям нужны разные стратегии.** Подстраивайте подход к управлению контекстом под сильные и слабые стороны модели.

На этом модуль 3 «Валидация и петля обратной связи» завершён. Теперь у вас есть инструменты, чтобы:
- сопоставлять спецификации с тестами (глава 1)
- предотвращать дрейф замысла автоматическим линтингом (глава 2)
- стратегически управлять контекстом ради оптимальной работы ИИ (глава 3)

В модуле 4 мы возьмём всё изученное и применим к полному реальному проекту от начала до конца.

---

*Конец модуля 3*

---

[← Оглавление курса](../INDEX.ru.md) · [← Глава 2: Автоматический линтинг замысла](CHAPTER_02.ru.md) · [Глава 1: Мультиагентный рабочий процесс →](../MODULE_04/CHAPTER_01.ru.md)
