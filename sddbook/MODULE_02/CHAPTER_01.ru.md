# Глава 1: Проектирование от схем

## МОДУЛЬ 02 — Определение архитектуры («как») | Средний уровень

> [Оглавление курса](../INDEX.ru.md) · [Модуль 02](../INDEX.ru.md#модуль-02--определение-архитектуры-как)

---

## Вступление к лекции

*Аудитория погружается в сосредоточенную тишину. На экране проектора на тёмном фоне светится определение одного интерфейса TypeScript. Профессор ставит кружку с кофе и поворачивается к классу.*

Доброе утро всем. В прошлом модуле мы говорили о «что» — фиксировали замысел, писали спецификации, описывающие, что должно делать ваше ПО. Сегодня мы переключаемся на «как». И начинаем с того, что я считаю самой важной дисциплиной в разработке через спецификации: **проектирование от схем**.

Вот утверждение, которое я собираюсь защищать следующий час: **если вы определите форму данных до того, как напишете хотя бы строку логики, вы уничтожите целые категории багов, на порядок уменьшите галлюцинации ИИ в сгенерированном коде и сделаете кодовую базу радикально проще для осмысления — и людьми, и машинами.**

Это смелое утверждение. Позвольте его обосновать.

---

## 1.1 Что такое проектирование от схем?

Проектирование от схем (Schema-First Design) — практика формального определения структур данных, их форм, типов, ограничений и связей до написания бизнес-логики, UI-кода или обработчиков API.

Подумайте так: прежде чем архитектор рисует планировки, он не выбирает мебель. Прежде чем инженер-строитель проектирует мост, он не выбирает цвет краски. Сначала структура. Сначала форма.

В ПО «форма» — это ваша модель данных. Это скелет, на котором держится всё остальное.

```typescript
// This is not just a type definition.
// This is a DECISION. A CONTRACT. A SPEC.
interface User {
  id: string;
  email: string;
  displayName: string;
  role: "admin" | "editor" | "viewer";
  createdAt: string; // ISO 8601
  lastLoginAt: string | null;
  preferences: UserPreferences;
}

interface UserPreferences {
  theme: "light" | "dark" | "system";
  language: string; // ISO 639-1 code
  notificationsEnabled: boolean;
  emailDigestFrequency: "daily" | "weekly" | "never";
}
```

Когда вы пишете это раньше всего остального, вы принимаете десятки решений:

- У пользователя есть роль, и ролей ровно три.
- У пользователя может быть null `lastLoginAt` (он зарегистрировался, но никогда не входил).
- У темы три варианта, а не два — «system» это явный выбор.
- Язык — строка, соответствующая стандарту ISO, а не свободное поле.
- Частота дайджеста — перечисление, а не булево «вкл/выкл».

Каждое из этих решений, зафиксированное в схеме, предотвращает разговор в будущем. Не даёт ИИ угадывать. Не даёт коллеге предполагать.

> **Заметка профессора:** За последние два года я просмотрел сотни ИИ-сгенерированных кодовых баз. Самый сильный предиктор качества кода — предоставил ли разработчик схему заранее. Когда предоставлял, ИИ выдавал согласованный, правильный код. Когда нет, ИИ изобретал собственные формы данных — и они были разными в каждом файле.

---

## 1.2 Почему «форма прежде логики»?

Приведу пять конкретных причин, почему форма-прежде-логики — основа надёжной ИИ-разработки.

### Причина 1: модели ИИ исключительно хорошо соответствуют схемам

Большие языковые модели — Claude, GPT-4, Gemini, Llama — по своей сути статистические сопоставители шаблонов. Когда вы даёте им хорошо определённую схему, вы даёте им жёсткое ограничение для сопоставления. Это резко сужает пространство решений.

Рассмотрим два промпта:

**Промпт A (без схемы):**
```
Build me a user authentication system.
```

**Промпт B (от схемы):**
```
Implement the following user authentication system.
The data model is defined by these TypeScript interfaces:

interface AuthRequest {
  email: string;
  password: string;
}

interface AuthResponse {
  success: boolean;
  token: string | null;
  user: AuthenticatedUser | null;
  error: AuthError | null;
}

interface AuthenticatedUser {
  id: string;
  email: string;
  displayName: string;
  role: "admin" | "editor" | "viewer";
}

interface AuthError {
  code: "INVALID_CREDENTIALS" | "ACCOUNT_LOCKED" | "EMAIL_NOT_VERIFIED";
  message: string;
  retryAfterSeconds: number | null;
}
```

Промпт B даст радикально лучший код от любой передовой модели. Схема устраняет неоднозначность о том, какие поля существуют, каких они типов, какие случаи ошибок нужно обработать и как выглядит форма ответа.

### Причина 2: схемы не зависят от языка

JSON Schema или интерфейс TypeScript может прочитать:
- Python-разработчик
- Go-разработчик
- Фронтенд-разработчик на React
- Бэкенд-разработчик на Node.js
- Модель ИИ на любом языке
- Генератор документации
- Тестовый фреймворк
- Библиотека валидации

Схемы — ближайшее к универсальному языку, что у нас есть в разработке ПО.

### Причина 3: схемы позволяют разрабатывать параллельно

Когда схема определена первой, фронтенд и бэкенд могут работать параллельно. Фронтенд мокает данные, соответствующие схеме. Бэкенд реализует конечные точки, выдающие данные по схеме. Когда они соединяются, всё работает — потому что они договорились о форме.

Это не теория. Так работают Google, Meta, Amazon и любая крупная технологическая компания в масштабе. Protocol Buffers от Google, которые мы обсудим позже в этой главе, существуют именно для этого.

### Причина 4: схемы проверяемы

Вы можете написать тесты против схемы до существования любой реализации:

```typescript
import { z } from "zod";

const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  displayName: z.string().min(1).max(100),
  role: z.enum(["admin", "editor", "viewer"]),
  createdAt: z.string().datetime(),
  lastLoginAt: z.string().datetime().nullable(),
});

// This test can be written BEFORE any backend code exists
test("API response conforms to User schema", async () => {
  const response = await fetch("/api/users/123");
  const data = await response.json();
  const result = UserSchema.safeParse(data);
  expect(result.success).toBe(true);
});
```

### Причина 5: схемы предотвращают «проблему дрейфа»

Без канонической схемы формы данных со временем дрейфуют. У базы данных одна форма, API возвращает слегка другую, фронтенд ожидает третью, а сгенерированные ИИ утилиты предполагают четвёртую. Это называют **дрейфом схемы**, и это один из самых частых источников багов в продакшн-приложениях.

Подход «от схемы» создаёт единый источник истины, на который ссылаются все слои.

---

## 1.3 Как ИИ-компании обеспечивают приоритет схем на уровне API

Это не просто лучшая практика, которую мы пропагандируем. Крупнейшие ИИ-компании мира встроили принципы «от схемы» прямо в свои API.

### Структурированные выводы OpenAI

В 2024 году OpenAI представила Structured Outputs — функцию, заставляющую модели GPT возвращать JSON, соответствующий предоставленной JSON Schema. Это был переломный момент. OpenAI по сути сказала: «Мы знаем, что наши модели могут вернуть произвольный текст, но для продакшена нужны гарантии формы вывода».

Вот как это работает:

```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "Extract product information from the user's description."
        },
        {
            "role": "user",
            "content": "I just bought a Sony WH-1000XM5 for $348 from Best Buy"
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "product_extraction",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "productName": {
                        "type": "string",
                        "description": "Full product name"
                    },
                    "brand": {
                        "type": "string",
                        "description": "Manufacturer brand"
                    },
                    "price": {
                        "type": "object",
                        "properties": {
                            "amount": { "type": "number" },
                            "currency": { "type": "string" }
                        },
                        "required": ["amount", "currency"],
                        "additionalProperties": False
                    },
                    "retailer": {
                        "type": "string",
                        "description": "Where the product was purchased"
                    }
                },
                "required": ["productName", "brand", "price", "retailer"],
                "additionalProperties": False
            }
        }
    }
)
```

Обратите внимание, что происходит: схема предоставляется **до** того, как модель генерирует вывод. Модель ограничена соответствием. Это проектирование от схемы на уровне инференса.

### Схемы инструментов Anthropic

Anthropic использует похожий подход в функции tool use (вызов функций) Claude. Когда вы определяете инструмент для Claude, вы предоставляете `input_schema` — JSON Schema, описывающую, какие параметры принимает инструмент:

```python
tools = [
    {
        "name": "search_products",
        "description": "Search the product catalog by various criteria",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string"
                },
                "category": {
                    "type": "string",
                    "enum": ["electronics", "clothing", "books", "home"],
                    "description": "Product category to filter by"
                },
                "priceRange": {
                    "type": "object",
                    "properties": {
                        "min": { "type": "number", "minimum": 0 },
                        "max": { "type": "number", "minimum": 0 }
                    },
                    "required": ["min", "max"]
                },
                "sortBy": {
                    "type": "string",
                    "enum": ["relevance", "price_asc", "price_desc", "rating"],
                    "description": "Sort order for results"
                }
            },
            "required": ["query"]
        }
    }
]
```

Claude сгенерирует вызовы инструментов, соответствующие этой схеме. Схема действует и как документация, и как принуждение. Это не опционально — так работает API. Anthropic спроектировала это так, потому что знает: неструктурированные выводы ведут к сбоям интеграции.

### Вызов функций Gemini от Google

Модели Gemini от Google следуют тому же шаблону. При определении функций для Gemini вы предоставляете схемы параметров, используя подмножество OpenAPI Schema:

```python
from google.generativeai import types

get_weather_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_current_weather",
            description="Get the current weather in a given location",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "location": types.Schema(
                        type=types.Type.STRING,
                        description="City and state, e.g. San Francisco, CA"
                    ),
                    "unit": types.Schema(
                        type=types.Type.STRING,
                        enum=["celsius", "fahrenheit"]
                    )
                },
                required=["location"]
            )
        )
    ]
)
```

Шаблон универсален: **определите форму, затем дайте ИИ её заполнить.**

> **Заметка профессора:** Обратите внимание на нечто примечательное в этом схождении. OpenAI, Anthropic и Google — три компании, которые жёстко конкурируют, — независимо пришли к одному архитектурному решению: использовать JSON Schema для ограничения выводов ИИ. Когда три конкурирующие организации сходятся на одном решении, обратите внимание. Это не совпадение. Это отрасль, открывающая фундаментальную истину.

---

## 1.4 JSON Schema: универсальный язык

Уделим момент признанию JSON Schema как технологии. Она стала лингва франка между людьми и ИИ-системами, между фронтендом и бэкендом, между документацией и валидацией.

### Что такое JSON Schema?

JSON Schema — словарь, позволяющий аннотировать и валидировать JSON-документы. Она сама написана на JSON, а значит машиночитаема, не зависит от языка и может храниться, версионироваться и передаваться как любые другие данные.

Вот полный пример:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/schemas/blog-post.json",
  "title": "BlogPost",
  "description": "A blog post in the content management system",
  "type": "object",
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for the blog post"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200,
      "description": "The title of the blog post"
    },
    "slug": {
      "type": "string",
      "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*$",
      "description": "URL-friendly version of the title"
    },
    "content": {
      "type": "string",
      "minLength": 1,
      "description": "The main content in Markdown format"
    },
    "excerpt": {
      "type": "string",
      "maxLength": 500,
      "description": "Short summary for previews and SEO"
    },
    "author": {
      "$ref": "#/$defs/Author"
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1,
        "maxLength": 50
      },
      "minItems": 1,
      "maxItems": 10,
      "uniqueItems": true,
      "description": "Tags for categorization"
    },
    "status": {
      "type": "string",
      "enum": ["draft", "review", "published", "archived"],
      "description": "Publication status"
    },
    "publishedAt": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "ISO 8601 timestamp when published, null if not yet published"
    },
    "metadata": {
      "$ref": "#/$defs/PostMetadata"
    }
  },
  "required": ["id", "title", "slug", "content", "author", "tags", "status"],
  "additionalProperties": false,
  "$defs": {
    "Author": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "format": "uuid" },
        "name": { "type": "string", "minLength": 1 },
        "email": { "type": "string", "format": "email" },
        "avatarUrl": { "type": "string", "format": "uri" }
      },
      "required": ["id", "name", "email"],
      "additionalProperties": false
    },
    "PostMetadata": {
      "type": "object",
      "properties": {
        "readTimeMinutes": { "type": "integer", "minimum": 1 },
        "wordCount": { "type": "integer", "minimum": 0 },
        "seoTitle": { "type": "string", "maxLength": 60 },
        "seoDescription": { "type": "string", "maxLength": 160 },
        "ogImageUrl": { "type": "string", "format": "uri" }
      },
      "additionalProperties": false
    }
  }
}
```

Посмотрите, сколько информации упаковано в эту схему:

- **Типы** — у каждого поля явный тип
- **Ограничения** — длины строк, числовые диапазоны, размеры массивов
- **Шаблоны** — slug должен соответствовать regex для URL
- **Перечисления** — у статуса ровно четыре допустимых значения
- **Nullable** — publishedAt может быть null (пост ещё не опубликован)
- **Ссылки** — Author и PostMetadata определены один раз и переиспользуются
- **Обязательные поля** — явно перечислены
- **Никаких лишних полей** — `additionalProperties: false` предотвращает дрейф схемы

Этот единственный документ рассказывает фронтенд-разработчику, бэкенд-разработчику, инженеру БД и ИИ-ассистенту всё, что нужно знать о посте блога.

### JSON Schema как протокол коммуникации с ИИ

Когда вы даёте модели ИИ JSON Schema, вы общаетесь максимально точно. Рассмотрим альтернативу:

**Без схемы (естественный язык):**
> «У поста блога должен быть заголовок, немного контента, автор и несколько тегов. Заголовок не должен быть слишком длинным. Статус может быть draft, review, published или archived.»

Это описание неоднозначно. Насколько «слишком длинный»? Какого типа автор — строка с именем или объект? Могут ли теги дублироваться? Что будет, если заголовок пуст?

**Со схемой (формальная спецификация):**

Каждый крайний случай, каждое ограничение, каждая связь явны. ИИ не нужно угадывать. ИИ не нужно проявлять креативность в вашей модели данных. Он просто соответствует.

---

## 1.5 Практический разбор: проектирование полной модели данных

Пройдём реальное упражнение. Спроектируем модель данных для **приложения управления задачами** — вроде упрощённого Jira или Linear.

### Шаг 1: определить основные сущности

Прежде чем писать схему, перечислите сущности:

- **Workspace** — верхнеуровневая организационная единица
- **Project** — коллекция связанных задач внутри workspace
- **Task** — основная единица работы
- **User** — человек, который может быть назначен на задачи или создавать их
- **Comment** — комментарий к задаче
- **Label** — тег, который можно применить к задачам

### Шаг 2: определить связи

Нарисуйте связи (можно буквально набросать на бумаге):

```
Workspace 1---* Project
Project   1---* Task
Task      *---1 User (assignee)
Task      *---1 User (creator)
Task      1---* Comment
Comment   *---1 User (author)
Task      *---* Label
```

### Шаг 3: написать схемы

Теперь пишем интерфейсы TypeScript. Обратите внимание, как мы фиксируем каждое решение:

```typescript
// ============================================
// TASK MANAGEMENT APP — SCHEMA-FIRST DESIGN
// Version: 1.0.0
// Last updated: 2026-02-24
// ============================================

// --- Shared Types ---

/** ISO 8601 date-time string */
type ISODateTime = string;

/** UUID v4 string */
type UUID = string;

// --- Workspace ---

interface Workspace {
  id: UUID;
  name: string;            // 1-100 characters
  slug: string;            // URL-friendly, lowercase, hyphens only
  ownerId: UUID;           // References User.id
  plan: "free" | "pro" | "enterprise";
  memberCount: number;     // Denormalized for display
  createdAt: ISODateTime;
  updatedAt: ISODateTime;
}

// --- Project ---

interface Project {
  id: UUID;
  workspaceId: UUID;       // References Workspace.id
  name: string;            // 1-150 characters
  description: string;     // Can be empty string, Markdown supported
  prefix: string;          // 2-5 uppercase letters, used for task IDs (e.g., "PROJ")
  status: "active" | "paused" | "archived";
  defaultAssigneeId: UUID | null;  // Optional default assignee
  createdAt: ISODateTime;
  updatedAt: ISODateTime;
}

// --- Task ---

type TaskPriority = "urgent" | "high" | "medium" | "low" | "none";

type TaskStatus =
  | "backlog"
  | "todo"
  | "in_progress"
  | "in_review"
  | "done"
  | "cancelled";

interface Task {
  id: UUID;
  projectId: UUID;          // References Project.id
  sequenceNumber: number;   // Auto-incrementing within project
  displayId: string;        // Computed: `${project.prefix}-${sequenceNumber}`

  title: string;            // 1-500 characters
  description: string;      // Markdown, can be empty
  status: TaskStatus;
  priority: TaskPriority;

  creatorId: UUID;          // References User.id — who created this task
  assigneeId: UUID | null;  // References User.id — who is responsible

  labelIds: UUID[];         // References Label.id — many-to-many

  parentTaskId: UUID | null;  // For sub-tasks
  dueDate: string | null;    // ISO 8601 date (not datetime)

  estimatePoints: number | null;  // Story points, nullable

  commentCount: number;     // Denormalized for display
  attachmentCount: number;  // Denormalized for display

  createdAt: ISODateTime;
  updatedAt: ISODateTime;
  completedAt: ISODateTime | null;
}

// --- Comment ---

interface Comment {
  id: UUID;
  taskId: UUID;             // References Task.id
  authorId: UUID;           // References User.id
  content: string;          // Markdown, 1-10000 characters
  editedAt: ISODateTime | null;  // Null if never edited
  createdAt: ISODateTime;
}

// --- Label ---

interface Label {
  id: UUID;
  workspaceId: UUID;        // Labels are workspace-scoped
  name: string;             // 1-50 characters
  color: string;            // Hex color, e.g., "#FF5733"
  description: string;      // Can be empty
  createdAt: ISODateTime;
}

// --- User ---

interface User {
  id: UUID;
  email: string;
  displayName: string;      // 1-100 characters
  avatarUrl: string | null;
  status: "active" | "deactivated";
  createdAt: ISODateTime;
  lastActiveAt: ISODateTime;
}

// --- Workspace Membership ---

interface WorkspaceMember {
  workspaceId: UUID;
  userId: UUID;
  role: "owner" | "admin" | "member" | "guest";
  joinedAt: ISODateTime;
}
```

### Шаг 4: документировать решения

После написания схемы задокументируйте неочевидные решения. Это критично для ИИ-разработки — ИИ нужно знать не только **что** вы решили, но и **почему**:

```markdown
## Schema Decision Log

### Task.displayId
- Computed field: `${project.prefix}-${sequenceNumber}`
- Stored denormalized for query performance
- Example: "PROJ-142"
- Decision: Display IDs are human-friendly references, not database IDs

### Task.commentCount / Task.attachmentCount
- Denormalized counters stored on the task
- Updated via database triggers or application-level hooks
- Decision: Avoids COUNT queries on every task list render

### Task.dueDate vs Task.createdAt
- dueDate is a DATE (no time component) — "due on March 15th"
- createdAt is a DATETIME — precise moment of creation
- Decision: Due dates are human concepts (calendar days), not timestamps

### Label scope
- Labels are workspace-scoped, not project-scoped
- Decision: Allows consistent labeling across projects (e.g., "bug", "feature")
- Tradeoff: Larger label namespace, but more flexibility

### User.status
- "deactivated" not "deleted" — we never hard-delete users
- Decision: Preserves referential integrity for historical data
```

### Шаг 5: проверить эквивалентной JSON Schema

Для максимальной совместимости может понадобиться и версия JSON Schema. Вот сущность Task в виде JSON Schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://taskapp.example.com/schemas/task.json",
  "title": "Task",
  "type": "object",
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "projectId": { "type": "string", "format": "uuid" },
    "sequenceNumber": { "type": "integer", "minimum": 1 },
    "displayId": {
      "type": "string",
      "pattern": "^[A-Z]{2,5}-[0-9]+$"
    },
    "title": { "type": "string", "minLength": 1, "maxLength": 500 },
    "description": { "type": "string" },
    "status": {
      "type": "string",
      "enum": ["backlog", "todo", "in_progress", "in_review", "done", "cancelled"]
    },
    "priority": {
      "type": "string",
      "enum": ["urgent", "high", "medium", "low", "none"]
    },
    "creatorId": { "type": "string", "format": "uuid" },
    "assigneeId": { "type": ["string", "null"], "format": "uuid" },
    "labelIds": {
      "type": "array",
      "items": { "type": "string", "format": "uuid" },
      "uniqueItems": true
    },
    "parentTaskId": { "type": ["string", "null"], "format": "uuid" },
    "dueDate": { "type": ["string", "null"], "format": "date" },
    "estimatePoints": { "type": ["number", "null"], "minimum": 0 },
    "commentCount": { "type": "integer", "minimum": 0 },
    "attachmentCount": { "type": "integer", "minimum": 0 },
    "createdAt": { "type": "string", "format": "date-time" },
    "updatedAt": { "type": "string", "format": "date-time" },
    "completedAt": { "type": ["string", "null"], "format": "date-time" }
  },
  "required": [
    "id", "projectId", "sequenceNumber", "displayId",
    "title", "description", "status", "priority",
    "creatorId", "labelIds",
    "commentCount", "attachmentCount",
    "createdAt", "updatedAt"
  ],
  "additionalProperties": false
}
```

> **Заметка профессора:** Обратите внимание, что мы сначала написали интерфейсы TypeScript, а затем вывели JSON Schema. Работает любое направление. Важно, что у вас есть формальная машиночитаемая спецификация данных до написания бизнес-логики. На практике я рекомендую интерфейсы TypeScript для команд, работающих в основном на TypeScript, и JSON Schema для кросс-языковых команд или проектов, ориентированных на API.

---

## 1.6 Protocol Buffers и gRPC: философия схем Google

Google практикует проектирование от схем задолго до нынешней волны ИИ. Их система Protocol Buffers (protobuf), впервые разработанная внутри компании в 2001 году и открытая в 2008-м, — одно из самых чистых выражений мышления «от схемы» в отрасли.

### Что такое Protocol Buffers?

Protocol Buffers — независимый от языка и платформы механизм сериализации структурированных данных. Вы определяете формы данных в файлах `.proto`, затем используете компилятор `protoc` для генерации кода на целевом языке.

```protobuf
// task_service.proto
syntax = "proto3";

package taskapp.v1;

import "google/protobuf/timestamp.proto";

// The Task message defines the shape of a task entity.
message Task {
  string id = 1;
  string project_id = 2;
  int32 sequence_number = 3;
  string display_id = 4;

  string title = 5;
  string description = 6;

  TaskStatus status = 7;
  TaskPriority priority = 8;

  string creator_id = 9;
  optional string assignee_id = 10;

  repeated string label_ids = 11;
  optional string parent_task_id = 12;
  optional string due_date = 13;
  optional float estimate_points = 14;

  int32 comment_count = 15;
  int32 attachment_count = 16;

  google.protobuf.Timestamp created_at = 17;
  google.protobuf.Timestamp updated_at = 18;
  optional google.protobuf.Timestamp completed_at = 19;
}

enum TaskStatus {
  TASK_STATUS_UNSPECIFIED = 0;
  TASK_STATUS_BACKLOG = 1;
  TASK_STATUS_TODO = 2;
  TASK_STATUS_IN_PROGRESS = 3;
  TASK_STATUS_IN_REVIEW = 4;
  TASK_STATUS_DONE = 5;
  TASK_STATUS_CANCELLED = 6;
}

enum TaskPriority {
  TASK_PRIORITY_UNSPECIFIED = 0;
  TASK_PRIORITY_URGENT = 1;
  TASK_PRIORITY_HIGH = 2;
  TASK_PRIORITY_MEDIUM = 3;
  TASK_PRIORITY_LOW = 4;
  TASK_PRIORITY_NONE = 5;
}

// Service definition — the API contract
service TaskService {
  rpc CreateTask(CreateTaskRequest) returns (Task);
  rpc GetTask(GetTaskRequest) returns (Task);
  rpc ListTasks(ListTasksRequest) returns (ListTasksResponse);
  rpc UpdateTask(UpdateTaskRequest) returns (Task);
  rpc DeleteTask(DeleteTaskRequest) returns (DeleteTaskResponse);
}

message CreateTaskRequest {
  string project_id = 1;
  string title = 2;
  string description = 3;
  TaskPriority priority = 4;
  optional string assignee_id = 5;
  repeated string label_ids = 6;
  optional string parent_task_id = 7;
  optional string due_date = 8;
}

message GetTaskRequest {
  string id = 1;
}

message ListTasksRequest {
  string project_id = 1;
  optional TaskStatus status_filter = 2;
  optional string assignee_id_filter = 3;
  int32 page_size = 4;
  string page_token = 5;
}

message ListTasksResponse {
  repeated Task tasks = 1;
  string next_page_token = 2;
  int32 total_count = 3;
}

message UpdateTaskRequest {
  string id = 1;
  optional string title = 2;
  optional string description = 3;
  optional TaskStatus status = 4;
  optional TaskPriority priority = 5;
  optional string assignee_id = 6;
}

message DeleteTaskRequest {
  string id = 1;
}

message DeleteTaskResponse {
  bool success = 1;
}
```

Из этого единственного `.proto` файла инструментарий Google генерирует:

- **Структуры Go** с методами сериализации
- **Классы Java** с билдерами и парсерами
- **Классы Python** с аннотациями типов
- **Интерфейсы TypeScript** с кодированием/декодированием
- **Классы C++** с эффективной по памяти сериализацией
- **Клиентские библиотеки** для вызова сервиса
- **Серверные заглушки** для реализации сервиса

Схема — единственный источник истины. Всё остальное — производные.

### Почему это важно для SDD

Подход protobuf воплощает принцип, центральный для разработки через спецификации: **спецификация генерирует реализацию, а не наоборот.** В эпоху ИИ мы делаем то же самое — определяем схемы, которые модели ИИ используют для генерации правильных реализаций.

Внутренние сервисы Google (Gmail, Drive, Maps, YouTube) общаются через protobuf. Когда команда DeepMind строит ИИ-сервисы, она определяет protobuf-схемы входов и выходов. Вся поверхность API Google Cloud Platform определена сначала в protobuf, затем выставлена как REST, gRPC или GraphQL.

Это проектирование от схем в планетарном масштабе.

---

## 1.7 Экосистема валидаторов: Pydantic и Zod

Схемы полезны ровно настолько, насколько полезны инструменты, обеспечивающие их соблюдение. Две библиотеки стали золотым стандартом валидации схем во время выполнения в своих экосистемах.

### Pydantic (Python)

Pydantic — библиотека валидации данных для Python, использующая аннотации типов Python для определения схем. Она стала основой FastAPI, LangChain и большинства ИИ/ML-фреймворков на Python.

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID


class TaskStatus(str, Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class Task(BaseModel):
    """A task in the project management system."""

    id: UUID
    project_id: UUID
    sequence_number: int = Field(ge=1)
    display_id: str = Field(pattern=r"^[A-Z]{2,5}-[0-9]+$")

    title: str = Field(min_length=1, max_length=500)
    description: str = ""
    status: TaskStatus = TaskStatus.BACKLOG
    priority: TaskPriority = TaskPriority.NONE

    creator_id: UUID
    assignee_id: Optional[UUID] = None

    label_ids: list[UUID] = Field(default_factory=list)
    parent_task_id: Optional[UUID] = None
    due_date: Optional[str] = None  # ISO 8601 date
    estimate_points: Optional[float] = Field(default=None, ge=0)

    comment_count: int = Field(default=0, ge=0)
    attachment_count: int = Field(default=0, ge=0)

    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            # Ensure it is a valid date format (YYYY-MM-DD)
            from datetime import date
            try:
                date.fromisoformat(v)
            except ValueError:
                raise ValueError("due_date must be in YYYY-MM-DD format")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "project_id": "660e8400-e29b-41d4-a716-446655440001",
                "sequence_number": 42,
                "display_id": "PROJ-42",
                "title": "Implement user authentication",
                "description": "Add JWT-based auth with refresh tokens",
                "status": "todo",
                "priority": "high",
                "creator_id": "770e8400-e29b-41d4-a716-446655440002",
                "assignee_id": "880e8400-e29b-41d4-a716-446655440003",
                "label_ids": [],
                "comment_count": 0,
                "attachment_count": 0,
                "created_at": "2026-02-24T10:00:00Z",
                "updated_at": "2026-02-24T10:00:00Z",
            }
        }


# Usage: Pydantic validates at runtime
task_data = {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "project_id": "660e8400-e29b-41d4-a716-446655440001",
    "sequence_number": 42,
    "display_id": "PROJ-42",
    "title": "Implement user authentication",
    "status": "todo",
    "priority": "high",
    "creator_id": "770e8400-e29b-41d4-a716-446655440002",
    "created_at": "2026-02-24T10:00:00Z",
    "updated_at": "2026-02-24T10:00:00Z",
}

task = Task(**task_data)  # Validates and creates typed object
print(task.model_dump_json(indent=2))  # Serialize to JSON

# Generate JSON Schema from Pydantic model
print(Task.model_json_schema())
```

Убойная особенность Pydantic для SDD: **вы можете генерировать JSON Schema из моделей Pydantic**. То есть схема определяется один раз на Python и экспортируется в JSON Schema для фронтендов, генераторов документации или моделей ИИ.

### Zod (TypeScript)

Zod — эквивалент Pydantic для TypeScript. Он обеспечивает валидацию во время выполнения с полным выведением типов TypeScript.

```typescript
import { z } from "zod";

// Define the schema with Zod
const TaskStatusSchema = z.enum([
  "backlog",
  "todo",
  "in_progress",
  "in_review",
  "done",
  "cancelled",
]);

const TaskPrioritySchema = z.enum([
  "urgent",
  "high",
  "medium",
  "low",
  "none",
]);

const TaskSchema = z.object({
  id: z.string().uuid(),
  projectId: z.string().uuid(),
  sequenceNumber: z.number().int().min(1),
  displayId: z.string().regex(/^[A-Z]{2,5}-[0-9]+$/),

  title: z.string().min(1).max(500),
  description: z.string().default(""),
  status: TaskStatusSchema.default("backlog"),
  priority: TaskPrioritySchema.default("none"),

  creatorId: z.string().uuid(),
  assigneeId: z.string().uuid().nullable().default(null),

  labelIds: z.array(z.string().uuid()).default([]),
  parentTaskId: z.string().uuid().nullable().default(null),
  dueDate: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/)
    .nullable()
    .default(null),
  estimatePoints: z.number().min(0).nullable().default(null),

  commentCount: z.number().int().min(0).default(0),
  attachmentCount: z.number().int().min(0).default(0),

  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  completedAt: z.string().datetime().nullable().default(null),
});

// Infer the TypeScript type from the Zod schema
type Task = z.infer<typeof TaskSchema>;

// Usage: Zod validates at runtime AND provides compile-time types
const result = TaskSchema.safeParse(someApiResponse);

if (result.success) {
  const task: Task = result.data;
  // task is fully typed — TypeScript knows every field and its type
  console.log(task.title);
  console.log(task.status); // Autocomplete: "backlog" | "todo" | ...
} else {
  console.error("Validation failed:", result.error.issues);
  // result.error.issues is an array of specific validation errors:
  // [
  //   { code: "too_small", minimum: 1, path: ["title"], message: "..." },
  //   { code: "invalid_enum_value", path: ["status"], message: "..." }
  // ]
}
```

Убойная особенность Zod для SDD: **схема И ЕСТЬ тип**. Нет разрыва между валидацией времени выполнения и типами времени компиляции. Они выводятся из одного источника.

### Другие заметные валидаторы

Экосистема «от схемы» выходит за пределы Pydantic и Zod:

| Язык       | Библиотека       | Примечания                                 |
|------------|------------------|--------------------------------------------|
| Python     | Pydantic         | Де-факто стандарт, основа FastAPI          |
| Python     | attrs + cattrs   | Более лёгкая альтернатива                  |
| TypeScript | Zod              | Самый популярный, отличный DX              |
| TypeScript | Yup              | Старше, широко используется в React-формах |
| TypeScript | Valibot          | Новее, tree-shakeable альтернатива Zod     |
| TypeScript | ArkType          | Оптимизирован для производительности       |
| Go         | go-playground    | Валидация через теги структур              |
| Rust       | serde + validator | Derive-макросы для сериализации + валидации|
| Java       | Jakarta Bean Val | Корпоративный стандарт (бывший JSR 380)    |
| Kotlin     | kotlinx.serialization | Мультиплатформенная сериализация       |

> **Заметка профессора:** Студенты часто спрашивают, какой валидатор выбрать. Мой ответ прост: выбирайте тот, с которым лучше работает ваш ИИ-ассистент. На начало 2026 года Claude и GPT оба выдают превосходный код на Zod и Pydantic. Если вы используете ИИ-разработку (а вам следует), выбирайте инструмент, который ИИ знает лучше всего. Обычно это Zod для TypeScript и Pydantic для Python.

---

## 1.8 Проектирование от схем на практике: рабочий процесс

Проведу вас через реальный процесс разработки от схемы в контексте SDD.

### Фаза 1: определить сущности и связи

Начните с описания простым языком или диаграммы:

```
We are building a notification system.
- Users receive notifications.
- Notifications can be of different types: mention, assignment, comment, status_change.
- Notifications can be read or unread.
- Notifications can be grouped by conversation.
- Users can configure notification preferences per channel (email, push, in-app).
```

### Фаза 2: написать схему

Переведите описание в формальные схемы:

```typescript
// notification-schemas.ts

interface Notification {
  id: string;                // UUID
  recipientId: string;       // UUID — who receives this notification
  type: NotificationType;
  title: string;             // Short display title
  body: string;              // Longer description, may contain Markdown
  isRead: boolean;
  readAt: string | null;     // ISO 8601, null if unread

  // Context: what triggered this notification
  sourceEntityType: "task" | "comment" | "project";
  sourceEntityId: string;    // UUID of the triggering entity
  actorId: string;           // UUID of the user who caused it

  // Grouping
  conversationId: string;    // Group related notifications together

  createdAt: string;         // ISO 8601
}

type NotificationType = "mention" | "assignment" | "comment" | "status_change";

interface NotificationPreferences {
  userId: string;            // UUID
  channels: {
    email: ChannelPreference;
    push: ChannelPreference;
    inApp: ChannelPreference;
  };
}

interface ChannelPreference {
  enabled: boolean;
  types: NotificationType[];  // Which notification types to receive on this channel
  quietHours: {
    enabled: boolean;
    startTime: string;        // HH:mm format, 24-hour
    endTime: string;          // HH:mm format, 24-hour
    timezone: string;         // IANA timezone, e.g., "America/New_York"
  };
}

// API Request/Response shapes
interface ListNotificationsRequest {
  recipientId: string;
  filter?: {
    isRead?: boolean;
    types?: NotificationType[];
    since?: string;           // ISO 8601
  };
  pagination: {
    cursor?: string;
    limit: number;            // 1-100, default 20
  };
}

interface ListNotificationsResponse {
  notifications: Notification[];
  nextCursor: string | null;
  unreadCount: number;
}

interface MarkNotificationsReadRequest {
  notificationIds: string[];  // 1-100 IDs
}

interface MarkNotificationsReadResponse {
  updatedCount: number;
}
```

### Фаза 3: ревью и уточнение

Прежде чем писать реализацию, проверьте схему:

- Все ли поля учтены?
- Явно ли помечены nullable-поля?
- Нет ли пропущенных ограничений (min/max, шаблоны)?
- Имеют ли смысл формы запросов/ответов API?
- Обработаны ли крайние случаи (пустые массивы, null-значения)?

### Фаза 4: передать ИИ для реализации

Теперь передайте схему модели ИИ вместе с инструкциями по реализации:

```
Using the following schemas, implement:

1. A Prisma database schema that stores these entities
2. A Next.js API route for listing notifications (GET /api/notifications)
3. A React hook `useNotifications` that fetches and caches notifications
4. Zod validation schemas that match these TypeScript interfaces

[paste schemas here]

Requirements:
- All data flowing through the system must conform to these schemas
- Use Zod for runtime validation on both server and client
- Use React Query for server state management
- Handle all error cases explicitly
```

Теперь у ИИ однозначные инструкции. Схемы убирают необходимость изобретать формы данных, угадывать имена полей или предполагать типы.

### Фаза 5: проверить вывод

После генерации кода проверьте, что он соответствует схемам. Это можно автоматизировать:

```typescript
// schema-conformance.test.ts
import { describe, it, expect } from "vitest";
import { NotificationSchema, ListNotificationsResponseSchema } from "./schemas";

describe("API Schema Conformance", () => {
  it("GET /api/notifications returns conformant response", async () => {
    const response = await fetch("/api/notifications?limit=5");
    const data = await response.json();

    const result = ListNotificationsResponseSchema.safeParse(data);

    if (!result.success) {
      console.error("Schema violations:", result.error.issues);
    }

    expect(result.success).toBe(true);
  });

  it("Each notification conforms to Notification schema", async () => {
    const response = await fetch("/api/notifications?limit=5");
    const data = await response.json();

    for (const notification of data.notifications) {
      const result = NotificationSchema.safeParse(notification);
      expect(result.success).toBe(true);
    }
  });
});
```

---

## 1.9 Распространённые шаблоны «от схемы»

Поделюсь несколькими шаблонами, которые я постоянно вижу в хорошо спроектированных системах «от схемы».

### Шаблон 1: конверт

Оборачивайте все ответы API в согласованный конверт:

```typescript
interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error: ApiError | null;
  metadata: {
    requestId: string;
    timestamp: string;     // ISO 8601
    processingTimeMs: number;
  };
}

interface ApiError {
  code: string;            // Machine-readable: "VALIDATION_ERROR"
  message: string;         // Human-readable: "Title is required"
  details: Record<string, unknown> | null;
}

// Usage:
type GetTaskResponse = ApiResponse<Task>;
type ListTasksResponse = ApiResponse<{
  items: Task[];
  pagination: PaginationInfo;
}>;
```

Этот шаблон означает, что каждый потребитель API точно знает, какую форму ожидать, каждый раз. Обработка ошибок становится стандартизованной.

### Шаблон 2: разделение Create/Update

Определяйте отдельные схемы для создания и обновления, поскольку у них часто разные обязательные поля:

```typescript
// Full entity (what you read)
interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  createdAt: string;
  updatedAt: string;
}

// Creation input (what you send to create)
interface CreateTaskInput {
  title: string;          // Required
  description?: string;   // Optional, defaults to ""
  status?: TaskStatus;    // Optional, defaults to "backlog"
}

// Update input (what you send to update — all fields optional)
interface UpdateTaskInput {
  title?: string;
  description?: string;
  status?: TaskStatus;
}
```

### Шаблон 3: дискриминированное объединение

Используйте поле `type`, чтобы создать схемы, представляющие несколько возможных форм:

```typescript
type NotificationPayload =
  | {
      type: "mention";
      mentionedIn: "comment" | "description";
      taskId: string;
      excerpt: string;     // The text around the mention
    }
  | {
      type: "assignment";
      taskId: string;
      assignedBy: string;  // User ID
      previousAssigneeId: string | null;
    }
  | {
      type: "comment";
      taskId: string;
      commentId: string;
      commentExcerpt: string;
    }
  | {
      type: "status_change";
      taskId: string;
      previousStatus: TaskStatus;
      newStatus: TaskStatus;
      changedBy: string;   // User ID
    };
```

Этот шаблон чрезвычайно мощный для ИИ-разработки. Поле `type` точно говорит ИИ, с каким вариантом он имеет дело, позволяя исчерпывающее сопоставление:

```typescript
function renderNotification(payload: NotificationPayload): string {
  switch (payload.type) {
    case "mention":
      return `You were mentioned in a ${payload.mentionedIn}`;
    case "assignment":
      return `You were assigned a task`;
    case "comment":
      return `New comment: "${payload.commentExcerpt}"`;
    case "status_change":
      return `Status changed from ${payload.previousStatus} to ${payload.newStatus}`;
  }
}
```

### Шаблон 4: версионированная схема

Для систем, эволюционирующих со временем, версионируйте схемы:

```typescript
// v1 — original
interface TaskV1 {
  schemaVersion: 1;
  id: string;
  title: string;
  assignee: string;  // Just a name string in v1
}

// v2 — assignee became an object
interface TaskV2 {
  schemaVersion: 2;
  id: string;
  title: string;
  assignee: {
    id: string;
    name: string;
    email: string;
  } | null;
}

type Task = TaskV1 | TaskV2;

function migrateTask(task: Task): TaskV2 {
  if (task.schemaVersion === 2) return task;
  return {
    schemaVersion: 2,
    id: task.id,
    title: task.title,
    assignee: task.assignee
      ? { id: "migrated", name: task.assignee, email: "" }
      : null,
  };
}
```

---

## 1.10 Антишаблоны проектирования от схем

Не всё, что выглядит как проектирование от схем, является хорошим проектированием от схем. Вот частые ошибки.

### Антишаблон 1: божественная схема

```typescript
// BAD: One massive interface that tries to represent everything
interface Item {
  id: string;
  type: "product" | "service" | "subscription" | "addon";
  name: string;
  price: number;
  // Only for products:
  weight?: number;
  dimensions?: { width: number; height: number; depth: number };
  // Only for subscriptions:
  billingCycle?: "monthly" | "yearly";
  trialDays?: number;
  // Only for services:
  durationMinutes?: number;
  requiresBooking?: boolean;
  // ... 50 more optional fields
}
```

**Исправление:** используйте дискриминированные объединения для разделения ответственностей.

### Антишаблон 2: схема из одних строк

```typescript
// BAD: Everything is a string
interface Task {
  id: string;
  priority: string;    // Should be an enum
  dueDate: string;     // What format? ISO? US? European?
  tags: string;        // Is this comma-separated? JSON? What?
  metadata: string;    // Serialized JSON in a string field
}
```

**Исправление:** используйте конкретные типы, перечисления и правильные вложенные объекты.

### Антишаблон 3: недостаточно ограниченная схема

```typescript
// BAD: No constraints at all
interface User {
  id: string;           // How long? What format?
  email: string;        // Any string is valid?
  age: number;          // Can it be negative? 10,000?
  bio: string;          // Can it be 10 million characters?
}
```

**Исправление:** добавьте значимые ограничения:

```typescript
interface User {
  id: string;           // UUID v4
  email: string;        // Must match email format
  age: number;          // 13-150 (legal + reasonable)
  bio: string;          // 0-2000 characters
}
```

### Антишаблон 4: схема как запоздалая мысль

Это самый опасный антишаблон: сначала написать код, затем «задокументировать» схему из кода. Это переворачивает весь смысл. Схема должна управлять кодом, а не описывать его постфактум.

> **Заметка профессора:** Однажды я консультировал стартап, в котором ИИ сгенерировал весь бэкенд. Когда я попросил показать спецификацию модели данных, мне ответили: «О, ИИ просто сам разобрался». Результат? Пять разных представлений «пользователя» по кодовой базе, два разных формата дат и поле `isActive`, которое местами было булевым, а местами строкой «true»/«false». Четырнадцать часов отладки можно было предотвратить тридцатью минутами написания схемы.

---

## 1.11 Упражнения

### Упражнение 1: схема аутентификации пользователей

Напишите полные интерфейсы TypeScript (или JSON Schema, или модели Pydantic) для системы аутентификации пользователей. Схема должна покрывать:

1. **Запрос регистрации** — какие данные предоставляет новый пользователь?
2. **Запрос входа** — email + пароль
3. **Ответ входа** — что возвращает сервер при успешном входе?
4. **Токен аутентификации** — что хранится в payload JWT?
5. **Запрос сброса пароля** — как пользователь запрашивает сброс?
6. **Подтверждение сброса пароля** — как пользователь завершает сброс?
7. **Сессия** — как выглядит сессия в вашей БД?
8. **Ответы с ошибками** — определите конкретные коды ошибок для сбоев аутентификации

Требования:
- Пароли от 8 до 128 символов
- Email должен валидироваться
- У токенов должны быть сроки истечения
- Определите и access-, и refresh-токены
- Обработайте случай «аккаунт заблокирован после слишком многих неудач»

### Упражнение 2: схема корзины интернет-магазина

Спроектируйте полную модель данных системы корзины:

1. **Product** — товар каталога
2. **CartItem** — товар в корзине конкретного пользователя (с количеством, опциями)
3. **Cart** — полная корзина с товарами, итогами, применёнными скидками
4. **Discount/Coupon** — как представлены скидки?
5. **Операции корзины** — определите запрос/ответ для:
   - Добавления товара в корзину
   - Обновления количества
   - Удаления товара
   - Применения кода купона
   - Получения сводки корзины

Требования:
- У товаров могут быть варианты (размер, цвет)
- Цены должны поддерживать несколько валют
- Корзина должна отслеживать, есть ли товары в наличии
- Купоны могут быть процентными или фиксированными
- Обработайте крайний случай: цена товара изменилась с момента добавления в корзину

### Упражнение 3: схема блог-системы

Спроектируйте систему управления контентом блога:

1. **Post** — сам пост блога
2. **Author** — человек, написавший его
3. **Category** — иерархические категории (у категории может быть родитель)
4. **Tag** — плоские теги (многие-ко-многим с постами)
5. **Comment** — комментарии к постам (с поддержкой вложенных/ветвящихся комментариев)
6. **Media** — изображения и файлы, прикреплённые к постам
7. **Конечные точки API** — определите формы запросов/ответов для:
   - Списка постов (с фильтрацией по категории, тегу, автору, статусу)
   - Получения одного поста (со связанными данными)
   - Создания/обновления поста (как черновик, затем публикация)
   - Публикации комментария (со статусом модерации)

Требования:
- У постов есть процесс публикации: draft -> review -> published -> archived
- Комментарии могут быть вложены до 3 уровней
- Категории иерархичны (например, «Tech > Programming > Python»)
- SEO-метаданные должны быть частью схемы поста
- Поддержка отложенной публикации (публикация в будущую дату/время)

> **Заметка профессора:** Для каждого упражнения я хочу, чтобы вы написали ТОЛЬКО схему — без реализации. Затем передайте схему ИИ и попросите реализовать систему. Сравните результат с тем, что получили бы, дав ИИ только прозаическое описание. Разница убедит вас, что проектирование от схемы стоит предварительных вложений.

---

## 1.12 Ключевые выводы

1. **Проектирование от схем** означает определение форм данных до написания логики. Это основа надёжной ИИ-разработки.

2. **JSON Schema** — универсальный язык спецификации формы данных. Его используют OpenAI, Anthropic, Google и остальная отрасль.

3. **ИИ-компании обеспечивают мышление «от схемы»** на уровне API: Structured Outputs OpenAI, схемы tool_use Anthropic и вызов функций Gemini от Google — все требуют определений JSON Schema.

4. **Protocol Buffers Google** — золотой стандарт проектирования от схем в масштабе, доказывающий, что шаблон работает для крупнейших систем на Земле.

5. **Pydantic (Python) и Zod (TypeScript)** — библиотеки валидации во время выполнения, соединяющие определения схем с работающим кодом.

6. **Рабочий процесс разработки**: определить сущности, написать схемы, проверить, передать ИИ, проверить соответствие.

7. **Распространённые шаблоны** включают конверт, разделение create/update, дискриминированные объединения и версионированные схемы.

8. **Антишаблоны, которых избегать**: божественные схемы, поля из одних строк, недостаточно ограниченные схемы и схема как запоздалая мысль.

---

## Взгляд вперёд

В следующей главе мы возьмём мышление «от схемы» и применим его к UI-компонентам. Вы узнаете, как писать **контракты компонентов** — спецификации, определяющие, что делает компонент (его пропсы, состояние и побочные эффекты), не описывая, как он выглядит. Здесь проектирование от схем встречается с фронтенд-архитектурой, и здесь ИИ-разработка UI действительно раскрывается.

---

*Конец главы 1 — Проектирование от схем*

---

[← Оглавление курса](../INDEX.ru.md) · [← Глава 4: Практика — от вайба к спецификации](../MODULE_01/CHAPTER_04.ru.md) · [Глава 2: Контракт компонента →](CHAPTER_02.ru.md)
