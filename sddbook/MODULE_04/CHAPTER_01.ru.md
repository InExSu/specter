# Глава 1: Мультиагентный рабочий процесс

## МОДУЛЬ 04 — Продвинутая оркестрация и агенты (продвинутый уровень)

> [Оглавление курса](../INDEX.ru.md) · [Модуль 04](../INDEX.ru.md#модуль-04--продвинутая-оркестрация-и-агенты)

---

### Вступление к лекции

*С возвращением. Если вы добрались до этого места курса, основы у вас уже в крови: что такое спецификация, почему она важна и как написать такую, которую ИИ-агент сможет использовать, не нагаллюцинировав себе проблем. Вы научились думать контрактами, отделять замысел от реализации и относиться к спецификации как к единственному источнику истины.*

*Теперь мы входим на территорию, где становится по-настоящему интересно — и, буду честен, по-настоящему сложно. Сегодня поговорим о том, что происходит, когда вы перестаёте думать об «ИИ-агенте» как об одной сущности и начинаете думать о нём как о команде. Команде специализированных агентов, у каждого своя роль, свои ограничения, и все они координируются спецификацией, которую пишете вы.*

*Это не научная фантастика. Так прямо сейчас, в 2026 году, работают самые продвинутые процессы разработки с ИИ. Claude Code от Anthropic порождает субагентов через инструмент Task. AutoGen от Microsoft оркестрирует многоагентные диалоги. Конвейеры Gemini от Google выстраивают шаги рассуждения через специализированные модули. Агентные фреймворки OpenAI собирают агентов, использующих инструменты, в рабочие процессы. Системы Meta на базе Llama разворачиваются в открытых многоагентных конфигурациях в тысячах организаций.*

*Но вот чего большинство упускает: ни одна из этих многоагентных систем не работает надёжно без спецификации, управляющей координацией. Спецификация — не просто входные данные для одного агента, это общий контракт, связывающий их всех. Сегодня мы разберём, как именно это устроено.*

---

## 1.1 Паттерн трёх агентов: архитектор, разработчик, критик

Начнём с базового паттерна. В разработке через спецификации самый эффективный многоагентный процесс раскладывает разработку на три отчётливые роли:

| Агент | Роль | Аналогия | Основной вход | Основной выход |
|-------|------|---------|---------------|----------------|
| **Агент-архитектор** | Пишет и уточняет спецификацию | Продакт-менеджер / техлид | Требования, ограничения, контекст | Полная проверенная спецификация |
| **Агент-разработчик** | Превращает спецификацию в работающий код | Разработчик ПО | Спецификация | Код, тесты, артефакты |
| **Агент-критик** | Проверяет код на соответствие спецификации | QA-инженер / ревьюер кода | Спецификация + код | Отчёт о валидации, список замечаний |

Это не произвольное разложение. Оно отражает фундаментальное напряжение всей разработки ПО: те, кто решает, *что* строить, не должны быть теми, кто решает, *как* строить, и ни одна из этих групп не должна судить, правильно ли построено.

> **Заметка профессора:** Если вы когда-нибудь работали в компании, где разработчик пишет код, пишет тесты, а потом сам же одобряет свой пул-реквест, — вы точно знаете, почему разделение ответственности так важно. Паттерн трёх агентов обеспечивает это разделение структурно, а не культурно.

Вот паттерн в виде схемы потока:

```
                    Requirements / User Story
                            |
                            v
                  +-------------------+
                  |  ARCHITECT AGENT  |
                  |  (Spec Writer)    |
                  +-------------------+
                            |
                       [THE SPEC]
                            |
                            v
                  +-------------------+
                  |   BUILDER AGENT   |
                  |  (Code Generator) |
                  +-------------------+
                            |
                    [CODE + TESTS]
                            |
                            v
                  +-------------------+
                  |   CRITIC AGENT    |
                  |  (Validator)      |
                  +-------------------+
                            |
                     [VALIDATION REPORT]
                            |
                    +-------+-------+
                    |               |
                    v               v
                 PASS            FAIL
                  |               |
                  v               v
               DEPLOY    Back to ARCHITECT
                         (with issue details)
```

Обратите внимание на критичную деталь схемы: найдя проблемы, критик возвращает их **архитектору**, а не разработчику. Это одно из важнейших проектных решений всего паттерна, и почему так — разберём дальше в этой главе.

---

## 1.2 Агент-архитектор: пишет и уточняет спецификацию

Агент-архитектор берёт размытые, неполные или высокоуровневые требования и превращает их в точную, однозначную спецификацию, которую может выполнить агент-разработчик.

### Что делает агент-архитектор

1. **Интерпретирует требования** — берёт пользовательские истории на естественном языке, запросы на функции или баг-репорты и извлекает суть замысла.
2. **Устраняет неоднозначность** — находит места, где требования неясны, и либо задаёт уточняющие вопросы, либо принимает явные решения.
3. **Структурирует спецификацию** — выдаёт её в согласованном машиночитаемом формате по схеме спецификаций проекта.
4. **Проверяет полноту** — следит, чтобы спецификация покрывала всё нужное: входы, выходы, ограничения, крайние случаи, обработку ошибок.
5. **Уточняет итеративно** — когда критик сообщает о проблемах, архитектор обновляет спецификацию, чтобы их закрыть.

### Возможности агента-архитектора

Агенту-архитектору нужен доступ к:

- **Существующей кодовой базе проекта** (только чтение) — чтобы понимать текущую архитектуру и соглашения
- **Существующим спецификациям** — чтобы обеспечить согласованность и избежать противоречий
- **Схеме или шаблону спецификаций** — чтобы выдавать спецификации в ожидаемом формате
- **Знанию предметной области** — контексту о бизнес-домене, контрактах API и т. п.

### Ограничения агента-архитектора

Не менее важно то, чего агент-архитектор делать **не** должен:

- **Не должен писать код** — его результат — спецификации, никогда не реализация
- **Не должен принимать решения о реализации** — он задаёт *что*, но никогда *как*
- **Не должен обходить схему** — каждая спецификация должна соответствовать согласованному формату
- **Не должен игнорировать критика** — когда приходят замечания, спецификация должна быть обновлена

Вот конкретный пример системного промпта агента-архитектора:

```markdown
# Architect Agent System Prompt

You are the Architect Agent in a Spec-Driven Development pipeline.

## Your Role
You transform requirements into precise, actionable specifications.

## Your Constraints
- You MUST output specs in the project's YAML spec format
- You MUST NOT include implementation code in specs
- You MUST ensure every spec includes: purpose, inputs, outputs,
  constraints, error cases, and acceptance criteria
- You MUST reference existing specs when your new spec interacts
  with existing functionality
- You MUST flag any ambiguity you cannot resolve as an
  "OPEN_QUESTION" in the spec

## Your Inputs
- User requirements (natural language)
- Existing project specs (YAML files)
- Project architecture context (read-only codebase access)

## Your Output Format
A single YAML spec file following the project schema.

## When You Receive Critic Feedback
- Address every issue raised by the Critic
- Update the spec, do not argue with the Critic
- If a Critic issue reveals a fundamental requirements problem,
  flag it as REQUIRES_HUMAN_INPUT
```

### Реальный результат работы агента-архитектора

Для требования *«Пользователи должны иметь возможность выгружать данные дашборда в CSV-файл»* агент-архитектор может выдать:

```yaml
# spec/features/dashboard-csv-export.spec.yaml
spec_version: "1.0.0"
feature: "dashboard-csv-export"
status: "draft"
created: "2026-02-24"
author: "architect-agent"

purpose: |
  Allow authenticated users to export the data currently displayed
  on their dashboard as a downloadable CSV file. The export should
  reflect the current filter and date range selections.

inputs:
  - name: "user_session"
    type: "AuthenticatedSession"
    required: true
    description: "The user must be authenticated with a valid session"
  - name: "dashboard_filters"
    type: "DashboardFilterState"
    required: true
    description: "Current filter state including date range, category, and search terms"

outputs:
  - name: "csv_file"
    type: "File"
    format: "text/csv"
    encoding: "UTF-8"
    description: "A CSV file containing the filtered dashboard data"
    properties:
      filename_pattern: "dashboard-export-{date}-{timestamp}.csv"
      headers: "First row must contain column headers matching display names"
      max_rows: 50000
      delimiter: ","
      quoting: "Fields containing commas or newlines must be quoted"

constraints:
  - "Export must respect current RBAC permissions -- users only export data they can see"
  - "Maximum export size: 50,000 rows"
  - "Export must complete within 30 seconds or return a timeout error"
  - "CSV must be valid per RFC 4180"
  - "Date fields must be formatted as ISO 8601"
  - "Numeric fields must not include locale-specific formatting (no commas in numbers)"

error_cases:
  - condition: "User session expired during export"
    behavior: "Return 401 with message 'Session expired. Please log in again.'"
  - condition: "Export exceeds 50,000 rows"
    behavior: "Return 413 with message 'Export too large. Please narrow your filters.'"
  - condition: "Export times out (>30s)"
    behavior: "Return 504 with message 'Export timed out. Please try a smaller date range.'"
  - condition: "No data matches current filters"
    behavior: "Return CSV with headers only and 200 status"

acceptance_criteria:
  - "Given a user with 100 dashboard records and no filters, when they click Export, then a CSV with 101 rows (1 header + 100 data) downloads"
  - "Given a user with date filter set to 'Last 7 days', when they export, the CSV contains only records from the last 7 days"
  - "Given a user without admin role, when they export, the CSV does not contain admin-only columns"
  - "Given an export of 50,001 rows, the system returns a 413 error before generating the file"

dependencies:
  - spec: "auth/session-management.spec.yaml"
    reason: "Requires authenticated session validation"
  - spec: "dashboard/filter-state.spec.yaml"
    reason: "Consumes the current filter state"

open_questions: []
```

> **Заметка профессора:** Посмотрите, сколько деталей в этой спецификации. Агент-архитектор не просто сказал «выгрузка в CSV». Он задал кодировку, поведение разделителя, максимальное число строк, тексты ошибок и точные условия, при которых каждая ошибка срабатывает. Именно такая точность делает работу агента-разработчика прямолинейной, а не догадками.

---

## 1.3 Агент-разработчик: добросовестный исполнитель контракта

У агента-разработчика одна работа: взять спецификацию и написать код, который её удовлетворяет. Звучит просто. Это не просто.

### Как разработчик сохраняет верность контракту

Отношения агента-разработчика со спецификацией — это **строгое соответствие**, а не творческая интерпретация. Вот принципы:

**1. Спецификация — полная истина.**
Разработчик не добавляет функций, о которых спецификация не просила. Если спецификация говорит «возвращать ошибку 413, когда строк больше 50 000», разработчик не добавляет ещё и предупреждение на 40 000 строках — даже если это кажется хорошей идеей.

**2. Неоднозначность — блокер, а не приглашение.**
Когда спецификация неясна, разработчик не гадает. Он возвращает архитектору структурированный отчёт об ошибке с указанием того, что именно неоднозначно.

**3. Решения о реализации — за разработчиком.**
Спецификация задаёт *что*, разработчик решает *как*. Спецификация говорит «выгрузка должна завершаться за 30 секунд». Разработчик решает, использовать ли стриминг, пагинацию, фоновую задачу с опросом или иной подход.

**4. Генерация тестов — часть разработки.**
Разработчик создаёт тесты, напрямую отображающиеся в критерии приёмки спецификации. Каждый критерий приёмки становится как минимум одним тестом.

Вот системный промпт агента-разработчика:

```markdown
# Builder Agent System Prompt

You are the Builder Agent in a Spec-Driven Development pipeline.

## Your Role
You transform specifications into working, tested code.

## Your Constraints
- You MUST implement every requirement in the spec
- You MUST NOT add functionality not specified in the spec
- You MUST generate tests for every acceptance criterion
- You MUST follow the project's coding conventions and patterns
- You MUST report any spec ambiguity rather than guessing

## Your Inputs
- A validated spec (YAML)
- Project codebase (read/write access)
- Project coding conventions document

## Your Outputs
- Implementation code
- Test code (unit + integration as appropriate)
- A build report listing:
  - Files created/modified
  - Spec requirements addressed (by ID)
  - Any spec ambiguities encountered

## When You Encounter Ambiguity
- DO NOT guess or make assumptions
- Output an AMBIGUITY_REPORT with:
  - The ambiguous spec section
  - What is unclear
  - Two or more possible interpretations
  - Your recommended interpretation (but do not act on it)
```

### Результат работы агента-разработчика: реализация

По спецификации выгрузки CSV выше агент-разработчик может выдать:

```typescript
// src/features/dashboard-export/csv-export.service.ts

import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { DashboardDataService } from '../dashboard/dashboard-data.service';
import { AuthService } from '../auth/auth.service';
import { DashboardFilterState } from '../dashboard/types/filter-state';
import { stringify } from 'csv-stringify/sync';

/**
 * CSV Export Service
 *
 * Implements: spec/features/dashboard-csv-export.spec.yaml
 * Spec Version: 1.0.0
 */

const MAX_EXPORT_ROWS = 50_000;
const EXPORT_TIMEOUT_MS = 30_000;

interface CsvExportResult {
  filename: string;
  content: string;
  contentType: 'text/csv';
  encoding: 'UTF-8';
}

@Injectable()
export class CsvExportService {
  constructor(
    private readonly dashboardData: DashboardDataService,
    private readonly auth: AuthService,
  ) {}

  /**
   * Export dashboard data as CSV.
   *
   * Spec constraints:
   * - Respects RBAC permissions
   * - Max 50,000 rows
   * - 30-second timeout
   * - RFC 4180 compliant CSV
   * - ISO 8601 dates
   * - No locale-specific number formatting
   */
  async exportDashboardCsv(
    sessionId: string,
    filters: DashboardFilterState,
  ): Promise<CsvExportResult> {
    // Validate session (spec: error_cases[0])
    const session = await this.auth.validateSession(sessionId);
    if (!session.valid) {
      throw new HttpException(
        'Session expired. Please log in again.',
        HttpStatus.UNAUTHORIZED,
      );
    }

    // Fetch data with timeout (spec: constraints[2])
    const data = await this.fetchWithTimeout(
      () => this.dashboardData.getFilteredData(filters, session.user),
      EXPORT_TIMEOUT_MS,
    );

    // Check row limit (spec: error_cases[1])
    if (data.rows.length > MAX_EXPORT_ROWS) {
      throw new HttpException(
        'Export too large. Please narrow your filters.',
        HttpStatus.PAYLOAD_TOO_LARGE,
      );
    }

    // Get visible columns based on user role (spec: constraints[0])
    const visibleColumns = this.dashboardData.getColumnsForRole(
      session.user.role,
    );

    // Build CSV (spec: output properties)
    const headers = visibleColumns.map((col) => col.displayName);
    const rows = data.rows.map((row) =>
      visibleColumns.map((col) => this.formatCellValue(row[col.key], col.type)),
    );

    const csvContent = stringify([headers, ...rows], {
      delimiter: ',',        // spec: outputs[0].properties.delimiter
      quoted_string: true,   // spec: outputs[0].properties.quoting
    });

    const now = new Date();
    const dateStr = now.toISOString().split('T')[0];
    const timestampStr = now.getTime().toString();

    return {
      filename: `dashboard-export-${dateStr}-${timestampStr}.csv`,
      content: csvContent,
      contentType: 'text/csv',
      encoding: 'UTF-8',
    };
  }

  /**
   * Format cell value according to spec constraints:
   * - Dates: ISO 8601
   * - Numbers: no locale formatting
   */
  private formatCellValue(
    value: unknown,
    type: 'string' | 'number' | 'date' | 'boolean',
  ): string {
    if (value === null || value === undefined) return '';

    switch (type) {
      case 'date':
        // spec: constraints[4] - ISO 8601
        return value instanceof Date
          ? value.toISOString()
          : new Date(value as string).toISOString();
      case 'number':
        // spec: constraints[5] - no locale formatting
        return String(value);
      case 'boolean':
        return value ? 'true' : 'false';
      default:
        return String(value);
    }
  }

  private async fetchWithTimeout<T>(
    fn: () => Promise<T>,
    timeoutMs: number,
  ): Promise<T> {
    const timeoutPromise = new Promise<never>((_, reject) =>
      setTimeout(
        () =>
          reject(
            new HttpException(
              // spec: error_cases[2]
              'Export timed out. Please try a smaller date range.',
              HttpStatus.GATEWAY_TIMEOUT,
            ),
          ),
        timeoutMs,
      ),
    );

    return Promise.race([fn(), timeoutPromise]);
  }
}
```

И соответствующие тесты:

```typescript
// src/features/dashboard-export/__tests__/csv-export.service.spec.ts

import { CsvExportService } from '../csv-export.service';
import { DashboardDataService } from '../../dashboard/dashboard-data.service';
import { AuthService } from '../../auth/auth.service';

/**
 * Tests for: spec/features/dashboard-csv-export.spec.yaml
 * Each test maps to a specific acceptance criterion.
 */
describe('CsvExportService', () => {
  let service: CsvExportService;
  let mockDashboardData: jest.Mocked<DashboardDataService>;
  let mockAuth: jest.Mocked<AuthService>;

  beforeEach(() => {
    mockAuth = {
      validateSession: jest.fn().mockResolvedValue({
        valid: true,
        user: { id: 'user-1', role: 'member' },
      }),
    } as any;

    mockDashboardData = {
      getFilteredData: jest.fn(),
      getColumnsForRole: jest.fn().mockReturnValue([
        { key: 'name', displayName: 'Name', type: 'string' },
        { key: 'value', displayName: 'Value', type: 'number' },
        { key: 'created', displayName: 'Created', type: 'date' },
      ]),
    } as any;

    service = new CsvExportService(mockDashboardData, mockAuth);
  });

  // Acceptance Criterion 1:
  // "Given a user with 100 dashboard records and no filters,
  //  when they click Export, then a CSV with 101 rows downloads"
  it('should export 101 rows for 100 records (header + data)', async () => {
    const rows = Array.from({ length: 100 }, (_, i) => ({
      name: `Item ${i}`,
      value: i * 10,
      created: new Date('2026-01-15'),
    }));

    mockDashboardData.getFilteredData.mockResolvedValue({ rows });

    const result = await service.exportDashboardCsv('session-1', {});
    const lines = result.content.trim().split('\n');

    expect(lines).toHaveLength(101); // 1 header + 100 data rows
    expect(lines[0]).toContain('Name');
    expect(result.contentType).toBe('text/csv');
    expect(result.encoding).toBe('UTF-8');
  });

  // Acceptance Criterion 2:
  // "Given a user with date filter set to 'Last 7 days',
  //  when they export, the CSV contains only records from the last 7 days"
  it('should pass date filters to data service', async () => {
    const filters = { dateRange: 'last_7_days' };
    mockDashboardData.getFilteredData.mockResolvedValue({ rows: [] });

    await service.exportDashboardCsv('session-1', filters);

    expect(mockDashboardData.getFilteredData).toHaveBeenCalledWith(
      filters,
      expect.objectContaining({ id: 'user-1' }),
    );
  });

  // Acceptance Criterion 3:
  // "Given a user without admin role, when they export,
  //  the CSV does not contain admin-only columns"
  it('should filter columns based on user role', async () => {
    mockDashboardData.getFilteredData.mockResolvedValue({
      rows: [{ name: 'Test', value: 42, created: new Date() }],
    });

    await service.exportDashboardCsv('session-1', {});

    expect(mockDashboardData.getColumnsForRole).toHaveBeenCalledWith('member');
  });

  // Acceptance Criterion 4:
  // "Given an export of 50,001 rows, the system returns a 413 error
  //  before generating the file"
  it('should throw 413 when rows exceed 50,000', async () => {
    const rows = Array.from({ length: 50_001 }, (_, i) => ({
      name: `Item ${i}`,
      value: i,
      created: new Date(),
    }));

    mockDashboardData.getFilteredData.mockResolvedValue({ rows });

    await expect(
      service.exportDashboardCsv('session-1', {}),
    ).rejects.toThrow('Export too large. Please narrow your filters.');
  });

  // Error case: expired session
  it('should throw 401 when session is expired', async () => {
    mockAuth.validateSession.mockResolvedValue({ valid: false });

    await expect(
      service.exportDashboardCsv('invalid-session', {}),
    ).rejects.toThrow('Session expired. Please log in again.');
  });

  // Edge case: no data matches filters
  it('should return CSV with headers only when no data matches', async () => {
    mockDashboardData.getFilteredData.mockResolvedValue({ rows: [] });

    const result = await service.exportDashboardCsv('session-1', {});
    const lines = result.content.trim().split('\n');

    expect(lines).toHaveLength(1); // Headers only
    expect(lines[0]).toContain('Name');
  });
});
```

> **Заметка профессора:** Обратите внимание: у каждого теста есть комментарий со ссылкой на конкретный критерий приёмки, который он проверяет. Эта прослеживаемость от спецификации к коду и тестам — хребет SDD. Когда кто-то спрашивает «делает ли система X?», вы можете провести цепочку от требования спецификации к реализации и к тесту, который это доказывает.

---

## 1.4 Агент-критик: автоматический ревьюер

Агент-критик — пожалуй, самая недооценённая роль паттерна трёх агентов. Его работа — взять спецификацию и код, созданный разработчиком, и систематически проверить, что код удовлетворяет каждому требованию спецификации.

### Что проверяет агент-критик

Агент-критик выполняет несколько категорий проверок:

**Проверка полноты** — учтено ли в коде каждое требование спецификации?

```yaml
# Critic Agent completeness check output
completeness_report:
  spec: "dashboard-csv-export.spec.yaml"
  total_requirements: 14
  implemented: 13
  missing:
    - requirement: "constraints[3]: CSV must be valid per RFC 4180"
      status: "PARTIALLY_IMPLEMENTED"
      detail: |
        The code uses csv-stringify which handles most RFC 4180 cases,
        but does not explicitly handle the CRLF line ending requirement.
        RFC 4180 specifies CRLF, but csv-stringify defaults to LF on
        Linux systems.
      severity: "medium"
```

**Проверка корректности** — делает ли код именно то, что говорит спецификация, а не что-то незаметно иное?

```yaml
# Critic Agent correctness check output
correctness_report:
  issues:
    - location: "csv-export.service.ts:L85"
      spec_reference: "error_cases[1]"
      expected: "Return 413 BEFORE generating the file"
      actual: "Code fetches all data first, then checks count"
      severity: "high"
      detail: |
        The spec says to return the error before generating the file,
        implying a count check before full data retrieval. The current
        implementation loads all 50,001+ rows into memory before
        checking the count. This could cause OOM errors for very
        large datasets. Consider a COUNT query first.
```

**Проверка согласованности** — соответствует ли код паттернам и соглашениям проекта?

**Проверка покрытия тестами** — есть ли у каждого критерия приёмки соответствующий тест?

### Системный промпт агента-критика

```markdown
# Critic Agent System Prompt

You are the Critic Agent in a Spec-Driven Development pipeline.

## Your Role
You validate that code produced by the Builder Agent faithfully
implements the specification produced by the Architect Agent.

## Your Constraints
- You MUST check every requirement in the spec against the code
- You MUST NOT suggest new features not in the spec
- You MUST NOT rewrite code -- you report issues only
- You MUST categorize issues by severity: critical, high, medium, low
- You MUST provide specific file and line references for every issue
- You MUST verify test coverage for every acceptance criterion

## Your Inputs
- The specification (YAML)
- The implementation code
- The test code
- Project coding conventions

## Your Output Format
A structured validation report in YAML containing:
- completeness_report: requirements coverage
- correctness_report: behavioral accuracy
- consistency_report: convention adherence
- test_coverage_report: acceptance criteria coverage
- verdict: PASS | FAIL | PASS_WITH_WARNINGS
- issues: detailed list of all problems found

## Severity Definitions
- critical: The code contradicts the spec or has security implications
- high: A spec requirement is missing or incorrectly implemented
- medium: Implementation works but deviates from spec intent
- low: Style or convention issues that don't affect behavior
```

---

## 1.5 Соответствие реальным командам разработки

Паттерн трёх агентов — не изобретение эпохи ИИ. Это формализация ролей, которые существуют в командах разработки десятилетиями:

| Роль агента | Традиционная роль | Ответственность |
|-----------|-----------------|----------------|
| Агент-архитектор | Продакт-менеджер + техлид | Определяет, что строится, устраняет неоднозначность, поддерживает контракт |
| Агент-разработчик | Разработчик ПО | Реализует решение, принимает технические решения, пишет тесты |
| Агент-критик | QA-инженер + ревьюер кода | Проверяет корректность, полноту и качество |

Ключевое наблюдение: **когда эти роли занимают люди, коммуникация идёт с потерями.** Продакт-менеджер пишет тикет в Jira. Разработчик его интерпретирует. QA-инженер интерпретирует и тикет, и код. На каждой передаче информация теряется, появляются допущения и накапливается дрейф.

В многоагентном паттерне SDD спецификация устраняет этот дрейф, потому что она:
- **Машиночитаема** — никакой неоднозначности при разборе
- **Версионируема** — изменения отслеживаются
- **Полна** — покрывает входы, выходы, ограничения и ошибочные случаи
- **Общая** — все агенты читают один и тот же документ

> **Заметка профессора:** Я не предлагаю заменить человеческие команды ИИ-агентами. Я говорю о том, что *механизм координации* — спецификация — один и тот же, будь у вас три человека, три ИИ-агента или смесь. Спецификация — это протокол, а агенты (люди или машины) — участники.

---

## 1.6 Как Claude Code от Anthropic использует многоагентные паттерны

Посмотрим, как это работает на практике в компаниях, которые строят такие системы.

Claude Code от Anthropic (CLI-инструмент для разработки с ИИ) реализует многоагентный паттерн через **инструмент Task**. Столкнувшись со сложной задачей, Claude Code может породить субагентов для её специализированных частей.

### Паттерн инструмента Task

Концептуально это работает так:

```
Main Claude Code Session (Orchestrator)
    |
    |--- Task: "Analyze the existing codebase structure"
    |         (Sub-agent with read-only access)
    |         Returns: Architecture summary
    |
    |--- Task: "Generate implementation for the CSV export feature"
    |         (Sub-agent with write access, scoped to specific files)
    |         Returns: Code files
    |
    |--- Task: "Review the generated code against these requirements"
    |         (Sub-agent with read-only access to both spec and code)
    |         Returns: Review report
    |
    Main Session synthesizes results and presents to user
```

Это прямая реализация паттерна «архитектор — разработчик — критик». Главная сессия выступает оркестратором, а каждая задача — специализированный агент с:

- **Ограниченным контекстом** — каждый субагент видит только то, что ему нужно
- **Заданным результатом** — у каждого субагента есть ясный результат
- **Ограниченными полномочиями** — субагенты не могут выходить за рамки мандата

### Порождение команды

Claude Code также поддерживает то, что в Anthropic называют «порождением команды» (team spawning): агенты могут динамически создавать других агентов под нужды задачи. Например:

```
Architect Agent assesses a complex feature request
    |
    |--- Determines it needs 3 Builder Agents:
    |    |--- Builder 1: Frontend component
    |    |--- Builder 2: Backend API
    |    |--- Builder 3: Database migration
    |
    |--- Spawns 3 parallel Builder tasks
    |--- Collects results
    |--- Spawns Critic Agent to review all three
```

Ключевой фактор здесь — спецификация. Без структурированной спецификации оркестратор не имел бы надёжного способа разделить работу, а критик — эталона, по которому судить результаты.

> **Заметка профессора:** Когда вы используете инструмент Task в Claude Code, вы неявно применяете этот паттерн. Промпт для каждой задачи — по сути мини-спецификация. Чем лучше промпт, тем лучше результат. SDD просто формализует это в строгую практику.

---

## 1.7 Как Gemini от Google и AlphaCode от DeepMind подходят к многошаговой генерации кода

Google использует несколько иную архитектуру, но принцип тот же.

### Многошаговое рассуждение Gemini

Модели Gemini от Google — особенно встроенные в процессы разработки через инструменты вроде Project IDX и Gemini Code Assist — используют многошаговый подход:

1. **Шаг планирования** — модель строит план того, какой код нужно написать (аналог фазы архитектора)
2. **Шаг генерации** — модель выдаёт код (фаза разработчика)
3. **Шаг проверки** — модель сверяет собственный вывод с планом (фаза критика)

Интересно, что у Google эти «агенты» часто — одна и та же модель, последовательно выполняющая разные промпты, а не действительно разные модели. Спецификация (план) по-прежнему служит механизмом координации между шагами.

### AlphaCode от DeepMind и его потомки

Исследование AlphaCode от DeepMind показало мощную вариацию: **сгенерировать много кандидатов, затем выбрать лучший**. Процесс выглядит так:

```
Problem Specification
        |
        v
+------------------+
| GENERATOR        |    Produces 100-1000 candidate solutions
| (Many Builders)  |
+------------------+
        |
        v
+------------------+
| FILTER/SELECTOR  |    Eliminates solutions that fail tests
| (Critic)         |    Clusters remaining by behavior
+------------------+    Selects representative from best cluster
        |
        v
   Best Solution
```

Это паттерн «архитектор — разработчик — критик» в масштабе. Спецификация (постановка задачи + тест-кейсы) ведёт весь конвейер. «Архитектор» здесь неявный — это сама постановка задачи. «Разработчики» работают массово параллельно. «Критик» — фильтр, который использует тест-кейсы спецификации, чтобы выбрать лучший результат.

---

## 1.8 Агентные фреймворки OpenAI и оркестрация SDD

OpenAI активно вкладывается в агентные фреймворки, и их подход раскрывает важные проектные паттерны для SDD.

### Assistants API и вызов функций

Assistants API от OpenAI позволяет создавать агентов с:
- **инструкциями** (спецификация поведения агента)
- **инструментами** (возможности, которые агент может использовать)
- **файлами** (контекст, на который агент может ссылаться)

В конвейере SDD вы можете настроить три ассистента:

```python
# Setting up a 3-agent SDD pipeline with OpenAI Assistants API

import openai

client = openai.OpenAI()

# The Architect Agent
architect = client.beta.assistants.create(
    name="Architect Agent",
    instructions="""
    You are a specification writer. Given requirements, produce
    a detailed YAML specification following the provided schema.
    Never write implementation code. Focus on what, not how.
    """,
    model="gpt-4o",
    tools=[{"type": "file_search"}],  # Can search existing specs
)

# The Builder Agent
builder = client.beta.assistants.create(
    name="Builder Agent",
    instructions="""
    You are a code implementer. Given a YAML specification, produce
    working code that satisfies every requirement. Generate tests
    for every acceptance criterion. Report any spec ambiguities.
    """,
    model="gpt-4o",
    tools=[
        {"type": "code_interpreter"},  # Can run and test code
        {"type": "file_search"},       # Can search codebase
    ],
)

# The Critic Agent
critic = client.beta.assistants.create(
    name="Critic Agent",
    instructions="""
    You are a code reviewer. Given a specification and implementation,
    verify that every spec requirement is correctly implemented.
    Output a structured validation report. Never write code yourself.
    """,
    model="gpt-4o",
    tools=[{"type": "file_search"}],
)
```

### Фреймворк Swarm от OpenAI

Экспериментальный фреймворк Swarm от OpenAI использует более динамичный подход: агенты передают работу друг другу в зависимости от текущего состояния разговора. В контексте SDD:

```python
from swarm import Swarm, Agent

client = Swarm()

def hand_off_to_builder(spec_yaml: str):
    """Architect hands off the completed spec to the Builder."""
    return builder_agent

def hand_off_to_critic(code: str, spec: str):
    """Builder hands off completed code to the Critic."""
    return critic_agent

def hand_off_to_architect(issues: str):
    """Critic sends issues back to the Architect for spec revision."""
    return architect_agent

architect_agent = Agent(
    name="Architect",
    instructions="Write specs from requirements. When done, hand off to Builder.",
    functions=[hand_off_to_builder],
)

builder_agent = Agent(
    name="Builder",
    instructions="Implement code from specs. When done, hand off to Critic.",
    functions=[hand_off_to_critic],
)

critic_agent = Agent(
    name="Critic",
    instructions="Validate code against spec. If issues, hand off to Architect.",
    functions=[hand_off_to_architect],
)
```

---

## 1.9 Подход Meta: кодирующие агенты на базе Llama

Вклад Meta в многоагентную сцену значим из-за открытости Llama. Это значит, что любой может строить многоагентные конвейеры SDD, не завися от коммерческого API.

### Конфигурации агентов на базе Llama

Сообщество открытого ПО построило на моделях Llama несколько многоагентных фреймворков:

```python
# Simplified example of a Llama-based 3-agent pipeline
# using a local model server (e.g., vLLM, Ollama, or TGI)

import requests
from dataclasses import dataclass
from typing import Literal

LLAMA_API_BASE = "http://localhost:8000/v1"

@dataclass
class AgentConfig:
    name: str
    role: Literal["architect", "builder", "critic"]
    system_prompt: str
    temperature: float
    max_tokens: int

AGENTS = {
    "architect": AgentConfig(
        name="Architect",
        role="architect",
        system_prompt="You write detailed YAML specifications...",
        temperature=0.3,   # Lower temp for precise specs
        max_tokens=4096,
    ),
    "builder": AgentConfig(
        name="Builder",
        role="builder",
        system_prompt="You implement code from YAML specifications...",
        temperature=0.2,   # Even lower for deterministic code
        max_tokens=8192,
    ),
    "critic": AgentConfig(
        name="Critic",
        role="critic",
        system_prompt="You validate code against specifications...",
        temperature=0.1,   # Lowest for rigorous analysis
        max_tokens=4096,
    ),
}

def run_agent(agent_name: str, user_message: str) -> str:
    """Run a single agent turn using the local Llama model."""
    config = AGENTS[agent_name]
    response = requests.post(
        f"{LLAMA_API_BASE}/chat/completions",
        json={
            "model": "meta-llama/Llama-3.3-70B-Instruct",
            "messages": [
                {"role": "system", "content": config.system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        },
    )
    return response.json()["choices"][0]["message"]["content"]

def run_sdd_pipeline(requirements: str, max_iterations: int = 3) -> dict:
    """
    Run the full Architect -> Builder -> Critic pipeline.
    Loops until Critic passes or max iterations reached.
    """
    spec = None
    code = None
    critic_feedback = None

    for iteration in range(max_iterations):
        # Phase 1: Architect writes/refines spec
        architect_input = f"Requirements:\n{requirements}"
        if critic_feedback:
            architect_input += f"\n\nCritic Feedback:\n{critic_feedback}"
        spec = run_agent("architect", architect_input)

        # Phase 2: Builder implements from spec
        builder_input = f"Specification:\n{spec}"
        code = run_agent("builder", builder_input)

        # Phase 3: Critic validates
        critic_input = f"Specification:\n{spec}\n\nCode:\n{code}"
        validation = run_agent("critic", critic_input)

        if "verdict: PASS" in validation:
            return {
                "status": "success",
                "iterations": iteration + 1,
                "spec": spec,
                "code": code,
                "validation": validation,
            }

        critic_feedback = validation

    return {
        "status": "max_iterations_reached",
        "iterations": max_iterations,
        "spec": spec,
        "code": code,
        "validation": validation,
    }
```

Преимущество открытого подхода Meta — гибкость: для каждой роли можно запускать специализированную дообученную модель. Модель-архитектор, дообученная писать спецификации. Модель-разработчик, дообученная генерировать код. Модель-критик, дообученная ревьюить код. Каждая оптимизирована под свою задачу.

---

## 1.10 AutoGen от Microsoft и многоагентные фреймворки

Фреймворк AutoGen от Microsoft — один из самых зрелых доступных многоагентных фреймворков, и он естественно ложится на процессы SDD.

### Паттерн диалоговых агентов в AutoGen

AutoGen рассматривает многоагентные процессы как разговоры между агентами. Вот как конвейер SDD выглядит в AutoGen:

```python
# AutoGen-based SDD pipeline (simplified)
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# Define agents with SDD-specific roles
architect = AssistantAgent(
    name="Architect",
    system_message="""You are the Architect Agent. Your job is to write
    detailed YAML specifications from requirements. You never write code.
    When you receive feedback from Critic, you refine the spec.
    Output only the YAML spec, wrapped in ```yaml``` code blocks.""",
    llm_config={"model": "gpt-4o", "temperature": 0.3},
)

builder = AssistantAgent(
    name="Builder",
    system_message="""You are the Builder Agent. Your job is to implement
    code from YAML specifications. You write code and tests. You never
    modify the spec. If the spec is ambiguous, you report the ambiguity
    instead of guessing.""",
    llm_config={"model": "gpt-4o", "temperature": 0.2},
)

critic = AssistantAgent(
    name="Critic",
    system_message="""You are the Critic Agent. You validate code against
    the spec. Check completeness, correctness, and test coverage.
    Output a structured report with verdict: PASS or FAIL.
    If FAIL, list specific issues for the Architect to address.""",
    llm_config={"model": "gpt-4o", "temperature": 0.1},
)

# The orchestrator manages the conversation flow
group_chat = GroupChat(
    agents=[architect, builder, critic],
    messages=[],
    max_round=12,
    speaker_selection_method="round_robin",  # Architect -> Builder -> Critic
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"model": "gpt-4o"},
)

# Kick off the pipeline
user_proxy = UserProxyAgent(
    name="Human",
    human_input_mode="NEVER",
    code_execution_config=False,
)

user_proxy.initiate_chat(
    manager,
    message="""
    Requirement: Users should be able to export their dashboard
    data as a CSV file. The export should respect their current
    filters and role-based access permissions.
    """,
)
```

AutoGen особенно хорошо подходит для SDD благодаря управлению диалогом: агенты могут ссылаться на предыдущие сообщения, история разговора служит журналом, а смена реплик обрабатывается фреймворком автоматически.

---

## 1.11 Протокол общения между агентами

Мы посмотрели на агентов по отдельности и в разных фреймворках — теперь формализуем протокол общения. Это важнейшее инженерное решение в многоагентной системе SDD.

### Что передаётся между агентами

```
ORCHESTRATOR -> ARCHITECT:
  {
    "type": "spec_request",
    "requirements": "Natural language requirements...",
    "existing_specs": ["path/to/related.spec.yaml"],
    "project_context": { ... },
    "previous_critic_feedback": null | CriticReport
  }

ARCHITECT -> BUILDER:
  {
    "type": "build_request",
    "spec": "The complete YAML spec",
    "project_conventions": "Coding standards doc",
    "target_files": ["suggested/file/paths"],
    "existing_code_context": { ... }
  }

BUILDER -> CRITIC:
  {
    "type": "review_request",
    "spec": "The same YAML spec the Builder received",
    "implementation": {
      "files_created": [...],
      "files_modified": [...],
      "code_content": { "path": "content" }
    },
    "tests": {
      "files_created": [...],
      "test_content": { "path": "content" }
    },
    "build_notes": "Any notes from the Builder about decisions made"
  }

CRITIC -> ORCHESTRATOR:
  {
    "type": "validation_report",
    "verdict": "PASS" | "FAIL" | "PASS_WITH_WARNINGS",
    "spec_reference": "dashboard-csv-export.spec.yaml",
    "completeness": { ... },
    "correctness": { ... },
    "test_coverage": { ... },
    "issues": [
      {
        "id": "ISSUE-001",
        "severity": "high",
        "category": "correctness",
        "spec_requirement": "error_cases[1]",
        "description": "...",
        "file": "csv-export.service.ts",
        "line": 45,
        "suggestion": "..."
      }
    ]
  }
```

### Вопрос формата: структурированные данные или естественный язык

В отрасли идёт активный спор: должно ли общение агентов быть структурированными данными (JSON, YAML) или естественным языком. Практическая рекомендация:

| Подход | Плюсы | Минусы | Для чего лучше |
|----------|------|------|----------|
| Структурированный (JSON/YAML) | Разбирается программно, согласован, меньше неоднозначности | Моделям труднее выдавать идеально, жёсткий | Общение агент-агент |
| Естественный язык | Легко порождать, гибок, богат | Неоднозначен, трудно разбирать надёжно, многословен | Общение человек-агент |
| Гибридный | Лучшее из двух миров | Сложнее в реализации | Продакшн-системы |

Рекомендуемый подход в 2026 году — **гибридный**: структурированные форматы для основных данных (спецификации, отчёты о валидации) и естественный язык для комментариев и пояснений.

```yaml
# Hybrid format example: Critic output
validation_report:
  verdict: "FAIL"
  issues:
    - id: "ISSUE-001"
      severity: "high"
      spec_requirement: "error_cases[1]"
      file: "csv-export.service.ts"
      line: 45
      # Structured fields above, natural language explanation below
      explanation: |
        The spec requires that the 413 error be returned *before*
        generating the file. The current implementation loads all
        rows into memory via getFilteredData() and then checks the
        count. For a dataset with 500,000 rows, this would consume
        significant memory before the check ever fires.

        Consider adding a COUNT query before the full data fetch,
        or using a streaming approach with an early-exit condition.
```

---

## 1.12 Практический разбор: собираем конвейер из трёх агентов для разработки функции

Разберём полный практический пример от начала до конца. Мы построим функцию пользовательских настроек уведомлений.

### Шаг 1: определяем оркестратор

```python
# orchestrator.py -- The pipeline coordinator

import yaml
import json
from pathlib import Path
from typing import Optional
from agents import ArchitectAgent, BuilderAgent, CriticAgent

class SDDPipeline:
    """
    Orchestrates the Architect -> Builder -> Critic pipeline.
    """

    def __init__(
        self,
        project_root: Path,
        spec_dir: Path,
        max_iterations: int = 3,
    ):
        self.project_root = project_root
        self.spec_dir = spec_dir
        self.max_iterations = max_iterations

        self.architect = ArchitectAgent(
            spec_dir=spec_dir,
            schema_path=spec_dir / "schema.yaml",
        )
        self.builder = BuilderAgent(
            project_root=project_root,
            conventions_path=project_root / "CONVENTIONS.md",
        )
        self.critic = CriticAgent(
            spec_dir=spec_dir,
            project_root=project_root,
        )

    def run(self, requirements: str) -> dict:
        """Execute the full SDD pipeline."""
        history = []
        critic_feedback: Optional[dict] = None

        for iteration in range(self.max_iterations):
            print(f"\n{'='*60}")
            print(f"ITERATION {iteration + 1}")
            print(f"{'='*60}")

            # --- ARCHITECT PHASE ---
            print("\n[ARCHITECT] Writing specification...")
            spec = self.architect.generate_spec(
                requirements=requirements,
                critic_feedback=critic_feedback,
            )
            print(f"[ARCHITECT] Spec generated: {spec['feature']}")

            # Validate spec against schema
            schema_errors = self.architect.validate_schema(spec)
            if schema_errors:
                print(f"[ARCHITECT] Schema errors: {schema_errors}")
                # Architect self-corrects schema issues
                spec = self.architect.fix_schema_errors(spec, schema_errors)

            # Save spec to disk
            spec_path = self.spec_dir / f"{spec['feature']}.spec.yaml"
            with open(spec_path, 'w') as f:
                yaml.dump(spec, f, default_flow_style=False)

            # --- BUILDER PHASE ---
            print("\n[BUILDER] Implementing specification...")
            build_result = self.builder.implement(spec=spec)
            print(f"[BUILDER] Files created: {len(build_result['files_created'])}")
            print(f"[BUILDER] Tests created: {len(build_result['tests_created'])}")

            if build_result.get("ambiguities"):
                print(f"[BUILDER] Ambiguities found: {len(build_result['ambiguities'])}")
                # Feed ambiguities back as critic feedback
                critic_feedback = {
                    "verdict": "FAIL",
                    "issues": [
                        {
                            "severity": "high",
                            "category": "ambiguity",
                            "description": amb["description"],
                            "spec_section": amb["section"],
                        }
                        for amb in build_result["ambiguities"]
                    ],
                }
                continue

            # --- CRITIC PHASE ---
            print("\n[CRITIC] Validating implementation...")
            validation = self.critic.validate(
                spec=spec,
                implementation=build_result,
            )
            print(f"[CRITIC] Verdict: {validation['verdict']}")

            history.append({
                "iteration": iteration + 1,
                "spec_version": spec.get("spec_version"),
                "verdict": validation["verdict"],
                "issue_count": len(validation.get("issues", [])),
            })

            if validation["verdict"] in ("PASS", "PASS_WITH_WARNINGS"):
                return {
                    "status": "success",
                    "iterations": iteration + 1,
                    "spec_path": str(spec_path),
                    "files": build_result["files_created"],
                    "tests": build_result["tests_created"],
                    "validation": validation,
                    "history": history,
                }

            # Feed issues back to Architect
            critic_feedback = validation
            print(f"[CRITIC] Sending {len(validation['issues'])} issues to Architect")

        return {
            "status": "max_iterations_reached",
            "iterations": self.max_iterations,
            "history": history,
            "final_validation": validation,
        }
```

### Шаг 2: запускаем конвейер

```python
# run_pipeline.py

from pathlib import Path
from orchestrator import SDDPipeline

pipeline = SDDPipeline(
    project_root=Path("./my-project"),
    spec_dir=Path("./my-project/specs"),
    max_iterations=3,
)

result = pipeline.run(
    requirements="""
    Users need to manage their notification preferences.
    They should be able to:
    - Toggle email notifications on/off
    - Toggle push notifications on/off
    - Set quiet hours (time range when no notifications are sent)
    - Choose notification frequency: immediate, hourly digest, daily digest
    The preferences should persist across sessions and sync across devices.
    """
)

print(f"\nPipeline completed: {result['status']}")
print(f"Iterations needed: {result['iterations']}")
if result['status'] == 'success':
    print(f"Files created: {result['files']}")
```

### Шаг 3: наблюдаем за выполнением конвейера

Вот как выглядит типичный запуск:

```
============================================================
ITERATION 1
============================================================

[ARCHITECT] Writing specification...
[ARCHITECT] Spec generated: notification-preferences

[BUILDER] Implementing specification...
[BUILDER] Files created: 4
[BUILDER] Tests created: 2

[CRITIC] Validating implementation...
[CRITIC] Verdict: FAIL
[CRITIC] Sending 2 issues to Architect:
  - ISSUE-001 (high): Spec does not define behavior when quiet hours
    span midnight (e.g., 22:00-06:00). Builder assumed wrapping behavior
    but this should be explicit.
  - ISSUE-002 (medium): Spec says "sync across devices" but does not
    specify conflict resolution when two devices set different preferences
    simultaneously.

============================================================
ITERATION 2
============================================================

[ARCHITECT] Writing specification...
  -> Addressing ISSUE-001: Added explicit midnight-spanning behavior
  -> Addressing ISSUE-002: Added last-write-wins conflict resolution
[ARCHITECT] Spec generated: notification-preferences (v1.0.1)

[BUILDER] Implementing specification...
[BUILDER] Files created: 4 (updated)
[BUILDER] Tests created: 3 (added midnight-spanning test)

[CRITIC] Validating implementation...
[CRITIC] Verdict: PASS

Pipeline completed: success
Iterations needed: 2
```

> **Заметка профессора:** Две итерации. Это типично. Первый проход ловит крупные проблемы — то, о чём архитектор не подумал. Второй обычно чистый. Если вы регулярно доходите до трёх и более итераций, значит агенту-архитектору нужно лучше составить промпт или схема спецификаций недостаточно полна.

---

## 1.13 Обработка ошибок между агентами: когда разработчик не может выполнить спецификацию

Что происходит, когда агент-разработчик получает спецификацию, которую не может реализовать? Это не сбой — это свойство системы. Вот категории неудач разработчика и как с ними работать:

### Категория 1: неоднозначность спецификации

Спецификация неясно говорит, что должно произойти.

```yaml
# Builder's ambiguity report
ambiguity_report:
  spec: "notification-preferences.spec.yaml"
  ambiguities:
    - section: "constraints[3]"
      spec_text: "Preferences should sync across devices"
      problem: "No conflict resolution strategy specified"
      interpretations:
        - "Last write wins (most recent timestamp)"
        - "Per-field merge (each field independently takes latest value)"
        - "Prompt user to resolve conflicts"
      recommendation: "Per-field merge -- most granular, least data loss"
```

**Путь разрешения:** отчёт о неоднозначности идёт архитектору. Архитектор обновляет спецификацию. Разработчик выполняется заново.

### Категория 2: техническая невыполнимость

Спецификация требует того, что нельзя сделать в заданных ограничениях.

```yaml
# Builder's impossibility report
impossibility_report:
  spec: "notification-preferences.spec.yaml"
  issue:
    spec_requirement: "constraints[5]: All operations must complete within 50ms"
    problem: |
      The spec requires syncing preferences to three external services
      (email provider, push service, analytics) on every save.
      Network round trips alone exceed the 50ms constraint.
    possible_resolutions:
      - "Relax the latency constraint to 500ms"
      - "Make external syncs asynchronous (save locally in 50ms, sync in background)"
      - "Remove the external sync requirement from this spec"
```

**Путь разрешения:** отчёт о невыполнимости идёт архитектору. Архитектор либо ослабляет ограничение, либо меняет подход, либо эскалирует человеку.

### Категория 3: отсутствующие зависимости

Спецификация ссылается на то, чего ещё нет.

```yaml
# Builder's dependency report
dependency_report:
  spec: "notification-preferences.spec.yaml"
  missing_dependencies:
    - dependency: "auth/session-management.spec.yaml"
      referenced_in: "inputs[0]"
      status: "spec exists but not implemented"
      blocks: "Cannot validate authenticated sessions"
    - dependency: "PushNotificationService"
      referenced_in: "constraints[2]"
      status: "no spec or implementation found"
      blocks: "Cannot send push notifications"
```

**Путь разрешения:** отчёт о зависимостях идёт оркестратору, которому может потребоваться запустить отдельные конвейеры для зависимостей.

---

## 1.14 Память и состояние агентов: спецификации как общая память

Одно из самых изящных свойств многоагентного паттерна SDD — то, как он решает проблему памяти.

Контекстные окна ИИ-агентов ограничены. Они забывают. Они теряют след ранее принятых решений. В многоагентной системе проблема умножается: агент A принимает решение, агенту B нужно о нём знать, но контекст агента B не содержит рассуждений агента A.

**Решение — спецификация.** Она служит **вынесенной наружу общей памятью** агентов.

```
Traditional Multi-Agent Memory Problem:
  Agent A decides X -> (context lost) -> Agent B does not know about X

SDD Multi-Agent Memory Solution:
  Agent A decides X -> writes X into spec -> Agent B reads spec -> knows X
```

### Что спецификация фиксирует как общая память

| Тип решения | Где в спецификации | Пример |
|--------------|-------------------|---------|
| Функциональные требования | `purpose`, `acceptance_criteria` | «Пользователи могут выгружать CSV» |
| Контракты данных | `inputs`, `outputs` | Имена полей, типы, форматы |
| Поведенческие ограничения | `constraints` | «Максимум 50 000 строк» |
| Поведение при ошибках | `error_cases` | «Возврат 413 при слишком большом числе строк» |
| Сквозные вопросы | `dependencies` | «Требуется спецификация auth v2.1» |
| Открытые вопросы | `open_questions` | «TBD: стратегия разрешения конфликтов» |
| История изменений | `changelog` | «v1.0.1: добавлена обработка периода через полночь» |

Это значит, что можно приостановить конвейер, заменить агента-разработчика на другого, и у нового разработчика будет в спецификации всё нужное. Можно запустить агента-критика через несколько дней на другой версии кода, и он всё равно будет знать, чего требует спецификация.

> **Заметка профессора:** Поэтому я так настойчиво повторяю про полноту спецификации. Неполная спецификация — не просто плохой вход для разработчика, это провал в памяти, который сказывается на всех агентах дальше по цепочке. Если архитектор забыл задать обработку ошибок, разработчик гадает, критику не с чем сверяться — и в продакшене получаются тихие отказы.

---

## 1.15 Петля обратной связи: почему критик отправляет замечания архитектору, а не разработчику

Это проектное решение, на котором многие спотыкаются, поэтому объясню аккуратно.

Когда критик обнаруживает, что код не соответствует спецификации, естественный порыв — «отправить замечание разработчику. Разработчик писал код, пусть он и исправляет».

**Это неверно.** Вот почему.

### Сценарий: разработчик получает замечания критика напрямую

```
Critic says: "The code doesn't handle the case where quiet hours span midnight."

Builder thinks: "The spec didn't mention midnight-spanning. I'll add handling for it."

Builder adds code to handle midnight-spanning quiet hours.

BUT: The spec still doesn't mention midnight-spanning behavior.
```

**Что пошло не так?** Разработчик только что добавил поведение, которого нет в спецификации. Теперь спецификация и код рассинхронизированы. Спецификация — которая должна быть единственным источником истины — неполна. Если работу возьмёт новый агент-разработчик, он не узнает о поведении через полночь, потому что этого нет в спецификации.

### Сценарий: замечания получает архитектор (правильный поток)

```
Critic says: "The code doesn't handle the case where quiet hours span midnight."

Architect thinks: "The spec needs to define midnight-spanning behavior."

Architect updates the spec with explicit midnight-spanning rules.

Builder receives updated spec and implements the now-specified behavior.
```

**Что прошло правильно?** Спецификация остаётся единственным источником истины. Поведение через полночь теперь задокументировано, специфицировано и тестируемо. Любой будущий агент-разработчик о нём узнает.

### Принцип

**Спецификация всегда должна идти впереди кода.** Каждое поведение в коде обязано прослеживаться до требования спецификации. Если критик нашёл недостающее поведение, значит неполна **спецификация**, а не только код.

```
                    +-------------------+
                    |   CRITIC AGENT    |
                    +-------------------+
                            |
                     FAIL: Issues found
                            |
                            v
                 +-----------------------+
                 |  Issues go to         |
                 |  ARCHITECT (not       |
                 |  Builder) because     |
                 |  the spec must be     |
                 |  updated first        |
                 +-----------------------+
                            |
                            v
                  +-------------------+
                  |  ARCHITECT AGENT  |
                  |  Updates the spec |
                  +-------------------+
                            |
                       Updated spec
                            |
                            v
                  +-------------------+
                  |   BUILDER AGENT   |
                  |  Re-implements    |
                  +-------------------+
```

---

## 1.16 Реальные примеры кода многоагентной оркестрации

Соберём всё вместе на примере оркестрации продакшн-уровня на TypeScript:

```typescript
// sdd-pipeline/src/orchestrator.ts

import { z } from 'zod';
import { EventEmitter } from 'events';

// ============================================================
// Type Definitions
// ============================================================

const SpecSchema = z.object({
  spec_version: z.string(),
  feature: z.string(),
  status: z.enum(['draft', 'approved', 'implemented', 'deprecated']),
  purpose: z.string(),
  inputs: z.array(z.object({
    name: z.string(),
    type: z.string(),
    required: z.boolean(),
    description: z.string(),
  })),
  outputs: z.array(z.object({
    name: z.string(),
    type: z.string(),
    description: z.string(),
  })),
  constraints: z.array(z.string()),
  error_cases: z.array(z.object({
    condition: z.string(),
    behavior: z.string(),
  })),
  acceptance_criteria: z.array(z.string()),
});

type Spec = z.infer<typeof SpecSchema>;

interface BuildResult {
  files: Record<string, string>;     // path -> content
  tests: Record<string, string>;     // path -> content
  ambiguities: AmbiguityReport[];
  buildNotes: string;
}

interface AmbiguityReport {
  section: string;
  description: string;
  interpretations: string[];
}

interface ValidationIssue {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: 'completeness' | 'correctness' | 'consistency' | 'coverage';
  specRequirement: string;
  description: string;
  file?: string;
  line?: number;
  suggestion?: string;
}

interface ValidationReport {
  verdict: 'PASS' | 'FAIL' | 'PASS_WITH_WARNINGS';
  issues: ValidationIssue[];
  completeness: { total: number; implemented: number };
  testCoverage: { criteria: number; tested: number };
}

// ============================================================
// Agent Interfaces
// ============================================================

interface AgentProvider {
  chat(systemPrompt: string, userMessage: string): Promise<string>;
}

// ============================================================
// The Orchestrator
// ============================================================

class SDDOrchestrator extends EventEmitter {
  private provider: AgentProvider;
  private maxIterations: number;

  constructor(provider: AgentProvider, maxIterations = 3) {
    super();
    this.provider = provider;
    this.maxIterations = maxIterations;
  }

  async execute(requirements: string): Promise<{
    status: 'success' | 'failed';
    iterations: number;
    spec: Spec | null;
    code: BuildResult | null;
    validation: ValidationReport | null;
  }> {
    let spec: Spec | null = null;
    let code: BuildResult | null = null;
    let validation: ValidationReport | null = null;
    let criticFeedback: ValidationReport | null = null;

    for (let i = 0; i < this.maxIterations; i++) {
      this.emit('iteration:start', { iteration: i + 1 });

      // ----- ARCHITECT PHASE -----
      this.emit('phase:start', { phase: 'architect', iteration: i + 1 });

      const architectPrompt = this.buildArchitectPrompt(
        requirements,
        criticFeedback,
      );
      const specYaml = await this.provider.chat(
        ARCHITECT_SYSTEM_PROMPT,
        architectPrompt,
      );

      try {
        spec = SpecSchema.parse(this.parseYaml(specYaml));
      } catch (parseError) {
        this.emit('error', {
          phase: 'architect',
          error: 'Spec did not conform to schema',
          details: parseError,
        });
        continue; // Retry iteration
      }

      this.emit('phase:complete', {
        phase: 'architect',
        result: { feature: spec.feature, version: spec.spec_version },
      });

      // ----- BUILDER PHASE -----
      this.emit('phase:start', { phase: 'builder', iteration: i + 1 });

      const builderPrompt = this.buildBuilderPrompt(spec);
      const buildOutput = await this.provider.chat(
        BUILDER_SYSTEM_PROMPT,
        builderPrompt,
      );
      code = this.parseBuildResult(buildOutput);

      if (code.ambiguities.length > 0) {
        this.emit('ambiguity', {
          count: code.ambiguities.length,
          details: code.ambiguities,
        });
        // Convert ambiguities to critic feedback format
        criticFeedback = {
          verdict: 'FAIL',
          issues: code.ambiguities.map((amb, idx) => ({
            id: `AMB-${String(idx + 1).padStart(3, '0')}`,
            severity: 'high' as const,
            category: 'completeness' as const,
            specRequirement: amb.section,
            description: amb.description,
          })),
          completeness: { total: 0, implemented: 0 },
          testCoverage: { criteria: 0, tested: 0 },
        };
        continue;
      }

      this.emit('phase:complete', {
        phase: 'builder',
        result: {
          filesCreated: Object.keys(code.files).length,
          testsCreated: Object.keys(code.tests).length,
        },
      });

      // ----- CRITIC PHASE -----
      this.emit('phase:start', { phase: 'critic', iteration: i + 1 });

      const criticPrompt = this.buildCriticPrompt(spec, code);
      const validationOutput = await this.provider.chat(
        CRITIC_SYSTEM_PROMPT,
        criticPrompt,
      );
      validation = this.parseValidationReport(validationOutput);

      this.emit('phase:complete', {
        phase: 'critic',
        result: {
          verdict: validation.verdict,
          issueCount: validation.issues.length,
        },
      });

      if (validation.verdict === 'PASS'
        || validation.verdict === 'PASS_WITH_WARNINGS') {
        return {
          status: 'success',
          iterations: i + 1,
          spec,
          code,
          validation,
        };
      }

      // Feed issues back to Architect
      criticFeedback = validation;
      this.emit('feedback', {
        fromPhase: 'critic',
        toPhase: 'architect',
        issueCount: validation.issues.length,
      });
    }

    return {
      status: 'failed',
      iterations: this.maxIterations,
      spec,
      code,
      validation,
    };
  }

  private buildArchitectPrompt(
    requirements: string,
    feedback: ValidationReport | null,
  ): string {
    let prompt = `## Requirements\n\n${requirements}`;
    if (feedback) {
      prompt += `\n\n## Issues from Previous Review\n\n`;
      prompt += `The Critic found ${feedback.issues.length} issues:\n\n`;
      for (const issue of feedback.issues) {
        prompt += `- [${issue.severity}] ${issue.description}\n`;
        prompt += `  Spec section: ${issue.specRequirement}\n`;
        if (issue.suggestion) {
          prompt += `  Suggestion: ${issue.suggestion}\n`;
        }
        prompt += '\n';
      }
      prompt += `Please update the spec to address ALL of these issues.`;
    }
    return prompt;
  }

  private buildBuilderPrompt(spec: Spec): string {
    return `## Specification\n\n\`\`\`yaml\n${JSON.stringify(spec, null, 2)}\n\`\`\`\n\nImplement this specification. Generate code and tests.`;
  }

  private buildCriticPrompt(spec: Spec, build: BuildResult): string {
    let prompt = `## Specification\n\n\`\`\`yaml\n${JSON.stringify(spec, null, 2)}\n\`\`\`\n\n`;
    prompt += `## Implementation\n\n`;
    for (const [path, content] of Object.entries(build.files)) {
      prompt += `### ${path}\n\`\`\`\n${content}\n\`\`\`\n\n`;
    }
    prompt += `## Tests\n\n`;
    for (const [path, content] of Object.entries(build.tests)) {
      prompt += `### ${path}\n\`\`\`\n${content}\n\`\`\`\n\n`;
    }
    prompt += `Validate the implementation against every spec requirement.`;
    return prompt;
  }

  // Parsing methods would handle extracting structured data
  // from the LLM's response -- omitted for brevity
  private parseYaml(raw: string): unknown { /* ... */ return {}; }
  private parseBuildResult(raw: string): BuildResult { /* ... */ return {} as any; }
  private parseValidationReport(raw: string): ValidationReport { /* ... */ return {} as any; }
}

// ============================================================
// System Prompts
// ============================================================

const ARCHITECT_SYSTEM_PROMPT = `You are the Architect Agent.
Write detailed YAML specifications from requirements.
Never write implementation code.
Output only valid YAML conforming to the spec schema.
Address all Critic feedback when provided.`;

const BUILDER_SYSTEM_PROMPT = `You are the Builder Agent.
Implement code from YAML specifications.
Generate tests for every acceptance criterion.
Report ambiguities rather than guessing.
Follow project coding conventions.`;

const CRITIC_SYSTEM_PROMPT = `You are the Critic Agent.
Validate code against the specification.
Check completeness, correctness, and test coverage.
Output a structured validation report.
Be thorough but fair -- only flag real issues.`;

export { SDDOrchestrator };
```

### Использование оркестратора

```typescript
// run.ts

import { SDDOrchestrator } from './orchestrator';
import { AnthropicProvider } from './providers/anthropic';

const provider = new AnthropicProvider({
  apiKey: process.env.ANTHROPIC_API_KEY!,
  model: 'claude-sonnet-4-20250514',
});

const pipeline = new SDDOrchestrator(provider, 3);

// Listen to pipeline events
pipeline.on('iteration:start', ({ iteration }) => {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`ITERATION ${iteration}`);
  console.log(`${'='.repeat(60)}`);
});

pipeline.on('phase:start', ({ phase, iteration }) => {
  console.log(`\n[${phase.toUpperCase()}] Starting...`);
});

pipeline.on('phase:complete', ({ phase, result }) => {
  console.log(`[${phase.toUpperCase()}] Complete:`, result);
});

pipeline.on('feedback', ({ fromPhase, toPhase, issueCount }) => {
  console.log(
    `[FEEDBACK] ${fromPhase} -> ${toPhase}: ${issueCount} issues`,
  );
});

// Execute
const result = await pipeline.execute(`
  Users need to manage their notification preferences.
  They should be able to:
  - Toggle email notifications on/off
  - Toggle push notifications on/off
  - Set quiet hours (time range when no notifications are sent)
  - Choose notification frequency: immediate, hourly, daily digest
  Preferences must persist and sync across devices.
`);

console.log(`\nResult: ${result.status}`);
console.log(`Iterations: ${result.iterations}`);
```

---

## 1.17 Собираем всё вместе: ключевые выводы

Подведём итог главных уроков главы:

1. **Паттерн трёх агентов (архитектор, разработчик, критик) повторяет естественное разделение труда в командах разработки.** Он разделяет заботу о том, *что* строить, *как* строить и *правильно ли построено*.

2. **Спецификация — это механизм координации.** Она одновременно общая память, протокол общения и контракт. Без неё многоагентные процессы превращаются в хаос.

3. **Критик отправляет обратную связь архитектору, а не разработчику.** Это гарантирует, что спецификация остаётся единственным источником истины и что каждое поведение описано до того, как реализовано.

4. **Все крупные ИИ-компании сходятся к этому паттерну.** Claude Code от Anthropic (инструмент Task), Gemini от Google (многошаговое рассуждение), агентные фреймворки OpenAI (Assistants, Swarm), Llama от Meta (агенты с открытым кодом) и AutoGen от Microsoft — все реализуют вариации процесса «архитектор — разработчик — критик».

5. **Обработка ошибок между агентами — первоклассная задача.** Отчёты о неоднозначности, невыполнимости и зависимостях — не сбои, а необходимые каналы коммуникации, делающие систему самокорректирующейся.

6. **Гибридная коммуникация (структурированные данные + естественный язык) — практичный выбор** для общения агентов в 2026 году.

> **Заметка профессора:** Если из этой главы нужно вынести одну вещь, пусть это будет вот что: качество вашей многоагентной системы ограничено качеством ваших спецификаций. Вложитесь в спецификацию — и агенты сделают остальное. Сэкономите на спецификации — и никакая изощрённость агентов вас не спасёт.

---

### Упражнения

**Упражнение 1.** Спроектируйте конвейер из трёх агентов для другой функции: аутентификации пользователей через OAuth2. Напишите системный промпт агента-архитектора, спецификацию, которую он создаст, и критерии валидации, которые будет проверять критик.

**Упражнение 2.** Измените код оркестратора, чтобы поддержать параллельных агентов-разработчиков: сложная спецификация раскладывается на подспецификации, которые можно реализовывать одновременно. Какие задачи координации при этом возникают?

**Упражнение 3.** Реализуйте сценарий «невыполнимой спецификации»: напишите спецификацию с противоречивыми ограничениями и посмотрите, как каждый агент (архитектор, разработчик, критик) должен обрабатывать противоречие. Кто должен поймать его первым?

---

*Следующая глава: «Эволюционирующие спецификации» — как управлять спецификациями, которые меняются со временем, не ломая всё вокруг.*

---

[← Оглавление курса](../INDEX.ru.md) · [← Глава 3: Стратегия контекстного окна](../MODULE_03/CHAPTER_03.ru.md) · [Глава 2: Эволюционирующие спецификации →](CHAPTER_02.ru.md)
