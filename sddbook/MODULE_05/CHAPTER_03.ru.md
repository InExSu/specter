# Глава 3: Человек в контуре

## МОДУЛЬ 05 — Сопровождение и масштабирование (продвинутый уровень)

> [Оглавление курса](../INDEX.ru.md) · [Модуль 05](../INDEX.ru.md#модуль-05--сопровождение-и-масштабирование)

---

### Вступление к лекции

> *Это последняя лекция курса, и логично завершить не техникой, а философией — хотя, как вы увидите, она глубоко практична.*

> *Пять модулей мы учились писать спецификации, которые машина может исполнить. Мы научились задавать контракты, проектировать архитектуру, валидировать результаты, оркестрировать агентов, управлять рефакторингами и генерировать документацию — и всё это через дисциплину спецификации. К этому моменту вы способны описать систему настолько точно, что ИИ может её построить.*

> *Но вот вопрос, который витал за каждым уроком: если ИИ исполняет спецификацию, зачем вообще нужен человек?*

> *Ответ: вы задаёте не тот вопрос. Правильный вопрос — где человек добавляет больше всего ценности? И ответ на него радикально изменился за последние три года. В 2023 году человек добавлял ценность тем, что писал код. В 2024-м — тем, что писал лучшие промпты. В 2025-м — тем, что писал спецификации. А в 2026-м человек добавляет ценность тем, что знает, когда ИИ должен остановиться и попросить помощи.*

> *Вот что такое шлюз утверждения. Это точка в процессе, где человеческое суждение незаменимо — не потому, что ИИ не может выдать результат, а потому, что ИИ не может оценить, верен ли этот результат в полном контексте человеческих нужд, бизнес-целей, этических соображений и реальных последствий.*

> *Сегодня мы узнаем, где должны стоять такие шлюзы, почему они важны и как закладывать их в спецификацию. Это венец всего, что мы построили. Слушайте внимательно.*

---

## 3.1 Почему полная автоматизация — миф (и почему это хорошо)

В индустрии ходит нарратив: «рано или поздно ИИ сможет всё, нужно лишь сделать его умнее». Этот нарратив ошибочен, и понимание этой ошибки сделает вас лучшим архитектором продукта.

Полная автоматизация предполагает, что все решения объективны — что у каждого вопроса есть верный ответ, если хватит данных и «ума». Но разработка ПО не такая. В ней полно решений не про правильность, а про ценности, приоритеты, компромиссы и контекст, которые невозможно уложить в спецификацию.

Вот вопросы, которые возникают даже при реализации простой функции:

— «В спецификации сказано возвращать 404 для удалённых пользователей. Но стоит ли сообщать вызывающему, что пользователь существовал и был удалён? Или вернуть тот же 404, что и для никогда не существовавших? Это решение о приватности, а не техническое».

— «В спецификации сказано сортировать результаты поиска по релевантности. Но что такое релевантность? Она одинакова для опытного пользователя, который ищет конкретный товар, и случайного посетителя, листающего каталог?»

— «В спецификации задан лимит 100 запросов в минуту. Но наш крупнейший клиент сейчас делает 300. Соблюсти спецификацию и сломать ему интеграцию или сделать исключение?»

Ни у одного из этих вопросов нет «правильного» ответа, который ИИ выведет из спецификации. Нужно суждение — человеческое суждение, — опирающееся на бизнес-контекст, эмпатию к пользователю, правовые требования и этику.

> **Заметка профессора:** Это не ограничение нынешнего ИИ, а фундаментальное свойство разработки ПО. Софт служит людям, а человеческие потребности беспорядочны, контекстны и часто противоречивы. Спецификация может зафиксировать «что» и «как», но не всегда может зафиксировать «почему» — а когда «почему» конфликтует с «что», решать должен человек.

### Парадокс автоматизации

Ирония в том, что чем лучше ваши спецификации, тем важнее человеческий надзор. С плохими спецификациями ИИ выдаёт очевидно неверный результат, который заметит любой. С хорошими — результат, который выглядит правильным, но может быть тонко неверным так, что заметит только эксперт в предметной области.

```
Bad Spec → Obvious Failures → Easy to Catch
Good Spec → Subtle Failures → Hard to Catch → MORE human attention needed
```

Это парадокс автоматизации, хорошо описанный в авиации, медицине и атомной энергетике. Чем лучше автоматизация, тем критичнее человеческий надзор — потому что проскакивают именно те отказы, которые автоматизация не была рассчитана ловить.

---

## 3.2 Спектр доверия

Не все части спецификации несут одинаковый риск. Одни разделы механические — ИИ сделает их правильно всегда. Другие нюансированы — обычно правильно, но с провалами в крайних случаях. А третьи — вопросы суждения: ИИ может выдать правдоподобный результат, в корне неверный.

### Как устроен спектр доверия

```
FULL AUTOMATION ◄────────────────────────────► FULL HUMAN CONTROL
    │                                                │
    │  Boilerplate    Logic      Business     Ethical │
    │  Generation    Implement.   Rules       Decisions
    │                                                │
    │  CRUD routes   Auth flow   Pricing     Privacy  │
    │  DTO creation  Caching     Compliance  Security │
    │  Test scaffolds Pagination  Edge cases  UX copy │
    │  Config files  Validation  Exceptions  Tone    │
    │                                                │
    ▼                                                ▼
  AI handles        AI proposes,              Human decides,
  autonomously      human approves            AI implements
```

### Спектр в спецификациях

В спецификации стоит явно помечать разделы уровнем доверия:

```markdown
## Feature Spec: User Search

### Section 1: Database Query Layer [TRUST: HIGH — AUTO-APPROVE]
The search query uses Prisma's full-text search with standard
pagination. This is mechanical and well-tested.

**AI Directive:** Implement and proceed. No human review needed
for this section unless tests fail.

### Section 2: Search Ranking Algorithm [TRUST: MEDIUM — REVIEW REQUIRED]
Search results are ranked by a weighted combination of:
- Text relevance (weight: 0.5)
- Recency (weight: 0.3)
- Popularity (weight: 0.2)

**AI Directive:** Implement the algorithm, then STOP. Generate a
report showing search results for the 10 test queries listed in
Appendix A. A human must review the results before proceeding.

### Section 3: Content Filtering [TRUST: LOW — HUMAN DECIDES]
Search results must be filtered to exclude:
- Content flagged by the moderation system
- Content from suspended accounts
- Content restricted by geographic licensing

**AI Directive:** DO NOT implement content filtering logic.
Present the filtering requirements to the human reviewer.
The human will specify the exact filtering rules after
reviewing the legal and compliance implications.
```

---

## 3.3 Паттерн шлюза утверждения

Шлюз утверждения — определённая контрольная точка в процессе разработки, где исполнение останавливается и человек валидирует работу перед продолжением. Это SDD-аналог автоматического выключателя: он не даёт проблемам распространяться дальше по потоку.

### Анатомия шлюза утверждения

```typescript
// Formal approval gate specification

interface ApprovalGate {
  /** Unique identifier for this gate */
  id: string;

  /** What triggers this gate */
  trigger: {
    type: 'phase-complete' | 'risk-threshold' | 'manual' | 'anomaly-detected';
    condition: string;
  };

  /** What the reviewer needs to evaluate */
  reviewScope: {
    artifacts: string[];      // What to review
    criteria: string[];       // What "good" looks like
    antiPatterns: string[];   // What "bad" looks like
    context: string[];        // Background information needed
  };

  /** Who can approve */
  approvers: {
    role: string;
    minimumCount: number;     // How many approvals needed
    escalation: string;       // Who to escalate to if blocked
  };

  /** What happens after review */
  outcomes: {
    approved: string;         // Next step if approved
    rejected: string;         // What to do if rejected
    conditionallyApproved: string; // Approved with modifications
  };

  /** Time constraints */
  sla: {
    maxWaitTime: string;      // How long to wait for review
    escalationAfter: string;  // When to escalate
    autoRejectAfter: string;  // When to auto-reject (safety)
  };
}

// Example: API endpoint deployment approval gate
const deploymentGate: ApprovalGate = {
  id: 'GATE-DEPLOY-001',

  trigger: {
    type: 'phase-complete',
    condition: 'All unit and integration tests pass. Code coverage >= 80%.',
  },

  reviewScope: {
    artifacts: [
      'Generated controller code',
      'Generated service code',
      'Generated test suite',
      'Performance benchmark results',
      'Security scan results',
    ],
    criteria: [
      'Code matches spec exactly — no extra features',
      'All error cases handled per spec',
      'No security vulnerabilities (OWASP Top 10)',
      'Performance meets SLA (p99 < 200ms)',
      'No breaking changes to existing API consumers',
    ],
    antiPatterns: [
      'AI added features not in the spec',
      'AI used a different library than specified',
      'AI skipped error handling for edge cases',
      'AI hardcoded values that should be configurable',
      'AI ignored specified constraints',
    ],
    context: [
      'Original spec document',
      'Archaeology report (if refactor)',
      'Previous review comments',
      'Related specs for dependent systems',
    ],
  },

  approvers: {
    role: 'Tech Lead or Senior Engineer',
    minimumCount: 1,
    escalation: 'Engineering Manager',
  },

  outcomes: {
    approved: 'Proceed to staging deployment',
    rejected: 'Return to implementation with review notes. Re-trigger gate when fixed.',
    conditionallyApproved: 'Proceed with listed modifications. Follow-up review in 48 hours.',
  },

  sla: {
    maxWaitTime: '24 hours',
    escalationAfter: '8 hours',
    autoRejectAfter: '72 hours',
  },
};
```

### Где ставить шлюзы утверждения

Шлюз нужен не на каждом шаге. Слишком много шлюзов тормозит разработку и вызывает «усталость от утверждений», когда ревьюеры штампуют всё подряд. Слишком мало — и проблемы проходят дальше. Вот рамка для решения:

```markdown
## Approval Gate Placement Framework

### ALWAYS gate these:
- [ ] Changes to authentication or authorization logic
- [ ] Changes to payment processing or financial calculations
- [ ] Changes to personally identifiable information (PII) handling
- [ ] Changes to rate limiting or security controls
- [ ] Changes to data deletion or retention logic
- [ ] Any change the spec marks as [TRUST: LOW]
- [ ] First deployment of a new service or major version
- [ ] Changes affecting more than 3 downstream systems

### SOMETIMES gate these (based on risk assessment):
- [ ] Performance-critical code paths (gate if SLA is tight)
- [ ] Complex business logic (gate if edge cases are numerous)
- [ ] Third-party API integrations (gate if SLA depends on them)
- [ ] Database schema changes (gate if data migration is needed)
- [ ] Changes to public API contracts (gate if consumers exist)

### RARELY gate these:
- [ ] CRUD boilerplate generation
- [ ] Test generation from specs
- [ ] Documentation generation
- [ ] Configuration file updates
- [ ] Linting and formatting changes
- [ ] Dependency version updates (minor/patch)
```

---

## 3.4 Как Anthropic реализует человеческий надзор

Подход Anthropic к человеческому надзору в разработке ИИ — пожалуй, самый строгий в индустрии, и он даёт ценные уроки для проектирования шлюзов утверждения в SDD.

### RLHF: обучение с подкреплением на человеческой обратной связи

Обучая Claude, Anthropic не просто оптимизирует точность. Используется процесс Reinforcement Learning from Human Feedback (RLHF), где люди-оценщики дают обратную связь по выходам модели. Модель учится не только тому, что правильно, но и тому, что полезно, честно и безопасно.

Ключевой вывод для SDD: **люди проверяют не техническую правильность выхода, а его уместность в контексте.** Технически верный ответ может быть бесполезным, вводящим в заблуждение или вредным. Человеческая петля обратной связи ловит эти нюансы, которые не поймает ни один автотест.

### Red-teaming

Перед выпуском новой версии Claude Anthropic проводит red-teaming: люди-оценщики намеренно пытаются заставить модель выдать вредный или неверный результат. Ищут режимы отказа — ситуации, где модель уверена, но ошибается, или где выполняет инструкции, которые должна отклонить.

В применении к SDD это прямо ложится на ревью спецификации:

```markdown
## Red-Team Checklist for Spec Review

### Adversarial Inputs
- What happens if the AI receives malformed input that the spec
  does not explicitly address?
- What happens if the AI receives input that technically meets the
  spec but is clearly malicious? (e.g., a product name that is
  actually an XSS payload)
- What happens if two spec requirements contradict each other?

### Failure Modes
- Where is the AI most likely to hallucinate (add features not
  in the spec)?
- Where is the AI most likely to shortcut (skip error handling)?
- Where is the AI most likely to misinterpret the spec (ambiguous
  language)?

### Edge Cases
- What are the boundary values for all numeric inputs?
- What happens at extreme scale? (1 million records, 10,000
  concurrent users)
- What happens when external dependencies fail? (Database down,
  API timeout, disk full)

### Security
- Can the AI-generated code be exploited? (SQL injection, XSS,
  CSRF, IDOR)
- Does the code properly sanitize all user input?
- Are authentication and authorization properly enforced?
```

### Constitutional AI

Подход Constitutional AI от Anthropic задаёт принципы, которым модель обязана следовать, — «конституцию», ограничивающую её поведение. В SDD у спецификации та же роль: это конституция, ограничивающая реализацию ИИ.

Но как Anthropic обнаружил, что одной конституции недостаточно (нужны ещё RLHF и red-teaming), так и одной спецификации недостаточно. Нужны человеческое ревью и состязательное тестирование.

---

## 3.5 Как OpenAI использует человеческую обратную связь

Подход OpenAI к человеческому надзору в разработке GPT делает ставку на итеративное уточнение через обратную связь. В процессе несколько этапов человеческой оценки:

1. **Оценка до обучения:** люди оценивают возможности базовой модели и выявляют пробелы.
2. **Направление дообучения:** оценщики дают данные предпочтений — «этот ответ лучше того» — чтобы направить поведение модели.
3. **Оценка безопасности:** выделенные команды по безопасности тестируют модель на известные категории рисков.
4. **Мониторинг после выпуска:** после релиза ревьюеры следят за реальным использованием на предмет неожиданного поведения.

Урок для практиков SDD: обратная связь — не разовое событие, а непрерывный процесс на каждом этапе жизненного цикла разработки.

```typescript
// Modeling OpenAI's feedback loop in an SDD workflow

interface FeedbackLoop {
  stage: 'spec-review' | 'implementation-review' | 'testing' | 'staging' | 'production';

  /**
   * What the human reviews at this stage
   */
  reviewFocus: string;

  /**
   * How feedback flows back to the spec
   */
  feedbackChannel: 'spec-amendment' | 'bug-report' | 'feature-request' | 'risk-flag';

  /**
   * What actions result from feedback
   */
  actions: {
    specUpdate: boolean;      // Does the spec need to change?
    reimplementation: boolean; // Does the code need to be regenerated?
    newGate: boolean;         // Should a new approval gate be added?
    escalation: boolean;      // Does this need leadership attention?
  };
}

const sddFeedbackLoops: FeedbackLoop[] = [
  {
    stage: 'spec-review',
    reviewFocus: 'Is the spec complete, unambiguous, and achievable?',
    feedbackChannel: 'spec-amendment',
    actions: {
      specUpdate: true,
      reimplementation: false,
      newGate: false,
      escalation: false,
    },
  },
  {
    stage: 'implementation-review',
    reviewFocus: 'Does the code match the spec? Are there deviations?',
    feedbackChannel: 'bug-report',
    actions: {
      specUpdate: false,  // The spec was right, the code was wrong
      reimplementation: true,
      newGate: false,
      escalation: false,
    },
  },
  {
    stage: 'testing',
    reviewFocus: 'Do edge cases reveal spec gaps?',
    feedbackChannel: 'spec-amendment',
    actions: {
      specUpdate: true,   // The spec was incomplete
      reimplementation: true,
      newGate: true,      // Add a gate for this edge case category
      escalation: false,
    },
  },
  {
    stage: 'staging',
    reviewFocus: 'Does the system behave correctly under realistic conditions?',
    feedbackChannel: 'risk-flag',
    actions: {
      specUpdate: true,
      reimplementation: true,
      newGate: true,
      escalation: true,   // Staging failures need leadership awareness
    },
  },
  {
    stage: 'production',
    reviewFocus: 'Are there unexpected behaviors or user complaints?',
    feedbackChannel: 'feature-request',
    actions: {
      specUpdate: true,
      reimplementation: true,
      newGate: true,
      escalation: true,
    },
  },
];
```

---

## 3.6 Практики ответственного ИИ в Google и человеческий надзор

Подход Google к ответственному ИИ, выросший из многолетней эксплуатации ИИ-систем в огромном масштабе, делает ставку на структурированный человеческий надзор на нескольких уровнях.

### Модель многослойного ревью

Google применяет то, что называет «многослойным ревью»: разные уровни человеческого надзора подключаются в зависимости от риска выхода ИИ:

- **Слой 1: автоматические проверки.** Юнит-тесты, интеграционные тесты, линтинг, сканирование безопасности. Человек не нужен.
- **Слой 2: ревью коллеги.** Стандартное ревью кода другим инженером. Требуется для всех изменений.
- **Слой 3: ревью эксперта предметной области.** Нужно для изменений, затрагивающих конкретные области (безопасность, приватность, доступность).
- **Слой 4: этическое ревью.** Нужно для изменений, влияющих на пользовательский опыт, сбор данных или способных навредить.
- **Слой 5: ревью руководства.** Нужно для изменений, затрагивающих политику компании, юридическое соответствие или публичное восприятие.

### Многослойная модель в SDD

```markdown
## Layered Review Model for SDD

### Layer 1: Automated (CI/CD Pipeline)
Triggers: Every commit
Checks:
- Spec syntax validation
- Type checking
- Unit tests pass
- Integration tests pass
- Security scan clean
- Performance benchmarks within SLA
- Documentation sync verified

Gate: Automated. Blocks merge if any check fails.

### Layer 2: Peer Review (Pull Request)
Triggers: Every pull request
Reviewers: Any team member
Checks:
- Code matches spec
- No unspecified features added
- Error handling complete
- Test coverage adequate
- Code style consistent

Gate: 1 approval required. Standard SLA: 24 hours.

### Layer 3: Domain Expert Review
Triggers: Changes tagged with domain flags
Reviewers: Designated domain experts
Domains and their experts:
- [SECURITY] → Security Engineer
- [DATA] → Data Engineer / DBA
- [PRIVACY] → Privacy Engineer
- [A11Y] → Accessibility Specialist
- [PERF] → Performance Engineer

Gate: Domain expert approval required. SLA: 48 hours.

### Layer 4: Architecture Review
Triggers: New services, major refactors, API changes
Reviewers: Tech Lead + Architect
Checks:
- Consistent with system architecture
- Scalability considerations addressed
- Backward compatibility maintained
- Migration path defined

Gate: Tech Lead approval required. SLA: 1 week.

### Layer 5: Business Review
Triggers: Customer-facing changes, pricing changes, compliance changes
Reviewers: Product Owner + Legal (if applicable)
Checks:
- Business requirements met
- Customer communication plan exists
- Legal/compliance requirements satisfied
- Risk assessment reviewed

Gate: Product Owner approval required. SLA: 1 week.
```

---

## 3.7 Концепция оценки уверенности

Одна из самых сильных идей в коллаборации человека и ИИ — оценка уверенности: ИИ сам сообщает, насколько он уверен в каждой части своего выхода. Эта идея, заимствованная из оценки моделей машинного обучения, встраивается прямо в ваш SDD-процесс.

### Как это работает

Когда ИИ генерирует код из спецификации, он одновременно выдаёт оценку уверенности по каждому разделу:

```typescript
// The AI's confidence report for a generated implementation

interface ConfidenceReport {
  overall: number;  // 0.0 to 1.0
  sections: {
    specSection: string;
    confidence: number;
    reasoning: string;
    suggestedReviewLevel: 'auto-approve' | 'quick-review' | 'deep-review';
  }[];
  uncertainties: {
    description: string;
    specReference: string;
    possibleInterpretations: string[];
    chosenInterpretation: string;
    alternativeImplications: string;
  }[];
}

// Example confidence report
const exampleReport: ConfidenceReport = {
  overall: 0.87,
  sections: [
    {
      specSection: 'CRUD Operations',
      confidence: 0.98,
      reasoning: 'Standard CRUD with Prisma. Well-defined spec, no ambiguity.',
      suggestedReviewLevel: 'auto-approve',
    },
    {
      specSection: 'Search Ranking Algorithm',
      confidence: 0.72,
      reasoning: 'Spec defines weights but not tie-breaking behavior. '
        + 'I assumed lexicographic tie-breaking by product name. '
        + 'This may not match business intent.',
      suggestedReviewLevel: 'deep-review',
    },
    {
      specSection: 'Rate Limiting',
      confidence: 0.85,
      reasoning: 'Spec says "100 requests per minute per user." '
        + 'Implemented sliding window. Spec does not specify '
        + 'window type (fixed vs sliding). Sliding is standard '
        + 'but may differ from existing implementation.',
      suggestedReviewLevel: 'quick-review',
    },
    {
      specSection: 'Error Handling',
      confidence: 0.65,
      reasoning: 'Spec lists error codes but not error message format. '
        + 'I used RFC 7807 Problem Details. Spec does not reference '
        + 'any error format standard. Existing API may use a different format.',
      suggestedReviewLevel: 'deep-review',
    },
  ],
  uncertainties: [
    {
      description: 'Pagination behavior when total changes during traversal',
      specReference: 'Section 3.2: Pagination',
      possibleInterpretations: [
        'Return stable snapshot (consistent pagination)',
        'Return live data (items may shift between pages)',
      ],
      chosenInterpretation: 'Live data — simpler, more common',
      alternativeImplications: 'Users may see duplicate or missing items '
        + 'if data changes while they are paginating.',
    },
  ],
};
```

### Маршрутизация ревью по оценке уверенности

```python
# scripts/route_reviews.py
# Reads AI confidence reports and routes to appropriate reviewers

from dataclasses import dataclass
from typing import Literal

@dataclass
class ReviewRouting:
    section: str
    confidence: float
    review_level: Literal["auto-approve", "quick-review", "deep-review"]
    reviewer: str | None
    priority: Literal["low", "medium", "high", "critical"]

def route_review(confidence_report: dict) -> list[ReviewRouting]:
    """Route each section to the appropriate review level based on
    AI confidence score."""

    routings = []

    for section in confidence_report["sections"]:
        confidence = section["confidence"]

        if confidence >= 0.95:
            # Very high confidence — auto-approve
            routing = ReviewRouting(
                section=section["specSection"],
                confidence=confidence,
                review_level="auto-approve",
                reviewer=None,
                priority="low",
            )
        elif confidence >= 0.80:
            # High confidence — quick review by any team member
            routing = ReviewRouting(
                section=section["specSection"],
                confidence=confidence,
                review_level="quick-review",
                reviewer="any-team-member",
                priority="medium",
            )
        elif confidence >= 0.60:
            # Medium confidence — deep review by senior engineer
            routing = ReviewRouting(
                section=section["specSection"],
                confidence=confidence,
                review_level="deep-review",
                reviewer="senior-engineer",
                priority="high",
            )
        else:
            # Low confidence — deep review by tech lead + domain expert
            routing = ReviewRouting(
                section=section["specSection"],
                confidence=confidence,
                review_level="deep-review",
                reviewer="tech-lead",
                priority="critical",
            )

        routings.append(routing)

    # Also route all uncertainties as high priority
    for uncertainty in confidence_report.get("uncertainties", []):
        routings.append(ReviewRouting(
            section=f"UNCERTAINTY: {uncertainty['description']}",
            confidence=0.0,
            review_level="deep-review",
            reviewer="tech-lead",
            priority="critical",
        ))

    return routings
```

> **Заметка профессора:** Оценка уверенности — не про скромность ИИ. Она про эффективное распределение человеческого внимания. Люди — узкое место любого процесса ревью. Если вы можете автоматически найти те 20% результата, которым нужно 80% внимания ревьюеров, вы резко улучшили соотношение качества и скорости разработки.

---

## 3.8 Частые паттерны отклонений: где ИИ чаще всего уходит от спецификации

За годы работы с генерацией кода вырисовались чёткие паттерны: как и где ИИ отклоняется от спецификации. Знание этих паттернов позволяет ставить шлюзы утверждения точно туда, где они нужнее всего.

### Паттерн 1: полезная добавка

ИИ добавляет функции, которых нет в спецификации, потому что они кажутся полезными.

```typescript
// SPEC SAYS:
// POST /api/users — Create a user. Return the created user.

// AI GENERATES (notice the extra feature):
@Post()
async createUser(@Body() dto: CreateUserDto): Promise<UserResponse> {
  const user = await this.userService.create(dto);

  // NOT IN SPEC: AI decided to send a welcome email
  await this.emailService.sendWelcomeEmail(user.email);

  // NOT IN SPEC: AI decided to create a default workspace
  await this.workspaceService.createDefault(user.id);

  // NOT IN SPEC: AI decided to log an analytics event
  await this.analyticsService.track('user.created', { userId: user.id });

  return this.mapToResponse(user);
}
```

**Почему так происходит:** в обучающих данных ИИ видел тысячи обработчиков создания пользователя, и в большинстве есть эти побочные эффекты. Он сопоставляет с типовыми реализациями, а не исполняет вашу конкретную спецификацию.

**Как предотвратить:** добавьте в спецификацию явные ограничения «НЕ делай»:

```markdown
## POST /api/users — Create User

### Behavior
1. Validate input
2. Create user in database
3. Return created user

### Constraints
- Do NOT send any emails from this endpoint
- Do NOT create any related entities
- Do NOT log analytics events
- Side effects are handled by separate event handlers (see Event Spec)
```

### Паттерн 2: преждевременная оптимизация

ИИ реализует более сложное решение, чем требует спецификация, предугадывая будущие нужды.

```typescript
// SPEC SAYS:
// Cache product listings for 5 minutes using Redis.

// AI GENERATES (massively over-engineered):
@Injectable()
export class ProductCacheService {
  private readonly localCache = new LRUCache<string, Product[]>({
    max: 1000,
    ttl: 60_000, // 1 minute local cache (NOT IN SPEC)
  });

  async getProducts(params: ListParams): Promise<Product[]> {
    const cacheKey = this.buildCacheKey(params);

    // Layer 1: Check local LRU cache (NOT IN SPEC)
    const localResult = this.localCache.get(cacheKey);
    if (localResult) return localResult;

    // Layer 2: Check Redis (THIS is what the spec asked for)
    const redisResult = await this.redis.get(cacheKey);
    if (redisResult) {
      const parsed = JSON.parse(redisResult);
      this.localCache.set(cacheKey, parsed); // NOT IN SPEC
      return parsed;
    }

    // Layer 3: Database query with read replica (NOT IN SPEC)
    const products = await this.prisma.product.findMany({
      ...params,
      // AI chose to use read replica — NOT IN SPEC
      // @ts-ignore custom Prisma extension
      $replica: true,
    });

    // Cache warming for related queries (NOT IN SPEC)
    await this.warmRelatedCaches(params, products);

    return products;
  }

  // NOT IN SPEC: 50 lines of cache warming logic
  private async warmRelatedCaches(/* ... */) { /* ... */ }
}
```

**Почему так происходит:** ИИ знает, что простое кеширование можно улучшить слоями. Он хочет быть полезным. Но спецификация просила кеш в Redis с TTL 5 минут, а не многослойную архитектуру кеширования.

**Как предотвратить:** явно очертите границы сложности:

```markdown
### Caching Spec
- Use Redis for caching product listings
- TTL: 5 minutes
- Cache key: `products:${page}:${limit}:${category}`
- NO local in-memory caching
- NO read replicas
- NO cache warming
- Keep it simple. We will optimize later if metrics show we need to.
```

### Паттерн 3: молчаливое проглатывание ошибок

ИИ перехватывает ошибки, но обрабатывает их не так, как задано спецификацией.

```typescript
// SPEC SAYS:
// If the database is unavailable, return 503 Service Unavailable
// with a retry-after header of 30 seconds.

// AI GENERATES:
async getUser(id: string): Promise<User> {
  try {
    return await this.prisma.user.findUniqueOrThrow({ where: { id } });
  } catch (error) {
    // AI swallowed the error with a generic handler
    this.logger.error('Failed to get user', error);
    throw new InternalServerErrorException('Something went wrong');
    // Missing: 503 status code
    // Missing: Retry-After header
    // Missing: distinction between "not found" and "database down"
  }
}
```

**Почему так происходит:** обобщённая обработка ошибок — самый частый паттерн в обучающих данных. Точная, соответствующая спецификации обработка встречается редко.

**Как предотвратить:** опишите ошибки исчерпывающе:

```markdown
### Error Handling for GET /api/users/:id

| Error Condition | Status | Body | Headers |
|----------------|--------|------|---------|
| User not found | 404 | `{"error":"USER_NOT_FOUND","message":"No user with ID {id}"}` | — |
| Database unavailable | 503 | `{"error":"SERVICE_UNAVAILABLE","message":"Please retry"}` | `Retry-After: 30` |
| Invalid ID format | 400 | `{"error":"INVALID_ID","message":"ID must be uuid format"}` | — |
| Rate limited | 429 | `{"error":"RATE_LIMITED","message":"Try again later"}` | `Retry-After: 60` |

DO NOT use generic error messages. Each error case must return
the EXACT status code and body shown above.
```

### Паттерн 4: подмена библиотеки

ИИ использует другую библиотеку, чем требует спецификация, потому что «знает» вариант лучше.

```typescript
// SPEC SAYS: Use bcrypt for password hashing
// AI GENERATES: Uses argon2 because it read that argon2 is "better"

import * as argon2 from 'argon2'; // WRONG — spec says bcrypt

async hashPassword(password: string): Promise<string> {
  return argon2.hash(password); // WRONG
}
```

**Почему так происходит:** у ИИ есть мнения о выборе библиотек из обучающих данных. Возможно, argon2 действительно лучше — но спецификация говорит не это.

**Как предотвратить:** зафиксируйте зависимости в спецификации:

```markdown
### Dependencies (EXACT — no substitutions)
- Password hashing: bcrypt (npm: bcryptjs@^2.4.3)
- JWT: jsonwebtoken (npm: jsonwebtoken@^9.0.0)
- Validation: class-validator (npm: class-validator@^0.14.0)
- ORM: Prisma (npm: @prisma/client@^5.0.0)

DO NOT substitute any of these libraries with alternatives,
even if the alternative is considered superior.
Reason: Our infrastructure team has vetted these specific
versions for security and compatibility.
```

### Паттерн 5: расползание объёма

ИИ выводит задачу за рамки, очерченные спецификацией.

```typescript
// SPEC SAYS: Add a "soft delete" to the User model
// (add a deletedAt field, modify queries to exclude deleted users)

// AI GENERATES: Complete soft-delete framework with:
// - Soft delete for ALL models (not just User)
// - Automatic query filtering middleware
// - Restoration endpoint
// - Scheduled permanent deletion job
// - Audit log for all deletions
// - Admin UI for managing deleted records
```

**Почему так происходит:** «мягкое удаление» ИИ видел реализованным комплексно много раз. Он выдаёт полное решение вместо минимального, которое просила спецификация.

**Как предотвратить:** ограничения объёма и явные границы:

```markdown
### Scope: User Soft Delete

IN SCOPE:
- Add `deletedAt: DateTime?` to User model
- Modify `findMany` queries to exclude where deletedAt is not null
- Add `DELETE /api/users/:id` that sets deletedAt

OUT OF SCOPE (do not implement):
- Soft delete for any model other than User
- Automatic query filtering middleware
- Restoration endpoint (future spec)
- Scheduled permanent deletion
- Audit logging (separate spec)
- Admin UI changes
```

---

## 3.9 Проектирование процессов ревью: PR-ревью как шлюзы утверждения

На практике большинство шлюзов утверждения реализуются через ревью пулл-реквестов. Спроектируем процесс ревью, в котором закодирован паттерн шлюза.

### Шаблон PR

```markdown
<!-- .github/pull_request_template.md -->

## Spec Reference
<!-- Link to the spec this PR implements -->
Spec: [SPEC-ID](link-to-spec)

## Changes
<!-- What this PR implements from the spec -->

## AI Confidence Report
<!-- Paste the AI's confidence report -->

### High Confidence Sections (>0.90)
<!-- These need quick review only -->

### Medium Confidence Sections (0.70-0.90)
<!-- These need careful review -->

### Low Confidence Sections (<0.70)
<!-- These need deep review — pay attention here -->

### Uncertainties
<!-- AI-reported ambiguities in the spec -->

## Spec Compliance Checklist
- [ ] All spec requirements implemented
- [ ] No features added beyond spec
- [ ] All error cases handled per spec
- [ ] All constraints respected
- [ ] Performance targets met
- [ ] Security requirements met

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Spec compliance tests pass
- [ ] Manual testing completed for low-confidence sections

## Review Request
- [ ] @tech-lead — Architecture review
- [ ] @security-engineer — Security review (if applicable)
- [ ] @domain-expert — Domain review (if applicable)
```

### Помощь в автоматическом ревью

```typescript
// scripts/pr-review-assistant.ts
// Runs in CI to help human reviewers focus their attention

import { Octokit } from '@octokit/rest';

interface ReviewSuggestion {
  file: string;
  line: number;
  severity: 'info' | 'warning' | 'critical';
  message: string;
  specReference: string;
}

async function generateReviewSuggestions(
  prNumber: number,
  specPath: string
): Promise<ReviewSuggestion[]> {
  const suggestions: ReviewSuggestion[] = [];

  // Load the spec
  const spec = await loadSpec(specPath);

  // Load the PR diff
  const diff = await loadPRDiff(prNumber);

  // Check for common deviation patterns
  for (const file of diff.files) {
    // Pattern 1: Check for imports not in the spec's dependency list
    const extraImports = findExtraImports(file, spec.dependencies);
    for (const imp of extraImports) {
      suggestions.push({
        file: file.path,
        line: imp.line,
        severity: 'warning',
        message: `Import "${imp.module}" is not listed in the spec's dependencies. `
          + `Was this intentional?`,
        specReference: 'Section: Dependencies',
      });
    }

    // Pattern 2: Check for functions not in the spec
    const extraFunctions = findExtraFunctions(file, spec.endpoints);
    for (const fn of extraFunctions) {
      suggestions.push({
        file: file.path,
        line: fn.line,
        severity: 'warning',
        message: `Function "${fn.name}" does not correspond to any spec endpoint. `
          + `Is this a helper function, or an unspecified feature?`,
        specReference: 'Section: Endpoints',
      });
    }

    // Pattern 3: Check for error handling mismatches
    const errorMismatches = findErrorMismatches(file, spec.errorHandling);
    for (const err of errorMismatches) {
      suggestions.push({
        file: file.path,
        line: err.line,
        severity: 'critical',
        message: `Error handling at this line does not match spec. `
          + `Spec expects status ${err.expectedStatus}, `
          + `code found: ${err.actualStatus}.`,
        specReference: err.specSection,
      });
    }
  }

  return suggestions;
}

// Post suggestions as PR review comments
async function postReviewComments(
  prNumber: number,
  suggestions: ReviewSuggestion[]
): Promise<void> {
  const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

  for (const suggestion of suggestions) {
    await octokit.pulls.createReviewComment({
      owner: 'org',
      repo: 'repo',
      pull_number: prNumber,
      body: `**[${suggestion.severity.toUpperCase()}]** ${suggestion.message}\n\n`
        + `_Spec reference: ${suggestion.specReference}_`,
      path: suggestion.file,
      line: suggestion.line,
      side: 'RIGHT',
    });
  }
}
```

---

## 3.10 Паттерн эскалации: когда ИИ должен остановиться и попросить помощи

Одно из самого важного, чему можно научить ИИ через спецификацию, — когда останавливаться. Не каждую проблему стоит решать автономно. Некоторые требуют участия человека, и хорошо спроектированная спецификация говорит об этом явно.

### Триггеры эскалации в спецификации

```markdown
## Escalation Rules

### STOP AND ASK if:
1. The spec is ambiguous and you see two valid interpretations
   → Present both interpretations and ask which to implement

2. The implementation requires a library not listed in dependencies
   → Present the need and suggest options. Do not install anything.

3. A test fails and the fix would require changing the spec
   → Report the failing test and the spec conflict. Do not change the spec.

4. Performance benchmarks cannot meet the SLA
   → Report the bottleneck and suggest optimizations. Do not implement
     optimizations without approval.

5. A security concern is identified during implementation
   → Report the concern immediately. Do not proceed with implementation
     of the affected section.

6. The implementation would require changing a file marked as
   "do not modify" in the spec
   → Report the conflict. The spec may need updating, or the
     implementation approach may need to change.

### PROCEED AUTONOMOUSLY if:
1. The spec is clear and unambiguous
2. All dependencies are available
3. All tests pass
4. Performance benchmarks meet SLA
5. No security concerns identified
6. No file conflicts
```

### Протокол эскалации на практике

```typescript
// The AI's decision loop during spec execution

interface EscalationDecision {
  shouldEscalate: boolean;
  reason?: string;
  context?: string;
  suggestedAction?: string;
  urgency: 'low' | 'medium' | 'high' | 'critical';
}

function evaluateEscalation(
  specSection: string,
  implementationState: object,
  testResults: object
): EscalationDecision {
  // Check for ambiguity
  if (hasMultipleValidInterpretations(specSection)) {
    return {
      shouldEscalate: true,
      reason: 'Spec ambiguity detected',
      context: `Section "${specSection}" can be interpreted in multiple ways.`,
      suggestedAction: 'Please clarify the intended behavior.',
      urgency: 'medium',
    };
  }

  // Check for dependency issues
  if (requiresUnlistedDependency(specSection)) {
    return {
      shouldEscalate: true,
      reason: 'Unlisted dependency required',
      context: `Implementation requires a package not in the spec.`,
      suggestedAction: 'Approve adding the dependency or suggest an alternative approach.',
      urgency: 'low',
    };
  }

  // Check for security concerns
  if (hasSecurityImplication(specSection)) {
    return {
      shouldEscalate: true,
      reason: 'Security-sensitive implementation',
      context: `This section involves authentication, authorization, or data handling.`,
      suggestedAction: 'Security review required before proceeding.',
      urgency: 'high',
    };
  }

  // Check for test failures
  if (hasTestFailures(specSection)) {
    return {
      shouldEscalate: true,
      reason: 'Test failures require spec clarification',
      context: `Tests are failing in ways that suggest the spec may be incomplete.`,
      suggestedAction: 'Review failing tests and update spec if needed.',
      urgency: 'high',
    };
  }

  return { shouldEscalate: false, urgency: 'low' };
}
```

---

## 3.11 Обратная связь в спецификации: явные маркеры «сверить с человеком»

Самая практичная техника разработки с человеком в контуре — встраивать маркеры ревью прямо в спецификацию. Они говорят ИИ (и человеку-ревьюеру), где именно нужно человеческое суждение.

```markdown
## Feature Spec: Product Recommendation Engine

### 3.1 Data Collection [AUTO]
Collect user browsing history and purchase history from the events table.
Standard SQL query, well-defined schema.

### 3.2 Similarity Calculation [AUTO]
Calculate product similarity using cosine similarity on TF-IDF vectors
of product descriptions.

### 3.3 Recommendation Ranking [HUMAN-CHECK: business-logic]
Rank recommendations using the following weights:
- Similarity score: 0.4
- Purchase probability: 0.3
- Margin contribution: 0.2
- Inventory level: 0.1

> **CHECK WITH HUMAN:** These weights significantly affect revenue.
> Before deploying, run the recommendation engine against the last
> 30 days of data and produce a report showing:
> 1. Top 10 recommended products per category
> 2. Estimated revenue impact vs current recommendations
> 3. Diversity score (are we over-recommending popular items?)
>
> A product manager must review this report before production deployment.

### 3.4 Filtering [HUMAN-CHECK: compliance]
Filter out products that are:
- Out of stock
- Age-restricted (if user age unknown)
- Geographically restricted

> **CHECK WITH HUMAN:** Geographic restrictions vary by jurisdiction.
> Legal team must verify the filtering rules for each supported region
> before launch. Do not deploy to any new region without legal sign-off.

### 3.5 Presentation [AUTO]
Return the top 8 recommendations as ProductDTO objects with
a `recommendationScore` field added.

### 3.6 A/B Testing [HUMAN-CHECK: experiment-design]
Implement A/B testing framework for recommendation algorithm variants.

> **CHECK WITH HUMAN:** A/B test design requires statistical review.
> Data science team must approve:
> 1. Sample size calculation
> 2. Test duration
> 3. Success metrics
> 4. Guardrail metrics (metrics that must NOT degrade)
```

### Таксономия маркеров

```typescript
// Standard markers for spec sections

type HumanCheckMarker =
  | 'HUMAN-CHECK: business-logic'    // Business decisions
  | 'HUMAN-CHECK: compliance'        // Legal/regulatory
  | 'HUMAN-CHECK: security'          // Security implications
  | 'HUMAN-CHECK: ux-copy'           // User-facing text
  | 'HUMAN-CHECK: data-handling'     // PII, sensitive data
  | 'HUMAN-CHECK: experiment-design' // A/B tests, experiments
  | 'HUMAN-CHECK: cost-impact'       // Financial implications
  | 'HUMAN-CHECK: external-api'      // Third-party integrations
  | 'HUMAN-CHECK: accessibility'     // A11y requirements
  | 'HUMAN-CHECK: performance'       // Performance-critical paths
  | 'AUTO';                          // Safe for full automation

// Processing markers
function processSpecSection(
  section: string,
  marker: HumanCheckMarker
): { action: 'proceed' | 'pause'; reviewer?: string } {
  if (marker === 'AUTO') {
    return { action: 'proceed' };
  }

  const reviewerMap: Record<string, string> = {
    'HUMAN-CHECK: business-logic': 'product-manager',
    'HUMAN-CHECK: compliance': 'legal-team',
    'HUMAN-CHECK: security': 'security-engineer',
    'HUMAN-CHECK: ux-copy': 'ux-writer',
    'HUMAN-CHECK: data-handling': 'privacy-engineer',
    'HUMAN-CHECK: experiment-design': 'data-scientist',
    'HUMAN-CHECK: cost-impact': 'engineering-manager',
    'HUMAN-CHECK: external-api': 'tech-lead',
    'HUMAN-CHECK: accessibility': 'a11y-specialist',
    'HUMAN-CHECK: performance': 'performance-engineer',
  };

  return {
    action: 'pause',
    reviewer: reviewerMap[marker] || 'tech-lead',
  };
}
```

---

## 3.12 Баланс между скоростью и безопасностью

В SDD есть врождённое напряжение между скоростью и безопасностью. Больше шлюзов — безопаснее, но медленнее. Меньше шлюзов — быстрее, но рискованнее. Искусство в том, чтобы найти баланс под свой контекст.

### Рамка «риск — скорость»

```
                    HIGH RISK
                        │
         ┌──────────────┼──────────────┐
         │   REGULATED   │   CRITICAL   │
         │   INDUSTRIES  │   PATH       │
         │              │              │
         │  Healthcare   │  Auth system │
         │  Finance      │  Payment flow│
         │  Aerospace    │  Data delete │
         │              │              │
         │  → Many gates │  → Key gates │
         │  → Slow is OK │  → Fast where│
         │              │    safe      │
  LOW    ├──────────────┼──────────────┤  HIGH
  SPEED  │   LEGACY     │   GREENFIELD │  SPEED
         │   MIGRATION  │   FEATURE    │
         │              │              │
         │  Known system │  New code    │
         │  Many unknowns│  Clean spec  │
         │              │              │
         │  → Phase gates│  → Minimal   │
         │  → Careful    │    gates     │
         │              │  → Ship fast  │
         └──────────────┼──────────────┘
                        │
                    LOW RISK
```

### Калибровка шлюзов под свой контекст

```markdown
## Gate Calibration Guide

### Startup (speed-optimized)
- Gate only security and data handling
- Auto-approve all mechanical code generation
- Weekly batch review for everything else
- Accept higher risk for faster iteration

### Scale-up (balanced)
- Gate security, data, and business logic
- Peer review for all PRs
- Domain expert review for specialized areas
- SLA: 24-hour review turnaround

### Enterprise (safety-optimized)
- Gate everything above plus compliance and architecture
- Multi-level review for all changes
- Mandatory security scanning
- Change advisory board for infrastructure changes
- SLA: formal review cycles (weekly or bi-weekly)

### Regulated Industry (compliance-first)
- All of the above plus regulatory approval
- Audit trail for every change
- Formal sign-off with electronic signatures
- Change freeze periods around critical business events
- Third-party security audits for major changes
```

---

## 3.13 Как тренировать себя как ревьюера спецификаций

Ревью кода, сгенерированного ИИ, — другой навык, чем ревью кода человека. Люди ошибаются предсказуемо: опечатки, ошибки на единицу, забытая проверка на null. ИИ ошибается иначе: правдоподобная, но неверная логика, незаметное расползание объёма, уверенное использование не той библиотеки.

### Чек-лист ревьюера спецификаций

```markdown
## Spec Review Checklist

### 1. Spec Compliance (most important)
- [ ] Does the code do EXACTLY what the spec says?
- [ ] Does the code do ONLY what the spec says? (no extras)
- [ ] Are all constraints from the spec respected?
- [ ] Are all error cases handled per spec?

### 2. Deviation Detection
- [ ] Are there any imports not in the spec's dependency list?
- [ ] Are there any functions/methods not in the spec?
- [ ] Are there any side effects not in the spec?
- [ ] Does the code make assumptions not stated in the spec?

### 3. Edge Case Coverage
- [ ] What happens with empty inputs?
- [ ] What happens with maximum-size inputs?
- [ ] What happens when dependencies fail?
- [ ] What happens under concurrent access?

### 4. Security Review
- [ ] Is all user input validated?
- [ ] Are all queries parameterized?
- [ ] Is authentication/authorization properly enforced?
- [ ] Are secrets properly managed?

### 5. Performance Review
- [ ] Are there N+1 query patterns?
- [ ] Is pagination properly implemented?
- [ ] Are expensive operations cached per spec?
- [ ] Are there unnecessary database calls?

### 6. Readability and Maintenance
- [ ] Is the code readable by a human?
- [ ] Are variable names meaningful?
- [ ] Is the code properly commented?
- [ ] Would a new team member understand this code?
```

### Наращивание ревьюерской мышцы

```markdown
## 30-Day Spec Review Training Plan

### Week 1: Pattern Recognition
- Day 1-2: Review 5 AI-generated PRs. Identify all deviations.
- Day 3-4: Categorize deviations (helpful addition, premature
  optimization, error swallow, library substitution, scope creep).
- Day 5: Write down the 3 most common deviations you found.

### Week 2: Adversarial Thinking
- Day 1-2: For each spec, list 5 ways the AI could misinterpret it.
- Day 3-4: Intentionally write an ambiguous spec. See how the AI
  interprets it. Learn from the ambiguity.
- Day 5: Rewrite the spec to eliminate all ambiguity.

### Week 3: Speed Training
- Day 1-2: Time yourself reviewing a PR. Target: 30 minutes for
  a 200-line PR.
- Day 3-4: Focus on the low-confidence sections first. Skip
  high-confidence sections on first pass.
- Day 5: Practice the "two-pass" technique: first pass for
  spec compliance, second pass for edge cases.

### Week 4: Calibration
- Day 1-2: Compare your review findings with another reviewer.
  What did you miss? What did they miss?
- Day 3-4: Track your false positive rate (things you flagged
  that were actually fine).
- Day 5: Adjust your mental model. Are you too strict? Too lenient?
```

---

## 3.14 Будущее коллаборации человека и ИИ: от ревьюера к архитектору

По мере роста возможностей ИИ роль человека в разработке ПО смещается. Понимание этой траектории помогает вкладывать обучение в нужные навыки.

### Эволюция ролей

```
2023: Human writes code, AI assists
      Human: 80% execution, 20% design
      AI: Autocomplete, code suggestions

2024: Human writes prompts, AI writes code
      Human: 50% execution, 50% design
      AI: Code generation from natural language

2025: Human writes specs, AI builds systems
      Human: 20% execution, 80% design
      AI: Full implementation from structured specs

2026: Human architects systems, AI executes and self-validates
      Human: 5% execution, 95% design and oversight
      AI: Implementation + testing + documentation + deployment

2027+: Human defines outcomes, AI designs and builds
      Human: 0% execution, 100% vision and judgment
      AI: Architecture + implementation + validation + maintenance
```

### Навыки, которые растут в цене

```markdown
## Skills for the SDD Architect (2026 and beyond)

### Increasing in Value
1. **Systems thinking** — Understanding how components interact
2. **Specification writing** — Precise, unambiguous communication
3. **Risk assessment** — Identifying what can go wrong
4. **Domain expertise** — Deep knowledge of your business domain
5. **Ethical judgment** — Knowing what should be built, not just what can
6. **Review and evaluation** — Assessing AI output quality
7. **Communication** — Explaining technical decisions to stakeholders
8. **Architecture** — Designing systems that are spec-friendly

### Stable in Value
1. **Debugging** — When specs fail, you need to understand why
2. **Performance optimization** — AI can optimize, but you set targets
3. **Security** — AI assists, but security requires adversarial thinking
4. **Testing strategy** — What to test is a design decision

### Decreasing in Value (but not to zero)
1. **Syntax knowledge** — AI handles language specifics
2. **Boilerplate writing** — Generated from specs
3. **Documentation writing** — Generated from specs
4. **Manual testing** — Increasingly automated
5. **Code formatting** — Solved by tooling
```

> **Заметка профессора:** Заметьте: навыки, растущие в цене, — все фундаментально человеческие: суждение, коммуникация, этика, экспертиза в предметной области. Дешевеют те, что можно формализовать в правила. Это не совпадение. Формализовать можно ровно то, что можно специфицировать, а что можно специфицировать — можно автоматизировать. Остаётся всё, что сопротивляется формализации, — туда и стоит направлять своё развитие.

---

## 3.15 Итоговый синтез курса: собираем все 5 модулей

Отступим на шаг назад и посмотрим на общую картину того, что вы узнали.

### Модуль 1: основы — мышление контрактами

Вы узнали, что спецификация — контракт между человеком (который знает, что нужно построить) и ИИ (который знает, как строить). Вы разобрали анатомию микроспецификации: контекст, цель и ограничения. Вы поняли, что естественный язык слишком «протекает» для сложных систем, и что решение — структурированные спецификации.

**Главный принцип:** спецификация — единственный источник истины.

### Модуль 2: определение архитектуры

Вы освоили проектирование от схемы, контракты компонентов, чертёж API и спецификации управления состоянием. Вы научились описывать форму данных до написания функций, задавать поведение компонента без описания стилей и чертить контракты API с явной обработкой ошибок.

**Главный принцип:** определите «что» и ограничения; «как» пусть решает ИИ.

### Модуль 3: валидация и петля обратной связи

Вы разобрали связь «спецификация — тест», автоматический линтинг замысла и управление контекстным окном. Вы узнали, что набор тестов выводится из спецификации, а не пишется отдельно. Вы научились дробить большие системы в реестр спецификаций, уважающих лимиты контекстного окна.

**Главный принцип:** что не тестируется, то не специфицировано.

### Модуль 4: продвинутая оркестрация и агенты

Вы прошли многоагентные процессы (архитектор, разработчик, критик), эволюционные спецификации под меняющиеся требования и средозависимые спецификации. Вы поняли, что сложные системы требуют нескольких ИИ-агентов, работающих вместе, у каждого своя роль и своя версия спецификации.

**Главный принцип:** ИИ нужно оркестрировать, а не просто инструктировать.

### Модуль 5: сопровождение и масштабирование

Вы изучили спецификацию рефакторинга (как приручить легаси-системы), документацию как код (как спецификации убивают устаревшие доки) и человека в контуре (где человеческое суждение незаменимо). Вы поняли, что самые сложные спецификации — не для новых систем, а для существующих; что документация и спецификация должны быть одним артефактом; и что роль человека — не писать код, а принимать решения, которые никакая спецификация не вместит.

**Главный принцип:** ценность человека в суждении, а не в исполнении.

### Полный процесс SDD

```
┌─────────────────────────────────────────────────────────────┐
│                    THE SDD LIFECYCLE                         │
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │  HUMAN   │───▶│   SPEC   │───▶│    AI    │             │
│  │ Architect│    │ Document │    │ Executor │             │
│  └──────────┘    └──────────┘    └──────────┘             │
│       │               │               │                    │
│       │               │               ▼                    │
│       │               │         ┌──────────┐              │
│       │               │         │   CODE   │              │
│       │               │         │  + TESTS │              │
│       │               │         │  + DOCS  │              │
│       │               │         └──────────┘              │
│       │               │               │                    │
│       │               │               ▼                    │
│       │               │         ┌──────────┐              │
│       │               │         │ VALIDATE │              │
│       │               │         │ (CI/CD)  │              │
│       │               │         └──────────┘              │
│       │               │               │                    │
│       │               │          Pass │ Fail               │
│       │               │           │   │                    │
│       │               │           ▼   ▼                    │
│       │               │     ┌─────┐ ┌─────┐              │
│       │               │     │GATE │ │LOOP │              │
│       │               │     │Human│ │Back │              │
│       │               │     │Review│ │to AI│              │
│       │               │     └──┬──┘ └──┬──┘              │
│       │               │        │       │                   │
│       │    ┌──────────┘        │       │                   │
│       │    │  Spec Update      │       │                   │
│       │    │  (if needed)      │       │                   │
│       ▼    ▼                   ▼       │                   │
│  ┌────────────┐          ┌──────────┐  │                  │
│  │  FEEDBACK  │◀─────────│  DEPLOY  │  │                  │
│  │   LOOP     │          │          │  │                  │
│  └────────────┘          └──────────┘  │                  │
│       │                                │                   │
│       └────────────────────────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3.16 Модель зрелости SDD: где вы на этом пути

Как и любая дисциплина, владение SDD развивается этапами. Используйте эту модель, чтобы оценить текущий уровень и понять, что развивать дальше.

### Уровень 1: осведомлённость о спецификациях

**Особенности:**
- Спецификации пишутся эпизодически, обычно после кода
- Спецификации неформальны и часто неполны
- ИИ используется для генерации кода, но не системно
- Тестирование отделено от спецификации
- Документация ведётся вручную

**Признаки:**
- Спецификации живут в вики, которую никто не читает
- Вы всё ещё считаете промпты основной моделью работы с ИИ
- Тесты писались независимо от спецификации
- Документация всегда устарела

**Как двигаться дальше:** начните писать спецификации до кода. Используйте интерфейсы TypeScript как формат спецификации. Доведите дисциплину spec-first хотя бы на одном проекте.

### Уровень 2: спецификация управляет разработкой

**Особенности:**
- Спецификации пишутся до реализации
- ИИ системно генерирует код из спецификаций
- Тесты выводятся из спецификаций
- Спецификации следуют единому формату
- Процесс ревью ссылается на спецификацию

**Признаки:**
- У вас есть шаблон спецификации для каждой функции
- PR ссылаются на реализуемую спецификацию
- Тесты падают, когда код отклоняется от спецификации
- Вы можете отдать спецификацию любой модели и получить рабочий результат

**Как двигаться дальше:** вложитесь в инфраструктуру валидации. Постройте проверки CI на соответствие спецификации. Начните генерировать документацию из спецификаций. Внедрите оценку уверенности.

### Уровень 3: оптимизация через спецификации

**Особенности:**
- Полная интеграция в CI/CD с валидацией спецификаций
- Документация генерируется из спецификаций
- Многоагентные процессы (архитектор, разработчик, критик)
- Шлюзы утверждения на соответствующих уровнях риска
- Петли обратной связи уточняют спецификации по продовым данным

**Признаки:**
- Документация не устаревает, потому что генерируется
- Вы точно знаете, где ставить шлюзы человеческого ревью
- CI автоматически ловит расхождение спецификации и кода
- Вы умеете рефакторить легаси-системы спецификационными техниками

**Как двигаться дальше:** масштабируйте SDD на всю организацию. Стройте общие библиотеки спецификаций. Создавайте корпоративные стандарты качества спецификаций. Обучайте команду ревью спецификаций.

### Уровень 4: спецификация как родной язык

**Особенности:**
- Организация мыслит спецификациями, а не кодом
- Спецификации — главный артефакт на совещаниях по планированию
- Неинженерные заказчики читают спецификации и вносят вклад в них
- ИИ-агенты работают автономно в границах спецификации
- Человеческие усилия сосредоточены на проектировании и суждении

**Признаки:**
- Продакт-менеджеры пишут черновики спецификаций
- Планирование спринта — это ревью спецификаций
- Новые члены команды вводятся в работу через спецификации, а не код
- Вы тратите больше времени на проектирование спецификаций, чем на ревью кода
- Вопрос «кто написал код» не имеет значения — важна спецификация

---

## 3.17 Что дальше: траектория развития ИИ и эволюция SDD

Ландшафт ИИ меняется стремительно. Подумаем, как SDD придётся адаптироваться по мере роста возможностей ИИ.

### Ближайшее время (2026–2027): ИИ как надёжный исполнитель

Модели Anthropic (Claude), OpenAI (GPT), Google (Gemini) и Meta (Llama) становятся всё надёжнее в исполнении чётко заданных спецификаций. Ближайшая эволюция SDD — в сторону:

- **богаче форматы спецификаций**, вмещающие больше нюансов (визуальные, поведенческие, производительные)
- **лучшие инструменты валидации**, автоматически ловящие больше паттернов отклонений
- **IDE, понимающие спецификации** — они видят ваш контекст и предупреждают, когда код расходится со спецификацией
- **межмодельная переносимость** — спецификации, которые исполнит любая модель, снижают зависимость от вендора

### Среднесрочно (2027–2029): ИИ как со-архитектор

Когда модели становятся способны на рассуждение более высокого уровня, процесс SDD смещается:

- **ИИ предлагает улучшения спецификаций** на основе паттернов, увиденных в тысячах проектов
- **Спецификации становятся двунаправленными** — ИИ может предлагать правки по итогам реализации
- **Автоматическое тестирование спецификаций** — ИИ генерирует состязательные тест-кейсы для спецификации до написания кода
- **Маркетплейсы спецификаций** — организации делятся шаблонами типовых паттернов

### Долгосрочно (2029+): ИИ как проектировщик систем

Предельная эволюция — ИИ-системы, которые проектируют архитектуры из целей высокого уровня:

- **спецификации результата** заменяют спецификации реализации: вы описываете, чего система должна достичь, а не как
- **самовосстанавливающиеся системы**, которые замечают расхождение со спецификацией и правят себя сами
- **непрерывная спецификация** — спецификации эволюционируют автоматически по паттернам использования и бизнес-метрикам
- **роль человека становится чисто стратегической** — постановка целей организации, этических границ и бизнес-приоритетов

### Что остаётся неизменным

Как бы ни развивался ИИ, некоторые принципы SDD останутся:

1. **Ясность замысла важнее объёма инструкций.** Чёткая и краткая спецификация всегда обойдёт многословную и двусмысленную.
2. **Валидация не обсуждается.** Как бы хорош ни стал ИИ, результат нужно проверять.
3. **Человеческое суждение в критических точках.** Самые важные решения — этика, приоритеты, компромиссы — всегда останутся за людьми.
4. **Спецификация — это контракт.** Границе между замыслом человека и исполнением машины нужен формальный интерфейс.
5. **Итеративное уточнение.** Ни одна спецификация не идеальна с первого черновика. Петля обратной связи постоянна.

---

## 3.18 Заключительные мысли

Мы начали курс с простого наблюдения: естественный язык слишком «протекает» для сложных систем. Заканчиваем более глубоким: **спецификация — не просто инструмент общения с ИИ, а инструмент прояснения собственного мышления.**

Когда вы пишете спецификацию, вас заставляют ответить на вопросы, которые иначе можно отложить: что именно должен вернуть этот эндпоинт, когда база недоступна? Что конкретно значит «релевантность поиска» для наших пользователей? Кому можно удалять запись и что должно происходить с её зависимостями?

Эти вопросы есть независимо от того, пишете вы спецификацию или нет. Разница в том, что без спецификации вы обнаруживаете их во время реализации — когда менять курс дорого, когда дедлайн уже близко и когда соблазн «просто сделать, чтобы работало» огромен.

Со спецификацией вы обнаруживаете эти вопросы на этапе проектирования — когда изменения дешевы, когда единственная инвестиция — мышление, и когда сделать правильно важнее, чем сделать побыстрее.

ИИ — мощный исполнитель. Но он хорош ровно настолько, насколько хороши его инструкции. И качество этих инструкций полностью в ваших руках.

> **Манифест SDD:**
>
> Мы верим, что качество ПО начинается с качества спецификаций.
>
> Мы верим, что высший вклад человека — в проектировании и суждении, а не в исполнении.
>
> Мы верим, что документация, тесты и реализация должны происходить из единого источника истины.
>
> Мы верим, что человеческий надзор — не ограничение, а возможность — та самая, что обеспечивает служение систем человеческим нуждам.
>
> Мы верим, что спецификация — не бюрократия. Это инженерия.
>
> И мы верим по существу, что:
>
> **«Если ИИ не смог построить это правильно, вина в спецификации, а не в коде».**

---

### Финальное упражнение: самооценка по SDD

Прежде чем закрыть книгу, уделите этому упражнению 30 минут.

**Часть 1: рефлексия (10 минут)**

1. Какая концепция курса удивила вас больше всего?
2. В каком модуле вы чувствуете себя увереннее всего? А меньше всего?
3. Какую практику из курса вы внедрите немедленно?
4. Какая практика вызывает у вас скепсис?

**Часть 2: оценка (10 минут)**

Оцените себя по модели зрелости SDD (раздел 3.16):
- Где вы сейчас?
- Где хотите быть через 6 месяцев?
- Какие конкретные шаги туда приведут?

**Часть 3: обязательство (10 минут)**

Напишите личную спецификацию внедрения SDD. Да, спецификацию о внедрении спецификаций. В неё должно войти:

```markdown
# Personal SDD Adoption Spec

## Context
[Where you are now in your development practice]

## Objective
[Where you want to be in 6 months]

## Constraints
[Time limitations, team dynamics, existing processes]

## Phase 1: Foundation (Month 1-2)
[Specific practices to adopt]

## Phase 2: Integration (Month 3-4)
[How to integrate SDD into your daily workflow]

## Phase 3: Mastery (Month 5-6)
[Advanced practices and team-level adoption]

## Approval Gate
[Who will hold you accountable?]
[When will you review progress?]
```

---

## Эпилог: слово от вашего профессора

> *Вы дошли до конца. Это немало. Теперь у вас есть рамка для создания ПО более дисциплинированного, надёжного и поддерживаемого, чем то, что большинство инженеров делает за всю карьеру.*

> *Но рамка хороша ровно настолько, насколько хорош её практик. Методология SDD не улучшит ваше ПО автоматически. Она улучшит его, если применять её строго, терпеливо и интеллектуально честно.*

> *Соблазн будет всегда: пропустить спецификацию, «просто быстро закодить», убедить себя, что эта функция достаточно проста и спецификация ей не нужна. Сопротивляйтесь. Самые простые на вид функции часто несут больше всего скрытой сложности. А спецификации, которые кажутся ненужными, часто предотвращают самые дорогие ошибки.*

> *Оставлю вам одну последнюю мысль. В мире, где ИИ умеет писать код, самый ценный навык — не писать код, а знать, что и зачем строить. Именно это вмещает спецификация. Именно это делает вас незаменимым.*

> *Идите и постройте что-нибудь выдающееся. И начните со спецификации.*

---

**Конец модуля 05: сопровождение и масштабирование**

**Конец курса: освоение разработки через спецификации (SDD)**

---

[← Оглавление курса](../INDEX.ru.md) · [← Глава 2: Документация как код](CHAPTER_02.ru.md) · [Начать курс заново →](../MODULE_01/CHAPTER_01.ru.md)
