# Глава 2: Автоматический линтинг замысла

## МОДУЛЬ 03 — Валидация и петля обратной связи (средний уровень)

> [Оглавление курса](../INDEX.ru.md) · [Модуль 03](../INDEX.ru.md#модуль-03--валидация-и-петля-обратной-связи)

---

## Вступление к лекции

*Профессор открывает две вкладки браузера рядом. Слева дифф пул-реквеста. Справа исходный документ спецификации. Несколько строк в диффе подсвечены красным.*

С возвращением. В прошлой главе мы построили первую линию обороны: тесты, выведенные напрямую из спецификации. Сегодня поговорим о том, что происходит *между* тестами, — в серой зоне, где ИИ соблюдает букву спецификации, но нарушает её дух.

Хочу кое-что показать. *Указывает на дифф пул-реквеста.* Этот код сгенерировал ИИ-ассистент на прошлой неделе. В спецификации было сказано: «Используйте Tailwind CSS для всей стилизации. Никаких собственных CSS-файлов». ИИ создал прекрасный компонент. Все тесты прошли: компонент рендерился правильно, взаимодействия работали, атрибуты доступности были на месте.

Но посмотрите на строку 47. Видите?

```css
.custom-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}
```

ИИ создал собственный CSS-класс. Это не Tailwind. Тесты этого не поймали, потому что проверяли *поведение*, а не *подход к реализации*. Компонент по-прежнему рендерится правильно. Подсказка по-прежнему появляется. Но ограничение спецификации — «Никаких собственных CSS-файлов» — было нарушено.

Это и есть **дрейф замысла** (intent drift). И сегодня мы научимся строить автоматические системы, которые его ловят.

---

## 2.1 Понимание дрейфа замысла

### Что такое дрейф замысла?

Дрейф замысла возникает, когда сгенерированный ИИ код постепенно отклоняется от замысла исходной спецификации, продолжая при этом выдавать функционально корректный результат. Проблема тонкая и коварная, потому что:

1. **Код работает.** Он проходит тесты. Он даёт правильные результаты.
2. **Код выглядит разумно.** Он следует хорошим практикам — просто не *вашим* заданным практикам.
3. **Дрейф накапливается.** Одно маленькое отклонение тянет за собой другое, и не успеете оглянуться, как кодовая база превратилась в несогласованную кашу.
4. **ИИ не знает, что дрейфует.** У него нет постоянной памяти о ваших архитектурных решениях. Каждый промпт — чистый лист.

### Три типа дрейфа замысла

#### Тип 1: архитектурный дрейф

В спецификации сказано «используйте технологию X», а ИИ использует технологию Y.

```markdown
# Spec says:
"All state management SHALL use Zustand stores."

# AI generates:
import { useState, useEffect } from 'react';
// Uses React local state instead of Zustand
```

Компонент работает нормально. Но теперь у вас несогласованное управление состоянием по всей кодовой базе. Одни компоненты используют Zustand (как предписано), другие — локальное состояние (как ИИ сделал по умолчанию).

#### Тип 2: дрейф паттернов

Спецификация задаёт паттерн кодирования, а ИИ использует другой (часто не менее валидный) паттерн.

```markdown
# Spec says:
"Error handling SHALL use Result types (Ok/Err pattern)."

# AI generates:
try {
  const data = await fetchUser(id);
  return data;
} catch (error) {
  throw new HttpException(error.message, 500);
}
// Uses try/catch instead of Result types
```

Оба подхода обрабатывают ошибки. Но спецификация выбрала типы Result не просто так — возможно, ради лучшей композируемости или чтобы избежать выброса исключений в горячем пути. Паттерн ИИ «корректен», но неправилен для *этой* кодовой базы.

#### Тип 3: дрейф зависимостей

Спецификация перечисляет одобренные зависимости, а ИИ вводит новые.

```markdown
# Spec says:
"Date handling SHALL use date-fns."

# AI generates:
import dayjs from 'dayjs';
// Introduces dayjs instead of using date-fns
```

Теперь в вашем бандле две библиотеки для работы с датами. ИИ выбрал dayjs, потому что «знает» dayjs по обучающим данным. Он не знает о решении вашей команды стандартизировать date-fns.

> **Заметка профессора:** Хочу сразу прояснить одну вещь. ИИ не злонамерен и не ленив, когда дрейфует. Он делает всё, что может, опираясь на паттерны из обучения. Проблема в том, что *ваших* конкретных паттернов и решений в его обучающих данных нет. Поэтому нам нужно автоматическое принуждение: воспитывать ИИ промптами ненадёжно, а ловить дрейф линтерами — детерминированно.

---

## 2.2 Как ИИ-компании думают о дрейфе замысла

### RLHF у OpenAI: предотвращение дрейфа на уровне модели

Обучение с подкреплением на основе обратной связи от людей (RLHF) у OpenAI — по сути система предотвращения дрейфа замысла, только на уровне модели, а не кода.

Процесс выглядит так:

1. **«Спецификация» — это человеческие предпочтения.** Люди-оценщики определяют, как выглядят «хороший» и «плохой» ответы.
2. **Модель генерирует ответы.** Это «реализации».
3. **Модель вознаграждения оценивает соответствие.** Это «линтер» — он проверяет, совпадает ли ответ с человеческими предпочтениями.
4. **Модель дообучается.** Ответы, отклоняющиеся от человеческих предпочтений, получают штраф.

Ключевое наблюдение: **RLHF — это автоматическая система линтинга поведения.** Она непрерывно сверяет выходы модели со спецификацией (человеческими предпочтениями) и исправляет дрейф.

### RLAIF и Constitutional AI у Anthropic: само-линтинг

Anthropic идёт дальше с RLAIF (обучение с подкреплением на основе обратной связи от ИИ) и Constitutional AI:

1. **«Спецификация» — набор принципов** (конституция) — явные правила о том, как должен вести себя Claude.
2. **Модель генерирует ответы**, а затем *оценивает собственные ответы* на соответствие принципам.
3. **Ответы, нарушающие принципы, переписываются** — по сути модель «линтит» саму себя.
4. **Переписанные ответы идут в обучение** — возникает петля обратной связи.

Это поразительно похоже на то, что мы построим для кода: система, где спецификация закодирована правилами, вывод ИИ сверяется с этими правилами, а нарушения помечаются автоматически.

### Gemini от Google: валидация структурированного вывода

Подход Google с Gemini делает ставку на структурированный вывод: ИИ ограничивают форматом, который можно провалидировать по схеме. Их инструмент Gemini Code Assist использует конфигурации уровня проекта для определения стандартов кодирования, и вывод ИИ проверяется по этим конфигурациям, прежде чем попасть к разработчику.

Это аналогично паттерну `.cursorrules`, о котором мы поговорим ниже в этой главе: постоянные конфигурационные файлы, ограничивающие поведение ИИ.

---

## 2.3 Пользовательские правила ESLint как исполнители спецификации

### ESLint: ваша первая линия автоматической обороны

ESLint (и его экосистема) — самый практичный инструмент принуждения к ограничениям спецификации в проектах на JavaScript/TypeScript. Давайте напишем несколько собственных правил.

### Пример 1: принуждение к стилизации только через Tailwind

Вспомните ограничение нашей спецификации: «Используйте Tailwind CSS для всей стилизации. Никаких собственных CSS-файлов».

```javascript
// eslint-rules/no-custom-css-imports.js

/**
 * ESLint rule: no-custom-css-imports
 *
 * Enforces spec constraint: "All styling SHALL use Tailwind CSS.
 * No custom CSS files shall be created or imported."
 *
 * @spec styling-standards v2.1
 * @specLine 3
 */
module.exports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow importing custom CSS files (spec: Tailwind-only styling)',
      category: 'Spec Compliance',
    },
    messages: {
      noCustomCSS:
        'Custom CSS imports are not allowed. Use Tailwind utility classes instead. ' +
        '(Spec: styling-standards v2.1, line 3)',
    },
    schema: [],
  },

  create(context) {
    return {
      ImportDeclaration(node) {
        const source = node.source.value;

        // Allow Tailwind's base imports
        if (source.includes('tailwindcss') || source === './globals.css') {
          return;
        }

        // Flag any .css, .scss, .less, or .styled imports
        if (/\.(css|scss|sass|less|styled)$/.test(source)) {
          context.report({
            node,
            messageId: 'noCustomCSS',
          });
        }
      },

      // Also catch CSS-in-JS patterns if spec prohibits them
      TaggedTemplateExpression(node) {
        if (
          node.tag.type === 'Identifier' &&
          node.tag.name === 'css'
        ) {
          context.report({
            node,
            messageId: 'noCustomCSS',
          });
        }
      },
    };
  },
};
```

### Пример 2: принуждение к паттернам управления состоянием

```javascript
// eslint-rules/enforce-zustand-state.js

/**
 * ESLint rule: enforce-zustand-state
 *
 * Enforces spec constraint: "All shared state SHALL be managed through
 * Zustand stores. Local React state (useState) is only permitted for
 * UI-only state that doesn't leave the component."
 *
 * @spec state-management v1.0
 * @specLine 1-2
 */
module.exports = {
  meta: {
    type: 'suggestion',
    docs: {
      description: 'Enforce Zustand for shared state management',
      category: 'Spec Compliance',
    },
    messages: {
      preferZustand:
        'Consider using a Zustand store instead of useState for state that may be ' +
        'shared across components. (Spec: state-management v1.0)',
      noRedux:
        'Redux is not permitted. Use Zustand for state management. ' +
        '(Spec: state-management v1.0, line 1)',
      noMobx:
        'MobX is not permitted. Use Zustand for state management. ' +
        '(Spec: state-management v1.0, line 1)',
    },
    schema: [],
  },

  create(context) {
    return {
      // Flag imports of prohibited state libraries
      ImportDeclaration(node) {
        const source = node.source.value;

        if (source === 'redux' || source.startsWith('@reduxjs/')) {
          context.report({ node, messageId: 'noRedux' });
        }

        if (source === 'mobx' || source.startsWith('mobx-')) {
          context.report({ node, messageId: 'noMobx' });
        }
      },

      // Warn on useState usage in files that look like they manage shared state
      CallExpression(node) {
        if (
          node.callee.type === 'Identifier' &&
          node.callee.name === 'useState'
        ) {
          const filename = context.getFilename();

          // If the file is in a 'stores/' or 'state/' directory,
          // useState is definitely wrong
          if (filename.includes('/stores/') || filename.includes('/state/')) {
            context.report({ node, messageId: 'preferZustand' });
          }
        }
      },
    };
  },
};
```

### Пример 3: принуждение к паттернам обработки ошибок

```javascript
// eslint-rules/enforce-result-type.js

/**
 * ESLint rule: enforce-result-type
 *
 * Enforces spec constraint: "All service layer functions SHALL return
 * Result<T, E> types instead of throwing exceptions."
 *
 * @spec error-handling v1.2
 * @specLine 4
 */
module.exports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Enforce Result type pattern for error handling in service layer',
      category: 'Spec Compliance',
    },
    messages: {
      noThrowInService:
        'Service functions must not throw exceptions. Return a Result type instead. ' +
        '(Spec: error-handling v1.2, line 4)',
      noTryCatchInService:
        'Service functions should not use try/catch for flow control. ' +
        'Use Result types for error propagation. ' +
        '(Spec: error-handling v1.2, line 4)',
    },
    schema: [],
  },

  create(context) {
    const filename = context.getFilename();

    // Only enforce in service layer files
    if (!filename.includes('/services/') && !filename.includes('.service.')) {
      return {};
    }

    return {
      ThrowStatement(node) {
        context.report({ node, messageId: 'noThrowInService' });
      },

      TryStatement(node) {
        context.report({ node, messageId: 'noTryCatchInService' });
      },
    };
  },
};
```

### Регистрация собственных правил

```javascript
// .eslintrc.js
module.exports = {
  plugins: ['spec-compliance'],
  rules: {
    'spec-compliance/no-custom-css-imports': 'error',
    'spec-compliance/enforce-zustand-state': 'warn',
    'spec-compliance/enforce-result-type': 'error',
  },

  // Override for test files -- different rules apply
  overrides: [
    {
      files: ['**/*.test.ts', '**/*.spec.ts'],
      rules: {
        'spec-compliance/enforce-result-type': 'off',
      },
    },
  ],
};
```

> **Заметка профессора:** Обратите внимание: каждое правило ссылается на конкретную спецификацию и конкретную её строку. Эта прослеживаемость критична. Когда разработчик (или ИИ) получает ошибку линтера, он должен сразу понять, *почему* существует это ограничение. Ошибка линтера — не просто «так не делай», а «спецификация говорит так, и вот почему».

---

## 2.4 Architecture Decision Records (ADRs) как формализованные ограничения

### Что такое ADR?

Architecture Decision Records — это документы, фиксирующие важные архитектурные решения, их контекст и последствия. В SDD ADR служат *обоснованием* ограничений спецификации.

### Шаблон ADR для SDD

```markdown
# ADR-003: Use Zustand for State Management

## Status
Accepted

## Date
2026-01-15

## Context
We are building a React-based SaaS dashboard that requires shared state across
many components. We need a state management solution that is:
- Lightweight (small bundle impact)
- Type-safe (works well with TypeScript)
- Simple (low learning curve for the team and AI assistants)
- Debuggable (devtools support)

## Decision
We will use Zustand for all shared state management.

## Constraints (to be enforced)
1. All shared state SHALL be managed through Zustand stores
2. React useState is ONLY permitted for component-local UI state
3. No other state management libraries (Redux, MobX, Jotai, Recoil) SHALL be used
4. Zustand stores SHALL be defined in `/src/stores/` directory
5. Each domain SHALL have its own store file (e.g., `user-store.ts`, `cart-store.ts`)

## Consequences
- Positive: Consistent state patterns across the codebase
- Positive: AI assistants can be constrained to generate Zustand-compatible code
- Negative: Some complex state machines may be less elegant than with XState
- Mitigation: For complex state machines, we will use a Zustand middleware pattern

## Enforcement
- ESLint rule: `spec-compliance/enforce-zustand-state`
- CI check: Scan for unauthorized state management imports
- AI constraint: Include in .cursorrules and CLAUDE.md

## Related Specs
- state-management v1.0
- frontend-architecture v2.3
```

### Как ADR связаны с конвейером SDD

```
ADR (Why) --> Spec Constraint (What) --> ESLint Rule (How) --> CI Check (When)
```

ADR объясняет, *почему* было принято решение. Ограничение спецификации определяет, *что* должно быть сделано. Правило ESLint реализует, *как* это проверить. Конвейер CI определяет, *когда* проверка выполняется.

Именно эта цепочка делает SDD принудительно исполняемой. Без неё ограничения живут только в чьей-то памяти или в документе, который никто не читает.

---

## 2.5 Постоянные ограничения спецификации: .cursorrules, CLAUDE.md и настройка IDE

### Проблема амнезии ИИ

Каждый раз, начиная новый разговор с ИИ-ассистентом, вы имеете дело с системой, которая ничего не помнит о ваших прошлых решениях. Она не знает ваших ADR. Не знает, что вы выбрали Zustand вместо Redux. Не знает вашего паттерна обработки ошибок.

Если только вы не расскажете ей. Каждый раз.

Здесь и появляются постоянные конфигурационные файлы. Они автоматически подмешивают ограничения спецификации в контекст ИИ, так что вам не нужно повторяться.

### .cursorrules (IDE Cursor)

Файл `.cursorrules` читается IDE Cursor и подставляется в каждый запрос к ИИ. Он работает как постоянное ограничение спецификации:

```markdown
# .cursorrules

## Project: SaaS Dashboard v2

## Architecture
- Framework: Next.js 14 with App Router
- Language: TypeScript (strict mode)
- Styling: Tailwind CSS ONLY. No custom CSS files. No CSS-in-JS.
- State Management: Zustand. No Redux, MobX, or other state libraries.
- Data Fetching: TanStack Query (React Query). No raw fetch in components.
- Forms: React Hook Form with Zod validation schemas.

## Code Patterns
- Error handling: Use Result<T, E> types in service layer. Never throw in services.
- API routes: Use Zod schemas for request validation. Return typed responses.
- Components: Functional components only. No class components.
- Exports: Named exports only. No default exports (except Next.js pages).

## File Structure
- Components: /src/components/{domain}/{ComponentName}.tsx
- Stores: /src/stores/{domain}-store.ts
- Services: /src/services/{domain}.service.ts
- API routes: /src/app/api/{domain}/route.ts
- Types: /src/types/{domain}.types.ts

## Testing
- Framework: Vitest for unit tests, Playwright for E2E
- Every function must have tests before implementation
- Test files: co-located with source ({file}.test.ts)

## Constraints
- NO console.log in production code (use structured logging)
- NO any type (use unknown if type is genuinely uncertain)
- NO synchronous file I/O
- ALL dates use date-fns (no Moment.js, no dayjs, no manual Date formatting)
- ALL IDs are UUIDs (no auto-increment integers)
```

### CLAUDE.md (Claude Code от Anthropic)

Claude Code читает файлы `CLAUDE.md` в корне проекта и в подкаталогах. Они служат той же цели, что `.cursorrules`, но для CLI-сценария Claude:

```markdown
# CLAUDE.md

## Project Context
This is a multi-tenant SaaS dashboard built with Next.js 14.
Read specs in /specs/ before implementing any feature.

## Critical Rules
1. ALWAYS read the relevant spec file before writing code
2. ALWAYS write tests before implementation
3. NEVER use default exports (except Next.js pages/layouts)
4. NEVER introduce new dependencies without checking /specs/approved-deps.md
5. NEVER use `any` type - use `unknown` and type guards instead

## Architecture Decisions
See /docs/adrs/ for full context. Key decisions:
- ADR-001: Next.js App Router (not Pages Router)
- ADR-002: Tailwind CSS only (no custom CSS)
- ADR-003: Zustand for state management
- ADR-004: Result types for error handling
- ADR-005: date-fns for all date operations

## When Implementing a Feature
1. Read the spec: /specs/{feature-name}.md
2. Check for existing patterns: look at similar features first
3. Write tests that map to spec requirements
4. Implement code that passes the tests
5. Run the linter: npm run lint:spec
6. Run the tests: npm run test

## File Naming Conventions
- Components: PascalCase (UserProfile.tsx)
- Hooks: camelCase with 'use' prefix (useAuth.ts)
- Stores: kebab-case with '-store' suffix (auth-store.ts)
- Services: kebab-case with '.service' suffix (auth.service.ts)
- Types: kebab-case with '.types' suffix (auth.types.ts)
```

### .github/copilot-instructions.md (GitHub Copilot)

GitHub Copilot тоже поддерживает инструкции уровня проекта:

```markdown
# .github/copilot-instructions.md

## Coding Standards
- Use TypeScript strict mode for all files
- Use Tailwind CSS utility classes, never custom CSS
- Use Zustand for shared state management
- Use TanStack Query for server state
- Use Zod for all runtime validation

## Patterns
- Services return Result<T, Error> types, never throw
- Components use named exports only
- All API endpoints validate input with Zod
- Tests come before implementation

## Forbidden Patterns
- No `any` type usage
- No `console.log` (use the logger service)
- No direct DOM manipulation
- No default exports (except Next.js convention files)
```

### Ключевое наблюдение: постоянные ограничения как живые спецификации

Эти конфигурационные файлы — не просто «инструкции для ИИ». Это **живые, версионируемые фрагменты спецификации**, которые путешествуют вместе с кодом. Они:

- **Под контролем версий** — изменения отслеживаются в git
- **Проходят ревью кода** — изменения требуют одобрения команды
- **Согласованы** — каждый участник команды (и каждый ИИ) получает одни и те же ограничения
- **Проверяемы** — их можно валидировать по фактической кодовой базе

> **Заметка профессора:** Один паттерн, который я видел в очень успешном исполнении, — держать эти файлы *сгенерированными* из спецификации. Когда спецификация меняется, скрипт пересоздаёт `.cursorrules`, `CLAUDE.md` и прочие конфигурационные файлы. Так постоянные ограничения всегда синхронны с каноническими документами спецификации. Подробнее разберём в модуле 5.

---

## 2.6 Техники обнаружения дрейфа

### Техника 1: анализ диффа на соответствие ограничениям спецификации

После того как ИИ сгенерировал код, проанализируйте дифф на соответствие известным ограничениям:

```python
# tools/drift-detector.py
"""
Drift Detector: Analyzes git diffs against spec constraints.
Runs as a pre-commit hook or CI step.
"""

import re
import subprocess
import sys
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DriftViolation:
    file: str
    line: int
    rule: str
    message: str
    spec_ref: str
    severity: str  # 'error' or 'warning'


@dataclass
class DriftRule:
    name: str
    spec_ref: str
    severity: str
    pattern: str  # regex pattern to match
    file_glob: str  # which files to check
    message: str
    negate: bool = False  # if True, flag when pattern is NOT found


# Load rules from spec constraints file
def load_rules(rules_path: str = '.spec-lint.json') -> list[DriftRule]:
    """Load drift detection rules from configuration."""
    with open(rules_path) as f:
        data = json.load(f)

    rules = []
    for rule_data in data['rules']:
        rules.append(DriftRule(**rule_data))
    return rules


# Example rules configuration
EXAMPLE_RULES_CONFIG = """
{
  "rules": [
    {
      "name": "no-custom-css",
      "spec_ref": "styling-standards v2.1, line 3",
      "severity": "error",
      "pattern": "import.*\\\\.css['\\\"]",
      "file_glob": "src/**/*.{ts,tsx}",
      "message": "Custom CSS imports are not allowed. Use Tailwind utility classes.",
      "negate": false
    },
    {
      "name": "no-redux",
      "spec_ref": "state-management v1.0, line 1",
      "severity": "error",
      "pattern": "from ['\\\"](@reduxjs|redux)",
      "file_glob": "src/**/*.{ts,tsx}",
      "message": "Redux is not permitted. Use Zustand for state management.",
      "negate": false
    },
    {
      "name": "no-throw-in-services",
      "spec_ref": "error-handling v1.2, line 4",
      "severity": "error",
      "pattern": "throw (new )?\\\\w+",
      "file_glob": "src/services/**/*.ts",
      "message": "Service functions must return Result types, not throw exceptions.",
      "negate": false
    },
    {
      "name": "no-console-log",
      "spec_ref": "logging-standards v1.0, line 2",
      "severity": "warning",
      "pattern": "console\\\\.(log|debug|info|warn|error)",
      "file_glob": "src/**/*.{ts,tsx}",
      "message": "Use the structured logger instead of console methods.",
      "negate": false
    },
    {
      "name": "no-any-type",
      "spec_ref": "typescript-standards v1.0, line 1",
      "severity": "error",
      "pattern": ":\\s*any[\\\\s;,)>]",
      "file_glob": "src/**/*.{ts,tsx}",
      "message": "The 'any' type is not permitted. Use 'unknown' with type guards.",
      "negate": false
    },
    {
      "name": "no-default-export",
      "spec_ref": "module-standards v1.0, line 5",
      "severity": "error",
      "pattern": "export default",
      "file_glob": "src/**/*.{ts,tsx}",
      "message": "Default exports are not allowed. Use named exports.",
      "negate": false
    }
  ]
}
"""


def get_changed_files() -> list[str]:
    """Get list of files changed in the current diff."""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'],
        capture_output=True,
        text=True,
    )
    return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]


def get_diff_lines(filepath: str) -> list[tuple[int, str]]:
    """Get added/modified lines from a specific file's diff."""
    result = subprocess.run(
        ['git', 'diff', '--cached', '-U0', filepath],
        capture_output=True,
        text=True,
    )

    lines = []
    current_line = 0

    for diff_line in result.stdout.split('\n'):
        # Parse hunk headers to track line numbers
        hunk_match = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', diff_line)
        if hunk_match:
            current_line = int(hunk_match.group(1))
            continue

        # Track added lines (starts with +, not ++)
        if diff_line.startswith('+') and not diff_line.startswith('+++'):
            lines.append((current_line, diff_line[1:]))  # Remove the + prefix
            current_line += 1
        elif not diff_line.startswith('-'):
            current_line += 1

    return lines


def check_file(filepath: str, rules: list[DriftRule]) -> list[DriftViolation]:
    """Check a file's diff against all applicable rules."""
    from fnmatch import fnmatch

    violations = []
    diff_lines = get_diff_lines(filepath)

    for rule in rules:
        # Check if this rule applies to this file
        if not fnmatch(filepath, rule.file_glob):
            continue

        pattern = re.compile(rule.pattern)

        for line_num, line_content in diff_lines:
            match = pattern.search(line_content)

            if rule.negate:
                # Negate mode: flag when pattern is NOT found
                if not match:
                    violations.append(DriftViolation(
                        file=filepath,
                        line=line_num,
                        rule=rule.name,
                        message=rule.message,
                        spec_ref=rule.spec_ref,
                        severity=rule.severity,
                    ))
            else:
                # Normal mode: flag when pattern IS found
                if match:
                    violations.append(DriftViolation(
                        file=filepath,
                        line=line_num,
                        rule=rule.name,
                        message=rule.message,
                        spec_ref=rule.spec_ref,
                        severity=rule.severity,
                    ))

    return violations


def main():
    rules = load_rules()
    changed_files = get_changed_files()
    all_violations: list[DriftViolation] = []

    for filepath in changed_files:
        violations = check_file(filepath, rules)
        all_violations.extend(violations)

    # Report
    errors = [v for v in all_violations if v.severity == 'error']
    warnings = [v for v in all_violations if v.severity == 'warning']

    if warnings:
        print(f"\n{'='*60}")
        print(f"SPEC DRIFT WARNINGS: {len(warnings)}")
        print(f"{'='*60}")
        for v in warnings:
            print(f"  [{v.rule}] {v.file}:{v.line}")
            print(f"    {v.message}")
            print(f"    Spec: {v.spec_ref}")
            print()

    if errors:
        print(f"\n{'='*60}")
        print(f"SPEC DRIFT ERRORS: {len(errors)}")
        print(f"{'='*60}")
        for v in errors:
            print(f"  [{v.rule}] {v.file}:{v.line}")
            print(f"    {v.message}")
            print(f"    Spec: {v.spec_ref}")
            print()

        print(f"\nCommit blocked: {len(errors)} spec compliance error(s) found.")
        print("Fix the errors above or update the spec if the constraint has changed.")
        sys.exit(1)

    if not all_violations:
        print("Spec compliance check passed. No drift detected.")

    sys.exit(0)


if __name__ == '__main__':
    main()
```

### Техника 2: сопоставление с образцами для одобренных зависимостей

```typescript
// tools/dependency-auditor.ts

/**
 * Dependency Auditor
 *
 * Checks that only approved dependencies are used in the project.
 * Approved dependencies are listed in the spec: /specs/approved-deps.md
 */

import { readFileSync } from 'fs';

interface AuditResult {
  approved: string[];
  unapproved: string[];
  specRef: string;
}

function loadApprovedDeps(specPath: string): Set<string> {
  const content = readFileSync(specPath, 'utf-8');
  const deps = new Set<string>();

  // Parse the approved deps spec (assumes a markdown list format)
  const lines = content.split('\n');
  for (const line of lines) {
    const match = line.match(/^[-*]\s+`([^`]+)`/);
    if (match) {
      deps.add(match[1]);
    }
  }

  return deps;
}

function loadInstalledDeps(packageJsonPath: string): string[] {
  const content = readFileSync(packageJsonPath, 'utf-8');
  const pkg = JSON.parse(content);

  return [
    ...Object.keys(pkg.dependencies || {}),
    ...Object.keys(pkg.devDependencies || {}),
  ];
}

function auditDependencies(): AuditResult {
  const approved = loadApprovedDeps('specs/approved-deps.md');
  const installed = loadInstalledDeps('package.json');

  const approvedList: string[] = [];
  const unapprovedList: string[] = [];

  for (const dep of installed) {
    if (approved.has(dep)) {
      approvedList.push(dep);
    } else {
      unapprovedList.push(dep);
    }
  }

  return {
    approved: approvedList,
    unapproved: unapprovedList,
    specRef: 'specs/approved-deps.md',
  };
}

// Run the audit
const result = auditDependencies();

if (result.unapproved.length > 0) {
  console.error('\nUNAPPROVED DEPENDENCIES DETECTED:');
  console.error('================================');
  for (const dep of result.unapproved) {
    console.error(`  - ${dep}`);
  }
  console.error(`\nApproved dependencies are listed in: ${result.specRef}`);
  console.error('To add a new dependency, update the spec and get team approval.');
  process.exit(1);
} else {
  console.log('All dependencies are approved per spec.');
}
```

### Техника 3: анализ импортов через AST

Для более глубокого анализа можно изучить абстрактное синтаксическое дерево сгенерированного кода:

```typescript
// tools/import-analyzer.ts

import * as ts from 'typescript';
import { readFileSync, readdirSync, statSync } from 'fs';
import { join, relative } from 'path';

interface ImportViolation {
  file: string;
  line: number;
  importSource: string;
  rule: string;
  message: string;
}

interface ImportRule {
  name: string;
  // Pattern for files this rule applies to
  filePattern: RegExp;
  // Allowed import patterns (regex)
  allowedImports: RegExp[];
  // Blocked import patterns (regex)
  blockedImports: RegExp[];
  message: string;
}

const IMPORT_RULES: ImportRule[] = [
  {
    name: 'component-isolation',
    filePattern: /src\/components\/.+\.tsx?$/,
    allowedImports: [
      /^react/,
      /^next/,
      /^@\/components/,
      /^@\/hooks/,
      /^@\/types/,
      /^@\/lib/,
      /^@\/stores/,
      /^\.\//,     // relative imports within component directory
      /^\.\.\//,   // parent directory imports
      /^class-variance-authority/,
      /^clsx/,
      /^tailwind-merge/,
    ],
    blockedImports: [
      /^@\/services/,  // Components should not import services directly
      /^@\/app\/api/,  // Components should not import API routes
      /^prisma/,       // Components should never touch the database
      /^@prisma/,
    ],
    message: 'Components must not import directly from services, API routes, or database layers. Use hooks or stores as intermediaries.',
  },
  {
    name: 'service-isolation',
    filePattern: /src\/services\/.+\.ts$/,
    allowedImports: [
      /^@\/types/,
      /^@\/lib/,
      /^@\/config/,
      /^prisma/,
      /^@prisma/,
      /^zod/,
      /^date-fns/,
      /^\.\//,
      /^\.\.\//,
    ],
    blockedImports: [
      /^react/,          // Services must not depend on React
      /^@\/components/,  // Services must not depend on UI
      /^@\/hooks/,       // Services must not depend on hooks
      /^@\/stores/,      // Services must not depend on stores
    ],
    message: 'Service layer must not depend on React, components, hooks, or stores. Services should be framework-agnostic.',
  },
];

function analyzeFile(filePath: string): ImportViolation[] {
  const violations: ImportViolation[] = [];
  const content = readFileSync(filePath, 'utf-8');
  const sourceFile = ts.createSourceFile(
    filePath,
    content,
    ts.ScriptTarget.Latest,
    true,
  );

  const relPath = relative(process.cwd(), filePath);

  for (const rule of IMPORT_RULES) {
    if (!rule.filePattern.test(relPath)) continue;

    ts.forEachChild(sourceFile, (node) => {
      if (ts.isImportDeclaration(node)) {
        const moduleSpecifier = (node.moduleSpecifier as ts.StringLiteral).text;
        const line = sourceFile.getLineAndCharacterOfPosition(node.getStart()).line + 1;

        // Check blocked imports
        for (const blocked of rule.blockedImports) {
          if (blocked.test(moduleSpecifier)) {
            violations.push({
              file: relPath,
              line,
              importSource: moduleSpecifier,
              rule: rule.name,
              message: rule.message,
            });
          }
        }
      }
    });
  }

  return violations;
}

function walkDir(dir: string, filePattern: RegExp): string[] {
  const files: string[] = [];

  for (const entry of readdirSync(dir)) {
    const fullPath = join(dir, entry);
    const stat = statSync(fullPath);

    if (stat.isDirectory() && !entry.startsWith('.') && entry !== 'node_modules') {
      files.push(...walkDir(fullPath, filePattern));
    } else if (filePattern.test(fullPath)) {
      files.push(fullPath);
    }
  }

  return files;
}

// Main analysis
const files = walkDir('src', /\.tsx?$/);
const allViolations: ImportViolation[] = [];

for (const file of files) {
  allViolations.push(...analyzeFile(file));
}

if (allViolations.length > 0) {
  console.error(`\nIMPORT POLICY VIOLATIONS: ${allViolations.length}`);
  console.error('========================================');
  for (const v of allViolations) {
    console.error(`\n  [${v.rule}] ${v.file}:${v.line}`);
    console.error(`    Import: ${v.importSource}`);
    console.error(`    ${v.message}`);
  }
  process.exit(1);
} else {
  console.log('Import policy check passed. No violations found.');
}
```

---

## 2.7 Строим собственный «Spec Linter»

### Полный фреймворк spec-линтера

Давайте построим полноценный фреймворк линтинга спецификаций, который можно настроить под любой проект:

```typescript
// tools/spec-linter/index.ts

import { readFileSync, existsSync } from 'fs';
import { resolve, relative } from 'path';

// =============================================
// Types
// =============================================

interface LintResult {
  passed: boolean;
  violations: Violation[];
  warnings: Violation[];
  checkedFiles: number;
  rulesApplied: number;
}

interface Violation {
  rule: string;
  severity: 'error' | 'warning';
  file: string;
  line?: number;
  message: string;
  specRef: string;
  fix?: string;
}

interface SpecRule {
  name: string;
  specRef: string;
  severity: 'error' | 'warning';
  check: (filePath: string, content: string) => Violation[];
}

// =============================================
// Rule Definitions
// =============================================

function createPatternRule(config: {
  name: string;
  specRef: string;
  severity: 'error' | 'warning';
  filePattern: RegExp;
  searchPattern: RegExp;
  message: string;
  fix?: string;
}): SpecRule {
  return {
    name: config.name,
    specRef: config.specRef,
    severity: config.severity,
    check(filePath: string, content: string): Violation[] {
      if (!config.filePattern.test(filePath)) return [];

      const violations: Violation[] = [];
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        if (config.searchPattern.test(lines[i])) {
          violations.push({
            rule: config.name,
            severity: config.severity,
            file: filePath,
            line: i + 1,
            message: config.message,
            specRef: config.specRef,
            fix: config.fix,
          });
        }
      }

      return violations;
    },
  };
}

// =============================================
// Standard Rule Library
// =============================================

const STANDARD_RULES: SpecRule[] = [
  // ---- Styling Constraints ----
  createPatternRule({
    name: 'no-inline-styles',
    specRef: 'styling-standards v2.1',
    severity: 'error',
    filePattern: /\.(tsx|jsx)$/,
    searchPattern: /style\s*=\s*\{\{/,
    message: 'Inline styles are not permitted. Use Tailwind utility classes.',
    fix: 'Replace inline styles with equivalent Tailwind classes.',
  }),

  createPatternRule({
    name: 'no-css-imports',
    specRef: 'styling-standards v2.1',
    severity: 'error',
    filePattern: /\.(ts|tsx|js|jsx)$/,
    searchPattern: /import\s+.*['"].*\.(css|scss|sass|less)['"]/,
    message: 'CSS file imports are not allowed. Use Tailwind utility classes.',
  }),

  // ---- Type Safety Constraints ----
  createPatternRule({
    name: 'no-any-type',
    specRef: 'typescript-standards v1.0',
    severity: 'error',
    filePattern: /\.(ts|tsx)$/,
    searchPattern: /:\s*any\b/,
    message: 'The "any" type is not permitted. Use "unknown" with type guards.',
    fix: 'Replace "any" with "unknown" and add appropriate type guards.',
  }),

  createPatternRule({
    name: 'no-ts-ignore',
    specRef: 'typescript-standards v1.0',
    severity: 'error',
    filePattern: /\.(ts|tsx)$/,
    searchPattern: /@ts-ignore/,
    message: '@ts-ignore is not permitted. Fix the type error or use @ts-expect-error with a reason.',
    fix: 'Replace @ts-ignore with @ts-expect-error and add explanation.',
  }),

  // ---- Error Handling Constraints ----
  createPatternRule({
    name: 'no-throw-in-services',
    specRef: 'error-handling v1.2',
    severity: 'error',
    filePattern: /src\/services\/.*\.ts$/,
    searchPattern: /\bthrow\s+/,
    message: 'Service functions must not throw. Return Result<T, E> types instead.',
  }),

  // ---- Logging Constraints ----
  createPatternRule({
    name: 'no-console-log',
    specRef: 'logging-standards v1.0',
    severity: 'warning',
    filePattern: /src\/(?!.*\.(test|spec)\.).*\.(ts|tsx)$/,
    searchPattern: /console\.(log|debug|info|warn|error)\(/,
    message: 'Use the structured logger instead of console methods.',
    fix: 'Replace console.xxx() with logger.xxx() from @/lib/logger.',
  }),

  // ---- Security Constraints ----
  createPatternRule({
    name: 'no-hardcoded-secrets',
    specRef: 'security-standards v1.0',
    severity: 'error',
    filePattern: /\.(ts|tsx|js|jsx)$/,
    searchPattern: /(password|secret|api_key|apikey|token)\s*[:=]\s*['"][^'"]+['"]/i,
    message: 'Potential hardcoded secret detected. Use environment variables.',
    fix: 'Move secrets to .env and access via process.env.VARIABLE_NAME.',
  }),

  // ---- Naming Convention Constraints ----
  {
    name: 'component-naming',
    specRef: 'naming-conventions v1.0',
    severity: 'warning',
    check(filePath: string, content: string): Violation[] {
      if (!/src\/components\/.*\.tsx$/.test(filePath)) return [];

      const violations: Violation[] = [];
      const fileName = filePath.split('/').pop()!;

      // Component files should be PascalCase
      if (!/^[A-Z][a-zA-Z0-9]*\.tsx$/.test(fileName)) {
        violations.push({
          rule: 'component-naming',
          severity: 'warning',
          file: filePath,
          message: `Component file "${fileName}" should be PascalCase (e.g., UserProfile.tsx).`,
          specRef: 'naming-conventions v1.0',
        });
      }

      return violations;
    },
  },

  // ---- Architecture Layer Constraints ----
  {
    name: 'layer-isolation',
    specRef: 'architecture v2.3',
    severity: 'error',
    check(filePath: string, content: string): Violation[] {
      const violations: Violation[] = [];

      // Components should not import from services directly
      if (/src\/components\//.test(filePath)) {
        const lines = content.split('\n');
        for (let i = 0; i < lines.length; i++) {
          if (/from\s+['"]@\/services\//.test(lines[i])) {
            violations.push({
              rule: 'layer-isolation',
              severity: 'error',
              file: filePath,
              line: i + 1,
              message: 'Components must not import from the service layer directly. Use hooks or stores as intermediaries.',
              specRef: 'architecture v2.3, layer isolation principle',
            });
          }
        }
      }

      return violations;
    },
  },
];

// =============================================
// Linter Engine
// =============================================

class SpecLinter {
  private rules: SpecRule[] = [];

  constructor(rules: SpecRule[] = STANDARD_RULES) {
    this.rules = rules;
  }

  addRule(rule: SpecRule): void {
    this.rules.push(rule);
  }

  lintFile(filePath: string): Violation[] {
    if (!existsSync(filePath)) return [];

    const content = readFileSync(filePath, 'utf-8');
    const violations: Violation[] = [];

    for (const rule of this.rules) {
      violations.push(...rule.check(filePath, content));
    }

    return violations;
  }

  lintFiles(filePaths: string[]): LintResult {
    const allViolations: Violation[] = [];

    for (const filePath of filePaths) {
      allViolations.push(...this.lintFile(filePath));
    }

    const errors = allViolations.filter(v => v.severity === 'error');
    const warnings = allViolations.filter(v => v.severity === 'warning');

    return {
      passed: errors.length === 0,
      violations: errors,
      warnings,
      checkedFiles: filePaths.length,
      rulesApplied: this.rules.length,
    };
  }
}

export { SpecLinter, SpecRule, Violation, LintResult, STANDARD_RULES };
```

### Использование spec-линтера

```typescript
// tools/spec-linter/run.ts

import { SpecLinter, STANDARD_RULES } from './index';
import { execSync } from 'child_process';

// Get files to lint (from git diff or all source files)
const mode = process.argv[2] || 'changed';

let files: string[];

if (mode === 'changed') {
  // Only lint changed files
  const output = execSync('git diff --cached --name-only --diff-filter=ACMR')
    .toString()
    .trim();
  files = output ? output.split('\n') : [];
} else {
  // Lint all source files
  const output = execSync('find src -name "*.ts" -o -name "*.tsx"')
    .toString()
    .trim();
  files = output ? output.split('\n') : [];
}

if (files.length === 0) {
  console.log('No files to lint.');
  process.exit(0);
}

const linter = new SpecLinter(STANDARD_RULES);
const result = linter.lintFiles(files);

// Output report
console.log('\n========================================');
console.log('       SPEC COMPLIANCE REPORT');
console.log('========================================');
console.log(`Files checked: ${result.checkedFiles}`);
console.log(`Rules applied: ${result.rulesApplied}`);
console.log(`Errors: ${result.violations.length}`);
console.log(`Warnings: ${result.warnings.length}`);
console.log('========================================\n');

if (result.warnings.length > 0) {
  console.log('WARNINGS:');
  for (const w of result.warnings) {
    const location = w.line ? `:${w.line}` : '';
    console.log(`  [${w.rule}] ${w.file}${location}`);
    console.log(`    ${w.message}`);
    console.log(`    Spec: ${w.specRef}`);
    if (w.fix) {
      console.log(`    Fix: ${w.fix}`);
    }
    console.log();
  }
}

if (result.violations.length > 0) {
  console.log('ERRORS:');
  for (const v of result.violations) {
    const location = v.line ? `:${v.line}` : '';
    console.log(`  [${v.rule}] ${v.file}${location}`);
    console.log(`    ${v.message}`);
    console.log(`    Spec: ${v.specRef}`);
    if (v.fix) {
      console.log(`    Fix: ${v.fix}`);
    }
    console.log();
  }

  console.log(`\nFAILED: ${result.violations.length} spec compliance error(s).`);
  process.exit(1);
}

console.log('PASSED: All spec compliance checks passed.');
process.exit(0);
```

---

## 2.8 Интеграция в CI/CD: автоматические проверки соответствия спецификации

### Рабочий процесс GitHub Actions

```yaml
# .github/workflows/spec-compliance.yml

name: Spec Compliance Check

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]

jobs:
  spec-lint:
    name: Spec Compliance Lint
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Need full history for diff analysis

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci

      # Step 1: Standard linting (ESLint with spec rules)
      - name: ESLint with Spec Rules
        run: npx eslint src/ --max-warnings 0

      # Step 2: Custom spec linting
      - name: Spec Compliance Lint
        run: npx tsx tools/spec-linter/run.ts all

      # Step 3: Dependency audit
      - name: Dependency Audit
        run: npx tsx tools/dependency-auditor.ts

      # Step 4: Import policy check
      - name: Import Policy Check
        run: npx tsx tools/import-analyzer.ts

      # Step 5: Spec coverage check
      - name: Spec Coverage Report
        run: |
          npx tsx tools/spec-coverage.ts \
            --specs-dir specs/ \
            --tests-dir src/ \
            --min-coverage 80 \
            --report-format markdown \
            --output spec-coverage-report.md

      # Step 6: Post results to PR
      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('spec-coverage-report.md', 'utf-8');

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Spec Compliance Report\n\n${report}`
            });

  spec-tests:
    name: Spec-Mapped Tests
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - run: npm ci

      - name: Run Tests with Spec Coverage
        run: |
          npx vitest run --reporter=verbose --coverage \
            2>&1 | tee test-output.txt

      - name: Verify Spec Coverage Thresholds
        run: npx tsx tools/spec-coverage.ts --min-coverage 80
```

### Интеграция в pre-commit хук

```bash
#!/bin/bash
# .husky/pre-commit

echo "Running spec compliance checks..."

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep -E '\.(ts|tsx)$')

if [ -z "$STAGED_FILES" ]; then
  echo "No TypeScript files staged. Skipping spec lint."
  exit 0
fi

# Run ESLint on staged files
echo "  [1/3] ESLint with spec rules..."
echo "$STAGED_FILES" | xargs npx eslint --quiet
if [ $? -ne 0 ]; then
  echo "ESLint failed. Fix errors before committing."
  exit 1
fi

# Run spec linter on staged files
echo "  [2/3] Spec compliance lint..."
npx tsx tools/spec-linter/run.ts changed
if [ $? -ne 0 ]; then
  echo "Spec compliance check failed. Fix errors before committing."
  exit 1
fi

# Run dependency audit (only if package.json changed)
if echo "$STAGED_FILES" | grep -q "package.json"; then
  echo "  [3/3] Dependency audit..."
  npx tsx tools/dependency-auditor.ts
  if [ $? -ne 0 ]; then
    echo "Dependency audit failed. Unapproved dependencies detected."
    exit 1
  fi
else
  echo "  [3/3] Dependency audit (skipped - package.json unchanged)"
fi

echo "All spec compliance checks passed."
exit 0
```

---

## 2.9 Реальные примеры дрейфа

### Случай 1: постепенная миграция, которой не случилось

**Спецификация:** «Все новые компоненты ДОЛЖНЫ использовать новую дизайн-систему (v2). Легаси-компоненты мигрируются постепенно».

**Что произошло:** для новых фич использовали ИИ-ассистента. Ему дали спецификацию, и поначалу он генерировал компоненты на дизайн-системе v2. Но существующая кодовая база была полна паттернов v1. Со временем, подтягивая существующий код в контекст, ИИ начал смешивать паттерны v1 и v2. Через три месяца:

- 40% новых компонентов использовали только v2
- 35% смешивали v1 и v2
- 25% использовали только v1 (ИИ копировал существующие паттерны)

**Как это можно было поймать:**

```javascript
// ESLint rule: enforce-design-system-v2
// Flags any import from the v1 design system in new files
createPatternRule({
  name: 'no-design-system-v1',
  specRef: 'design-system-migration v1.0',
  severity: 'error',
  filePattern: /src\/components\/.*\.tsx$/,
  searchPattern: /from\s+['"]@\/design-system\/v1/,
  message: 'New components must use design system v2. Import from @/design-system/v2 instead.',
});
```

### Случай 2: несанкционированная миграция базы данных

**Спецификация:** «Приложение ДОЛЖНО использовать PostgreSQL с ORM Prisma. Весь доступ к базе данных ДОЛЖЕН идти через сервисный слой».

**Что произошло:** разработчик попросил ИИ «быстро добавить слой кеширования для поиска пользователей». ИИ выдал решение на Redis — совершенно разумный инженерный выбор, который, однако, принёс:

- Новую рантайм-зависимость (Redis)
- Новое требование к инфраструктуре (сервер Redis)
- Прямой доступ к базе данных из слоя кеша (в обход сервисного слоя)
- Иной паттерн доступа к данным, чем в остальном приложении

В разработке код работал безупречно (ИИ заботливо добавил настройку подключения к Redis). Он сломался только в staging-окружении, где экземпляра Redis не было.

**Как это можно было поймать:**

```typescript
// Dependency audit would have flagged 'ioredis' or 'redis' as unapproved
// Import analyzer would have flagged direct database access outside service layer
// Architecture layer check would have flagged the violation

// Additionally, a spec linter rule for infrastructure dependencies:
createPatternRule({
  name: 'approved-infrastructure-only',
  specRef: 'infrastructure v2.0',
  severity: 'error',
  filePattern: /\.(ts|tsx)$/,
  searchPattern: /from\s+['"](?:ioredis|redis|mongodb|mongoose|dynamodb)/,
  message: 'Only approved infrastructure dependencies may be used. Current approved: PostgreSQL (via Prisma). See specs/infrastructure.md.',
});
```

### Случай 3: тихое размывание типов

**Спецификация:** «Режим strict в TypeScript ДОЛЖЕН быть включён. Использование типа `any` запрещено».

**Что произошло:** за 200 коммитов с участием ИИ использование `any` росло постепенно:

1. Сначала `any` появился в тестовых файлах (казалось безобидным)
2. Затем в служебных функциях («это же просто хелпер»)
3. Затем в определениях типов (`Record<string, any>`)
4. Затем в функциях сервисного слоя
5. Наконец в обработчиках API-маршрутов

К тому моменту, когда кто-то это заметил, в кодовой базе было 147 вхождений `any`. Настройка strict в TypeScript всё ещё была включена, но `any` фактически её обходит.

**Как это можно было поймать:**

```yaml
# In the CI pipeline: zero-tolerance policy for `any`
- name: Type Safety Audit
  run: |
    ANY_COUNT=$(grep -r ": any\b" src/ --include="*.ts" --include="*.tsx" -c || echo 0)
    if [ "$ANY_COUNT" -gt "0" ]; then
      echo "ERROR: Found $ANY_COUNT instances of 'any' type in source code."
      echo "Spec violation: typescript-standards v1.0"
      grep -rn ": any\b" src/ --include="*.ts" --include="*.tsx"
      exit 1
    fi
```

> **Заметка профессора:** Этот последний случай мой любимый, потому что он иллюстрирует проблему варёной лягушки. Ни одно отдельное вхождение `any` не выглядело тревожно. У каждого было правдоподобное обоснование. Но в сумме они размыли типовую безопасность, которую спецификация должна была гарантировать. Именно поэтому важно автоматическое принуждение: люди находят исключениям оправдания, а линтеры — нет.

---

## 2.10 Петля обратной связи: от обнаружения к предотвращению

### Цикл обнаружения и исправления дрейфа

```
  +------------------+
  |   AI Generates   |
  |      Code        |
  +--------+---------+
           |
           v
  +--------+---------+
  |   Spec Linter    |
  |   Runs Checks    |
  +--------+---------+
           |
      +----+----+
      |         |
   PASS      FAIL
      |         |
      v         v
  +---+---+ +---+----------+
  | Merge | | Report       |
  |       | | Violations   |
  +-------+ +---+----------+
                |
                v
        +-------+--------+
        |  Determine     |
        |  Root Cause    |
        +-------+--------+
                |
        +-------+--------+
        |                |
   Spec Gap         AI Drift
        |                |
        v                v
  +-----+------+  +-----+--------+
  | Update     |  | Update       |
  | Spec       |  | AI Context   |
  | Add Rule   |  | (.cursorrules|
  +-----+------+  | CLAUDE.md)   |
        |         +-----+--------+
        v               |
  +-----+------+        |
  | Add Test   |        |
  | for Gap    |<-------+
  +------------+
```

Ключевое соображение: каждое нарушение дрейфа должно возвращаться в систему одним из двух способов:

1. **В спецификации был пробел** — дополните спецификацию и добавьте новое правило, чтобы предотвратить дрейф в будущем
2. **ИИ отклонился от ясной спецификации** — обновите файлы контекста ИИ, чтобы усилить ограничение

### Ведение журнала обратной связи

Ведите журнал дрейфа, в котором нарушения прослеживаются во времени:

```markdown
# Drift Log

## 2026-02-10

### Violation: Unauthorized Redis dependency
- **Detected by:** Dependency audit (CI)
- **Root cause:** AI introduced Redis without checking approved deps list
- **Action taken:**
  - Removed Redis dependency
  - Implemented caching with approved infrastructure (Prisma with PostgreSQL materialized views)
  - Added `redis`, `ioredis`, `memcached` to blocked dependency list
  - Updated CLAUDE.md to emphasize checking approved-deps.md before adding dependencies

## 2026-02-03

### Violation: Custom CSS in tooltip component
- **Detected by:** Spec linter (pre-commit hook)
- **Root cause:** AI fell back to CSS for `position: absolute` tooltips
- **Action taken:**
  - Replaced custom CSS with Tailwind positioning classes
  - Added comment in .cursorrules: "Tooltips: use Tailwind absolute positioning, not custom CSS"
  - Created shared Tooltip component to prevent repeated drift
```

---

## 2.11 Упражнения

### Упражнение 1: напишите собственное правило ESLint (начальный уровень)

Напишите собственное правило ESLint, которое обеспечивает соблюдение ограничения спецификации:

```
"All React components SHALL use named exports. Default exports are only permitted
for Next.js page and layout files (page.tsx, layout.tsx, template.tsx)."
```

Ваше правило должно:
- Помечать `export default` в файлах `.tsx`
- Разрешать `export default` в файлах с именами `page.tsx`, `layout.tsx` или `template.tsx`
- Включать ссылку на спецификацию в сообщение об ошибке

### Упражнение 2: составьте конфигурацию spec-линтера (средний уровень)

По следующему ADR создайте полный конфигурационный файл `.spec-lint.json` минимум с 8 правилами:

```markdown
# ADR-007: API Design Standards

## Decision
- All API endpoints use REST conventions
- Request/response bodies use camelCase JSON
- All endpoints require authentication (except /health and /auth/*)
- Rate limiting: 100 requests per minute per user
- Pagination: cursor-based, not offset-based
- Errors: RFC 7807 Problem Details format
- Dates: ISO 8601 format, always UTC
- IDs: UUIDs v4, never auto-increment integers
```

### Упражнение 3: найдите дрейф в пул-реквесте (продвинутый уровень)

Разберите следующий смоделированный дифф пул-реквеста и найдите все нарушения спецификации. Сначала перечислены ограничения спецификации, затем идёт дифф.

**Ограничения спецификации:**
1. Только Tailwind CSS
2. Zustand для управления состоянием
3. date-fns для операций с датами
4. Никакого типа `any`
5. Только именованные экспорты
6. Сервисы возвращают типы Result

**Дифф PR:**
```diff
+ // src/components/Dashboard.tsx
+ import React, { useState } from 'react';
+ import moment from 'moment';
+ import styles from './Dashboard.module.css';
+
+ export default function Dashboard() {
+   const [data, setData] = useState<any>(null);
+
+   const formattedDate = moment().format('YYYY-MM-DD');
+
+   return (
+     <div className={styles.container}>
+       <h1 style={{ color: 'blue', fontSize: '24px' }}>
+         Dashboard - {formattedDate}
+       </h1>
+     </div>
+   );
+ }
```

```diff
+ // src/services/user.service.ts
+ import { prisma } from '@/lib/db';
+
+ export async function getUser(id: string) {
+   try {
+     const user = await prisma.user.findUnique({ where: { id } });
+     if (!user) {
+       throw new Error('User not found');
+     }
+     return user;
+   } catch (error) {
+     throw error;
+   }
+ }
```

**Что нужно сдать:** список всех нарушений спецификации с указанием нарушенного правила, файла и строки, а также предлагаемое исправление.

### Упражнение 4: спроектируйте полную систему предотвращения дрейфа (продвинутый уровень)

Для проекта на ваш выбор (или для SaaS-дашборда, который мы используем как пример) спроектируйте полную систему предотвращения дрейфа, включающую:

1. Конфигурацию `.spec-lint.json` минимум с 12 правилами
2. Файл `.cursorrules` (или `CLAUDE.md`), кодирующий ключевые ограничения
3. Рабочий процесс GitHub Actions, запускающий все проверки
4. Конфигурацию pre-commit хука
5. ADR, документирующий вашу стратегию предотвращения дрейфа

**Что нужно сдать:** все пять файлов с комментариями, объясняющими назначение каждого правила и проверки.

---

## Итоги

В этой главе мы разобрали понятие дрейфа замысла и построили целостную систему его обнаружения и предотвращения.

**Ключевые выводы:**

1. **Дрейф замысла — тихий убийца разработки с ИИ.** Код может быть функционально корректным, нарушая при этом архитектурные решения, ограничения стиля и политику зависимостей.

2. **Три типа дрейфа:** архитектурный (не та технология), паттерновый (не тот подход) и зависимостей (не та библиотека). Каждый требует своей стратегии обнаружения.

3. **Правила ESLint — ваша первая линия обороны.** Собственные правила, ссылающиеся на ограничения спецификации, создают детерминированный слой принуждения.

4. **Постоянные конфигурационные файлы (.cursorrules, CLAUDE.md) снижают дрейф**, автоматически подмешивая ограничения в контекст ИИ.

5. **Интеграция в CI/CD делает принуждение автоматическим.** Проверки соответствия спецификации должны выполняться на каждом коммите и в каждом PR, как и тесты.

6. **Петля обратной связи важна.** Каждое нарушение дрейфа должно приводить либо к обновлению спецификации, либо к обновлению контекста ИИ — чтобы тот же дрейф не повторялся.

7. **RLHF и RLAIF — предотвращение дрейфа в промышленном масштабе**: те же принципы, которыми Anthropic и OpenAI выравнивают свои модели, стоит применять, чтобы выравнивать сгенерированный ИИ код по вашим спецификациям.

В следующей главе мы займёмся практической задачей управления большими спецификациями в больших кодовых базах — стратегией контекстного окна.

---

*Далее: Глава 3 — Стратегия контекстного окна*

---

[← Оглавление курса](../INDEX.ru.md) · [← Глава 1: Сопоставление спецификации и тестов (TDD для ИИ)](CHAPTER_01.ru.md) · [Глава 3: Стратегия контекстного окна →](CHAPTER_03.ru.md)
