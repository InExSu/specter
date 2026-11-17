# Глава 2: Документация как код

## МОДУЛЬ 05 — Сопровождение и масштабирование (продвинутый уровень)

> [Оглавление курса](../INDEX.ru.md) · [Модуль 05](../INDEX.ru.md#модуль-05--сопровождение-и-масштабирование)

---

### Вступление к лекции

> *Позвольте рассказать историю, которую пережил каждый из вас. Вы выходите на новый проект. Кто-то отправляет вас в вики с документацией. Вы открываете. Последняя правка — девять месяцев назад. Перечисленные эндпоинты API не совпадают с реальным API. На схеме архитектуры — микросервис, выведенный из эксплуатации в январе. Гайд «С чего начать» ссылается на CLI-инструмент, который давно заменили другим. Вы закрываете вики и идёте читать код.*

> *Это универсальная проблема документации: она всегда устарела. Причина проста — документация и код — разные артефакты, поддерживаемые разными процессами. Когда код меняется, кто-то должен вспомнить обновить документацию. И никто не вспоминает. Никто и никогда.*

> *А что если бы документация и спецификация были одним и тем же? Что если обновление спецификации автоматически обновляет документацию? Что если документация вообще не могла бы разойтись с реализацией, потому что генерируется из того же источника истины, из которого генерируется реализация?*

> *Именно это мы построим сегодня. Не документацию, которая описывает код, а документацию, которая И ЕСТЬ код. Документацию, которая генерируется, валидируется и разворачивается с той же строгостью, что и продакшн-ПО. Это «документация как код», и это одна из самых преображающих идей в инструментарии SDD.*

---

## 2.1 Принцип DRY в применении к документации

Вы знаете принцип DRY — Don't Repeat Yourself, «не повторяйся». Каждый фрагмент знания должен иметь единственное авторитетное представление в системе. К коду мы применяем этот принцип религиозно: выносим общую логику в функции, создаём абстракции, устраняем дублирование. Но когда доходит до документации, мы нарушаем DRY постоянно.

Возьмём типичный проект. Одна и та же информация об эндпоинте API живёт в:

1. Определении интерфейса TypeScript
2. Спецификации OpenAPI/Swagger
3. Реализации обработчика маршрута
4. Юнит-тестах
5. Интеграционных тестах
6. Сайт документации API
7. Внутренней вики
8. Гайде для новичков
9. Документации клиентского SDK
10. Changelog

Десять мест, где записана одна и та же истина. Когда эндпоинт меняется, сколько из этих десяти обновляется? По моему опыту — одно: реализация. Может, два, если повезёт и разработчик обновит ещё и тесты. Остальные восемь становятся ложью.

### Решение SDD: спецификации И ЕСТЬ документация

В процессе разработки через спецификации спецификация — единственный источник истины. Всё остальное — реализация, тесты И документация — производится из спецификации.

```
                    ┌─────────────┐
                    │    SPEC     │ ← Single Source of Truth
                    │  (source)   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │   CODE   │ │  TESTS   │ │   DOCS   │
        │(derived) │ │(derived) │ │(derived) │
        └──────────┘ └──────────┘ └──────────┘
```

Когда спецификация меняется, все три производных артефакта перегенерируются. Документация не может устареть, потому что её не поддерживают отдельно — её производят из той же спецификации, из которой производят код.

```typescript
// The spec IS the documentation. Look at this interface:

/**
 * @title User Management API
 * @version 2.0.0
 * @description Manages user accounts, authentication, and profiles.
 *
 * @baseUrl https://api.example.com/v2
 * @auth Bearer token required for all endpoints except POST /users
 */

/**
 * Creates a new user account.
 *
 * @endpoint POST /users
 * @tag Users
 * @tag Onboarding
 * @since 2.0.0
 *
 * @param {CreateUserDTO} body - The user data
 * @returns {UserResponseDTO} 201 - The created user
 * @throws {ValidationError} 400 - Invalid input data
 * @throws {ConflictError} 409 - Email already registered
 *
 * @example
 * // Request
 * POST /users
 * Content-Type: application/json
 * {
 *   "email": "ada@example.com",
 *   "name": "Ada Lovelace",
 *   "password": "securePassword123!"
 * }
 *
 * // Response (201 Created)
 * {
 *   "id": "usr_abc123",
 *   "email": "ada@example.com",
 *   "name": "Ada Lovelace",
 *   "createdAt": "2026-02-24T10:30:00Z"
 * }
 *
 * @rateLimit 10 requests per minute per IP
 * @sideEffects Sends welcome email via email service
 */
interface CreateUser {
  body: CreateUserDTO;
  response: UserResponseDTO;
  errors: ValidationError | ConflictError;
}
```

Этот интерфейс одновременно:
- **спецификация**, которая говорит ИИ, что реализовывать
- **определение типа**, которое проверяет компилятор
- **документация API**, из которой можно собрать сайт
- **контракт тестов**, задающий, что валидировать
- **чертёж клиентского SDK**, определяющий сигнатуры методов

Один источник. Пять применений. Ноль дублирования.

---

## 2.2 Как спецификации устраняют проблему «документация всегда устарела»

Документация устаревает потому, что живёт в отдельном от кода цикле поддержки. Обновление документации — ручной процесс «потом как-нибудь», без механизма принуждения. Сравним традиционный процесс с процессом SDD:

### Традиционный процесс

```
1. Developer receives feature request
2. Developer writes code
3. Developer writes tests (sometimes)
4. Developer submits PR
5. PR is reviewed and merged
6. Developer remembers they should update docs (rare)
7. Developer opens wiki, makes edits (rarer)
8. Edits are reviewed and published (rarest)

Result: Docs are 3 steps removed from the code change,
with no enforcement at any step.
```

### Процесс SDD

```
1. Developer receives feature request
2. Developer updates the SPEC
3. Code is regenerated/updated from spec
4. Tests are regenerated/updated from spec
5. Docs are regenerated/updated from spec
6. CI validates that code, tests, AND docs are in sync with spec
7. PR includes spec change, code change, test change, AND doc change
8. Review covers all four together

Result: Docs are updated in the same commit as the code,
enforced by CI, reviewed in the same PR.
```

### Слой принуждения в CI

Вот как построить механизм принуждения:

```yaml
# .github/workflows/doc-sync.yml
name: Documentation Sync Check

on:
  pull_request:
    branches: [main]

jobs:
  check-doc-sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: npm ci

      - name: Generate docs from specs
        run: npm run generate:docs

      - name: Check for uncommitted doc changes
        run: |
          # If generating docs from specs produces changes,
          # it means the PR has spec changes without doc updates
          if [ -n "$(git status --porcelain docs/)" ]; then
            echo "ERROR: Documentation is out of sync with specs."
            echo "The following doc files need to be regenerated:"
            git status --porcelain docs/
            echo ""
            echo "Run 'npm run generate:docs' and commit the changes."
            exit 1
          fi

      - name: Validate generated docs
        run: |
          # Check that all links are valid
          npm run docs:validate-links
          # Check that all code examples compile
          npm run docs:validate-examples
          # Check that all API examples match spec types
          npm run docs:validate-contracts
```

> **Заметка профессора:** Эта проверка в CI — ключ, на котором держится вся система. Она не опциональна. Без принуждения разработчики неизбежно забудут перегенерировать документацию, и вы вернётесь к той же проблеме. Проверка в CI делает физически невозможным слияние PR с изменениями спецификации без соответствующих правок документации. Именно в этом разница между политикой и процессом.

---

## 2.3 Инструменты

Обзор инструментов, которые делают «документацию как код» практичной в 2026 году.

### 2.3.1 TypeDoc — документация API на TypeScript

TypeDoc генерирует документацию из исходников TypeScript и комментариев JSDoc. В процессе SDD ваши интерфейсы-спецификации и есть источник для TypeDoc.

```typescript
// src/specs/user.spec.ts
// This file IS your spec AND your doc source

/**
 * Represents a user in the system.
 *
 * Users are created through the registration flow and can
 * have one of several roles that determine their permissions.
 *
 * @category Domain Models
 * @see {@link UserService} for operations on users
 * @see {@link AuthService} for authentication
 *
 * @example
 * ```typescript
 * const user: User = {
 *   id: 'usr_abc123',
 *   email: 'ada@example.com',
 *   name: 'Ada Lovelace',
 *   role: UserRole.ADMIN,
 *   createdAt: new Date('2026-02-24'),
 *   updatedAt: new Date('2026-02-24'),
 * };
 * ```
 */
export interface User {
  /** Unique identifier. Format: usr_{alphanumeric} */
  id: string;

  /** User's email address. Must be unique across all users. */
  email: string;

  /** User's display name. 1-100 characters. */
  name: string;

  /** User's role. Determines permissions. */
  role: UserRole;

  /** When the user account was created. ISO 8601. */
  createdAt: Date;

  /** When the user account was last modified. ISO 8601. */
  updatedAt: Date;
}

/**
 * Available user roles.
 *
 * Roles are hierarchical: ADMIN > MANAGER > USER > VIEWER
 *
 * @category Domain Models
 */
export enum UserRole {
  /** Full system access. Can manage all users and settings. */
  ADMIN = 'admin',

  /** Can manage team members and their resources. */
  MANAGER = 'manager',

  /** Standard user. Can manage their own resources. */
  USER = 'user',

  /** Read-only access. Cannot create or modify resources. */
  VIEWER = 'viewer',
}
```

```json
// typedoc.json — Configuration for doc generation
{
  "entryPoints": ["src/specs/**/*.spec.ts"],
  "out": "docs/api-reference",
  "theme": "default",
  "includeVersion": true,
  "categorizeByGroup": true,
  "categoryOrder": [
    "Domain Models",
    "API Endpoints",
    "Services",
    "Utilities"
  ],
  "plugin": [
    "typedoc-plugin-markdown",
    "typedoc-plugin-mermaid"
  ],
  "excludePrivate": true,
  "excludeInternal": true
}
```

### 2.3.2 Swagger/OpenAPI — документация API

Спецификация OpenAPI — отраслевой стандарт описания REST API. В SDD спецификации API могут порождать и реализацию, и документ OpenAPI.

```yaml
# Generated from specs — not written by hand
# openapi.generated.yaml

openapi: 3.1.0
info:
  title: E-Commerce API
  version: 2.0.0
  description: |
    The E-Commerce API provides access to products, users, and orders.
    This documentation is auto-generated from the API specification files
    and is guaranteed to match the current implementation.

    **Last generated:** 2026-02-24T10:30:00Z
    **Spec hash:** a3f7b2c (for cache-busting)

servers:
  - url: https://api.example.com/v2
    description: Production
  - url: https://staging-api.example.com/v2
    description: Staging

paths:
  /products:
    get:
      operationId: listProducts
      summary: List products with pagination and filtering
      tags:
        - Products
      parameters:
        - name: page
          in: query
          required: true
          schema:
            type: integer
            minimum: 1
          description: Page number (1-indexed)
        - name: limit
          in: query
          required: true
          schema:
            type: integer
            minimum: 1
            maximum: 100
          description: Number of items per page
        - name: category
          in: query
          required: false
          schema:
            $ref: '#/components/schemas/ProductCategory'
          description: Filter by product category
      responses:
        '200':
          description: Paginated list of products
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedProductResponse'
              example:
                data:
                  - id: "prod_abc123"
                    name: "Mechanical Keyboard"
                    price: 149.99
                    category: "electronics"
                pagination:
                  page: 1
                  limit: 20
                  total: 156
                  totalPages: 8
        '400':
          $ref: '#/components/responses/ValidationError'
        '401':
          $ref: '#/components/responses/UnauthorizedError'
```

### 2.3.3 Storybook — документация компонентов

Для фронтенд-компонентов Storybook генерирует интерактивную документацию из контрактов компонентов. В SDD спецификации компонентов задают и контракт реализации, и истории Storybook.

```typescript
// src/specs/components/Button.spec.ts
// This spec drives both implementation AND documentation

/**
 * @component Button
 * @category UI Components
 * @figma https://figma.com/file/abc123/design-system
 *
 * @description
 * Primary interactive element for user actions.
 * Supports multiple variants, sizes, and states.
 */
export interface ButtonSpec {
  props: {
    /** The button's visual variant */
    variant: 'primary' | 'secondary' | 'danger' | 'ghost';

    /** Size of the button */
    size: 'sm' | 'md' | 'lg';

    /** Button label text */
    label: string;

    /** Whether the button is disabled */
    disabled?: boolean;

    /** Whether to show a loading spinner */
    loading?: boolean;

    /** Click handler */
    onClick: () => void;

    /** Optional icon to show before the label */
    icon?: React.ReactNode;
  };

  /** Accessibility requirements */
  a11y: {
    role: 'button';
    ariaLabel: string;
    ariaDisabled: boolean;
    focusable: boolean;
    keyboardActivation: 'Enter' | 'Space';
  };

  /** Visual states */
  states: {
    default: { cursor: 'pointer' };
    hover: { opacity: 0.9 };
    active: { transform: 'scale(0.98)' };
    disabled: { cursor: 'not-allowed'; opacity: 0.5 };
    loading: { cursor: 'wait' };
    focused: { outline: '2px solid blue' };
  };
}
```

```typescript
// Generated Storybook stories from the spec
// src/stories/Button.stories.ts (auto-generated)

import type { Meta, StoryObj } from '@storybook/react';
import { Button } from '../components/Button';

// Auto-generated from ButtonSpec
const meta: Meta<typeof Button> = {
  title: 'UI Components/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'danger', 'ghost'],
      description: "The button's visual variant",
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'Size of the button',
    },
    label: {
      control: 'text',
      description: 'Button label text',
    },
    disabled: {
      control: 'boolean',
      description: 'Whether the button is disabled',
    },
    loading: {
      control: 'boolean',
      description: 'Whether to show a loading spinner',
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

// Auto-generated stories for each variant
export const Primary: Story = {
  args: { variant: 'primary', size: 'md', label: 'Click Me' },
};

export const Secondary: Story = {
  args: { variant: 'secondary', size: 'md', label: 'Click Me' },
};

export const Danger: Story = {
  args: { variant: 'danger', size: 'md', label: 'Delete' },
};

export const Ghost: Story = {
  args: { variant: 'ghost', size: 'md', label: 'Cancel' },
};

// Auto-generated stories for each state
export const Disabled: Story = {
  args: { variant: 'primary', size: 'md', label: 'Disabled', disabled: true },
};

export const Loading: Story = {
  args: { variant: 'primary', size: 'md', label: 'Loading', loading: true },
};

// Auto-generated stories for each size
export const Small: Story = {
  args: { variant: 'primary', size: 'sm', label: 'Small' },
};

export const Large: Story = {
  args: { variant: 'primary', size: 'lg', label: 'Large' },
};
```

### 2.3.4 Docusaurus — полноценные сайты документации

Docusaurus — открытый фреймворк документации от Meta. Он превращает Markdown- (и MDX-) файлы в аккуратные сайты документации. В процессе SDD Docusaurus потребляет Markdown, сгенерированный из ваших спецификаций.

```javascript
// docusaurus.config.js
/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'E-Commerce API Documentation',
  tagline: 'Auto-generated from specifications',
  url: 'https://docs.example.com',
  baseUrl: '/',

  // Custom plugin to regenerate docs from specs before build
  plugins: [
    [
      './plugins/spec-to-docs',
      {
        specsDir: 'src/specs',
        outputDir: 'docs/api',
        templateDir: 'doc-templates',
      },
    ],
  ],

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.auto-generated.js',
          editUrl: 'https://github.com/org/repo/edit/main/specs/',
          // Note: edit URL points to SPECS, not docs
          // because specs are the source of truth
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
        },
      },
    ],
  ],
};

module.exports = config;
```

---

## 2.4 Генерация документации API из спецификаций OpenAPI

Построим полный конвейер, который берёт спецификацию на TypeScript и выдаёт готовый сайт документации API.

### Шаг 1: определить спецификацию

```typescript
// src/specs/api/products.spec.ts

import { z } from 'zod';

/**
 * @api Product Endpoints
 * @baseUrl /api/v2/products
 * @auth Bearer token required
 */

// --- Request/Response Schemas (using Zod for runtime validation) ---

export const ProductCategorySchema = z.enum([
  'electronics',
  'clothing',
  'home',
  'sports',
  'books',
]);

export const CreateProductSchema = z.object({
  name: z.string().min(1).max(200).describe('Product name'),
  price: z.number().positive().describe('Price in USD'),
  category: ProductCategorySchema.describe('Product category'),
  description: z.string().max(5000).optional().describe('Product description'),
  images: z.array(z.string().url()).max(10).describe('Product image URLs'),
  tags: z.array(z.string()).max(20).optional().describe('Searchable tags'),
});

export const ProductResponseSchema = z.object({
  id: z.string().describe('Unique product identifier (prod_*)'),
  name: z.string().describe('Product name'),
  price: z.number().describe('Price in USD'),
  category: ProductCategorySchema.describe('Product category'),
  description: z.string().nullable().describe('Product description'),
  images: z.array(z.string()).describe('Product image URLs'),
  tags: z.array(z.string()).describe('Searchable tags'),
  createdAt: z.string().datetime().describe('ISO 8601 creation timestamp'),
  updatedAt: z.string().datetime().describe('ISO 8601 last update timestamp'),
});

export const PaginatedProductsSchema = z.object({
  data: z.array(ProductResponseSchema),
  pagination: z.object({
    page: z.number().int().positive(),
    limit: z.number().int().positive(),
    total: z.number().int().nonnegative(),
    totalPages: z.number().int().nonnegative(),
  }),
});

// --- Type Exports (derived from schemas) ---

export type ProductCategory = z.infer<typeof ProductCategorySchema>;
export type CreateProduct = z.infer<typeof CreateProductSchema>;
export type ProductResponse = z.infer<typeof ProductResponseSchema>;
export type PaginatedProducts = z.infer<typeof PaginatedProductsSchema>;
```

### Шаг 2: сгенерировать OpenAPI из схем Zod

```typescript
// scripts/generate-openapi.ts

import { z } from 'zod';
import { zodToJsonSchema } from 'zod-to-json-schema';
import {
  CreateProductSchema,
  ProductResponseSchema,
  PaginatedProductsSchema,
  ProductCategorySchema,
} from '../src/specs/api/products.spec';
import * as fs from 'fs';
import * as yaml from 'yaml';

interface OpenAPISpec {
  openapi: string;
  info: { title: string; version: string; description: string };
  paths: Record<string, unknown>;
  components: { schemas: Record<string, unknown> };
}

function generateOpenAPI(): OpenAPISpec {
  const spec: OpenAPISpec = {
    openapi: '3.1.0',
    info: {
      title: 'E-Commerce API',
      version: '2.0.0',
      description: 'Auto-generated from TypeScript specifications.',
    },
    paths: {
      '/api/v2/products': {
        get: {
          operationId: 'listProducts',
          summary: 'List products with pagination',
          tags: ['Products'],
          parameters: [
            {
              name: 'page',
              in: 'query',
              required: true,
              schema: { type: 'integer', minimum: 1 },
            },
            {
              name: 'limit',
              in: 'query',
              required: true,
              schema: { type: 'integer', minimum: 1, maximum: 100 },
            },
            {
              name: 'category',
              in: 'query',
              required: false,
              schema: zodToJsonSchema(ProductCategorySchema),
            },
          ],
          responses: {
            '200': {
              description: 'Paginated product list',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/PaginatedProducts' },
                },
              },
            },
          },
        },
        post: {
          operationId: 'createProduct',
          summary: 'Create a new product',
          tags: ['Products'],
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/CreateProduct' },
              },
            },
          },
          responses: {
            '201': {
              description: 'Product created successfully',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/ProductResponse' },
                },
              },
            },
          },
        },
      },
    },
    components: {
      schemas: {
        CreateProduct: zodToJsonSchema(CreateProductSchema),
        ProductResponse: zodToJsonSchema(ProductResponseSchema),
        PaginatedProducts: zodToJsonSchema(PaginatedProductsSchema),
      },
    },
  };

  return spec;
}

// Generate and write the OpenAPI spec
const openApiSpec = generateOpenAPI();
fs.writeFileSync(
  'docs/openapi.yaml',
  yaml.stringify(openApiSpec, { indent: 2 })
);
console.log('OpenAPI spec generated at docs/openapi.yaml');
```

### Шаг 3: сгенерировать читаемую документацию из OpenAPI

```typescript
// scripts/generate-markdown-docs.ts

import * as fs from 'fs';
import * as yaml from 'yaml';
import * as path from 'path';

interface Parameter {
  name: string;
  in: string;
  required: boolean;
  schema: Record<string, unknown>;
  description?: string;
}

interface PathOperation {
  operationId: string;
  summary: string;
  tags: string[];
  parameters?: Parameter[];
  requestBody?: {
    required: boolean;
    content: Record<string, { schema: Record<string, unknown> }>;
  };
  responses: Record<string, {
    description: string;
    content?: Record<string, { schema: Record<string, unknown> }>;
  }>;
}

function generateMarkdownFromOpenAPI(specPath: string, outputDir: string): void {
  const specContent = fs.readFileSync(specPath, 'utf-8');
  const spec = yaml.parse(specContent);

  for (const [pathUrl, methods] of Object.entries(spec.paths)) {
    for (const [method, operation] of Object.entries(
      methods as Record<string, PathOperation>
    )) {
      const op = operation as PathOperation;
      const filename = `${op.operationId}.md`;

      let markdown = `---
title: "${op.summary}"
sidebar_label: "${method.toUpperCase()} ${pathUrl}"
---

# ${op.summary}

\`\`\`
${method.toUpperCase()} ${pathUrl}
\`\`\`

`;

      // Parameters
      if (op.parameters && op.parameters.length > 0) {
        markdown += `## Parameters\n\n`;
        markdown += `| Name | Location | Required | Type | Description |\n`;
        markdown += `|------|----------|----------|------|-------------|\n`;
        for (const param of op.parameters) {
          markdown += `| \`${param.name}\` | ${param.in} | ${
            param.required ? 'Yes' : 'No'
          } | ${JSON.stringify(param.schema)} | ${param.description || ''} |\n`;
        }
        markdown += '\n';
      }

      // Request Body
      if (op.requestBody) {
        markdown += `## Request Body\n\n`;
        markdown += `Required: ${op.requestBody.required ? 'Yes' : 'No'}\n\n`;
        const jsonContent = op.requestBody.content['application/json'];
        if (jsonContent) {
          markdown += `\`\`\`json\n${JSON.stringify(
            resolveRef(spec, jsonContent.schema),
            null,
            2
          )}\n\`\`\`\n\n`;
        }
      }

      // Responses
      markdown += `## Responses\n\n`;
      for (const [statusCode, response] of Object.entries(op.responses)) {
        const resp = response as {
          description: string;
          content?: Record<string, { schema: Record<string, unknown> }>;
        };
        markdown += `### ${statusCode} — ${resp.description}\n\n`;
        if (resp.content && resp.content['application/json']) {
          markdown += `\`\`\`json\n${JSON.stringify(
            resolveRef(spec, resp.content['application/json'].schema),
            null,
            2
          )}\n\`\`\`\n\n`;
        }
      }

      const outputPath = path.join(outputDir, filename);
      fs.writeFileSync(outputPath, markdown);
      console.log(`Generated: ${outputPath}`);
    }
  }
}

function resolveRef(spec: any, schema: Record<string, unknown>): unknown {
  if ('$ref' in schema) {
    const refPath = (schema['$ref'] as string).replace('#/', '').split('/');
    let resolved: any = spec;
    for (const segment of refPath) {
      resolved = resolved[segment];
    }
    return resolved;
  }
  return schema;
}

// Run generation
generateMarkdownFromOpenAPI('docs/openapi.yaml', 'docs/api-reference/');
```

---

## 2.5 Как API-first компании используют документацию из спецификаций

Самая уважаемая документация API в индустрии — у компаний, которые считают спецификацию источником истины для документации. Разберём, почему их подход работает.

### Документация API от Anthropic

Документацию Anthropic по API Claude широко считают образцовой. Причина есть: она построена на спецификациях. Документацию не пишут после того, как API готов, — и документация, и API производятся из одной спецификации.

Что делает подход Anthropic эффективным:

1. **Спецификация сначала определяет контракт.** Прежде чем реализовать новую возможность API, спецификация точно задаёт, что принимает эндпоинт, что возвращает и какие ошибки порождает.

2. **Примеры кода тестируются.** Примеры в документации не написаны руками и не забыты — они извлекаются из секции примеров спецификации и проверяются против реального API в CI.

3. **SDK и документация из одного источника.** Python SDK, TypeScript SDK и справочник API происходят из одной спецификации OpenAPI. Когда спецификация меняется, обновляются все три.

4. **Версионирование явное.** Документация ясно показывает, к какой версии API относится каждая возможность, потому что информация о версии закодирована в спецификации.

### Модель документации Stripe

Stripe часто называют золотым стандартом документации API. Их подход полностью совпадает с принципами SDD:

- **У каждого эндпоинта API есть машиночитаемая спецификация**, задающая формат запроса, формат ответа и случаи ошибок.
- **Документация генерируется из этих спецификаций**, а не пишется отдельно.
- **Примеры кода в документации генерируются автоматически** для многих языков (Python, Ruby, Node.js, Go, Java и т. д.) из одной спецификации.
- **Changelog API получается из диффов спецификаций.** Когда спецификация меняется, запись в changelog генерируется автоматически и описывает, что изменилось.

### Архитектура документации Twilio

Twilio идёт дальше с тем, что называет «документацией на основе кода»:

- **Вспомогательные библиотеки генерируются из спецификаций OpenAPI.** SDK Twilio для каждого языка создаются автоматически.
- **Quickstart-гайды ссылаются на сгенерированный код.** Туториалы «с чего начать» используют автоматически созданные методы SDK, поэтому не устаревают.
- **Интерактивный проводник по API на основе спецификаций.** Проводник Twilio позволяет делать реальные вызовы API прямо из документации, а формат запроса и ответа задан спецификацией.

> **Заметка профессора:** Видите закономерность? Лучшая документация не у тех, кто нанял больше всего технических писателей, а у тех, кто вложился в инфраструктуру генерации документации из спецификаций. Качество документации — побочный эффект качества спецификаций. Хотите лучшую документацию — пишите лучшие спецификации.

---

## 2.6 Пирамида документации

Не вся документация служит одной цели. Типы документации образуют иерархию, и в процессе SDD все они могут быть выведены из спецификаций — но у них разные аудитории и задачи.

```
                    ┌───────────────┐
                    │   TUTORIALS   │  ← "Learning-oriented"
                    │  (narrative)  │     For newcomers
                    ├───────────────┤
                    │    GUIDES     │  ← "Goal-oriented"
                    │  (task-based) │     For practitioners
                    ├───────────────┤
                    │  API REFERENCE│  ← "Information-oriented"
                    │  (exhaustive) │     For implementers
                    ├───────────────┤
                    │   CHANGELOG   │  ← "Change-oriented"
                    │ (what changed)│     For upgraders
                    └───────────────┘
```

### Генерация каждого уровня из спецификаций

**Уровень 1: справочник API (полностью автоматизируется)**

Справочник API — прямое и полное представление ваших спецификаций. Каждый эндпоинт, каждый тип, каждый код ошибки, каждый пример. Этот уровень автоматизируется на 100%.

```typescript
// From this spec...
interface ListProductsSpec {
  method: 'GET';
  path: '/api/v2/products';
  query: {
    page: number;    // Required, >= 1
    limit: number;   // Required, 1-100
    category?: ProductCategory;
  };
  response: PaginatedResponse<ProductDTO>;
  errors: [ValidationError, UnauthorizedError];
}

// ...generate this reference doc automatically:
// ## GET /api/v2/products
// List products with pagination and filtering.
//
// ### Query Parameters
// | Parameter | Type | Required | Description |
// |-----------|------|----------|-------------|
// | page      | integer | Yes | Page number (min: 1) |
// | limit     | integer | Yes | Items per page (1-100) |
// | category  | string  | No  | Filter by category |
//
// ### Response (200 OK)
// ```json
// { "data": [...], "pagination": { ... } }
// ```
//
// ### Errors
// | Status | Code | Description |
// |--------|------|-------------|
// | 400    | VALIDATION_ERROR | Invalid query parameters |
// | 401    | UNAUTHORIZED | Missing or invalid token |
```

**Уровень 2: changelog (полностью автоматизируется)**

Changelog генерируется сравнением версий спецификации.

```typescript
// scripts/generate-changelog.ts

interface SpecDiff {
  added: string[];
  removed: string[];
  modified: {
    path: string;
    changes: string[];
  }[];
}

function generateChangelog(oldSpec: object, newSpec: object): string {
  const diff = computeSpecDiff(oldSpec, newSpec);
  let changelog = `# Changelog\n\n## v2.1.0 (2026-02-24)\n\n`;

  if (diff.added.length > 0) {
    changelog += `### Added\n`;
    for (const item of diff.added) {
      changelog += `- ${item}\n`;
    }
    changelog += '\n';
  }

  if (diff.modified.length > 0) {
    changelog += `### Changed\n`;
    for (const mod of diff.modified) {
      changelog += `- **${mod.path}**: ${mod.changes.join(', ')}\n`;
    }
    changelog += '\n';
  }

  if (diff.removed.length > 0) {
    changelog += `### Deprecated\n`;
    for (const item of diff.removed) {
      changelog += `- ${item} (removed in next major version)\n`;
    }
    changelog += '\n';
  }

  return changelog;
}

// Usage: diff between git tags
// git show v2.0.0:specs/api.yaml > /tmp/old-spec.yaml
// git show v2.1.0:specs/api.yaml > /tmp/new-spec.yaml
// npx ts-node scripts/generate-changelog.ts
```

**Уровень 3: практические руководства (полуавтоматические)**

Руководствам нужен более связный текст, чем справочнику, но структура и примеры всё равно выводятся из спецификаций. Нарративный каркас вы пишете один раз, а технические детали подставляются из спецификаций.

```markdown
<!-- docs/guides/creating-products.mdx -->
<!-- The narrative is hand-written. The technical details are injected. -->

# Creating Products

This guide walks you through creating products in the E-Commerce API.

## Prerequisites

Before you begin, make sure you have:
- An API key with `products:write` scope
- The API client library installed

## Step 1: Prepare Your Product Data

<!-- AUTO-INJECTED from CreateProductSchema -->
<SchemaTable schema="CreateProduct" />
<!-- Renders the schema as a table with field names, types, and descriptions -->

## Step 2: Make the API Call

<!-- AUTO-INJECTED from spec examples, for each supported language -->
<CodeExamples operationId="createProduct" />
<!-- Renders code examples in TypeScript, Python, curl -->

## Step 3: Handle the Response

<!-- AUTO-INJECTED from ProductResponseSchema -->
<SchemaTable schema="ProductResponse" />

## Error Handling

<!-- AUTO-INJECTED from spec error definitions -->
<ErrorTable operationId="createProduct" />
```

**Уровень 4: туториалы (в основном вручную, но с опорой на спецификацию)**

Туториалы нарративны и педагогичны, полностью их не автоматизировать. Но они могут ссылаться на компоненты, сгенерированные из спецификации, чтобы не устаревать.

````markdown
<!-- docs/tutorials/build-a-product-catalog.mdx -->

# Tutorial: Build a Product Catalog

In this tutorial, you will build a simple product catalog using the
E-Commerce API. By the end, you will have a working application that
lists, creates, and filters products.

## What You Will Build

A React application that:
1. Displays products in a grid
2. Supports pagination
3. Allows filtering by category
4. Lets admins create new products

## Setting Up

First, install the API client:

```bash
npm install @example/ecommerce-sdk
```

The SDK is auto-generated from our API specification, so the TypeScript
types will always match the current API.

<!-- AUTO-INJECTED: current SDK type definitions -->
<SDKTypes module="products" />

## Fetching Products

Here is how to list products using the SDK:

<!-- AUTO-INJECTED: working code example from spec -->
<TutorialStep operationId="listProducts">
```typescript
import { ECommerceClient } from '@example/ecommerce-sdk';

const client = new ECommerceClient({ apiKey: 'your-api-key' });

// Types are auto-generated from the API spec
const response = await client.products.list({
  page: 1,
  limit: 20,
  category: 'electronics',
});

console.log(`Found ${response.pagination.total} products`);
for (const product of response.data) {
  console.log(`${product.name}: $${product.price}`);
}
```
</TutorialStep>
````

---

## 2.7 Живая документация: обновляется вместе со спецификацией

Конечная цель — документация, которая «жива»: обновляется автоматически при каждом изменении спецификации. Вот как построить такой конвейер от начала до конца.

### Полный конвейер

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Spec    │────▶│ Generate │────▶│  Build   │────▶│  Deploy  │
│  Change  │     │  Docs    │     │  Site    │     │  Docs    │
│  (PR)    │     │ (CI job) │     │(Docusaurus)│   │  (CDN)   │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                                                   │
     │           ┌──────────┐                            │
     └──────────▶│ Validate │                            │
                 │  Sync    │◀───────────────────────────┘
                 └──────────┘
                 "Are docs in sync with specs?"
```

### Реализация

```yaml
# .github/workflows/living-docs.yml
name: Living Documentation Pipeline

on:
  push:
    branches: [main]
    paths:
      - 'src/specs/**'  # Only trigger when specs change
  pull_request:
    branches: [main]
    paths:
      - 'src/specs/**'

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      # Step 1: Generate OpenAPI from TypeScript specs
      - name: Generate OpenAPI spec
        run: npx ts-node scripts/generate-openapi.ts

      # Step 2: Generate Markdown docs from OpenAPI
      - name: Generate API reference docs
        run: npx ts-node scripts/generate-markdown-docs.ts

      # Step 3: Generate TypeDoc from spec interfaces
      - name: Generate TypeDoc
        run: npx typedoc

      # Step 4: Generate changelog from spec diff
      - name: Generate changelog
        run: npx ts-node scripts/generate-changelog.ts

      # Step 5: Validate all generated docs
      - name: Validate documentation
        run: |
          npm run docs:validate-links
          npm run docs:validate-examples
          npm run docs:validate-schemas

      # Step 6: Build the documentation site
      - name: Build Docusaurus site
        run: cd docs-site && npm run build

      # Step 7: Deploy (only on main branch)
      - name: Deploy to CDN
        if: github.ref == 'refs/heads/main'
        run: |
          npm run docs:deploy
          echo "Documentation deployed at $(date)"

      # Step 8: Notify team of doc updates
      - name: Notify documentation changes
        if: github.ref == 'refs/heads/main'
        run: |
          npx ts-node scripts/notify-doc-changes.ts \
            --commit=${{ github.sha }} \
            --channel=docs-updates
```

### Валидация: документация должна совпадать со спецификациями

```typescript
// scripts/validate-doc-sync.ts
// Run in CI to ensure docs are never out of sync with specs

import * as fs from 'fs';
import * as crypto from 'crypto';

interface SyncManifest {
  specs: Record<string, string>;  // filename -> content hash
  docs: Record<string, string>;   // filename -> content hash
  generatedAt: string;
}

function hashFile(filePath: string): string {
  const content = fs.readFileSync(filePath, 'utf-8');
  return crypto.createHash('sha256').update(content).digest('hex').slice(0, 12);
}

function validateSync(): void {
  // Read the sync manifest (generated during doc build)
  const manifest: SyncManifest = JSON.parse(
    fs.readFileSync('.doc-sync-manifest.json', 'utf-8')
  );

  const errors: string[] = [];

  // Check each spec file
  for (const [specFile, expectedHash] of Object.entries(manifest.specs)) {
    const currentHash = hashFile(specFile);
    if (currentHash !== expectedHash) {
      errors.push(
        `SPEC CHANGED: ${specFile} has been modified since docs were generated. ` +
        `Expected hash: ${expectedHash}, Current hash: ${currentHash}. ` +
        `Run 'npm run generate:docs' to update documentation.`
      );
    }
  }

  // Check each generated doc file
  for (const [docFile, expectedHash] of Object.entries(manifest.docs)) {
    if (!fs.existsSync(docFile)) {
      errors.push(`DOC MISSING: ${docFile} should exist but was not found.`);
      continue;
    }
    const currentHash = hashFile(docFile);
    if (currentHash !== expectedHash) {
      errors.push(
        `DOC MODIFIED: ${docFile} has been manually edited. ` +
        `This file is auto-generated and should not be edited directly. ` +
        `Edit the source spec instead and run 'npm run generate:docs'.`
      );
    }
  }

  if (errors.length > 0) {
    console.error('Documentation sync validation FAILED:\n');
    errors.forEach(e => console.error(`  - ${e}\n`));
    process.exit(1);
  }

  console.log('Documentation sync validation PASSED.');
  console.log(`  ${Object.keys(manifest.specs).length} specs checked.`);
  console.log(`  ${Object.keys(manifest.docs).length} doc files verified.`);
}

validateSync();
```

---

## 2.8 MDX как мост между спецификациями и читаемой документацией

MDX — Markdown с JSX — идеальный формат для документации из спецификаций: он позволяет встраивать динамические компоненты, выведенные из спецификации, прямо в повествовательную документацию.

### Почему MDX важен для SDD

Обычный Markdown статичен. Написали — и он не меняется. MDX позволяет импортировать живые компоненты, которые выбирают данные из спецификаций на этапе сборки:

```mdx
{/* docs/api/products.mdx */}

import { SchemaTable } from '../components/SchemaTable';
import { CodeExample } from '../components/CodeExample';
import { Endpoint } from '../components/Endpoint';
import { ErrorTable } from '../components/ErrorTable';
import { VersionBadge } from '../components/VersionBadge';

# Products API

<VersionBadge version="2.0.0" since="2026-01-15" />

The Products API allows you to manage your product catalog.

## List Products

<Endpoint method="GET" path="/api/v2/products" auth="required" />

Retrieve a paginated list of products with optional filtering.

### Parameters

<SchemaTable
  spec="ListProductsQuery"
  columns={['name', 'type', 'required', 'description', 'example']}
/>

{/* This component reads the spec file and renders a table.
    If the spec changes, this table updates automatically
    on the next build. No manual editing needed. */}

### Response

<CodeExample
  operationId="listProducts"
  languages={['typescript', 'python', 'curl']}
/>

{/* This component generates working code examples from the spec.
    The examples are validated against the actual API in CI. */}

### Errors

<ErrorTable operationId="listProducts" />

{/* This component lists all possible errors from the spec,
    including status codes, error codes, and descriptions. */}
```

### Сборка MDX-компонентов

```typescript
// docs-site/src/components/SchemaTable.tsx
// Renders a spec schema as a documentation table

import React from 'react';
import specs from '../../generated/spec-data.json';

interface SchemaTableProps {
  spec: string;
  columns?: string[];
}

export function SchemaTable({
  spec,
  columns = ['name', 'type', 'required', 'description'],
}: SchemaTableProps): React.ReactElement {
  const schema = specs.schemas[spec];

  if (!schema) {
    return (
      <div className="admonition admonition-danger">
        Schema "{spec}" not found. Has the spec been updated?
      </div>
    );
  }

  return (
    <table>
      <thead>
        <tr>
          {columns.map(col => (
            <th key={col}>{col.charAt(0).toUpperCase() + col.slice(1)}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {Object.entries(schema.properties || {}).map(([name, prop]: [string, any]) => (
          <tr key={name}>
            {columns.includes('name') && <td><code>{name}</code></td>}
            {columns.includes('type') && <td><code>{prop.type}</code></td>}
            {columns.includes('required') && (
              <td>{schema.required?.includes(name) ? 'Yes' : 'No'}</td>
            )}
            {columns.includes('description') && <td>{prop.description}</td>}
            {columns.includes('example') && (
              <td><code>{JSON.stringify(prop.example)}</code></td>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

```typescript
// docs-site/src/components/CodeExample.tsx
// Generates code examples from spec definitions

import React from 'react';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import CodeBlock from '@theme/CodeBlock';
import specs from '../../generated/spec-data.json';

interface CodeExampleProps {
  operationId: string;
  languages?: string[];
}

const generators: Record<string, (op: any) => string> = {
  typescript: (op) => `import { client } from './api-client';

const response = await client.${op.operationId}(${
    op.parameters
      ? JSON.stringify(op.exampleParams, null, 2)
      : ''
  });

console.log(response.data);`,

  python: (op) => `from ecommerce_sdk import Client

client = Client(api_key="your-api-key")

response = client.${toSnakeCase(op.operationId)}(${
    op.parameters
      ? Object.entries(op.exampleParams)
          .map(([k, v]) => `${toSnakeCase(k)}=${JSON.stringify(v)}`)
          .join(', ')
      : ''
  })

print(response.data)`,

  curl: (op) => {
    const params = op.exampleParams
      ? '?' + new URLSearchParams(op.exampleParams as any).toString()
      : '';
    return `curl -X ${op.method.toUpperCase()} \\
  "https://api.example.com${op.path}${params}" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"`;
  },
};

function toSnakeCase(str: string): string {
  return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
}

export function CodeExample({
  operationId,
  languages = ['typescript', 'python', 'curl'],
}: CodeExampleProps): React.ReactElement {
  const operation = specs.operations[operationId];

  if (!operation) {
    return (
      <div className="admonition admonition-danger">
        Operation "{operationId}" not found in specs.
      </div>
    );
  }

  return (
    <Tabs>
      {languages.map(lang => (
        <TabItem key={lang} value={lang} label={lang.charAt(0).toUpperCase() + lang.slice(1)}>
          <CodeBlock language={lang === 'curl' ? 'bash' : lang}>
            {generators[lang](operation)}
          </CodeBlock>
        </TabItem>
      ))}
    </Tabs>
  );
}
```

---

## 2.9 Автоматизация генерации документации в конвейерах CI/CD

Соберём полный раздел `scripts` в `package.json`, покрывающий весь жизненный цикл документации:

```json
{
  "scripts": {
    "specs:validate": "ts-node scripts/validate-specs.ts",
    "specs:lint": "spectral lint src/specs/**/*.spec.ts",

    "docs:generate:openapi": "ts-node scripts/generate-openapi.ts",
    "docs:generate:markdown": "ts-node scripts/generate-markdown-docs.ts",
    "docs:generate:typedoc": "typedoc --options typedoc.json",
    "docs:generate:storybook": "storybook build",
    "docs:generate:changelog": "ts-node scripts/generate-changelog.ts",
    "docs:generate:all": "npm-run-all docs:generate:*",

    "docs:validate:links": "ts-node scripts/validate-links.ts",
    "docs:validate:examples": "ts-node scripts/validate-code-examples.ts",
    "docs:validate:sync": "ts-node scripts/validate-doc-sync.ts",
    "docs:validate:all": "npm-run-all docs:validate:*",

    "docs:build": "npm run docs:generate:all && cd docs-site && npm run build",
    "docs:serve": "cd docs-site && npm run start",
    "docs:deploy": "cd docs-site && npm run deploy",

    "docs:full-pipeline": "npm run specs:validate && npm run docs:generate:all && npm run docs:validate:all && npm run docs:build"
  }
}
```

### Хук pre-commit

```bash
#!/bin/bash
# .husky/pre-commit
# Ensure docs are regenerated when specs change

SPEC_CHANGES=$(git diff --cached --name-only -- 'src/specs/')

if [ -n "$SPEC_CHANGES" ]; then
  echo "Spec changes detected. Regenerating documentation..."

  npm run docs:generate:all

  # Check if generated docs have changed
  DOC_CHANGES=$(git diff --name-only -- 'docs/')

  if [ -n "$DOC_CHANGES" ]; then
    echo ""
    echo "WARNING: Spec changes produced documentation updates."
    echo "The following doc files were regenerated:"
    echo "$DOC_CHANGES"
    echo ""
    echo "These changes have been staged automatically."
    git add docs/
  fi
fi
```

---

## 2.10 Роль ИИ в документации

Вот здесь становится действительно интересно. Модели вроде Claude и GPT исключительно хороши в одной задаче: перевод технической спецификации в человечный текст. Это мост между машиночитаемой спецификацией и документацией, которую людям приятно читать.

### Генерация документации из спецификаций с помощью ИИ

```typescript
// scripts/ai-doc-generator.ts
// Uses Claude to generate human-friendly documentation from specs

import Anthropic from '@anthropic-ai/sdk';
import * as fs from 'fs';

const anthropic = new Anthropic();

interface DocGenerationRequest {
  specContent: string;
  docType: 'api-reference' | 'guide' | 'tutorial';
  audience: 'beginner' | 'intermediate' | 'advanced';
  tone: 'formal' | 'conversational' | 'tutorial';
}

async function generateDocFromSpec(
  request: DocGenerationRequest
): Promise<string> {
  const systemPrompt = `You are a technical writer generating documentation
from API specifications. Your documentation should be:
- Accurate to the spec (never add information not in the spec)
- Clear and well-structured
- Appropriate for a ${request.audience} audience
- Written in a ${request.tone} tone
- Include practical examples derived from the spec
- Highlight common pitfalls and edge cases`;

  const userPrompt = `Generate a ${request.docType} document from this
TypeScript specification:

\`\`\`typescript
${request.specContent}
\`\`\`

Requirements:
- Cover every field and endpoint in the spec
- Include code examples in TypeScript and Python
- Document all error cases
- Add a "Common Mistakes" section
- Include a "Quick Start" section at the top`;

  const message = await anthropic.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 4096,
    messages: [
      { role: 'user', content: userPrompt },
    ],
    system: systemPrompt,
  });

  const textContent = message.content.find(block => block.type === 'text');
  return textContent ? textContent.text : '';
}

// Usage in the documentation pipeline
async function generateAllDocs(): Promise<void> {
  const specFiles = fs.readdirSync('src/specs/api/')
    .filter(f => f.endsWith('.spec.ts'));

  for (const specFile of specFiles) {
    const specContent = fs.readFileSync(
      `src/specs/api/${specFile}`,
      'utf-8'
    );

    // Generate API reference (formal, exhaustive)
    const reference = await generateDocFromSpec({
      specContent,
      docType: 'api-reference',
      audience: 'advanced',
      tone: 'formal',
    });

    // Generate guide (practical, goal-oriented)
    const guide = await generateDocFromSpec({
      specContent,
      docType: 'guide',
      audience: 'intermediate',
      tone: 'conversational',
    });

    const baseName = specFile.replace('.spec.ts', '');
    fs.writeFileSync(`docs/api-reference/${baseName}.md`, reference);
    fs.writeFileSync(`docs/guides/${baseName}.md`, guide);

    console.log(`Generated docs for ${baseName}`);
  }
}

generateAllDocs().catch(console.error);
```

### Слой человеческого ревью

Документацию, сгенерированную ИИ, нельзя публиковать без человеческого ревью. ИИ прекрасен в структуре, полноте и ясности, но может выдумать детали, упустить тонкие нюансы и иногда выдать текст технически верный, но педагогически бесполезный.

```markdown
## AI Documentation Review Checklist

### Accuracy
- [ ] Every statement is supported by the spec
- [ ] No hallucinated features or behaviors
- [ ] Code examples compile and run correctly
- [ ] Error codes match the spec exactly

### Completeness
- [ ] All endpoints/types/errors covered
- [ ] Edge cases documented
- [ ] Authentication requirements stated
- [ ] Rate limits documented

### Clarity
- [ ] Jargon is explained on first use
- [ ] Examples are practical (not contrived)
- [ ] Complex concepts have analogies or diagrams
- [ ] Reading order makes sense for the target audience

### Tone
- [ ] Consistent with existing documentation
- [ ] Appropriate for the target audience
- [ ] No condescending language
- [ ] No unexplained assumptions
```

> **Заметка профессора:** ИИ — машина первого черновика. Он превращает спецификации в текст быстрее любого человека. Но именно человеческое ревью превращает черновик в документацию, за которую не стыдно. ИИ делает 80% механической работы — структуру, полноту, шаблонные фразы. Человек делает 20%, где нужно суждение: тон, педагогическая логика, чутьё на «что запутает новичка».

---

## 2.11 Интернационализация документации из спецификаций

Когда спецификации — источник истины, интернационализация (i18n) становится заметно проще. Вместо перевода целых сайтов документации вы переводите структурированную спецификацию и перегенерируете документацию на каждом языке.

### Конвейер i18n

```typescript
// scripts/i18n-doc-generator.ts

interface TranslationManifest {
  sourceLocale: string;
  targetLocales: string[];
  translationStrategy: 'ai-assisted' | 'professional' | 'community';
  specsToTranslate: string[];
}

const manifest: TranslationManifest = {
  sourceLocale: 'en',
  targetLocales: ['es', 'fr', 'de', 'ja', 'zh', 'ko', 'pt-br'],
  translationStrategy: 'ai-assisted',
  specsToTranslate: [
    'src/specs/api/products.spec.ts',
    'src/specs/api/users.spec.ts',
    'src/specs/api/orders.spec.ts',
  ],
};

interface TranslatableContent {
  // These get translated
  descriptions: Record<string, string>;
  examples: Record<string, string>;
  errorMessages: Record<string, string>;
  guideContent: string;

  // These stay in English (technical identifiers)
  fieldNames: string[];
  endpointPaths: string[];
  statusCodes: number[];
  typeDefinitions: string[];
}

function extractTranslatableContent(specPath: string): TranslatableContent {
  // Parse the spec and separate translatable strings
  // from technical identifiers
  // ...
  return {} as TranslatableContent;
}

async function translateWithAI(
  content: TranslatableContent,
  targetLocale: string
): Promise<TranslatableContent> {
  // Use Claude to translate descriptions and guide content
  // Keep code examples in English but translate comments
  // Preserve technical terms with glossary consistency
  // ...
  return {} as TranslatableContent;
}

function generateLocalizedDocs(
  specPath: string,
  translatedContent: TranslatableContent,
  locale: string
): void {
  // Generate the same doc structure but with translated content
  // Technical details (types, endpoints, code) stay in English
  // Descriptions, guides, error messages are localized
  // ...
}
```

### Что переводится, а что нет

```markdown
## i18n Rules for Spec-Driven Docs

### TRANSLATE (locale-specific)
- Endpoint descriptions and summaries
- Field descriptions
- Error message descriptions
- Guide narrative text
- Tutorial content
- Code comments (within examples)
- UI labels referenced in docs

### DO NOT TRANSLATE (universal)
- Field names (e.g., `createdAt` stays `createdAt`)
- Endpoint paths (e.g., `/api/v2/products` stays the same)
- Type names (e.g., `ProductDTO` stays `ProductDTO`)
- Status codes (e.g., `200 OK`, `404 Not Found`)
- Code syntax (obviously)
- JSON keys
- Header names (e.g., `Authorization`, `Content-Type`)
```

---

## 2.12 Практический разбор: от спецификации-интерфейса на TypeScript к сгенерированной документации API и гайду для пользователя

Проследим весь путь от одной спецификации на TypeScript до опубликованной страницы документации.

### Спецификация

```typescript
// src/specs/api/orders.spec.ts

/**
 * @api Order Management
 * @version 2.0.0
 * @description Create, track, and manage customer orders.
 * @baseUrl /api/v2/orders
 */

import { z } from 'zod';

// --- Enums ---

export const OrderStatusSchema = z.enum([
  'pending',
  'confirmed',
  'processing',
  'shipped',
  'delivered',
  'cancelled',
  'refunded',
]);

// --- DTOs ---

export const OrderItemSchema = z.object({
  productId: z.string().describe('Product identifier'),
  quantity: z.number().int().positive().describe('Quantity ordered'),
  priceAtPurchase: z.number().positive().describe('Price at time of purchase (USD)'),
});

export const CreateOrderSchema = z.object({
  items: z.array(OrderItemSchema).min(1).max(50)
    .describe('Items to order (1-50 items per order)'),
  shippingAddressId: z.string()
    .describe('ID of saved shipping address'),
  paymentMethodId: z.string()
    .describe('ID of saved payment method'),
  notes: z.string().max(500).optional()
    .describe('Optional order notes'),
});

export const OrderResponseSchema = z.object({
  id: z.string().describe('Order identifier (ord_*)'),
  status: OrderStatusSchema.describe('Current order status'),
  items: z.array(OrderItemSchema).describe('Ordered items'),
  subtotal: z.number().describe('Sum of item prices'),
  tax: z.number().describe('Calculated tax amount'),
  shipping: z.number().describe('Shipping cost'),
  total: z.number().describe('Grand total (subtotal + tax + shipping)'),
  createdAt: z.string().datetime().describe('Order creation timestamp'),
  estimatedDelivery: z.string().datetime().nullable()
    .describe('Estimated delivery date (null if not shipped)'),
});

// --- Type Exports ---
export type OrderStatus = z.infer<typeof OrderStatusSchema>;
export type OrderItem = z.infer<typeof OrderItemSchema>;
export type CreateOrder = z.infer<typeof CreateOrderSchema>;
export type OrderResponse = z.infer<typeof OrderResponseSchema>;

// --- Endpoint Specs ---

/**
 * @endpoint POST /api/v2/orders
 * @auth Required (Bearer token)
 * @rateLimit 5 orders per minute per user
 *
 * @example
 * Request:
 * {
 *   "items": [
 *     { "productId": "prod_abc123", "quantity": 2, "priceAtPurchase": 29.99 }
 *   ],
 *   "shippingAddressId": "addr_xyz789",
 *   "paymentMethodId": "pm_def456"
 * }
 *
 * Response (201):
 * {
 *   "id": "ord_ghi012",
 *   "status": "pending",
 *   "items": [...],
 *   "subtotal": 59.98,
 *   "tax": 5.40,
 *   "shipping": 7.99,
 *   "total": 73.37,
 *   "createdAt": "2026-02-24T10:30:00Z",
 *   "estimatedDelivery": null
 * }
 *
 * @errors
 * 400 VALIDATION_ERROR — Invalid order data
 * 402 PAYMENT_REQUIRED — Payment method declined
 * 404 NOT_FOUND — Product or address not found
 * 409 CONFLICT — Insufficient inventory
 * 429 RATE_LIMITED — Too many orders
 */
export interface CreateOrderEndpoint {
  method: 'POST';
  path: '/api/v2/orders';
  body: CreateOrder;
  response: OrderResponse;
}
```

### Сгенерированный фрагмент OpenAPI

```yaml
# Auto-generated — do not edit manually
# Source: src/specs/api/orders.spec.ts
# Generated: 2026-02-24T10:30:00Z

paths:
  /api/v2/orders:
    post:
      operationId: createOrder
      summary: Create a new order
      description: Create, track, and manage customer orders.
      tags:
        - Orders
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateOrder'
            example:
              items:
                - productId: "prod_abc123"
                  quantity: 2
                  priceAtPurchase: 29.99
              shippingAddressId: "addr_xyz789"
              paymentMethodId: "pm_def456"
      responses:
        '201':
          description: Order created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/OrderResponse'
        '400':
          description: Invalid order data
        '402':
          description: Payment method declined
        '404':
          description: Product or address not found
        '409':
          description: Insufficient inventory
        '429':
          description: Too many orders (rate limit exceeded)
```

### Сгенерированная страница справочника API

```markdown
<!-- Auto-generated from orders.spec.ts — do not edit -->
<!-- Regenerate with: npm run docs:generate:all -->

---
title: "Create Order"
sidebar_label: "POST /orders"
---

# Create Order

```
POST /api/v2/orders
```

Create a new order with one or more items.

**Authentication:** Required (Bearer token)
**Rate Limit:** 5 orders per minute per user

## Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `items` | OrderItem[] | Yes | Items to order (1-50 items) |
| `items[].productId` | string | Yes | Product identifier |
| `items[].quantity` | integer | Yes | Quantity (min: 1) |
| `items[].priceAtPurchase` | number | Yes | Price in USD |
| `shippingAddressId` | string | Yes | Saved shipping address ID |
| `paymentMethodId` | string | Yes | Saved payment method ID |
| `notes` | string | No | Order notes (max 500 chars) |

## Response (201 Created)

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Order identifier (ord_*) |
| `status` | OrderStatus | Current status |
| `items` | OrderItem[] | Ordered items |
| `subtotal` | number | Sum of items |
| `tax` | number | Tax amount |
| `shipping` | number | Shipping cost |
| `total` | number | Grand total |
| `createdAt` | datetime | Creation timestamp |
| `estimatedDelivery` | datetime | Delivery estimate (null if not shipped) |

## Errors

| Status | Code | Description |
|--------|------|-------------|
| 400 | VALIDATION_ERROR | Invalid order data |
| 402 | PAYMENT_REQUIRED | Payment declined |
| 404 | NOT_FOUND | Product or address not found |
| 409 | CONFLICT | Insufficient inventory |
| 429 | RATE_LIMITED | Too many orders |
```

### Дружелюбный гайд для человека (с помощью ИИ)

```markdown
<!-- Generated by AI from orders.spec.ts, reviewed by technical writer -->

---
title: "Placing Orders"
sidebar_label: "Placing Orders"
---

# How to Place an Order

This guide walks you through creating an order using the E-Commerce API.

## Before You Start

You will need:
- An API key with `orders:write` permission
- At least one saved shipping address (see Addresses guide)
- At least one saved payment method (see Payments guide)
- Product IDs for the items you want to order

## Creating an Order

To create an order, send a POST request to `/api/v2/orders` with your
items, shipping address, and payment method.

### TypeScript

```typescript
const order = await client.orders.create({
  items: [
    {
      productId: 'prod_abc123',
      quantity: 2,
      priceAtPurchase: 29.99,
    },
  ],
  shippingAddressId: 'addr_xyz789',
  paymentMethodId: 'pm_def456',
  notes: 'Please gift wrap',
});

console.log(`Order ${order.id} created. Total: $${order.total}`);
```

### Python

```python
order = client.orders.create(
    items=[
        {
            "product_id": "prod_abc123",
            "quantity": 2,
            "price_at_purchase": 29.99,
        }
    ],
    shipping_address_id="addr_xyz789",
    payment_method_id="pm_def456",
    notes="Please gift wrap",
)

print(f"Order {order.id} created. Total: ${order.total}")
```

## Understanding Order Status

Orders move through these statuses:

```
pending → confirmed → processing → shipped → delivered
    ↓                      ↓
 cancelled              cancelled
                           ↓
                        refunded
```

## Common Mistakes

1. **Forgetting to include `priceAtPurchase`**: This field is required
   for audit purposes. Use the current product price from the catalog.

2. **Exceeding the item limit**: Orders are limited to 50 items.
   For larger orders, split them into multiple API calls.

3. **Rate limiting**: You can create at most 5 orders per minute.
   If you need bulk order creation, contact support for a higher limit.
```

---

## 2.13 Упражнение: возьмите 3 спецификации из предыдущих модулей и сгенерируйте полную документацию

### Задание

Выберите три спецификации, написанные вами в предыдущих модулях (или используйте примеры из этого курса). Для каждой спецификации соберите полный набор документации.

**Часть 1: генерация справочника API**

Для каждой спецификации:
1. Создайте схему Zod (если она ещё не на Zod)
2. Сгенерируйте фрагмент OpenAPI
3. Сгенерируйте страницу справочника API в Markdown
4. Проверьте, что все поля документированы
5. Включите минимум два примера кода (TypeScript + Python)

**Часть 2: генерация руководства**

Для каждой спецификации:
1. Напишите практическое руководство, используя спецификацию как исходный материал
2. Используйте MDX-компоненты, которые ссылаются на спецификацию (без захардкоженных значений)
3. Добавьте раздел «Частые ошибки»
4. Добавьте раздел «Быстрый старт»

**Часть 3: настройка конвейера**

1. Создайте `package.json` со всеми скриптами генерации
2. Создайте CI-процесс, проверяющий синхронизацию документации и спецификаций
3. Создайте pre-commit-хук, перегенерирующий документацию при изменении спецификаций
4. Поднимите сайт Docusaurus, который потребляет сгенерированную документацию

**Часть 4: документация с помощью ИИ**

1. Попросите Claude или GPT сгенерировать первый черновик туториала по одной из ваших спецификаций
2. Проверьте вывод ИИ на точность, полноту и тон
3. Доведите вывод ИИ до продакшн-качества
4. Опишите, что ИИ сделал правильно, а что потребовало человеческой правки

### Критерии оценки

```markdown
## Evaluation Rubric

### API Reference (25 points)
- All fields documented ..................... 5 pts
- Types accurate ........................... 5 pts
- Examples compile and run ................. 5 pts
- Error cases documented ................... 5 pts
- Generated (not hand-written) ............. 5 pts

### Guides (25 points)
- Task-oriented structure .................. 5 pts
- Uses MDX spec components ................. 5 pts
- Common mistakes section .................. 5 pts
- Quick start works end-to-end ............. 5 pts
- Appropriate for target audience .......... 5 pts

### Pipeline (25 points)
- Generation scripts work .................. 5 pts
- CI validation catches drift .............. 5 pts
- Pre-commit hook works .................... 5 pts
- Docusaurus site builds ................... 5 pts
- Full pipeline runs end-to-end ............ 5 pts

### AI-Assisted Documentation (25 points)
- AI prompt is well-structured ............. 5 pts
- AI output reviewed thoroughly ............ 5 pts
- Human edits improve quality .............. 5 pts
- Reflection on AI strengths/weaknesses .... 5 pts
- Final doc is production quality .......... 5 pts
```

---

## Итоги главы

«Документация как код» — не просто добрая практика, а смена парадигмы. Когда спецификации служат источником документации, вечная проблема устаревших доков просто исчезает. Документация не может устареть, потому что генерируется из того же артефакта, что движет реализацию и тесты.

Ключевые принципы главы:

1. **Спецификации И ЕСТЬ документация.** Один источник истины, несколько производных результатов.
2. **Генерация вместо поддержки.** Документация генерируется, а не ведётся вручную.
3. **Принуждение в CI.** Конвейер физически не даёт спецификации и документации разойтись.
4. **Пирамида документации.** Разным аудиториям нужны разные типы документации, и все они выводятся из одних и тех же спецификаций.
5. **ИИ как машина первого черновика.** Позвольте Claude или GPT написать текст из спецификации, а затем примените человеческое редакторское суждение.
6. **MDX как мост.** MDX-компоненты подтягивают живые данные из спецификаций в повествовательную документацию.

В следующей и последней главе мы обратимся к самой важной теме во всём SDD — к человеку. Где его место в мире, где ИИ генерирует код, тесты и документацию из спецификаций? Ответ, как выясняется, — везде, где это важно.

> *«Лучшая документация — та, что пишет себя сама, потому что происходит из той же истины, из которой происходит ПО».*

---

**Следующая глава:** Человек в контуре — как освоить шлюз утверждения

---

[← Оглавление курса](../INDEX.ru.md) · [← Глава 1: Спецификация рефакторинга](CHAPTER_01.ru.md) · [Глава 3: Человек в контуре →](CHAPTER_03.ru.md)
