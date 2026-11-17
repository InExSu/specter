# Глава 3: Спецификации с учётом среды

## МОДУЛЬ 04 — Продвинутая оркестрация и агенты (продвинутый уровень)

> [Оглавление курса](../INDEX.ru.md) · [Модуль 04](../INDEX.ru.md#модуль-04--продвинутая-оркестрация-и-агенты)

---

### Вступление к лекции

*Вот сценарий, над которым я прошу подумать. Вы пишете идеальную спецификацию. Агент-архитектор создаёт её безупречно. Агент-разработчик реализует ровно по ней. Агент-критик проверяет и выдаёт чистый PASS. Вы запускаете тесты. Всё зелёное. Вы выкатываете в продакшн. И оно ломается.*

*Почему? Потому что спецификация описывала, **что** должна делать программа. Описывала, **как** она должна себя вести. Но не описывала, **где** она будет работать. В среде разработки было 4 ГБ памяти, в продакшене — 16 ГБ, но там ещё и 10 000 одновременных пользователей. Локальная база была SQLite, в продакшене — PostgreSQL. В тестах использовался замоканный почтовый сервис, а в продакшене нужны настоящие SMTP-данные. В конвейере CI таймаут был 10 минут, в конвейере деплоя — 5.*

*Спецификации с учётом среды решают это. Это спецификации, которые описывают не просто программу, а программу **в её среде обитания**. Они отвечают на вопросы: что системе нужно от окружения, чтобы работать правильно? Что меняется между средами? Что остаётся тем же? Что где тестируется?*

*Здесь разработка через спецификации встречается с DevOps, с Infrastructure as Code и с реальностью: программа не живёт в вакууме. Она живёт на серверах, в контейнерах, за балансировщиками, с переменными окружения, в конвейерах CI/CD, в средах разработки, staging и продакшена. И если ваша спецификация не учитывает всё это, она неполна.*

*Google, Amazon, Microsoft, Anthropic — каждая из этих компаний выучила этот урок горьким опытом, и каждая вложилась в декларативную инфраструктуру, управляемую спецификациями. Сегодня мы учимся на их опыте.*

---

## 3.1 Почему контекст развёртывания важен для спецификаций

Начнём с фундаментального вопроса: почему спецификации должно быть дело до развёртывания?

Традиционный ответ из архитектуры ПО: «Не должно. Спецификации описывают поведение, а не развёртывание». В идеальном мире это так. Но мы живём не в идеальном мире. Мы живём в мире, где:

### Один и тот же код ведёт себя по-разному в разных средах

```
Environment    Database       Cache     Email Provider    Max Memory    Log Level
─────────────────────────────────────────────────────────────────────────────────
Local Dev      SQLite         None      Console logger    512MB         debug
CI/Test        PostgreSQL     Redis     Mock SMTP         2GB           info
Staging        PostgreSQL     Redis     SendGrid (test)   4GB           info
Production     PostgreSQL     Redis     SendGrid (live)   16GB          warn
```

Спецификация, говорящая «отправить письмо с подтверждением», означает в каждой из этих сред разное:

- **Локальная разработка:** вывести содержимое письма в консоль
- **CI/тесты:** отправить на замоканный SMTP-сервер и проверить доставку
- **Staging:** отправить в тестовом режиме SendGrid (без реальной доставки)
- **Продакшн:** отправить по-настоящему реальным пользователям с реальными последствиями

Если спецификация это не учитывает, агент-разработчик создаст код, который работает в одной среде и ломается в другой.

### Ограничения зависят от среды

Возьмём ограничение из спецификации: «Выгрузка должна завершаться за 30 секунд».

В локальной разработке 30 секунд могут быть пустяком: маленький набор данных, локальная база, без сетевых задержек. В продакшене с 50 000 строк, удалённой базой и конкурирующей нагрузкой 30 секунд могут быть амбициозной целью.

Спецификация с учётом среды делает это явным:

```yaml
constraints:
  - name: "export_timeout"
    description: "Maximum time for export to complete"
    values:
      local: "60s"       # Relaxed for development
      ci: "30s"          # Matches production target
      staging: "30s"     # Same as production
      production: "30s"  # The actual requirement
```

> **Заметка профессора:** Я видел, как команды теряли недели на отладку «нестабильных тестов», которые вовсе не были нестабильными. Они зависели от среды. Тест проходил на ноутбуке разработчика (быстрый SSD, много памяти) и падал в CI (общие раннеры, медленный ввод-вывод). Спецификация с учётом среды поймала бы это на этапе спецификации, а не отладки.

---

## 3.2 Переменные окружения как входы спецификации

Переменные окружения — самый распространённый механизм настройки ПО по средам. В SDD мы рассматриваем их как **входы спецификации**: явные объявления того, что системе нужно от окружения.

### Проблема недокументированных переменных окружения

В большинстве проектов переменные окружения разбросаны по:
- README-файлам (если повезёт)
- файлам `.env.example` (часто устаревшим)
- файлам Docker Compose
- конфигурации CI
- скриптам деплоя
- устному знанию («а, ещё нужно задать ВОТ_ТУ_ПЕРЕМЕННУЮ»)

Подход SDD: **каждая переменная окружения объявлена в спецификации.**

### Спецификация переменных окружения

```yaml
# spec/environment/environment-variables.spec.yaml

spec_version: "1.0.0"
feature: "environment-configuration"
type: "environment"

purpose: |
  Declares all environment variables required by the application,
  their types, validation rules, defaults, and which environments
  require them.

variables:
  # ──────────────────────────────────────────────────────
  # Database Configuration
  # ──────────────────────────────────────────────────────
  - name: "DATABASE_URL"
    type: "string"
    format: "connection-string"
    required:
      local: true
      ci: true
      staging: true
      production: true
    sensitive: true
    description: "PostgreSQL connection string"
    examples:
      local: "postgresql://localhost:5432/myapp_dev"
      ci: "postgresql://postgres:postgres@localhost:5432/myapp_test"
      staging: "postgresql://user:pass@staging-db.internal:5432/myapp_staging"
      production: "postgresql://user:pass@prod-db.internal:5432/myapp_prod"
    validation:
      pattern: "^postgresql://.*"
      must_contain: ["postgresql://"]

  - name: "DATABASE_POOL_SIZE"
    type: "integer"
    required:
      local: false
      ci: false
      staging: true
      production: true
    sensitive: false
    description: "Maximum number of database connections in the pool"
    defaults:
      local: 5
      ci: 5
      staging: 10
      production: 50
    validation:
      min: 1
      max: 200

  - name: "DATABASE_SSL_MODE"
    type: "enum"
    values: ["disable", "require", "verify-ca", "verify-full"]
    required:
      local: false
      ci: false
      staging: true
      production: true
    defaults:
      local: "disable"
      ci: "disable"
      staging: "require"
      production: "verify-full"

  # ──────────────────────────────────────────────────────
  # Authentication
  # ──────────────────────────────────────────────────────
  - name: "JWT_SECRET"
    type: "string"
    required:
      local: true
      ci: true
      staging: true
      production: true
    sensitive: true
    description: "Secret key for signing JWT tokens"
    validation:
      min_length: 32
      must_not_be: ["secret", "password", "changeme", "jwt_secret"]
    generation:
      method: "random"
      length: 64
      charset: "alphanumeric+special"

  - name: "OAUTH_CLIENT_ID"
    type: "string"
    required:
      local: false       # Can use mock auth locally
      ci: false           # Tests use mock auth
      staging: true
      production: true
    sensitive: false
    description: "OAuth provider client ID"

  - name: "OAUTH_CLIENT_SECRET"
    type: "string"
    required:
      local: false
      ci: false
      staging: true
      production: true
    sensitive: true
    description: "OAuth provider client secret"

  # ──────────────────────────────────────────────────────
  # Email Service
  # ──────────────────────────────────────────────────────
  - name: "EMAIL_PROVIDER"
    type: "enum"
    values: ["console", "smtp", "sendgrid", "ses"]
    required:
      local: true
      ci: true
      staging: true
      production: true
    defaults:
      local: "console"      # Print to console in dev
      ci: "smtp"             # Use mock SMTP in tests
      staging: "sendgrid"    # Use SendGrid test mode
      production: "sendgrid" # Use SendGrid live mode

  - name: "SENDGRID_API_KEY"
    type: "string"
    required:
      local: false                    # Not needed with console provider
      ci: false                       # Not needed with mock SMTP
      staging: true                   # Required for SendGrid
      production: true
    sensitive: true
    depends_on:
      variable: "EMAIL_PROVIDER"
      condition: "value in ['sendgrid']"

  # ──────────────────────────────────────────────────────
  # Application Settings
  # ──────────────────────────────────────────────────────
  - name: "NODE_ENV"
    type: "enum"
    values: ["development", "test", "staging", "production"]
    required:
      local: true
      ci: true
      staging: true
      production: true
    defaults:
      local: "development"
      ci: "test"
      staging: "staging"
      production: "production"

  - name: "LOG_LEVEL"
    type: "enum"
    values: ["debug", "info", "warn", "error"]
    required:
      local: false
      ci: false
      staging: true
      production: true
    defaults:
      local: "debug"
      ci: "info"
      staging: "info"
      production: "warn"

  - name: "CORS_ALLOWED_ORIGINS"
    type: "string[]"
    separator: ","
    required:
      local: false
      ci: false
      staging: true
      production: true
    defaults:
      local: ["http://localhost:3000"]
      ci: ["http://localhost:3000"]
      staging: ["https://staging.myapp.com"]
      production: ["https://myapp.com", "https://www.myapp.com"]

  # ──────────────────────────────────────────────────────
  # Feature Flags
  # ──────────────────────────────────────────────────────
  - name: "FEATURE_FLAG_PROVIDER"
    type: "enum"
    values: ["local", "launchdarkly", "unleash"]
    required:
      local: false
      ci: false
      staging: true
      production: true
    defaults:
      local: "local"
      ci: "local"
      staging: "launchdarkly"
      production: "launchdarkly"

validation_rules:
  - rule: "All sensitive variables must not appear in logs or error messages"
  - rule: "All required variables must be present at application startup"
  - rule: "Missing optional variables must use their documented defaults"
  - rule: "Invalid variable values must cause startup failure with clear error messages"
  - rule: "Variables with depends_on conditions are only required when the condition is met"
```

### Валидация переменных окружения при старте

По спецификации выше агент-разработчик создаёт модуль валидации:

```typescript
// src/config/environment.ts

import { z } from 'zod';

/**
 * Environment variable validation.
 * Implements: spec/environment/environment-variables.spec.yaml v1.0.0
 *
 * This module validates all environment variables at application startup.
 * If any required variable is missing or invalid, the application fails
 * fast with a clear error message.
 */

const environmentSchema = z.object({
  // Database
  DATABASE_URL: z
    .string()
    .startsWith('postgresql://', 'DATABASE_URL must be a PostgreSQL connection string'),
  DATABASE_POOL_SIZE: z
    .string()
    .transform(Number)
    .pipe(z.number().int().min(1).max(200))
    .default('5'),
  DATABASE_SSL_MODE: z
    .enum(['disable', 'require', 'verify-ca', 'verify-full'])
    .default('disable'),

  // Authentication
  JWT_SECRET: z
    .string()
    .min(32, 'JWT_SECRET must be at least 32 characters')
    .refine(
      (val) => !['secret', 'password', 'changeme', 'jwt_secret'].includes(val),
      'JWT_SECRET must not be a common/default value',
    ),
  OAUTH_CLIENT_ID: z.string().optional(),
  OAUTH_CLIENT_SECRET: z.string().optional(),

  // Email
  EMAIL_PROVIDER: z
    .enum(['console', 'smtp', 'sendgrid', 'ses'])
    .default('console'),
  SENDGRID_API_KEY: z.string().optional(),

  // Application
  NODE_ENV: z
    .enum(['development', 'test', 'staging', 'production'])
    .default('development'),
  LOG_LEVEL: z
    .enum(['debug', 'info', 'warn', 'error'])
    .default('debug'),
  CORS_ALLOWED_ORIGINS: z
    .string()
    .transform((val) => val.split(',').map((s) => s.trim()))
    .default('http://localhost:3000'),

  // Feature Flags
  FEATURE_FLAG_PROVIDER: z
    .enum(['local', 'launchdarkly', 'unleash'])
    .default('local'),
});

type Environment = z.infer<typeof environmentSchema>;

/**
 * Cross-field validation rules from the spec.
 */
function validateCrossFieldDependencies(env: Environment): string[] {
  const errors: string[] = [];

  // SENDGRID_API_KEY depends on EMAIL_PROVIDER being 'sendgrid'
  if (env.EMAIL_PROVIDER === 'sendgrid' && !env.SENDGRID_API_KEY) {
    errors.push(
      'SENDGRID_API_KEY is required when EMAIL_PROVIDER is "sendgrid"',
    );
  }

  // OAUTH credentials required in staging and production
  if (['staging', 'production'].includes(env.NODE_ENV)) {
    if (!env.OAUTH_CLIENT_ID) {
      errors.push(
        `OAUTH_CLIENT_ID is required in ${env.NODE_ENV} environment`,
      );
    }
    if (!env.OAUTH_CLIENT_SECRET) {
      errors.push(
        `OAUTH_CLIENT_SECRET is required in ${env.NODE_ENV} environment`,
      );
    }
  }

  // DATABASE_SSL_MODE should be verify-full in production
  if (
    env.NODE_ENV === 'production' &&
    env.DATABASE_SSL_MODE !== 'verify-full'
  ) {
    errors.push(
      'DATABASE_SSL_MODE must be "verify-full" in production '
      + `(currently "${env.DATABASE_SSL_MODE}")`,
    );
  }

  return errors;
}

/**
 * Validate and load environment configuration.
 * Fails fast with clear error messages if validation fails.
 */
export function loadEnvironment(): Environment {
  console.log('Validating environment configuration...');

  // Phase 1: Schema validation
  const result = environmentSchema.safeParse(process.env);
  if (!result.success) {
    const errors = result.error.issues.map(
      (issue) => `  ${issue.path.join('.')}: ${issue.message}`,
    );
    console.error('Environment validation failed:');
    console.error(errors.join('\n'));
    process.exit(1);
  }

  // Phase 2: Cross-field validation
  const crossFieldErrors = validateCrossFieldDependencies(result.data);
  if (crossFieldErrors.length > 0) {
    console.error('Environment cross-field validation failed:');
    console.error(crossFieldErrors.map((e) => `  ${e}`).join('\n'));
    process.exit(1);
  }

  // Phase 3: Sensitive variable protection
  const sensitiveVars = [
    'DATABASE_URL', 'JWT_SECRET', 'OAUTH_CLIENT_SECRET', 'SENDGRID_API_KEY',
  ];
  for (const varName of sensitiveVars) {
    if (process.env[varName]) {
      // Mask sensitive variables in any future logging
      Object.defineProperty(result.data, `${varName}_MASKED`, {
        get: () => `${varName}=***`,
        enumerable: false,
      });
    }
  }

  console.log(
    `Environment validated successfully (${result.data.NODE_ENV} mode)`,
  );
  return result.data;
}

// Export the validated config as a singleton
export const env = loadEnvironment();
```

> **Заметка профессора:** Обратите внимание на паттерн «падать быстро». Приложение не стартует, если окружение невалидно. Это несравнимо лучше, чем в три часа ночи обнаружить, что не хватало SENDGRID_API_KEY и письма для сброса пароля шесть часов молча не отправлялись. Валидируйте рано, валидируйте громко и валидируйте всё.

---

## 3.3 Конвейеры CI/CD как спецификации

Смена перспективы, центральная для этой главы: **конвейер CI/CD — это спецификация**. Он задаёт:

- какие шаги нужно выполнить для проверки кода
- в каком порядке эти шаги выполняются
- что считается успехом или провалом
- что происходит при сбое шага
- какие артефакты создаются

Когда вы пишете рабочий процесс GitHub Actions или конвейер GitLab CI, вы пишете декларативную спецификацию своего процесса разработки. SDD это признаёт и применяет к спецификациям конвейеров ту же строгость, что и к спецификациям функций.

### GitHub Actions как спецификация

```yaml
# .github/workflows/sdd-pipeline.yml
#
# This workflow IS a spec. It specifies the complete validation
# pipeline for our SDD project.
#
# Spec dependencies:
#   - spec/environment/environment-variables.spec.yaml
#   - spec/schemas/spec-schema.yaml
#   - spec/constraints/backward-compatibility.constraint.yaml

name: SDD Pipeline

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

# ──────────────────────────────────────────────────────
# ENVIRONMENT SPEC: CI-specific configuration
# Maps to: spec/environment/environment-variables.spec.yaml
# ──────────────────────────────────────────────────────
env:
  NODE_ENV: "test"
  DATABASE_URL: "postgresql://postgres:postgres@localhost:5432/myapp_test"
  DATABASE_POOL_SIZE: "5"
  DATABASE_SSL_MODE: "disable"
  JWT_SECRET: "ci-test-secret-that-is-at-least-32-characters-long"
  EMAIL_PROVIDER: "smtp"
  LOG_LEVEL: "info"
  CORS_ALLOWED_ORIGINS: "http://localhost:3000"
  FEATURE_FLAG_PROVIDER: "local"

jobs:
  # ──────────────────────────────────────────────────────
  # PHASE 1: Spec Validation
  # Validates specs before any code runs
  # ──────────────────────────────────────────────────────
  spec-validation:
    name: "Validate Specifications"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'

      - run: npm ci

      - name: "Schema conformance check"
        run: npx ts-node scripts/validate-spec-schema.ts

      - name: "Backward compatibility check"
        run: npx ts-node scripts/check-backward-compat.ts
        if: github.event_name == 'pull_request'

      - name: "Migration spec completeness check"
        run: npx ts-node scripts/check-migrations.ts
        if: github.event_name == 'pull_request'

      - name: "Changelog entry check"
        run: npx ts-node scripts/check-changelog.ts
        if: github.event_name == 'pull_request'

  # ──────────────────────────────────────────────────────
  # PHASE 2: Code Quality
  # Linting, type checking, formatting
  # ──────────────────────────────────────────────────────
  code-quality:
    name: "Code Quality"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run format:check

  # ──────────────────────────────────────────────────────
  # PHASE 3: Unit Tests
  # Fast, isolated tests -- no external dependencies
  # ──────────────────────────────────────────────────────
  unit-tests:
    name: "Unit Tests"
    needs: [spec-validation, code-quality]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npm run test:unit -- --coverage
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-unit
          path: coverage/

  # ──────────────────────────────────────────────────────
  # PHASE 4: Integration Tests
  # Tests with real database and services
  # ──────────────────────────────────────────────────────
  integration-tests:
    name: "Integration Tests"
    needs: [spec-validation, code-quality]
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: myapp_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npm run db:migrate
      - run: npm run test:integration

  # ──────────────────────────────────────────────────────
  # PHASE 5: Spec Compliance Tests
  # Validates code against spec acceptance criteria
  # ──────────────────────────────────────────────────────
  spec-compliance:
    name: "Spec Compliance Tests"
    needs: [unit-tests, integration-tests]
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_DB: myapp_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      - run: npm ci
      - run: npm run db:migrate
      - name: "Run spec acceptance criteria tests"
        run: npm run test:spec-compliance
      - name: "Generate spec coverage report"
        run: npx ts-node scripts/spec-coverage-report.ts
      - uses: actions/upload-artifact@v4
        with:
          name: spec-coverage
          path: reports/spec-coverage.json

  # ──────────────────────────────────────────────────────
  # PHASE 6: Build & Deploy (main branch only)
  # ──────────────────────────────────────────────────────
  deploy-staging:
    name: "Deploy to Staging"
    needs: [spec-compliance]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run build
      - name: "Deploy to staging"
        run: npx ts-node scripts/deploy.ts --environment staging
        env:
          DEPLOY_TOKEN: ${{ secrets.STAGING_DEPLOY_TOKEN }}
```

### Спецификация конвейера как контракт

Обратите внимание, как конвейер CI/CD воплощает несколько принципов, движимых спецификацией:

1. **Порядок фаз** — валидация спецификаций идёт до контроля качества, а тот — до тестов. Вы не тратите минуты CI на тестирование кода по невалидной спецификации.

2. **Конфигурация окружения** — переменные окружения CI объявлены явно и совпадают со спецификацией окружения. Никакой неявной конфигурации.

3. **Зависимости-сервисы** — PostgreSQL и Redis объявлены как сервисы, что совпадает с требованиями приложения к инфраструктуре.

4. **Поэтапные шлюзы** — каждая фаза зависит от успеха предыдущей. Тесты соответствия спецификации не запускаются, пока не прошли юнит- и интеграционные тесты.

5. **Артефакты** — отчёты о покрытии и о соответствии спецификации загружаются как артефакты, обеспечивая прослеживаемость.

---

## 3.4 Infrastructure as Code: предельная спецификация среды

Инструменты Infrastructure as Code (IaC) вроде Terraform, Pulumi и AWS CDK — по сути движки спецификаций для инфраструктуры. Они объявляют, какая инфраструктура должна существовать, а инструмент приводит реальность в соответствие с объявлением.

С точки зрения SDD ваш IaC-код — это спецификация среды для продакшн-инфраструктуры.

### Terraform как спецификация среды

```hcl
# infrastructure/terraform/main.tf
#
# This Terraform configuration IS the environment spec for production.
# It declares every infrastructure resource the application needs.
#
# Related spec: spec/environment/environment-variables.spec.yaml
# Related spec: spec/environment/infrastructure.spec.yaml

terraform {
  required_version = ">= 1.7"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "myapp-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
  }
}

# ──────────────────────────────────────────────────────
# Variables (inputs to the environment spec)
# ──────────────────────────────────────────────────────
variable "environment" {
  type        = string
  description = "Deployment environment (staging or production)"
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be 'staging' or 'production'."
  }
}

variable "db_instance_class" {
  type = string
  default = "db.t3.medium"
  description = "RDS instance class"
}

# Environment-specific configuration
# Maps to: spec/environment/environment-variables.spec.yaml
locals {
  env_config = {
    staging = {
      db_instance_class    = "db.t3.medium"
      db_pool_size         = 10
      db_ssl_mode          = "require"
      app_instance_count   = 2
      app_instance_type    = "t3.medium"
      log_level            = "info"
      feature_flag_provider = "launchdarkly"
    }
    production = {
      db_instance_class    = "db.r6g.large"
      db_pool_size         = 50
      db_ssl_mode          = "verify-full"
      app_instance_count   = 4
      app_instance_type    = "t3.large"
      log_level            = "warn"
      feature_flag_provider = "launchdarkly"
    }
  }

  config = local.env_config[var.environment]
}

# ──────────────────────────────────────────────────────
# Database (spec: DATABASE_URL, DATABASE_POOL_SIZE, DATABASE_SSL_MODE)
# ──────────────────────────────────────────────────────
resource "aws_db_instance" "main" {
  identifier     = "myapp-${var.environment}"
  engine         = "postgres"
  engine_version = "16.2"
  instance_class = local.config.db_instance_class

  db_name  = "myapp_${var.environment}"
  username = "myapp_admin"
  password = aws_secretsmanager_secret_version.db_password.secret_string

  # From spec: DATABASE_SSL_MODE
  parameter_group_name = aws_db_parameter_group.main.name

  # Production-grade settings
  multi_az                = var.environment == "production"
  backup_retention_period = var.environment == "production" ? 30 : 7
  deletion_protection     = var.environment == "production"

  storage_encrypted = true
  storage_type      = "gp3"
  allocated_storage = var.environment == "production" ? 100 : 20

  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
    Spec        = "spec/environment/infrastructure.spec.yaml"
  }
}

# ──────────────────────────────────────────────────────
# Application (ECS Fargate)
# ──────────────────────────────────────────────────────
resource "aws_ecs_task_definition" "app" {
  family                   = "myapp-${var.environment}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.environment == "production" ? 1024 : 512
  memory                   = var.environment == "production" ? 2048 : 1024

  container_definitions = jsonencode([
    {
      name  = "myapp"
      image = "myapp:${var.app_version}"

      # Environment variables from spec
      environment = [
        { name = "NODE_ENV", value = var.environment },
        { name = "DATABASE_POOL_SIZE", value = tostring(local.config.db_pool_size) },
        { name = "DATABASE_SSL_MODE", value = local.config.db_ssl_mode },
        { name = "LOG_LEVEL", value = local.config.log_level },
        { name = "EMAIL_PROVIDER", value = "sendgrid" },
        { name = "FEATURE_FLAG_PROVIDER", value = local.config.feature_flag_provider },
        {
          name  = "CORS_ALLOWED_ORIGINS",
          value = var.environment == "production"
            ? "https://myapp.com,https://www.myapp.com"
            : "https://staging.myapp.com"
        },
      ]

      # Sensitive variables from AWS Secrets Manager
      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = aws_secretsmanager_secret.db_url.arn
        },
        {
          name      = "JWT_SECRET"
          valueFrom = aws_secretsmanager_secret.jwt_secret.arn
        },
        {
          name      = "SENDGRID_API_KEY"
          valueFrom = aws_secretsmanager_secret.sendgrid_key.arn
        },
        {
          name      = "OAUTH_CLIENT_SECRET"
          valueFrom = aws_secretsmanager_secret.oauth_secret.arn
        },
      ]

      portMappings = [
        { containerPort = 3000, protocol = "tcp" }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/myapp-${var.environment}"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "app"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:3000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
}
```

> **Заметка профессора:** Посмотрите, как код Terraform ссылается на спецификацию. Переменные окружения не произвольны — они явно привязаны к спецификации среды. Конфигурация базы соответствует ограничениям спецификации. Интервал, таймаут и число повторов health check — не магические числа, они происходят из эксплуатационных требований, которым место в спецификации. Infrastructure as Code — не просто автоматизация; это инфраструктура, ведомая спецификацией.

---

## 3.5 Спецификации Docker/контейнеров: Dockerfile как спецификация развёртывания

Dockerfile — это спецификация среды выполнения. В SDD мы рассматриваем его как часть спецификации среды и следим, чтобы он соответствовал требованиям приложения.

### Dockerfile, ведомый спецификацией

```dockerfile
# Dockerfile
#
# Environment spec: spec/environment/runtime.spec.yaml
# This Dockerfile specifies the application's runtime environment.
#
# Requirements from spec:
# - Node.js 22 LTS
# - Non-root user for security
# - Health check endpoint
# - Minimal attack surface (no dev dependencies in production)
# - Reproducible builds (pinned base image)

# ── Build Stage ──────────────────────────────────────
FROM node:22.14-bookworm-slim AS builder

# Spec: build environment requires these system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Spec: dependency installation (deterministic via lockfile)
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts && \
    npm run postinstall

# Spec: build step
COPY . .
RUN npm run build

# Spec: prune dev dependencies for production image
RUN npm prune --production

# ── Runtime Stage ────────────────────────────────────
FROM node:22.14-bookworm-slim AS runtime

# Spec: security -- run as non-root user
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --shell /bin/false appuser

WORKDIR /app

# Spec: minimal runtime -- only production artifacts
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/package.json ./

# Spec: environment configuration
# These are defaults; actual values come from orchestrator (ECS, K8s, etc.)
ENV NODE_ENV=production
ENV PORT=3000

# Spec: security -- drop to non-root
USER appuser

# Spec: expose the application port
EXPOSE 3000

# Spec: health check (must match spec/environment/health-check.spec.yaml)
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD node -e "fetch('http://localhost:3000/health').then(r => { if (!r.ok) process.exit(1) })"

# Spec: application entry point
CMD ["node", "dist/main.js"]
```

### Спецификация среды выполнения

Dockerfile выше реализует эту спецификацию:

```yaml
# spec/environment/runtime.spec.yaml

spec_version: "1.0.0"
feature: "runtime-environment"
type: "environment"

purpose: |
  Specifies the runtime environment requirements for the application.
  This spec is implemented by the Dockerfile and validated by CI.

runtime:
  language: "node"
  version: "22.14"
  base_image: "node:22.14-bookworm-slim"
  package_manager: "npm"
  lockfile: "package-lock.json"

security:
  run_as_root: false
  user: "appuser"
  uid: 1001
  gid: 1001
  read_only_filesystem: false  # Would require volume mounts for temp files
  no_new_privileges: true
  capabilities_drop: ["ALL"]

health_check:
  endpoint: "/health"
  port: 3000
  interval: "30s"
  timeout: "5s"
  start_period: "60s"
  retries: 3
  expected_response:
    status: 200
    body_contains: '{"status":"healthy"}'

build:
  strategy: "multi-stage"
  stages:
    - name: "builder"
      purpose: "Install dependencies and compile TypeScript"
      includes: ["source code", "dev dependencies", "build tools"]
    - name: "runtime"
      purpose: "Minimal production image"
      includes: ["compiled code", "production dependencies"]
      excludes: ["source code", "dev dependencies", "build tools", "tests"]

  constraints:
    - "Build must be deterministic (npm ci, not npm install)"
    - "Dev dependencies must not be in the runtime image"
    - "Source code must not be in the runtime image"
    - "Build must complete in under 5 minutes on CI hardware"

ports:
  - number: 3000
    protocol: "tcp"
    purpose: "HTTP application server"

resource_limits:
  cpu:
    request: "250m"
    limit: "1000m"
  memory:
    request: "256Mi"
    limit: "512Mi"
  description: |
    These are Kubernetes resource requests/limits.
    The application should function within these bounds under normal load.
    Exceeding the memory limit will result in OOM kill.
```

---

## 3.6 Как облачные провайдеры используют декларативные спецификации для инфраструктуры

Крупные облачные провайдеры разработали собственные декларативные форматы спецификаций инфраструктуры. Их понимание помогает писать более качественные спецификации с учётом среды.

### Google Cloud: декларативное управление ресурсами

Подход Google Cloud строится вокруг декларативных конфигураций:

- **Google Kubernetes Engine (GKE)** использует YAML-манифесты для задания желаемого состояния
- **Cloud Run** использует YAML-спецификации сервисов для serverless-развёртываний
- **Google Cloud Deploy** использует конфигурации конвейеров для доставки

```yaml
# Google Cloud Run service specification
# This is an environment-aware deployment spec
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: myapp
  annotations:
    run.googleapis.com/description: |
      Implements: spec/environment/infrastructure.spec.yaml
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: '2'
        autoscaling.knative.dev/maxScale: '10'
        run.googleapis.com/cpu-throttling: 'false'
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
        - image: gcr.io/myproject/myapp:latest
          ports:
            - containerPort: 3000
          resources:
            limits:
              cpu: '1'
              memory: 512Mi
          env:
            - name: NODE_ENV
              value: production
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: connection-string
          startupProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 10
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            periodSeconds: 30
```

### AWS: CloudFormation и CDK

AWS использует шаблоны CloudFormation (YAML/JSON) и Cloud Development Kit (CDK) для декларативной инфраструктуры:

```typescript
// AWS CDK -- Infrastructure as spec (TypeScript)
// Implements: spec/environment/infrastructure.spec.yaml

import * as cdk from 'aws-cdk-lib';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as rds from 'aws-cdk-lib/aws-rds';

/**
 * Application Infrastructure Stack
 *
 * This CDK stack is the executable form of the infrastructure spec.
 * Every resource maps to a requirement in the environment spec.
 */
export class AppStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props: {
    environment: 'staging' | 'production';
  }) {
    super(scope, id);

    const isProduction = props.environment === 'production';

    // Database (spec: DATABASE_URL, DATABASE_POOL_SIZE)
    const database = new rds.DatabaseInstance(this, 'Database', {
      engine: rds.DatabaseInstanceEngine.postgres({
        version: rds.PostgresEngineVersion.VER_16_2,
      }),
      instanceType: isProduction
        ? ec2.InstanceType.of(ec2.InstanceClass.R6G, ec2.InstanceSize.LARGE)
        : ec2.InstanceType.of(ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM),
      multiAz: isProduction,
      deletionProtection: isProduction,
      backupRetention: cdk.Duration.days(isProduction ? 30 : 7),
      storageEncrypted: true,
    });

    // Application (spec: runtime, health_check, resource_limits)
    const taskDefinition = new ecs.FargateTaskDefinition(this, 'TaskDef', {
      cpu: isProduction ? 1024 : 512,
      memoryLimitMiB: isProduction ? 2048 : 1024,
    });

    const container = taskDefinition.addContainer('App', {
      image: ecs.ContainerImage.fromRegistry('myapp:latest'),
      logging: ecs.LogDrivers.awsLogs({ streamPrefix: 'app' }),
      healthCheck: {
        command: ['CMD-SHELL', 'curl -f http://localhost:3000/health || exit 1'],
        interval: cdk.Duration.seconds(30),   // From spec
        timeout: cdk.Duration.seconds(5),     // From spec
        retries: 3,                           // From spec
        startPeriod: cdk.Duration.seconds(60), // From spec
      },
      environment: {
        NODE_ENV: props.environment,
        DATABASE_POOL_SIZE: String(isProduction ? 50 : 10),
        DATABASE_SSL_MODE: isProduction ? 'verify-full' : 'require',
        LOG_LEVEL: isProduction ? 'warn' : 'info',
        EMAIL_PROVIDER: 'sendgrid',
      },
    });

    container.addPortMappings({ containerPort: 3000 });
  }
}
```

### Azure: шаблоны ARM и Bicep

Microsoft Azure использует шаблоны ARM (Azure Resource Manager) и язык Bicep для декларативной инфраструктуры. Принцип тот же: объявите желаемое состояние — платформа его обеспечит.

Все три облачных провайдера сошлись на одной фундаментальной идее: **инфраструктуру следует задавать декларативно, версионировать в системе контроля версий и применять автоматически.** Именно это SDD делает для кода приложения, а спецификации с учётом среды связывают одно с другим.

---

## 3.7 Фича-флаги как переключатели спецификации с учётом среды

Фича-флаги — один из самых мощных инструментов разработки с учётом среды. Они позволяют выкатывать один и тот же код во все среды, управляя тем, какие функции активны.

В SDD фича-флаги — элементы спецификации:

```yaml
# spec/features/notification-preferences.spec.yaml (excerpt)

feature_flags:
  - name: "ENABLE_SLACK_NOTIFICATIONS"
    description: "Controls availability of Slack as a notification channel"
    type: "boolean"
    default: false
    environments:
      local: true       # Enabled for development
      ci: true           # Enabled for testing
      staging: true      # Enabled for QA
      production: false  # Disabled until launch date
    rollout:
      strategy: "percentage"
      production_rollout_plan:
        - date: "2026-04-01"
          percentage: 5
          criteria: "Internal users only"
        - date: "2026-04-08"
          percentage: 25
          criteria: "Users who opted into beta"
        - date: "2026-04-15"
          percentage: 100
          criteria: "All users"

  - name: "ENABLE_NOTIFICATION_DIGEST"
    description: "Controls availability of digest notification mode"
    type: "boolean"
    default: false
    environments:
      local: true
      ci: true
      staging: true
      production: true   # Already launched
    launched_in: "1.1.0"

  - name: "MAX_SOCIAL_LINKS"
    description: "Maximum number of social links per user profile"
    type: "integer"
    default: 10
    environments:
      local: 10
      ci: 10
      staging: 10
      production: 10
    notes: "Can be adjusted without code deployment"
```

### Реализация фича-флагов, привязанная к спецификации

```typescript
// src/config/feature-flags.ts

/**
 * Feature flag configuration.
 * Implements: feature_flags sections across all feature specs.
 *
 * In production, these are managed by LaunchDarkly.
 * In development/CI, these use local defaults from the spec.
 */

import { env } from './environment';

interface FeatureFlag {
  name: string;
  enabled: boolean;
  value?: unknown;
}

interface FeatureFlagProvider {
  isEnabled(flagName: string, defaultValue: boolean): boolean;
  getValue<T>(flagName: string, defaultValue: T): T;
}

class LocalFeatureFlagProvider implements FeatureFlagProvider {
  private flags: Record<string, unknown>;

  constructor(environment: string) {
    // Defaults from spec, per environment
    this.flags = LOCAL_FLAG_DEFAULTS[environment] ?? {};
  }

  isEnabled(flagName: string, defaultValue: boolean): boolean {
    const value = this.flags[flagName];
    return typeof value === 'boolean' ? value : defaultValue;
  }

  getValue<T>(flagName: string, defaultValue: T): T {
    const value = this.flags[flagName];
    return value !== undefined ? (value as T) : defaultValue;
  }
}

// From spec: feature flag defaults per environment
const LOCAL_FLAG_DEFAULTS: Record<string, Record<string, unknown>> = {
  development: {
    ENABLE_SLACK_NOTIFICATIONS: true,
    ENABLE_NOTIFICATION_DIGEST: true,
    MAX_SOCIAL_LINKS: 10,
  },
  test: {
    ENABLE_SLACK_NOTIFICATIONS: true,
    ENABLE_NOTIFICATION_DIGEST: true,
    MAX_SOCIAL_LINKS: 10,
  },
  staging: {
    ENABLE_SLACK_NOTIFICATIONS: true,
    ENABLE_NOTIFICATION_DIGEST: true,
    MAX_SOCIAL_LINKS: 10,
  },
  production: {
    ENABLE_SLACK_NOTIFICATIONS: false,  // Controlled by LaunchDarkly
    ENABLE_NOTIFICATION_DIGEST: true,
    MAX_SOCIAL_LINKS: 10,
  },
};

/**
 * Create the appropriate feature flag provider based on environment.
 */
export function createFeatureFlagProvider(): FeatureFlagProvider {
  if (env.FEATURE_FLAG_PROVIDER === 'local') {
    return new LocalFeatureFlagProvider(env.NODE_ENV);
  }

  // In production/staging, use LaunchDarkly
  // (implementation would import LaunchDarkly SDK)
  return new LocalFeatureFlagProvider(env.NODE_ENV); // Simplified
}

export const featureFlags = createFeatureFlagProvider();
```

### Использование фича-флагов в коде, ведомом спецификацией

```typescript
// src/features/notifications/notification-channels.ts

import { featureFlags } from '../../config/feature-flags';

/**
 * Get available notification channels.
 *
 * The available channels depend on feature flags, which in turn
 * depend on the environment (spec: feature_flags section).
 */
export function getAvailableChannels(): string[] {
  const channels = ['email', 'push'];  // Always available (spec v1.0.0)

  // spec: feature_flags.ENABLE_SLACK_NOTIFICATIONS
  if (featureFlags.isEnabled('ENABLE_SLACK_NOTIFICATIONS', false)) {
    channels.push('slack');
  }

  return channels;
}
```

> **Заметка профессора:** Фича-флаги — мост между «в спецификации эта функция есть» и «развёртывание говорит, что функция активна». Функция может быть полностью реализована и проходить все тесты, но оставаться невидимой для пользователей в продакшене, пока флаг не переключён. Поэтому спецификация должна объявлять фича-флаги: они часть контракта функции со средой.

---

## 3.8 Спецификации тестирования по средам

Разным средам нужны разные стратегии тестирования. Спецификация должна определять, что где тестируется.

```yaml
# spec/testing/testing-strategy.spec.yaml

spec_version: "1.0.0"
feature: "testing-strategy"
type: "testing"

purpose: |
  Defines what tests run in which environments, with what data,
  and under what conditions.

environments:
  local:
    test_types: ["unit", "integration"]
    database: "sqlite"          # Fast, no setup required
    external_services: "mocked"
    test_data: "fixtures"
    coverage_requirement: "none" # Development speed over coverage
    timeout: "60s per test"

  ci:
    test_types: ["unit", "integration", "spec-compliance"]
    database: "postgresql"       # Match production
    external_services: "mocked"  # No real API calls in CI
    test_data: "fixtures + generated"
    coverage_requirement:
      line: 80
      branch: 70
      function: 85
    timeout: "30s per test"
    parallelism: 4               # Run test suites in parallel

  staging:
    test_types: ["smoke", "e2e", "performance"]
    database: "postgresql"       # Real database with test data
    external_services: "real (test mode)"  # Real APIs in test mode
    test_data: "synthetic production-like"
    coverage_requirement: "none" # Coverage checked in CI
    timeout: "120s per test"

  production:
    test_types: ["smoke", "synthetic-monitoring"]
    database: "production"       # Real production database
    external_services: "real"    # Real everything
    test_data: "none (read-only tests only)"
    coverage_requirement: "none"
    timeout: "10s per test"
    constraints:
      - "Tests MUST be read-only -- no writes to production data"
      - "Tests MUST NOT affect real users"
      - "Tests MUST complete within 10 seconds"
      - "Tests run on a 5-minute interval"

test_types:
  unit:
    description: "Isolated tests with mocked dependencies"
    runs_in: ["local", "ci"]
    characteristics:
      - "No external dependencies"
      - "No database access"
      - "No network calls"
      - "Fast: <100ms per test"
    naming_convention: "*.spec.ts or *.test.ts"

  integration:
    description: "Tests with real database and internal services"
    runs_in: ["local", "ci"]
    characteristics:
      - "Uses real database (test instance)"
      - "Uses real internal services"
      - "External APIs are mocked"
      - "Medium speed: <5s per test"
    naming_convention: "*.integration.test.ts"

  spec-compliance:
    description: "Tests that validate acceptance criteria from specs"
    runs_in: ["ci"]
    characteristics:
      - "One test per acceptance criterion"
      - "Tests are generated from spec YAML"
      - "Failure means spec violation"
    naming_convention: "*.compliance.test.ts"

  smoke:
    description: "Quick health checks after deployment"
    runs_in: ["staging", "production"]
    characteristics:
      - "Tests critical user paths only"
      - "Fast: <30s total"
      - "Read-only in production"
    tests:
      - "Health endpoint returns 200"
      - "Authentication flow works"
      - "Main page loads"
      - "API returns valid responses"

  e2e:
    description: "Full end-to-end tests with browser automation"
    runs_in: ["staging"]
    characteristics:
      - "Uses real browser (Playwright)"
      - "Tests complete user flows"
      - "Uses test accounts"
      - "Slow: may take minutes per test"

  performance:
    description: "Load and latency tests"
    runs_in: ["staging"]
    characteristics:
      - "Tests response times under load"
      - "Tests concurrent user capacity"
      - "Validates spec latency constraints"
    thresholds:
      p50_latency: "100ms"
      p95_latency: "500ms"
      p99_latency: "2000ms"
      max_error_rate: "0.1%"
      concurrent_users: 1000

  synthetic-monitoring:
    description: "Continuous production health monitoring"
    runs_in: ["production"]
    characteristics:
      - "Runs every 5 minutes"
      - "Alerts on failure"
      - "Read-only operations only"
      - "Uses synthetic test accounts"
    alert_on_failure:
      channel: "pagerduty"
      severity: "high"
```

### Генерация тестов соответствия спецификации

Один из самых мощных паттернов SDD — генерация тестов прямо из критериев приёмки спецификации:

```typescript
// scripts/generate-spec-compliance-tests.ts

/**
 * Reads spec YAML files and generates test stubs for each
 * acceptance criterion. These tests validate that the code
 * faithfully implements the spec.
 */

import * as yaml from 'js-yaml';
import * as fs from 'fs';
import * as path from 'path';
import * as glob from 'glob';

interface Spec {
  feature: string;
  spec_version: string;
  acceptance_criteria: string[];
}

function generateTestFile(spec: Spec): string {
  const testCases = spec.acceptance_criteria
    .map((criterion, index) => {
      // Parse "Given X, when Y, then Z" format
      const parts = parseCriterion(criterion);

      return `
  // Acceptance Criterion ${index + 1}
  // ${criterion}
  it('${escapeTestName(criterion)}', async () => {
    // GIVEN: ${parts.given}
    // TODO: Set up test preconditions

    // WHEN: ${parts.when}
    // TODO: Execute the action

    // THEN: ${parts.then}
    // TODO: Assert the expected outcome

    throw new Error('Test not implemented -- implement this acceptance criterion');
  });`;
    })
    .join('\n');

  return `/**
 * Spec Compliance Tests
 * Feature: ${spec.feature}
 * Spec Version: ${spec.spec_version}
 *
 * AUTO-GENERATED from spec acceptance criteria.
 * Implement each test to validate spec compliance.
 */

describe('Spec Compliance: ${spec.feature} v${spec.spec_version}', () => {
${testCases}
});
`;
}

function parseCriterion(criterion: string): {
  given: string;
  when: string;
  then: string;
} {
  const givenMatch = criterion.match(/[Gg]iven\s+(.+?)(?:,\s*[Ww]hen)/);
  const whenMatch = criterion.match(/[Ww]hen\s+(.+?)(?:,\s*[Tt]hen)/);
  const thenMatch = criterion.match(/[Tt]hen\s+(.+)/);

  return {
    given: givenMatch?.[1] ?? 'precondition not parsed',
    when: whenMatch?.[1] ?? 'action not parsed',
    then: thenMatch?.[1] ?? 'expectation not parsed',
  };
}

function escapeTestName(name: string): string {
  return name.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

// Main execution
const specFiles = glob.sync('specs/features/**/*.spec.yaml');

for (const specFile of specFiles) {
  const content = fs.readFileSync(specFile, 'utf-8');
  const spec = yaml.load(content) as Spec;

  if (!spec.acceptance_criteria?.length) continue;

  const testPath = specFile
    .replace('specs/features/', 'tests/spec-compliance/')
    .replace('.spec.yaml', '.compliance.test.ts');

  const testDir = path.dirname(testPath);
  fs.mkdirSync(testDir, { recursive: true });

  const testContent = generateTestFile(spec);
  fs.writeFileSync(testPath, testContent);

  console.log(`Generated: ${testPath} (${spec.acceptance_criteria.length} tests)`);
}
```

---

## 3.9 Спецификации безопасности: требования, зависящие от среды

Требования безопасности часто различаются по средам. В разработке могут допускаться самоподписанные сертификаты, а продакшн требует проверенного TLS. Staging может допускать широкие CORS-источники, а продакшн обязан быть строгим.

```yaml
# spec/environment/security.spec.yaml

spec_version: "1.0.0"
feature: "security-configuration"
type: "environment"

purpose: |
  Specifies security requirements for each deployment environment.
  These constraints are enforced at deployment time and validated
  by the Critic Agent.

tls:
  local:
    required: false
    certificate: "self-signed (optional)"
    min_version: "none"
  ci:
    required: false
    certificate: "none"
    min_version: "none"
  staging:
    required: true
    certificate: "Let's Encrypt"
    min_version: "TLS 1.2"
  production:
    required: true
    certificate: "Organization-validated (OV) or Extended Validation (EV)"
    min_version: "TLS 1.2"
    preferred_version: "TLS 1.3"
    hsts:
      enabled: true
      max_age: 31536000       # 1 year
      include_subdomains: true
      preload: true

cors:
  local:
    allowed_origins: ["*"]                           # Permissive for dev
    allowed_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: ["*"]
    credentials: true
  ci:
    allowed_origins: ["http://localhost:3000"]
    allowed_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: ["*"]
    credentials: true
  staging:
    allowed_origins: ["https://staging.myapp.com"]
    allowed_methods: ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: ["Content-Type", "Authorization", "X-Request-ID"]
    credentials: true
    max_age: 86400
  production:
    allowed_origins: ["https://myapp.com", "https://www.myapp.com"]
    allowed_methods: ["GET", "POST", "PUT", "DELETE"]
    allowed_headers: ["Content-Type", "Authorization", "X-Request-ID"]
    credentials: true
    max_age: 86400

headers:
  production:
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    "X-Content-Type-Options": "nosniff"
    "X-Frame-Options": "DENY"
    "X-XSS-Protection": "0"    # Disabled in favor of CSP
    "Referrer-Policy": "strict-origin-when-cross-origin"
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()"

authentication:
  session_timeout:
    local: "24h"       # Long sessions for dev convenience
    ci: "1h"           # Short for tests
    staging: "8h"
    production: "8h"

  rate_limiting:
    local:
      enabled: false
    ci:
      enabled: false
    staging:
      enabled: true
      login_attempts: 10       # More lenient for testing
      window: "15m"
    production:
      enabled: true
      login_attempts: 5
      window: "15m"
      lockout_duration: "30m"

secrets_management:
  local:
    provider: ".env file"
    rotation: "none"
  ci:
    provider: "GitHub Secrets"
    rotation: "none"
  staging:
    provider: "AWS Secrets Manager"
    rotation: "90 days"
  production:
    provider: "AWS Secrets Manager"
    rotation: "30 days"
    encryption: "AES-256"
    access_logging: true
    constraints:
      - "Secrets must never appear in logs"
      - "Secrets must never be committed to source control"
      - "Secret access must be audited"
      - "Secret rotation must not cause downtime"

data_protection:
  pii_handling:
    local:
      encryption_at_rest: false
      encryption_in_transit: false
      data_masking: false
    staging:
      encryption_at_rest: true
      encryption_in_transit: true
      data_masking: true          # Mask PII in logs
    production:
      encryption_at_rest: true
      encryption_in_transit: true
      data_masking: true
      data_retention: "7 years"   # Regulatory requirement
      right_to_erasure: true      # GDPR compliance
```

### Обеспечение соблюдения спецификации безопасности

```typescript
// src/middleware/security-headers.middleware.ts

/**
 * Security headers middleware.
 * Implements: spec/environment/security.spec.yaml -- headers section.
 *
 * Headers are environment-aware: production gets strict CSP,
 * development gets none.
 */

import { Request, Response, NextFunction } from 'express';
import { env } from '../config/environment';

interface SecurityHeaders {
  [key: string]: string;
}

// From spec: environment-specific security headers
const SECURITY_HEADERS: Record<string, SecurityHeaders> = {
  production: {
    'Content-Security-Policy':
      "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '0',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
    'Strict-Transport-Security':
      'max-age=31536000; includeSubDomains; preload',
  },
  staging: {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '0',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
  },
  // Development and test: minimal headers
  development: {},
  test: {},
};

export function securityHeadersMiddleware(
  req: Request,
  res: Response,
  next: NextFunction,
): void {
  const headers = SECURITY_HEADERS[env.NODE_ENV] ?? {};

  for (const [key, value] of Object.entries(headers)) {
    res.setHeader(key, value);
  }

  next();
}
```

---

## 3.10 Как Anthropic разворачивает Claude по средам с конфигурацией, ведомой спецификацией

Развёртывание Claude в Anthropic — полезная иллюстрация спецификаций с учётом среды на практике. Внутренние детали закрыты, но общие паттерны видны в публичной документации и дизайне API.

### Среды развёртывания модели

Anthropic эксплуатирует Claude в нескольких средах, у каждой свои характеристики:

```yaml
# Conceptual representation of Anthropic's deployment environments

environments:
  research:
    purpose: "Model training and evaluation"
    characteristics:
      - "Full model capabilities enabled"
      - "Extensive logging for analysis"
      - "Performance metrics collection"
      - "Safety evaluation suites"
    access: "Internal researchers only"

  internal_testing:
    purpose: "Pre-release testing and red-teaming"
    characteristics:
      - "Safety filters in test mode"
      - "Behavior logging for review"
      - "A/B testing of model versions"
    access: "Internal teams and trusted testers"

  api_production:
    purpose: "Public API (api.anthropic.com)"
    characteristics:
      - "Full safety filters active"
      - "Rate limiting enforced"
      - "Usage tracking and billing"
      - "Model version pinning available"
      - "SLA guarantees"
    access: "API customers with keys"

  consumer_production:
    purpose: "claude.ai consumer product"
    characteristics:
      - "Additional content filtering"
      - "User-facing safety features"
      - "Usage quotas per subscription tier"
      - "Different model selection logic"
    access: "Consumer users"
```

### Чему могут научиться практики SDD

Главный урок: одна и та же модель (Claude) ведёт себя по-разному в разных средах из-за **конфигурации, зависящей от среды**, а не из-за изменений кода. Фильтры безопасности, лимиты запросов, уровни логирования, доступность функций — всё это настройки, учитывающие среду.

Ваш конвейер SDD должен следовать тому же паттерну: один и тот же код, настроенный по-разному для каждой среды через вашу спецификацию среды.

---

## 3.11 Практический разбор: пишем полную спецификацию с учётом среды

Построим с нуля полную, готовую к продакшену спецификацию с учётом среды для одной функции. Мы специфицируем «систему доставки вебхуков», которая отправляет HTTP-вебхуки на внешние URL при наступлении событий.

Это отличный пример, потому что вебхуки по своей природе чувствительны к среде: в CI нельзя отправлять настоящие вебхуки, в staging и продакшене нужны разные политики повторов, а для отладки и для эксплуатации — разные уровни логирования.

```yaml
# spec/features/webhook-delivery.spec.yaml

spec_version: "1.0.0"
feature: "webhook-delivery"
status: "ga"
created: "2026-02-24"

purpose: |
  Deliver HTTP webhook notifications to external URLs when
  application events occur. Supports retry logic, signature
  verification, and delivery tracking.

# ──────────────────────────────────────────────────────
# Feature Specification (environment-independent)
# ──────────────────────────────────────────────────────
inputs:
  - name: "event"
    type: "WebhookEvent"
    required: true
    properties:
      type:
        type: "string"
        description: "Event type (e.g., 'user.created', 'order.completed')"
      payload:
        type: "object"
        description: "Event data"
      timestamp:
        type: "ISO8601DateTime"
      idempotency_key:
        type: "string"
        description: "Unique key to prevent duplicate deliveries"

  - name: "subscription"
    type: "WebhookSubscription"
    required: true
    properties:
      url:
        type: "string"
        format: "url"
        description: "The endpoint to deliver the webhook to"
      secret:
        type: "string"
        description: "Shared secret for HMAC signature"
      events:
        type: "string[]"
        description: "Event types this subscription listens for"
      active:
        type: "boolean"

outputs:
  - name: "delivery_result"
    type: "DeliveryResult"
    properties:
      delivery_id:
        type: "string"
      status:
        type: "enum"
        values: ["delivered", "failed", "retrying"]
      http_status:
        type: "integer"
        nullable: true
      attempts:
        type: "integer"
      next_retry_at:
        type: "ISO8601DateTime"
        nullable: true

constraints:
  - "Webhook payloads must be signed using HMAC-SHA256"
  - "Signature must be included in the X-Webhook-Signature header"
  - "Deliveries must include an X-Webhook-ID header with the delivery_id"
  - "Deliveries must include an X-Webhook-Timestamp header"
  - "Successful delivery: HTTP 2xx response within timeout"
  - "Webhook payload must be JSON with Content-Type: application/json"

error_cases:
  - condition: "Target URL returns non-2xx status"
    behavior: "Mark as failed, schedule retry according to retry policy"
  - condition: "Target URL is unreachable (DNS failure, connection refused)"
    behavior: "Mark as failed, schedule retry"
  - condition: "Request times out"
    behavior: "Mark as failed, schedule retry"
  - condition: "Maximum retries exhausted"
    behavior: "Mark as permanently failed, send alert"
  - condition: "Duplicate idempotency_key"
    behavior: "Return existing delivery result, do not re-deliver"

acceptance_criteria:
  - "Given a valid event and active subscription, the webhook is delivered to the subscription URL"
  - "Given a successful delivery (2xx response), the delivery status is 'delivered'"
  - "Given a failed delivery, the system retries according to the retry policy"
  - "Given max retries exhausted, the delivery status is 'failed' and an alert is sent"
  - "Given a duplicate idempotency_key, the webhook is not re-delivered"
  - "Given the webhook payload, the X-Webhook-Signature header contains a valid HMAC-SHA256"

# ──────────────────────────────────────────────────────
# Environment-Aware Configuration
# ──────────────────────────────────────────────────────
environment_config:
  delivery:
    timeout:
      local: "10s"
      ci: "5s"
      staging: "15s"
      production: "30s"

    retry_policy:
      local:
        max_retries: 1
        backoff: "fixed"
        interval: "5s"
        description: "Fast retries for development feedback"
      ci:
        max_retries: 2
        backoff: "fixed"
        interval: "1s"
        description: "Quick retries for test speed"
      staging:
        max_retries: 3
        backoff: "exponential"
        initial_interval: "30s"
        max_interval: "5m"
        multiplier: 2
        description: "Production-like but faster for testing"
      production:
        max_retries: 5
        backoff: "exponential"
        initial_interval: "1m"
        max_interval: "1h"
        multiplier: 2
        jitter: true
        description: "Full production retry with jitter to avoid thundering herd"

    concurrency:
      local: 2
      ci: 4
      staging: 10
      production: 50
      description: "Maximum concurrent webhook deliveries"

  target_url_restrictions:
    local:
      allowed_schemes: ["http", "https"]        # Allow HTTP for local testing
      allow_localhost: true                      # Can target localhost
      allow_private_ip: true                     # Can target private IPs
    ci:
      allowed_schemes: ["http", "https"]
      allow_localhost: true                      # Mock webhook receivers
      allow_private_ip: true
    staging:
      allowed_schemes: ["https"]                 # HTTPS only
      allow_localhost: false
      allow_private_ip: false
      blocklist: ["*.internal.company.com"]      # No internal URLs
    production:
      allowed_schemes: ["https"]                 # HTTPS only
      allow_localhost: false
      allow_private_ip: false
      blocklist: ["*.internal.company.com"]
      require_ssl_verification: true

  logging:
    local:
      log_request_body: true                     # Full payload logging for debugging
      log_response_body: true
      log_headers: true
      log_level: "debug"
    ci:
      log_request_body: true
      log_response_body: true
      log_headers: true
      log_level: "info"
    staging:
      log_request_body: true                     # For debugging integration issues
      log_response_body: true
      log_headers: false                         # Headers may contain secrets
      log_level: "info"
    production:
      log_request_body: false                    # Payloads may contain PII
      log_response_body: false                   # Response may contain PII
      log_headers: false
      log_level: "warn"
      log_delivery_status: true                  # Always log success/failure
      log_delivery_latency: true                 # Always log timing

  alerting:
    local:
      enabled: false
    ci:
      enabled: false
    staging:
      enabled: true
      channel: "slack"
      alert_on: ["permanent_failure"]
      throttle: "1 per minute"
    production:
      enabled: true
      channel: "pagerduty"
      alert_on: ["permanent_failure", "high_failure_rate"]
      high_failure_rate_threshold: "5% over 15 minutes"
      throttle: "1 per 5 minutes"

  mock_mode:
    description: |
      In mock mode, webhooks are not actually delivered. Instead,
      they are recorded in a mock delivery log for testing.
    local:
      enabled: false                             # Real delivery for local testing
      mock_receiver_port: 9999                   # Local mock server available
    ci:
      enabled: true                              # NEVER make real HTTP calls in CI
      mock_response_status: 200
      mock_response_delay: "50ms"
    staging:
      enabled: false                             # Real delivery to test endpoints
    production:
      enabled: false                             # Real delivery always

# ──────────────────────────────────────────────────────
# Feature Flags
# ──────────────────────────────────────────────────────
feature_flags:
  - name: "WEBHOOK_DELIVERY_ENABLED"
    type: "boolean"
    environments:
      local: true
      ci: true
      staging: true
      production: true

  - name: "WEBHOOK_BATCH_DELIVERY"
    type: "boolean"
    description: "Enable batching multiple events into a single delivery"
    environments:
      local: true
      ci: true
      staging: true
      production: false              # Not yet launched

# ──────────────────────────────────────────────────────
# Dependencies
# ──────────────────────────────────────────────────────
dependencies:
  - spec: "environment/environment-variables.spec.yaml"
    variables_used:
      - "WEBHOOK_SIGNING_SECRET"
      - "WEBHOOK_MAX_CONCURRENT"
  - spec: "environment/security.spec.yaml"
    sections_used:
      - "tls (for outbound HTTPS)"
```

### Реализация доставки вебхуков с учётом среды

```typescript
// src/features/webhooks/webhook-delivery.service.ts

import { env } from '../../config/environment';

/**
 * Webhook Delivery Service
 * Implements: spec/features/webhook-delivery.spec.yaml v1.0.0
 *
 * Environment-aware: behavior changes based on NODE_ENV.
 */

interface RetryPolicy {
  maxRetries: number;
  backoff: 'fixed' | 'exponential';
  initialIntervalMs: number;
  maxIntervalMs: number;
  multiplier: number;
  jitter: boolean;
}

interface DeliveryConfig {
  timeoutMs: number;
  retryPolicy: RetryPolicy;
  maxConcurrent: number;
  mockMode: boolean;
  logRequestBody: boolean;
  logResponseBody: boolean;
  allowHttp: boolean;
  allowLocalhost: boolean;
  allowPrivateIp: boolean;
}

/**
 * Load delivery configuration based on current environment.
 * All values come from the spec's environment_config section.
 */
function loadDeliveryConfig(): DeliveryConfig {
  const configs: Record<string, DeliveryConfig> = {
    development: {
      timeoutMs: 10_000,
      retryPolicy: {
        maxRetries: 1,
        backoff: 'fixed',
        initialIntervalMs: 5_000,
        maxIntervalMs: 5_000,
        multiplier: 1,
        jitter: false,
      },
      maxConcurrent: 2,
      mockMode: false,
      logRequestBody: true,
      logResponseBody: true,
      allowHttp: true,
      allowLocalhost: true,
      allowPrivateIp: true,
    },
    test: {
      timeoutMs: 5_000,
      retryPolicy: {
        maxRetries: 2,
        backoff: 'fixed',
        initialIntervalMs: 1_000,
        maxIntervalMs: 1_000,
        multiplier: 1,
        jitter: false,
      },
      maxConcurrent: 4,
      mockMode: true,                   // NEVER make real calls in CI
      logRequestBody: true,
      logResponseBody: true,
      allowHttp: true,
      allowLocalhost: true,
      allowPrivateIp: true,
    },
    staging: {
      timeoutMs: 15_000,
      retryPolicy: {
        maxRetries: 3,
        backoff: 'exponential',
        initialIntervalMs: 30_000,
        maxIntervalMs: 300_000,
        multiplier: 2,
        jitter: false,
      },
      maxConcurrent: 10,
      mockMode: false,
      logRequestBody: true,
      logResponseBody: true,
      allowHttp: false,                  // HTTPS only
      allowLocalhost: false,
      allowPrivateIp: false,
    },
    production: {
      timeoutMs: 30_000,
      retryPolicy: {
        maxRetries: 5,
        backoff: 'exponential',
        initialIntervalMs: 60_000,
        maxIntervalMs: 3_600_000,
        multiplier: 2,
        jitter: true,                    // Prevent thundering herd
      },
      maxConcurrent: 50,
      mockMode: false,
      logRequestBody: false,             // PII protection
      logResponseBody: false,
      allowHttp: false,
      allowLocalhost: false,
      allowPrivateIp: false,
    },
  };

  const config = configs[env.NODE_ENV];
  if (!config) {
    throw new Error(`No delivery config for environment: ${env.NODE_ENV}`);
  }

  return config;
}

export const deliveryConfig = loadDeliveryConfig();

/**
 * Calculate next retry delay using the environment's retry policy.
 */
export function calculateRetryDelay(
  attemptNumber: number,
  policy: RetryPolicy,
): number {
  let delay: number;

  if (policy.backoff === 'fixed') {
    delay = policy.initialIntervalMs;
  } else {
    // Exponential backoff
    delay = Math.min(
      policy.initialIntervalMs * Math.pow(policy.multiplier, attemptNumber - 1),
      policy.maxIntervalMs,
    );
  }

  if (policy.jitter) {
    // Add random jitter (0-50% of delay)
    delay = delay + Math.random() * delay * 0.5;
  }

  return Math.round(delay);
}

/**
 * Validate that a target URL is allowed in the current environment.
 * From spec: environment_config.target_url_restrictions
 */
export function validateTargetUrl(url: string): {
  valid: boolean;
  reason?: string;
} {
  const parsed = new URL(url);

  // Check scheme
  if (!deliveryConfig.allowHttp && parsed.protocol === 'http:') {
    return {
      valid: false,
      reason: `HTTP is not allowed in ${env.NODE_ENV}. Use HTTPS.`,
    };
  }

  // Check localhost
  if (
    !deliveryConfig.allowLocalhost &&
    (parsed.hostname === 'localhost' || parsed.hostname === '127.0.0.1')
  ) {
    return {
      valid: false,
      reason: `Localhost URLs are not allowed in ${env.NODE_ENV}.`,
    };
  }

  // Check private IP ranges
  if (!deliveryConfig.allowPrivateIp && isPrivateIp(parsed.hostname)) {
    return {
      valid: false,
      reason: `Private IP addresses are not allowed in ${env.NODE_ENV}.`,
    };
  }

  return { valid: true };
}

function isPrivateIp(hostname: string): boolean {
  const privateRanges = [
    /^10\./,
    /^172\.(1[6-9]|2[0-9]|3[0-1])\./,
    /^192\.168\./,
    /^fc00:/,
    /^fd/,
  ];
  return privateRanges.some((range) => range.test(hostname));
}
```

---

## 3.12 Связь спецификаций среды и спецификаций приложения

Закроем тему общей картиной: как соотносятся спецификации среды и спецификации приложения.

```
                    ┌──────────────────────────┐
                    │    Application Specs      │
                    │                            │
                    │  What the system does.     │
                    │  Features, behaviors,      │
                    │  inputs, outputs,          │
                    │  acceptance criteria.      │
                    │                            │
                    │  Example:                  │
                    │  "Export dashboard to CSV"  │
                    └─────────┬────────────────┘
                              │
                              │ DEPENDS ON
                              │
                    ┌─────────▼────────────────┐
                    │    Environment Specs       │
                    │                            │
                    │  Where the system runs.    │
                    │  Infrastructure, config,   │
                    │  variables, security,      │
                    │  deployment targets.       │
                    │                            │
                    │  Example:                  │
                    │  "PostgreSQL, 30s timeout, │
                    │   HTTPS only in prod"      │
                    └─────────┬────────────────┘
                              │
                              │ IMPLEMENTED BY
                              │
                    ┌─────────▼────────────────┐
                    │  Infrastructure as Code    │
                    │                            │
                    │  How the system is built.  │
                    │  Terraform, Docker, K8s,   │
                    │  CI/CD pipelines.          │
                    │                            │
                    │  Example:                  │
                    │  "RDS instance, ECS task,  │
                    │   GitHub Actions pipeline" │
                    └──────────────────────────┘
```

### Три слоя спецификации

**Слой 1: спецификации приложения** отвечают на вопрос «что делает программа?»
- Спецификации функций, API, поведения
- Не зависят от среды (в идеале)
- Читаются агентами-разработчиками для создания кода приложения

**Слой 2: спецификации среды** отвечают на вопрос «где работает программа?»
- Требования к инфраструктуре, конфигурация, безопасность
- Зависят от среды (по определению)
- Читаются DevOps-агентами для настройки развёртываний

**Слой 3: Infrastructure as Code** отвечает на вопрос «как готовится среда?»
- Terraform, CloudFormation, манифесты Kubernetes
- Исполняемая форма спецификаций среды
- Применяются конвейерами развёртывания

### Где эти слои взаимодействуют

Слои взаимодействуют в конкретных точках:

1. **Спецификация приложения ссылается на конфигурацию среды:**
   ```yaml
   # Application spec
   constraints:
     - "Export must complete within ${ENV.EXPORT_TIMEOUT}"
   ```

2. **Спецификация среды даёт значения:**
   ```yaml
   # Environment spec
   EXPORT_TIMEOUT:
     local: "60s"
     production: "30s"
   ```

3. **IaC реализует среду:**
   ```hcl
   # Terraform
   environment = [
     { name = "EXPORT_TIMEOUT", value = "30s" }
   ]
   ```

Агент-разработчик читает спецификацию приложения и пишет код. Код читает переменную окружения во время работы. IaC задаёт эту переменную при развёртывании. Спецификация среды обеспечивает согласованность всех трёх.

> **Заметка профессора:** По такой трёхслойной модели в 2026 году работают лучшие инженерные организации. Разработчики приложения пишут спецификации функций и код. Платформенная команда пишет спецификации среды и IaC. Конвейер CI/CD проверяет согласованность всего. А спецификации — это контракты, удерживающие все три слоя в согласии. Если какой-то слой отходит от спецификации, конвейер это поймает. Вот в чём сила разработки через спецификации.

---

## 3.13 Ключевые выводы

1. **Контекст среды — забота спецификации.** Спецификации, игнорирующие контекст развёртывания, неполны. Один и тот же код ведёт себя по-разному в разработке, CI, staging и продакшене, и ваша спецификация должна это признавать и контролировать.

2. **Переменные окружения — входы спецификации.** Объявляйте их формально: имя, тип, в каких средах они обязательны, значения по умолчанию, правила валидации и классификация чувствительности.

3. **Конвейеры CI/CD — спецификации.** Ваш рабочий процесс GitHub Actions — декларативная спецификация процесса разработки. Относитесь к нему с той же строгостью, что к спецификациям функций.

4. **Infrastructure as Code — предельная спецификация среды.** Terraform, CloudFormation, CDK и манифесты Kubernetes — исполняемые спецификации вашей инфраструктуры.

5. **Фича-флаги соединяют спецификации и среды.** Они позволяют одному коду вести себя по-разному в разных средах под управлением переключателей, объявленных в спецификации.

6. **Требования безопасности зависят от среды.** Что допустимо в разработке (HTTP, широкий CORS, самоподписанные сертификаты), недопустимо в продакшене (только HTTPS, строгий CORS, проверенные сертификаты).

7. **Стратегии тестирования различаются по средам.** Юнит-тесты в CI, smoke-тесты в продакшене, нагрузочные тесты в staging. Спецификация должна объявлять, что где тестируется.

8. **Три слоя (спецификации приложения, спецификации среды, IaC) должны оставаться согласованными.** Спецификация — контракт, обеспечивающий согласованность между слоями.

---

### Упражнения

**Упражнение 1.** Напишите полную спецификацию с учётом среды для функции загрузки файлов. Спецификация должна покрывать: локальную разработку (файловое хранилище), CI (замоканное хранилище), staging (тестовый бакет S3) и продакшн (продакшн-бакет S3 с шифрованием). Включите переменные окружения, ограничения безопасности и стратегию тестирования.

**Упражнение 2.** Создайте конвейер CI/CD (GitHub Actions), проверяющий спецификацию доставки вебхуков из раздела 3.11. Конвейер должен: проверить схему спецификации, прогнать тесты в режиме моков в CI, прогнать интеграционные тесты против настоящего приёмника вебхуков в staging и выкатить в продакшн со smoke-тестом.

**Упражнение 3.** Напишите спецификацию безопасности для приложения, работающего с медицинскими данными (соответствие HIPAA). Чем ограничения безопасности различаются между средами? Какие дополнительные ограничения HIPAA накладывает на продакшн-среду, которых нет в разработке?

---

*На этом модуль 04 «Продвинутая оркестрация и агенты» завершён. Теперь у вас есть инструменты, чтобы строить многоагентные конвейеры SDD, управлять эволюцией спецификаций во времени и писать спецификации, учитывающие весь жизненный цикл развёртывания. В модуле 05 мы заглянем на передний край: как SDD интегрируется с новыми возможностями ИИ и куда движется область.*

---

[← Оглавление курса](../INDEX.ru.md) · [← Глава 2: Эволюционирующие спецификации](CHAPTER_02.ru.md) · [Глава 1: Спецификация рефакторинга →](../MODULE_05/CHAPTER_01.ru.md)
