# Глава 1: Спецификация рефакторинга

## МОДУЛЬ 05 — Сопровождение и масштабирование (продвинутый уровень)

---

### Вступление к лекции

> *С возвращением. Если вы добрались до модуля 5, вы уже доказали о себе важное: вы мыслите системами, а не промптами. Вы научились писать спецификации с нуля, валидировать их, оркестрировать вокруг них многоагентные процессы и версионировать их по мере эволюции требований. Но теперь мы сталкиваемся с реальностью, которую рано или поздно встречает каждый работающий инженер: код уже существует, он грязный, и никто не написал для него спецификацию.*

> *Это самая распространённая ситуация в профессиональной разработке. Проекты с чистого листа — редкость. Большую часть карьеры вы проведёте с кодом, который написал кто-то другой: или код, который вы написали полгода назад и который вполне мог быть написан чужим человеком. Вопрос не в том, столкнётесь ли вы с легаси-кодом. Вопрос в том, подойдёте ли вы к нему с планом или с молитвой.*

> *Сегодня мы учимся писать спецификацию рефакторинга — самый требовательный и, возможно, самый ценный тип спецификации в инструментарии SDD. Здесь ремесло встречается с археологией, терпение — с точностью, а настоящие продуктовые архитекторы отделяются от промпт-инженеров.*

---

## 1.1 Почему рефакторингу нужна спецификация

Начнём с неуютной правды: большинство рефакторингов проваливается. Не потому, что инженерам не хватает мастерства, а потому, что им не хватает ясности в том, чего они вообще хотят добиться. Они ныряют в код, начинают «прибираться», а через три недели приложение в худшем состоянии, чем было. Функции сломаны. Тесты красные. Сроки сорваны. Команда деморализована.

Так происходит, потому что рефакторинг без спецификации — как ремонт дома без чертежей. Вы можете знать, что хотите «сделать кухню больше», но без плана несущих стен, сантехники и электрики вы получите кучу обломков.

Спецификация рефакторинга решает это, заставляя ответить на три вопроса прежде, чем вы тронете хоть одну строку кода:

1. **Что существует прямо сейчас?** (фаза археологии)
2. **Что должно существовать, когда мы закончим?** (целевая архитектура)
3. **Как пройти отсюда туда, ничего не сломав?** (путь миграции)

> **Заметка профессора:** Не устану повторять: причина номер один провальных рефакторингов — пропущенный первый шаг. Инженеры по природе оптимисты. Им хочется строить новое. Но если вы не понимаете старое досконально, вы упустите скрытые зависимости, недокументированное поведение и неявные контракты, на которые система опирается. Уважайте археологию.

---

## 1.2 Фаза археологии: понимаем, что существует

Прежде чем описывать, что должно измениться, нужно понять, что есть. Это фаза археологии — самая интеллектуально требовательная часть написания спецификации рефакторинга. Вы не просто читаете код, вы реконструируете замысел по артефактам.

### 1.2.1 Четыре слоя археологии кода

Подступаясь к существующей кодовой базе, нужно раскопать четыре разных слоя:

**Слой 1: структурный**
Какие файлы существуют? Как они организованы? Какие между ними зависимости?

```bash
# Generate a dependency graph of an Express.js project
# This is your first archaeological tool
npx madge --image dependency-graph.svg src/

# Count lines of code by file type
find src/ -name "*.ts" -o -name "*.js" | xargs wc -l | sort -n

# List all route definitions
grep -rn "router\.\(get\|post\|put\|delete\|patch\)" src/
```

**Слой 2: поведенческий**
Что система на самом деле делает? Не то, что говорят комментарии и обещает README, а то, что происходит, когда приходят запросы.

```typescript
// Archaeological tool: request logging middleware
// Deploy this BEFORE you start specifying changes
import { Request, Response, NextFunction } from 'express';

interface RequestLog {
  timestamp: string;
  method: string;
  path: string;
  queryParams: Record<string, unknown>;
  bodyShape: Record<string, string>;  // key -> typeof value
  responseStatus: number;
  responseTime: number;
  headers: Record<string, string>;
}

const archaeologyMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const start = Date.now();
  const originalSend = res.send;

  res.send = function (body: any) {
    const log: RequestLog = {
      timestamp: new Date().toISOString(),
      method: req.method,
      path: req.path,
      queryParams: req.query as Record<string, unknown>,
      bodyShape: Object.fromEntries(
        Object.entries(req.body || {}).map(([k, v]) => [k, typeof v])
      ),
      responseStatus: res.statusCode,
      responseTime: Date.now() - start,
      headers: req.headers as Record<string, string>,
    };

    // Write to archaeology log — NOT to production logs
    appendToArchaeologyLog(log);
    return originalSend.call(this, body);
  };

  next();
};
```

**Слой 3: контрактный**
Какие неявные и явные контракты существуют? Кто вызывает этот код? Чего они ожидают?

```typescript
// Document discovered contracts in your archaeology notes
interface DiscoveredContract {
  endpoint: string;
  consumers: string[];          // Who calls this?
  expectedInputShape: object;   // What do they send?
  expectedOutputShape: object;  // What do they expect back?
  errorBehaviors: string[];     // What happens on failure?
  sideEffects: string[];        // Database writes, emails, etc.
  undocumentedBehaviors: string[]; // Surprises you found
}
```

**Слой 4: исторический**
Почему код выглядит так? Какие решения принимались и какие ограничения были тогда?

```bash
# Git archaeology: who changed what and when
git log --oneline --all --graph -- src/api/users.ts

# Find the commit that introduced a suspicious pattern
git log -S "workaround" --oneline

# Show the full context of when a file was created
git log --diff-filter=A -- src/utils/legacyHelper.ts
```

### 1.2.2 Отчёт об археологии

Результат фазы археологии — структурированный документ, отчёт об археологии. Он станет фундаментом вашей спецификации рефакторинга.

```markdown
# Archaeology Report: User Service API

## Date: 2026-02-24
## Archaeologist: [Your Name]
## Scope: src/api/users/, src/services/userService.ts, src/models/user.ts

### System Overview
The User Service handles CRUD operations for user accounts.
It was originally written in 2023 using Express.js with raw SQL queries.
A partial migration to Prisma ORM was attempted in 2024 but abandoned.

### Structural Findings
- 14 route handlers across 3 files (should be 1)
- Mixed use of callbacks and async/await
- No consistent error handling pattern
- Two competing user models: `User` (Prisma) and `UserLegacy` (raw SQL)

### Behavioral Findings (from 7-day request log)
- 47 unique endpoints discovered (docs list only 31)
- 16 undocumented endpoints still receiving traffic
- Average response time: 340ms (target: <100ms)
- 3 endpoints return inconsistent shapes based on query params

### Contractual Findings
- Mobile app v2.1 depends on legacy field `user.fullName` (deprecated)
- Admin dashboard calls 4 undocumented endpoints
- Webhook system assumes synchronous user creation

### Historical Findings
- Original author left company in 2024
- Prisma migration abandoned due to deadline pressure (see commit a3f7b2c)
- "Temporary" workaround for auth added 2023-11-15, never removed

### Risk Assessment
- HIGH: 16 undocumented endpoints — consumers unknown
- MEDIUM: Mixed ORM state — partial Prisma, partial raw SQL
- LOW: Inconsistent error handling — no known production issues
```

> **Заметка профессора:** Обратите внимание: отчёт об археологии — ещё не спецификация. Это доказательства. Это факты о мире, какой он есть. Спецификация идёт следом и опирается на эти факты. Слишком многие инженеры перескакивают сразу к «вот как я хочу, чтобы это выглядело», не поняв сперва «вот как это выглядит на самом деле». Именно так всё и ломается.

---

## 1.3 Техника обратной спецификации

Когда археология завершена, в вашем распоряжении мощная техника: обратная спецификация. Вместо того чтобы писать спецификацию того, что хотите построить, а потом строить, вы пишете спецификацию того, что уже существует, — как если бы написали её до кода.

Зачем это нужно? Потому что так разрыв между «что есть» и «что должно быть» становится явным и измеримым.

```typescript
// REVERSE SPEC: What the User Service currently does
// (Not what it should do — what it actually does right now)

/**
 * @reverse-spec UserService
 * @status DISCOVERED (not designed)
 * @archaeology-date 2026-02-24
 */
interface UserServiceCurrentBehavior {
  // === DOCUMENTED ENDPOINTS ===

  /**
   * GET /api/users
   * Returns paginated user list
   * @note Pagination is broken — returns all users if page param missing
   * @note Response shape changes if `?legacy=true` is passed
   */
  listUsers(params: {
    page?: number;      // Optional — defaults to returning ALL (bug)
    limit?: number;     // Optional — defaults to 50
    legacy?: boolean;   // Undocumented flag that changes response shape
  }): Promise<UserListResponse | LegacyUserListResponse>;

  /**
   * POST /api/users
   * Creates a new user
   * @note Synchronous — blocks until DB write completes
   * @note Sends welcome email inline (not queued)
   * @note No input validation on email field
   */
  createUser(data: {
    email: string;      // Not validated — accepts malformed emails
    name: string;
    password: string;   // Stored as bcrypt hash (good)
    role?: string;      // Defaults to "user" — no enum validation
  }): Promise<User>;

  // === UNDOCUMENTED ENDPOINTS ===

  /**
   * GET /api/users/search
   * @undocumented — Not in API docs
   * @consumers Admin Dashboard (confirmed), possibly others
   * Full-text search across user records
   * @warning Uses raw SQL — potential injection vulnerability
   */
  searchUsers(query: string): Promise<User[]>;

  // ... (16 more undocumented endpoints)
}
```

Теперь сравните эту обратную спецификацию с тем, как система *должна* выглядеть:

```typescript
// TARGET SPEC: What the User Service should do after refactor

/**
 * @spec UserService v2.0
 * @migration-from UserServiceCurrentBehavior
 * @target-date 2026-Q2
 */
interface UserServiceTargetBehavior {
  /**
   * GET /api/v2/users
   * Returns paginated user list
   * @requires Pagination is mandatory — no full-table scans
   * @validation page >= 1, limit between 1 and 100
   */
  listUsers(params: {
    page: number;       // Required — enforced
    limit: number;      // Required — enforced, max 100
  }): Promise<PaginatedResponse<UserDTO>>;

  /**
   * POST /api/v2/users
   * Creates a new user
   * @requires Async processing — returns 202 Accepted
   * @requires Email validation via regex + MX record check
   * @requires Welcome email queued via job system
   */
  createUser(data: CreateUserDTO): Promise<{
    id: string;
    status: 'pending';
  }>;

  /**
   * GET /api/v2/users/search
   * @requires Parameterized queries only — no raw SQL
   * @requires Rate limiting: 10 requests/minute per client
   */
  searchUsers(params: SearchParams): Promise<PaginatedResponse<UserDTO>>;
}
```

Разрыв между двумя спецификациями и есть ваш объём рефакторинга. Каждое различие — рабочий пункт. Каждое совпадение — то, что трогать не нужно.

---

## 1.4 Определяем объём: что трогать, а что оставить

Одно из самых сложных умений в рефакторинге — вовремя остановиться. Соблазн «починить всё, раз уж мы здесь» силён, и это ловушка. Каждое дополнительное изменение повышает риск, удлиняет сроки и усложняет тестирование.

### Матрица объёма

Используйте эту матрицу, чтобы классифицировать каждое возможное изменение:

```
                    HIGH IMPACT
                        |
         QUADRANT 2     |     QUADRANT 1
         "Schedule It"  |     "Do It Now"
                        |
  LOW EFFORT -----------+------------ HIGH EFFORT
                        |
         QUADRANT 3     |     QUADRANT 4
         "Maybe Never"  |     "Think Twice"
                        |
                    LOW IMPACT
```

**Квадрант 1 (высокое влияние, большие усилия):** это ядро рефакторинга. Эти пункты оправдывают его существование. Пропишите их тщательно.

**Квадрант 2 (высокое влияние, малые усилия):** быстрые победы. Включите их в спецификацию рефакторинга, но держите отдельно от основных изменений, чтобы выпускать независимо.

**Квадрант 3 (низкое влияние, малые усилия):** соблазнительно добавить «раз уж мы здесь». Сопротивляйтесь. Занесите в список будущих улучшений. Они размывают фокус.

**Квадрант 4 (низкое влияние, большие усилия):** категорически нет. Это убийцы рефакторинга. Кто-то будет доказывать: «раз уж мы трогаем этот код, сделаем и это». Ответ — нет.

### Объём в спецификации

В спецификации рефакторинга должен быть явный раздел об объёме:

```markdown
## Refactor Scope

### IN SCOPE (Will be changed in this refactor)
- [ ] Migrate all user endpoints from Express routes to NestJS controllers
- [ ] Replace raw SQL queries with Prisma ORM
- [ ] Implement proper input validation using class-validator
- [ ] Add consistent error handling with NestJS exception filters
- [ ] Migrate 16 undocumented endpoints to documented v2 API

### OUT OF SCOPE (Explicitly will NOT be changed)
- [ ] Authentication system (working correctly, separate refactor planned)
- [ ] Database schema (no schema changes in this refactor)
- [ ] Frontend API client code (will be updated in a follow-up)
- [ ] Email sending infrastructure (works, just needs to be async)

### BOUNDARY CONDITIONS
- Legacy v1 endpoints must remain functional during migration
- No downtime during migration — both v1 and v2 run simultaneously
- Performance must not degrade — target p99 latency <= 200ms
```

> **Заметка профессора:** Раздел «вне объёма», пожалуй, важнее раздела «в объёме». Это ваш щит от расползания объёма. Когда кто-то говорит «раз уж вы там, не могли бы вы ещё…», вы показываете на спецификацию. Это не в объёме. Это явно исключено. Хотят — пусть пишут отдельную спецификацию.

---

## 1.5 Паттерн «фикус-душитель» в применении к спецификациям

Паттерн «фикус-душитель» (Strangler Fig), впервые описанный Мартином Фаулером, — одна из самых мощных техник крупномасштабного рефакторинга. Идея проста: вместо единовременной замены системы вы постепенно выращиваете новую вокруг старой, направляя на неё всё больше трафика, пока старую нельзя будет удалить полностью.

В применении к спецификациям это значит: вы пишете серию инкрементальных спецификаций, каждая из которых душит часть старой системы:

```markdown
# Strangler Fig Spec Series: User Service Migration

## Phase 1 Spec: The Facade (Week 1-2)
### Objective
Stand up a NestJS application that proxies ALL requests to the existing
Express.js service. Zero behavior change. Pure passthrough.

### Success Criteria
- All existing tests pass against the new facade
- Response times increase by no more than 10ms (proxy overhead)
- No client-visible changes

### What Changes
- New NestJS app deployed alongside Express app
- Load balancer routes to NestJS
- NestJS proxies all requests to Express

### What Does Not Change
- Express app continues running
- All business logic remains in Express
- No data model changes

---

## Phase 2 Spec: First Endpoint Migration (Week 3-4)
### Objective
Migrate GET /api/users (list users) to native NestJS implementation.
All other endpoints continue to proxy to Express.

### Success Criteria
- GET /api/users served natively by NestJS
- Response shape identical to Express version
- Response time improved (target: <100ms, currently 340ms)
- All other endpoints still proxied successfully

---

## Phase 3 Spec: CRUD Migration (Week 5-8)
### Objective
Migrate all documented CRUD endpoints to native NestJS.
Undocumented endpoints continue to proxy.

---

## Phase 4 Spec: Undocumented Endpoint Resolution (Week 9-10)
### Objective
For each of the 16 undocumented endpoints:
- Confirm active consumers
- Either migrate to v2 API or deprecate with notice

---

## Phase 5 Spec: Express Decommission (Week 11-12)
### Objective
Remove the Express application entirely.
All traffic served natively by NestJS.

### Prerequisites
- Zero requests proxied to Express for 7 consecutive days
- All consumer teams have confirmed migration to v2 endpoints
```

Спецификация каждой фазы — законченная самостоятельная спецификация. У неё свои критерии успеха, свой план тестирования и своя стратегия отката. Если какая-то фаза провалится, миграцию можно остановить на этом месте, и система останется работоспособной.

### Почему это хорошо работает с ИИ

Подход «фикуса-душителя» особенно хорош для разработки с ИИ: спецификация каждой фазы достаточно мала, чтобы уместиться в одно контекстное окно. Вы не просите ИИ понять всю миграцию сразу — вы просите выполнить одну чётко определённую фазу.

```typescript
// Phase 1: The Facade — this is what you hand to the AI

// spec: nestjs-facade.spec.md
// context: existing Express routes (provided as reference)
// constraint: ZERO business logic in this phase
// constraint: EVERY request must be proxied to Express backend

import { Controller, All, Req, Res } from '@nestjs/common';
import { Request, Response } from 'express';
import axios from 'axios';

@Controller()
export class ProxyController {
  private readonly expressBackend = process.env.EXPRESS_BACKEND_URL;

  @All('*')
  async proxyRequest(
    @Req() req: Request,
    @Res() res: Response,
  ): Promise<void> {
    try {
      const response = await axios({
        method: req.method,
        url: `${this.expressBackend}${req.originalUrl}`,
        headers: {
          ...req.headers,
          host: new URL(this.expressBackend).host,
        },
        data: req.body,
        validateStatus: () => true, // Forward ALL status codes
      });

      res.status(response.status);
      Object.entries(response.headers).forEach(([key, value]) => {
        if (value) res.setHeader(key, value as string);
      });
      res.send(response.data);
    } catch (error) {
      // If Express is down, return 502 — do not fabricate responses
      res.status(502).json({
        error: 'Backend service unavailable',
        timestamp: new Date().toISOString(),
      });
    }
  }
}
```

---

## 1.6 Оценка рисков в спецификации рефакторинга

Любой рефакторинг несёт риск. Раздел оценки рисков в спецификации нужен не для того, чтобы устранить риск — это невозможно, — а чтобы перечислить его, оценить количественно и определить стратегии смягчения для каждого выявленного риска.

### Реестр рисков

```markdown
## Risk Registry

### RISK-001: Undocumented Endpoint Consumers
- **Probability:** HIGH
- **Impact:** HIGH (broken functionality for unknown consumers)
- **Mitigation:** Deploy request logging 2 weeks before migration.
  Identify all consumers of undocumented endpoints.
  Contact consumer teams before deprecating any endpoint.
- **Fallback:** Maintain Express proxy for undocumented endpoints
  indefinitely until all consumers are identified.

### RISK-002: Data Shape Differences Between v1 and v2
- **Probability:** MEDIUM
- **Impact:** HIGH (client-side parsing failures)
- **Mitigation:** v2 responses include all v1 fields (deprecated).
  New fields added alongside, not replacing.
  Provide 90-day deprecation window for old fields.
- **Fallback:** Content negotiation header allows clients to
  request v1 response shape from v2 endpoints.

### RISK-003: Performance Regression During Proxy Phase
- **Probability:** LOW
- **Impact:** MEDIUM (increased latency during Phase 1-3)
- **Mitigation:** Proxy adds <10ms overhead (benchmarked).
  Circuit breaker prevents cascade failures.
  Health checks monitor both NestJS and Express.
- **Fallback:** Load balancer can route directly to Express
  within 30 seconds if NestJS proxy degrades.

### RISK-004: Prisma ORM Query Performance
- **Probability:** MEDIUM
- **Impact:** MEDIUM (slower queries than hand-optimized SQL)
- **Mitigation:** Benchmark all migrated queries against originals.
  Use Prisma raw queries for performance-critical paths.
  Query analysis in staging before production deploy.
- **Fallback:** Maintain raw SQL fallback for top 5 queries by volume.
```

> **Заметка профессора:** Обратите внимание: у каждого риска есть и смягчение (как предотвратить проблему), и запасной план (что делать, если проблема всё же случится). Это не паранойя, это инженерия. Надежда — не стратегия.

---

## 1.7 Как Google управляет крупномасштабными рефакторингами

Чтобы понять, как выглядит рефакторинг в предельном масштабе, посмотрим на подход Google. Их монорепозиторий содержит миллиарды строк кода. Когда нужно изменить тысячи файлов — скажем, перейти с одной версии API на другую, — просто открыть пул-реквест нельзя.

### Rosie и крупномасштабные изменения (LSC)

Google разработал внутреннюю систему Rosie для управления крупномасштабными изменениями. Процесс такой:

1. **Автор изменения пишет спецификацию** трансформации: какой паттерн искать, на что заменять и каково ожидаемое изменение поведения (для чистых рефакторингов — обычно «никакое»).

2. **Автоматические инструменты генерируют изменения** по всему монорепозиторию. Это могут быть десятки тысяч файлов.

3. **Изменения автоматически шардируются** на куски, пригодные для ревью. Каждый шард достаточно мал, чтобы человек мог его осмысленно проверить, — обычно 100–500 файлов.

4. **Каждый шард уходит соответствующим владельцам кода** на ревью. Ревьюеру не нужно понимать всё изменение целиком — достаточно убедиться, что трансформация правильно применена к его коду.

5. **Одобренные шарды сливаются постепенно.** Система отслеживает, какие шарды одобрены, какие ждут, а какие отклонены (требуя ручного вмешательства).

Ключевое наблюдение: Google не рассматривает крупный рефакторинг как одно гигантское изменение. Это тысячи маленьких изменений, соответствующих спецификации, которые можно ревьюить и сливать независимо.

### Что из этого можно взять

Даже если вы работаете не в масштабе Google, принципы применимы:

```markdown
## Large-Scale Change Principles (Adapted for SDD)

1. **Spec the transformation, not the result.**
   Do not describe what every file should look like after.
   Describe the RULE for transforming any file that matches the pattern.

2. **Automate the application.**
   If you can describe the transformation precisely enough to spec it,
   you can describe it precisely enough to automate it.

3. **Shard the review.**
   No human should have to review more than they can hold in their head.
   Break changes into logical, reviewable chunks.

4. **Track progress mechanically.**
   Do not rely on status meetings to know where you are.
   Build dashboards that show transformation progress in real time.

5. **Allow partial completion.**
   The system must be functional at every intermediate state.
   If you can only complete 60% of the migration this quarter,
   the 60% that is done must work alongside the 40% that is not.
```

### Масштаб Google в вашей спецификации рефакторинга

```typescript
// Define the transformation rule, not the individual changes
interface TransformationRule {
  name: string;
  description: string;

  // Pattern to match in existing code
  match: {
    fileGlob: string;
    codePattern: RegExp;
    astPattern?: string; // For AST-based matching
  };

  // Transformation to apply
  transform: {
    type: 'replace' | 'wrap' | 'extract' | 'inline';
    template: string;
    preserveComments: boolean;
    preserveFormatting: boolean;
  };

  // Validation after transformation
  validate: {
    mustCompile: boolean;
    mustPassTests: boolean;
    customChecks: string[];
  };
}

// Example: migrate Express route handlers to NestJS controllers
const expressToNestMigration: TransformationRule = {
  name: 'express-route-to-nest-controller',
  description: 'Convert Express router.get/post/etc to NestJS @Get/@Post decorators',

  match: {
    fileGlob: 'src/routes/**/*.ts',
    codePattern: /router\.(get|post|put|delete|patch)\(['"]([^'"]+)['"]/,
  },

  transform: {
    type: 'replace',
    template: `
      @{{METHOD}}('{{PATH}}')
      async {{HANDLER_NAME}}(
        @Req() req: Request,
        @Res() res: Response,
      ): Promise<void> {
        {{BODY}}
      }
    `,
    preserveComments: true,
    preserveFormatting: false, // NestJS has different conventions
  },

  validate: {
    mustCompile: true,
    mustPassTests: true,
    customChecks: [
      'no-express-imports-in-controllers',
      'all-routes-have-decorators',
      'response-types-are-explicit',
    ],
  },
};
```

---

## 1.8 Как Anthropic подходит к итеративным улучшениям

Подход Anthropic к итерациям в кодовой базе Claude даёт другой взгляд на дисциплину рефакторинга. Если Google делает акцент на масштабе и автоматизации, Anthropic — на безопасности и тщательной оценке на каждом шаге.

Когда Anthropic перерабатывает компонент системы Claude — конвейер обучения, фреймворк оценки или инфраструктуру обслуживания, — они следуют схеме, близкой к принципам SDD:

1. **Зафиксировать поведенческую базовую линию.** Прежде чем что-то менять, исчерпывающе зафиксируйте текущее поведение системы. Для Claude это прогон обширных наборов оценок, измеряющих не только точность, но и безопасность, полезность и честность на тысячах тест-кейсов.

2. **Специфицировать изменение с явными ограничениями безопасности.** В каждой спецификации описано не только что должно улучшиться, но и что не имеет права ухудшиться. Спецификация задаёт допустимый разброс для любой метрики.

3. **Реализовать за фича-флагами.** Изменения выкатываются, но не включаются. Старый и новый пути кода существуют одновременно.

4. **Постепенная выкатка с непрерывной оценкой.** Трафик переключается инкрементально — 1%, 5%, 10%, 25%, 50%, 100% — с оценкой на каждом шаге. Любая регрессия вызывает автоматический откат.

5. **Оценка после миграции.** После полной выкатки старый путь кода остаётся доступным ещё 30 дней, прежде чем его удалят.

Эта схема напрямую ложится на наш подход с «фикусом-душителем», добавляя строгие шлюзы оценки на каждом этапе.

### Спецификация рефакторинга с учётом безопасности

Вдохновляясь подходом Anthropic, включайте в спецификацию рефакторинга критерии оценки для каждой фазы:

```markdown
## Phase 2 Spec: User List Endpoint Migration

### Evaluation Gates

#### Gate 1: Unit Test Parity
- All existing unit tests pass against new implementation
- New implementation has >= 90% code coverage
- MUST PASS before proceeding to Gate 2

#### Gate 2: Integration Test Parity
- All existing integration tests pass
- New tests added for previously untested edge cases
- Response shape validation: v2 output matches v1 output exactly
- MUST PASS before proceeding to Gate 3

#### Gate 3: Performance Benchmarking
- p50 latency: must be <= v1 p50 (currently 120ms)
- p99 latency: must be <= v1 p99 (currently 890ms)
- Throughput: must handle >= v1 peak load (currently 450 req/s)
- MUST PASS before proceeding to Gate 4

#### Gate 4: Shadow Traffic Validation
- Run new implementation in shadow mode for 48 hours
- Compare responses with v1 for every request
- Discrepancy rate must be < 0.01%
- MUST PASS before proceeding to production cutover

#### Gate 5: Production Canary
- Route 5% of production traffic to v2
- Monitor error rates, latency, and business metrics for 24 hours
- No alerts triggered
- MUST PASS before full rollout
```

---

## 1.9 Паттерны «заморозить и заменить» и «инкрементальная миграция»

Есть два принципиально разных подхода к спецификации рефакторинга, и неверный выбор может погубить проект ещё до старта.

### Паттерн 1: заморозить и заменить

При этом паттерне вы замораживаете старую систему (никаких новых функций), параллельно строите новую и в назначенную дату переключаетесь.

```markdown
## Freeze and Replace Spec

### Phase 1: Feature Freeze (2 weeks)
- No new features added to v1
- Bug fixes only, with approval
- Complete archaeology and reverse spec

### Phase 2: Parallel Build (6 weeks)
- Build v2 from target spec
- v1 continues serving production traffic
- v2 tested against v1 behavioral baseline

### Phase 3: Cutover (1 week)
- Switch production traffic from v1 to v2
- v1 remains on standby for rollback
- 24/7 monitoring during transition

### Phase 4: Decommission (2 weeks)
- Remove v1 after 14 days with zero rollbacks
- Archive v1 code
- Update all documentation
```

**Когда использовать «заморозить и заменить»:**
- Старая система настолько запутана, что инкрементальные изменения невозможны
- Нужен чистый разрыв с легаси-технологией
- У команды есть ресурс на отдельный спринт миграции
- Допустимы простой или заморозка функций

**Когда НЕ использовать «заморозить и заменить»:**
- Система должна продолжать развиваться во время миграции
- Заинтересованные стороны не примут заморозку функций
- Старая система слишком велика для одномоментной замены
- Вы не можете позволить риск развёртывания «большим взрывом»

### Паттерн 2: инкрементальная миграция

При этом паттерне вы мигрируете по частям, и старая и новая системы сосуществуют всё время.

```markdown
## Incremental Migration Spec

### Principles
- Both v1 and v2 code coexist in the same deployment
- Each migration step is independently deployable and reversible
- New features are built against v2 specs
- v1 features are migrated on a prioritized schedule

### Migration Queue (Priority Order)
1. User CRUD endpoints (highest traffic, most bugs)
2. Search functionality (security concerns with raw SQL)
3. Admin endpoints (high business impact)
4. Reporting endpoints (low traffic, low risk)
5. Legacy webhook handlers (need consumer coordination)

### Per-Item Migration Process
For each item in the migration queue:
1. Write target spec for this component
2. Implement v2 version behind feature flag
3. Run shadow traffic comparison for 48 hours
4. Gradual rollout: 5% → 25% → 50% → 100%
5. Monitor for 7 days at 100%
6. Remove v1 code path
```

**Когда использовать инкрементальную миграцию:**
- Система должна продолжать принимать новые функции
- Толерантность к риску низкая (финансовые системы, медицина и т. п.)
- Миграция занимает несколько кварталов
- Несколько команд должны координироваться

> **Заметка профессора:** По моему опыту, инкрементальная миграция — правильный выбор примерно в 80% случаев. «Заморозить и заменить» выглядит чище, и инженеры её любят, потому что можно начать с чистого листа. Но бизнес-заказчики редко соглашаются на заморозку функций, а переключение «большим взрывом» — то место, где большинство таких проектов проваливается. «Фикус-душитель» — ваш друг. Полюбите его.

---

## 1.10 Практический разбор: грязный Express.js API — в чистую архитектуру NestJS

Пройдём полную спецификацию рефакторинга — от археологии до плана выполнения. Это документ, который вы бы подготовили в реальной работе.

### Сценарий

Вам достался трёхлетний Express.js API интернет-магазина. В нём 47 эндпоинтов, нет единой обработки ошибок, смесь колбэков и промисов и три разных подхода к доступу к базе. Задача: перейти на NestJS с ORM Prisma, ничего не сломав.

### Шаг 1: отчёт об археологии (сокращённо)

```markdown
# Archaeology Report: E-Commerce API

## Structure
- 23 route files in src/routes/
- 8 "service" files (really just utility functions)
- 4 database access patterns:
  1. Raw pg queries (oldest endpoints)
  2. Knex query builder (mid-era endpoints)
  3. Sequelize ORM (newest endpoints, poorly configured)
  4. Direct SQL strings in route handlers (worst offenders)

## Traffic Analysis (14-day sample)
- Total endpoints: 47
- Active endpoints (>1 req/day): 31
- High-traffic endpoints (>1000 req/day): 8
- Zero-traffic endpoints: 9 (candidates for removal)

## Critical Findings
- No request validation on 38 of 47 endpoints
- SQL injection possible on 6 endpoints (raw SQL with string concat)
- No rate limiting anywhere
- Authentication middleware inconsistently applied
- 3 endpoints have hardcoded database credentials (!!!)
```

### Шаг 2: обратная спецификация (ключевые эндпоинты)

```typescript
// reverse-spec: what the product endpoint actually does today
interface ProductEndpointCurrentBehavior {
  /**
   * GET /products
   * @quirk Returns max 1000 products, no pagination support
   * @quirk Includes soft-deleted products if no filter specified
   * @quirk Price is returned as string, not number
   * @quirk Images array sometimes null, sometimes empty array
   */
  listProducts(): Promise<{
    products: Array<{
      id: number;          // Auto-increment integer
      name: string;
      price: string;       // "19.99" — string, not number
      category: string;    // Free text, no enum
      images: string[] | null;  // Inconsistent nullability
      deleted: boolean;    // Soft delete flag, exposed to clients
      created_at: string;  // ISO string
    }>;
  }>;
}
```

### Шаг 3: целевая спецификация

```typescript
// target-spec: what the product endpoint should do after migration
interface ProductEndpointTargetBehavior {
  /**
   * GET /api/v2/products
   * @spec Paginated product listing with filtering
   * @validation All query params validated by class-validator
   * @performance Response time p99 < 150ms
   */
  listProducts(params: {
    page: number;           // Required, >= 1
    limit: number;          // Required, 1-100
    category?: ProductCategory;  // Enum, validated
    minPrice?: number;      // Decimal, >= 0
    maxPrice?: number;      // Decimal, >= minPrice
    sortBy?: 'price' | 'name' | 'created';
    sortOrder?: 'asc' | 'desc';
  }): Promise<{
    data: ProductDTO[];
    pagination: {
      page: number;
      limit: number;
      total: number;
      totalPages: number;
    };
  }>;
}

// Clean DTO — no internal fields exposed
interface ProductDTO {
  id: string;              // UUID, not auto-increment
  name: string;
  price: number;           // Number, not string
  category: ProductCategory;
  images: string[];        // Always array, never null
  createdAt: string;       // ISO 8601
  updatedAt: string;       // ISO 8601
}

enum ProductCategory {
  ELECTRONICS = 'electronics',
  CLOTHING = 'clothing',
  HOME = 'home',
  SPORTS = 'sports',
  BOOKS = 'books',
}
```

### Шаг 4: спецификация миграции

```markdown
# Refactor Spec: E-Commerce API Migration
# Express.js → NestJS + Prisma

## Metadata
- **Author:** [Your Name]
- **Status:** Draft
- **Created:** 2026-02-24
- **Target Completion:** 2026-05-15
- **Reviewers:** [Tech Lead], [Product Owner], [SRE Lead]

## Executive Summary
Migrate the e-commerce API from Express.js to NestJS with Prisma ORM.
The migration will be incremental, using the Strangler Fig pattern over
12 weeks. Zero downtime. Zero breaking changes for existing clients.

## Phases

### Phase 1: Foundation (Week 1-2)
**Deliverables:**
- NestJS application scaffold
- Prisma schema matching existing database
- Proxy controller forwarding all traffic to Express
- CI/CD pipeline for new NestJS app
- Health check and monitoring integration

**Spec for AI Agent:**
```text
CONTEXT: We have an existing Express.js e-commerce API. We are
beginning a migration to NestJS. In this phase, you will create
the NestJS scaffold ONLY.

OBJECTIVE: Create a NestJS application that:
1. Starts on port 3001 (Express runs on 3000)
2. Proxies ALL incoming requests to http://localhost:3000
3. Logs every proxied request (method, path, status, latency)
4. Has a /health endpoint that checks both NestJS and Express

CONSTRAINTS:
- Do NOT implement any business logic
- Do NOT create any database connections
- Do NOT modify the existing Express application
- Use axios for proxying
- Use @nestjs/config for configuration
- Use @nestjs/terminus for health checks

TEST REQUIREMENTS:
- Unit test the proxy controller
- Integration test: request to NestJS returns same response as
  direct request to Express (for 10 sample endpoints)
- Health check test: returns healthy when Express is up,
  unhealthy when Express is down
```

### Phase 2: Data Layer (Week 3-4)
**Deliverables:**
- Prisma schema with all models
- Prisma client configured in NestJS
- Database migration scripts (Prisma Migrate)
- Seed data for testing

**Spec for AI Agent:**
```text
CONTEXT: NestJS proxy is running. Express handles all business
logic. We need to set up the Prisma data layer.

OBJECTIVE: Create Prisma schema matching the existing PostgreSQL
database. Generate Prisma client. Create NestJS database module.

CONSTRAINTS:
- Schema must match existing tables EXACTLY
  (we are NOT changing the database schema yet)
- Use Prisma introspection: npx prisma db pull
- Clean up introspected schema (add proper types, relations)
- Do NOT run any Prisma migrations against production
- Configure separate database URLs for dev/staging/prod
- Create a DatabaseModule that provides PrismaService

REFERENCE: See archaeology report section "Database Schema"
for current table definitions and relationships.

TEST REQUIREMENTS:
- PrismaService connects successfully
- All models queryable
- Relation traversals work correctly
- Connection pooling configured (min: 5, max: 20)
```

### Phase 3: Product Endpoints (Week 5-6)
[Detailed spec for migrating the 8 product-related endpoints]

### Phase 4: User Endpoints (Week 7-8)
[Detailed spec for migrating the 12 user-related endpoints]

### Phase 5: Order Endpoints (Week 9-10)
[Detailed spec for migrating the 11 order-related endpoints]

### Phase 6: Cleanup and Decommission (Week 11-12)
[Spec for removing Express, cleaning up proxies, final testing]
```

### Шаг 5: план миграции тестов

```markdown
## Test Migration Plan

### Current Test State
- 127 unit tests (Jest) — 94% passing (8 known failures)
- 43 integration tests — 88% passing (5 flaky tests)
- 0 end-to-end tests
- No performance tests
- No contract tests

### Target Test State
- All existing passing tests migrated to NestJS testing framework
- 8 known failures fixed or documented as tech debt
- 5 flaky tests stabilized or replaced
- New E2E test suite using Supertest
- Performance benchmarks using k6
- Contract tests using Pact

### Migration Strategy
1. DO NOT delete any existing tests until v2 equivalents exist
2. Tests migrate WITH their corresponding endpoints
3. Each phase includes its own test deliverables
4. Shadow testing: run both v1 and v2 tests during migration
5. Test coverage must not decrease at any phase

### Per-Phase Test Requirements

#### Phase 1 Tests (Foundation)
- Proxy passthrough tests: verify request/response fidelity
- Health check tests: NestJS up/down, Express up/down scenarios
- Latency overhead tests: proxy adds < 10ms

#### Phase 2 Tests (Data Layer)
- Model relationship tests: all FK relations traversable
- Query performance tests: baseline measurements for comparison
- Connection pool tests: concurrent access patterns

#### Phase 3-5 Tests (Endpoint Migration)
For EACH migrated endpoint:
- [ ] Unit tests for controller
- [ ] Unit tests for service
- [ ] Unit tests for DTOs/validation
- [ ] Integration test: full request → response cycle
- [ ] Contract test: response matches API contract
- [ ] Performance test: meets latency SLA
- [ ] Shadow test: v2 response matches v1 response
```

---

## 1.11 Зависимости и побочные эффекты

Когда вы перерабатываете одну часть системы, остальные чувствуют толчок. Спецификация должна явно описать эти зависимости.

### Карта зависимостей

```typescript
// Formal dependency specification for the refactor
interface RefactorDependencyMap {
  // Components we are changing
  targets: {
    component: string;
    changeType: 'rewrite' | 'modify' | 'replace' | 'remove';
    affectedInterfaces: string[];
  }[];

  // Components that depend on what we are changing
  downstreamDependencies: {
    component: string;
    dependsOn: string;      // Which target
    interfaceUsed: string;  // Which interface
    impactAssessment: 'none' | 'minor' | 'major' | 'breaking';
    mitigationPlan: string;
  }[];

  // Components that our targets depend on
  upstreamDependencies: {
    component: string;
    usedBy: string;         // Which target
    changeRequired: boolean;
    changeDescription?: string;
  }[];
}

// Example for our e-commerce migration
const ecommerceDependencyMap: RefactorDependencyMap = {
  targets: [
    {
      component: 'ProductAPI',
      changeType: 'rewrite',
      affectedInterfaces: ['GET /products', 'GET /products/:id', 'POST /products'],
    },
  ],

  downstreamDependencies: [
    {
      component: 'Mobile App v2.1',
      dependsOn: 'ProductAPI',
      interfaceUsed: 'GET /products',
      impactAssessment: 'minor',
      mitigationPlan: 'v2 API returns superset of v1 fields. Mobile app ignores unknown fields.',
    },
    {
      component: 'Search Indexer',
      dependsOn: 'ProductAPI',
      interfaceUsed: 'GET /products (internal)',
      impactAssessment: 'major',
      mitigationPlan: 'Search indexer must be updated to use v2 pagination. Coordinate with Search team.',
    },
    {
      component: 'Analytics Pipeline',
      dependsOn: 'ProductAPI',
      interfaceUsed: 'Webhook: product.created',
      impactAssessment: 'none',
      mitigationPlan: 'Webhook payload unchanged in v2.',
    },
  ],

  upstreamDependencies: [
    {
      component: 'PostgreSQL Database',
      usedBy: 'ProductAPI',
      changeRequired: false,
      changeDescription: 'Schema unchanged. Only data access layer changes (raw SQL → Prisma).',
    },
    {
      component: 'Redis Cache',
      usedBy: 'ProductAPI',
      changeRequired: true,
      changeDescription: 'Cache key format changes from product:{id} to v2:product:{uuid}. Cache must be flushed during migration.',
    },
  ],
};
```

### Анализ побочных эффектов

```markdown
## Ripple Effect Analysis

### Direct Effects (Tier 1)
Components directly modified by this refactor:
- Product API: Rewritten in NestJS
- User API: Rewritten in NestJS
- Order API: Rewritten in NestJS

### Indirect Effects (Tier 2)
Components that must adapt to Tier 1 changes:
- Mobile App: Update API client for v2 endpoints
- Admin Dashboard: Update API calls (16 undocumented endpoints)
- Search Indexer: Update to use pagination
- Redis Cache: Flush and re-warm with new key format

### Tertiary Effects (Tier 3)
Components that might be affected by Tier 2 changes:
- CDN: Cache invalidation patterns may change
- Monitoring: Alert thresholds need recalibration for new latency baselines
- CI/CD: Pipeline needs NestJS build steps

### Coordination Requirements
| Team          | Coordination Need              | Timeline     |
|---------------|-------------------------------|--------------|
| Mobile        | v2 API client update          | Week 6-8     |
| Admin         | Dashboard API migration       | Week 8-10    |
| Search        | Indexer pagination support     | Week 5-6     |
| SRE           | Monitoring recalibration      | Week 1 + each phase |
| QA            | Regression testing per phase  | Continuous   |
```

---

## 1.12 Шлюз утверждения рефакторинга

Спецификация рефакторинга — не просто технический документ, а предложение. Её утверждают несколько заинтересованных сторон, каждая со своей точки зрения.

### Матрица утверждений

```markdown
## Approval Requirements

### Technical Lead — Architectural Review
- [ ] Target architecture is sound
- [ ] Migration path is feasible
- [ ] Risk assessment is comprehensive
- [ ] Testing plan is adequate
- [ ] Performance targets are realistic

### Product Owner — Business Impact Review
- [ ] Feature freeze duration is acceptable
- [ ] No customer-facing changes without communication plan
- [ ] Business metrics monitoring included
- [ ] Rollback plan protects revenue-critical paths

### SRE/DevOps Lead — Operational Review
- [ ] Deployment plan is sound
- [ ] Monitoring and alerting included
- [ ] Rollback procedures are tested
- [ ] Resource requirements (compute, memory) identified
- [ ] On-call procedures updated for migration period

### Security Lead — Security Review
- [ ] SQL injection vulnerabilities addressed in migration
- [ ] Authentication/authorization not weakened
- [ ] No new attack surface introduced
- [ ] Credentials properly managed (no hardcoded secrets)

### QA Lead — Quality Review
- [ ] Test migration plan is complete
- [ ] No test coverage regression
- [ ] Performance benchmarking plan included
- [ ] Regression test suite updated

## Approval Status
| Reviewer        | Status    | Date       | Notes           |
|----------------|-----------|------------|-----------------|
| Tech Lead      | PENDING   |            |                 |
| Product Owner  | PENDING   |            |                 |
| SRE Lead       | PENDING   |            |                 |
| Security Lead  | PENDING   |            |                 |
| QA Lead        | PENDING   |            |                 |

## Approval Rule
All five approvals required before Phase 1 begins.
Phase-level approvals required from Tech Lead and QA Lead only.
```

> **Заметка профессора:** Шлюз утверждения — не бюрократия. Это форсирующая функция, которая делает спецификацию полной. Если руководитель безопасности спрашивает «как вы закрываете уязвимости SQL-инъекций?», а в спецификации об этом ничего нет, значит спецификация неполна. Процесс утверждения делает её лучше.

---

## 1.13 Упражнение: проведите аудит легаси-кодовой базы и составьте приоритизированную спецификацию рефакторинга

### Задание

Вам дали доступ к легаси-приложению на Node.js — API управления задачами, написанному два года назад. Исходный разработчик уволился. Спецификаций нет, тестов минимум, а документация — один README, не обновлявшийся 18 месяцев.

**Часть 1: археология (оценка: 2 часа)**

1. Склонируйте репозиторий и запустите приложение локально
2. Постройте граф зависимостей
3. Составьте каталог всех эндпоинтов (документированных и нет)
4. Прогоните набор тестов и зафиксируйте результаты
5. Определите все паттерны доступа к базе данных
6. Изучите историю git на предмет значимых изменений
7. Подготовьте отчёт об археологии по шаблону из раздела 1.2.2

**Часть 2: обратная спецификация (оценка: 2 часа)**

1. Для каждого найденного эндпоинта напишите обратную спецификацию текущего поведения
2. Опишите все особенности, баги и недокументированное поведение
3. Определите неявные контракты с нижестоящими потребителями
4. Составьте карту всех побочных эффектов (письма, вебхуки, записи в кеш и т. п.)

**Часть 3: целевая спецификация (оценка: 3 часа)**

1. Спроектируйте целевую архитектуру (фреймворк на ваш выбор)
2. Напишите целевые спецификации для всех эндпоинтов
3. Определите улучшения модели данных
4. Задайте правила валидации
5. Определите цели по производительности

**Часть 4: план миграции (оценка: 3 часа)**

1. Выберите стратегию миграции («заморозить и заменить» или инкрементальную)
2. Определите фазы с чёткими результатами
3. Напишите готовые для ИИ спецификации минимум для двух фаз
4. Составьте план миграции тестов
5. Опишите зависимости и побочные эффекты
6. Определите шлюзы утверждения

**Часть 5: оценка рисков (оценка: 1 час)**

1. Выявите минимум 5 рисков
2. Для каждого: вероятность, влияние, смягчение и запасной план
3. Определите мониторинг и алерты для каждого риска

### Критерии сдачи

Ваша спецификация рефакторинга должна быть одним Markdown-документом, который другой инженер (или ИИ-агент) мог бы взять и выполнить, не задавая вам вопросов. Каждое решение должно быть обосновано. Каждое ограничение — явным. У каждого риска должен быть план смягчения.

```markdown
# Evaluation Rubric

## Archaeology (20 points)
- Complete structural analysis ............ 5 pts
- Behavioral analysis with evidence ....... 5 pts
- Contract identification ................. 5 pts
- Historical context ...................... 5 pts

## Reverse Spec (20 points)
- All endpoints documented ................ 5 pts
- Quirks and bugs identified .............. 5 pts
- Implicit contracts mapped ............... 5 pts
- Side effects cataloged .................. 5 pts

## Target Spec (20 points)
- Clean architecture design ............... 5 pts
- Complete endpoint specifications ........ 5 pts
- Validation and security rules ........... 5 pts
- Performance targets defined ............. 5 pts

## Migration Plan (25 points)
- Strategy choice justified ............... 5 pts
- Phases well-defined .................... 5 pts
- AI-ready spec quality .................. 5 pts
- Test migration plan .................... 5 pts
- Dependency mapping ..................... 5 pts

## Risk Assessment (15 points)
- Risk identification .................... 5 pts
- Mitigation strategies .................. 5 pts
- Monitoring and alerting ................ 5 pts
```

---

## Итоги главы

Спецификация рефакторинга — пожалуй, самый сложный тип спецификации, потому что требует понимать две системы сразу: ту, что существует, и ту, что вы хотите создать. Техники из этой главы — фаза археологии, обратная спецификация, матрица объёма, паттерн «фикус-душитель» и реестр рисков — дают системный подход к задаче, которая иначе кажется неподъёмной.

Помните главный принцип: **пойми, прежде чем специфицировать; специфицируй, прежде чем менять; меняй инкрементально, с валидацией на каждом шаге.**

В следующей главе разберём, как спецификации выполняют двойную работу — служат документацией, устраняя вечную проблему документации, которая всегда устарела. Если спецификация — единственный источник истины, а документация генерируется из неё, то документация всегда актуальна. Это не просто удобно — это меняет правила игры.

> *«Лучший рефакторинг — тот, после которого никто не заметил, что что-то изменилось. Система просто стала быстрее, надёжнее и удобнее, а пользователи так и не узнали. Вот в чём сила хорошо исполненной спецификации рефакторинга».*

---

**Следующая глава:** Документация как код — как спецификации устраняют проблему «документация всегда устарела»

---
