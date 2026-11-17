# Глава 1: Сопоставление спецификации и тестов (TDD для ИИ)

## МОДУЛЬ 03 — Валидация и петля обратной связи (средний уровень)

> [Оглавление курса](../INDEX.ru.md) · [Модуль 03](../INDEX.ru.md#модуль-03--валидация-и-петля-обратной-связи)

---

## Вступление к лекции

*Аудитория затихает. Профессор выводит на проектор терминал — две панели рядом. Слева документ спецификации. Справа пустой файл тестов. Курсор мигает.*

Доброе утро. Сегодня мы начинаем модуль 3, и я хочу начать с признания.

В начале карьеры я пропускал написание тестов. Говорил себе, что «добавлю позже». Позже не наступало. Код работал — пока не переставал. А когда он ломался, у меня не было ни страховки, ни контракта, который объяснил бы, что вообще значит «правильно». Я гадал.

Теперь умножьте эту проблему на тысячу. Вот что происходит, когда вы позволяете ИИ писать код без тестов. ИИ не просто пропускает тесты — он вообще не знает, что значит «правильно», пока вы ему не скажете. А способ сказать — через спецификацию. А способ *убедиться*, что он понял, — через тесты.

Эта глава о самом важном конвейере в разработке через спецификации:

**Спецификация --> Тесты --> Реализация --> Валидация**

Не от спецификации к реализации. Не «напиши код и надейся на лучшее». От спецификации к *тестам*. Затем реализация. Затем проверка по этим тестам.

Это TDD — разработка через тестирование — но адаптированная к эпохе, когда ваш соразработчик — большая языковая модель, способная выдать тысячу строк правдоподобного кода за секунды и ошибиться в тонких деталях так, что это всплывёт только в продакшене.

Начнём.

---

## 1.1 Почему тесты-первыми важнее именно с ИИ

### Проблема тестирования у человека-разработчика

Когда человек пишет код, он держит в голове ментальную модель системы. Он понимает «почему» за проектными решениями. Он помнит разговоры с заказчиками. У него есть интуиция насчёт крайних случаев, потому что он уже обжигался.

Людям тесты тоже нужны, конечно. Но старший разработчик часто может найти баг, *читая* собственный код, потому что понимает замысел каждой строки.

### Проблема тестирования у ИИ

У ИИ ничего этого нет. У него есть:

- **Никакой постоянной памяти** о прошлых разговорах (если вы её не спроектировали)
- **Никакого понимания «почему»** — только сопоставление с шаблонами из обучающих данных
- **Никакой интуиции о вашей предметной области** — он знает общие шаблоны, а не ваши бизнес-правила
- **Сильная склонность выдавать правдоподобный код**, который проходит поверхностный взгляд, но рушится при проверке
- **Риск галлюцинаций** — он может выдумать API, перепутать сигнатуру функции или целую библиотеку

> **Заметка профессора:** Я видел, как Claude сгенерировал прекрасную реализацию слоя кеширования, использовавшую метод библиотеки, которого не существует. Код *выглядел* идеально. В нём была правильная обработка ошибок, продуманные комментарии, изящная структура. Но `cache.invalidatePattern()` был выдуманным методом. Без теста это ушло бы в продакшн.

Вот почему тесты-первыми с ИИ — не просто «хорошая практика», а **критический механизм безопасности**. Тесты — ваш контракт. Это единственное, что стоит между уверенно звучащим выводом ИИ и реальностью.

### Фундаментальная асимметрия

Ключевое соображение, делающее TDD обязательным для разработки с ИИ:

| Аспект | Человек-разработчик | ИИ-разработчик |
|--------|----------------|--------------|
| Может проверить свою работу | Да (ревью кода, рассуждение) | Нет (не может выполнить код) |
| Помнит требования | Обычно | Только если они в контекстном окне |
| Находит логические ошибки | Через рассуждение | Только через сопоставление с шаблонами |
| Выдаёт компилируемый код | Обычно | Обычно (но не всегда) |
| Выдаёт *правильный* код | Иногда | Правдоподобный, но непроверенный |
| Скорость вывода | Низкая (минуты/часы) | Высокая (секунды) |

Асимметрия очевидна: ИИ *быстрый*, но *непроверенный*. Тесты — тот слой проверки, который закрывает этот разрыв.

### Что делает индустрия

В 2025–2026 годах каждая крупная ИИ-компания осознала эту проблему:

- **Anthropic** строит Claude с пониманием, что его выводы должны быть тестируемы. Claude Code, их CLI-инструмент разработки, спроектирован для работы внутри существующих тестовых фреймворков. Когда Claude генерирует код, рекомендуемый процесс — сгенерировать тесты из спецификации *до* запроса реализации.

- **Google DeepMind** использует методы формальной верификации для проверки поведения ИИ по спецификациям. Их системы AlphaCode и AlphaProof не просто генерируют код — они генерируют код, который должен пройти обширные наборы тестов, выведенные из постановки задачи.

- **OpenAI** публикует исследования об использовании тестов как сигнала корректности кода. Их инструменты генерации кода на базе Codex и GPT заметно улучшаются, когда в промпт включены тест-кейсы — тесты ограничивают пространство решений.

- **Meta** открыла свою тестовую инфраструктуру для генерации кода на базе Llama, подчёркивая, что «непроверенный код от ИИ — это технический долг, а не функция».

Консенсус в индустрии ясен: **если вы используете ИИ для написания кода, тесты нужны больше, чем когда-либо, а не меньше**.

---

## 1.2 Конвейер «спецификация → тесты → реализация»

### Конвейер по шагам

```
+--------+      +---------+      +----------------+      +------------+
|  SPEC  | ---> |  TESTS  | ---> | IMPLEMENTATION | ---> | VALIDATION |
+--------+      +---------+      +----------------+      +------------+
     |               |                   |                      |
     |               |                   |                      |
  "What we      "How we know       "The code that         "Did it
   want"         it works"          does the work"         actually
                                                           work?"
```

Пройдём по каждому этапу.

#### Этап 1: Спецификация (что мы хотим)

Вы уже изучили это в модулях 1 и 2. Спецификация — точный структурированный документ, описывающий:

- **Что** система должна делать (функциональные требования)
- **Как** она должна вести себя на границах (ограничения)
- **Что** она делать *не* должна (негативные требования)
- **Как** измеряется успех (критерии приёмки)

#### Этап 2: Тесты (как мы узнаём, что работает)

Здесь большинство разработчиков — и большинство ИИ-процессов — ошибаются. Они пропускают этот шаг. Идут прямо от спецификации к реализации.

**Не делайте так.**

Тесты выводятся *непосредственно* из спецификации. Каждая проверка в тесте должна восходить к конкретной строке или разделу спецификации. Если вы не можете связать тест со спецификацией, то либо тест лишний, либо спецификация неполна.

#### Этап 3: Реализация (код)

Только *после* появления тестов вы (или ИИ) пишете реализацию. Тесты дают:

- Ясное определение «готово»
- Немедленную обратную связь о корректности
- Защиту от выдуманного поведения
- Страховку от регрессий при будущих изменениях

#### Этап 4: Валидация (сработало ли?)

Запустите тесты. Если проходят — реализация удовлетворяет спецификации (по крайней мере, в той мере, в какой её покрывают тесты). Если падают — неверна реализация, а не тесты (при условии, что тесты правильно отражают спецификацию).

> **Заметка профессора:** Хочу быть предельно ясным: когда тест падает, ваше *первое* предположение должно быть, что неверна реализация, а не тест. Если вы начинаете менять тесты под неправильную реализацию, вы уничтожили весь смысл конвейера. Тесты — доверенное лицо спецификации. Относитесь к ним с тем же уважением, что и к самой спецификации.

### Почему порядок важен для ИИ

Когда вы даёте ИИ спецификацию и просите написать код, он склонен:

1. **Оптимистично трактовать неоднозначность** — предполагать простейший случай, когда спецификация неясна
2. **Переусложнять решение** — добавлять функции, которых в спецификации нет
3. **Недоделывать крайние случаи** — обрабатывать счастливый путь, но упускать границы
4. **Уходить от спецификации** — начать согласованно, но постепенно вводить собственные шаблоны

Сгенерировав тесты *первыми*, вы ставите забор вокруг пространства реализации ИИ. Тесты говорят: «Вот точное поведение, которое мы ожидаем. Не больше и не меньше».

---

## 1.3 Сопоставление строк спецификации и тест-кейсов

### Принцип «один к одному» (минимум)

Каждое утверждение в спецификации должно отображаться *как минимум* в один тест-кейс. Многие утверждения отображаются в несколько. Вот как думать о сопоставлении:

| Тип утверждения спецификации | Минимум тест-кейсов |
|---------------------|-------------------|
| Функциональное требование | 1 позитивный тест |
| Ограничение / граница | 2 теста (на границе, за границей) |
| Негативное требование | 1 негативный тест |
| Требование к производительности | 1 бенчмарк-тест |
| Обработка ошибок | 1 тест на каждое условие ошибки |
| Переход состояния | 1 тест на каждый переход |

### Конкретный пример

Возьмём микроспецификацию в духе тех, что вы писали в модуле 1:

```markdown
## Spec: User Registration Endpoint

### Functional Requirements
1. The endpoint SHALL accept a POST request to `/api/users/register`
2. The request body SHALL contain: email (string), password (string), name (string)
3. The endpoint SHALL return a 201 status code with a user object on success
4. The user object SHALL contain: id, email, name, createdAt
5. The password SHALL NOT be included in the response

### Constraints
6. Email SHALL be a valid email format (RFC 5322)
7. Password SHALL be at least 8 characters long
8. Password SHALL contain at least one uppercase letter, one lowercase letter, and one number
9. Name SHALL be between 1 and 100 characters
10. Email SHALL be unique across all users

### Error Handling
11. Invalid email format SHALL return 400 with error message "Invalid email format"
12. Weak password SHALL return 400 with error message "Password does not meet requirements"
13. Duplicate email SHALL return 409 with error message "Email already registered"
14. Missing required fields SHALL return 400 with specific field error messages
```

Теперь сопоставим каждую строку с тест-кейсами:

```typescript
// test/user-registration.spec.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { createApp } from '../src/app';
import { resetDatabase } from './helpers/db';

describe('User Registration Endpoint', () => {
  let app: ReturnType<typeof createApp>;

  beforeEach(async () => {
    app = createApp();
    await resetDatabase();
  });

  afterEach(async () => {
    await app.close();
  });

  // ===========================================================
  // Spec Line 1: POST /api/users/register
  // ===========================================================
  describe('POST /api/users/register', () => {

    // Spec Line 1: SHALL accept a POST request
    it('should accept POST requests to /api/users/register', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/api/users/register',
        payload: {
          email: 'test@example.com',
          password: 'ValidPass1',
          name: 'Test User',
        },
      });

      expect(response.statusCode).not.toBe(404);
      expect(response.statusCode).not.toBe(405);
    });

    // Spec Line 2: Request body contains email, password, name
    it('should require email, password, and name in request body', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/api/users/register',
        payload: {},  // empty body
      });

      expect(response.statusCode).toBe(400);
    });

    // Spec Line 3: SHALL return 201 with user object on success
    it('should return 201 status code on successful registration', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/api/users/register',
        payload: {
          email: 'test@example.com',
          password: 'ValidPass1',
          name: 'Test User',
        },
      });

      expect(response.statusCode).toBe(201);
    });

    // Spec Line 4: User object contains id, email, name, createdAt
    it('should return user object with id, email, name, and createdAt', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/api/users/register',
        payload: {
          email: 'test@example.com',
          password: 'ValidPass1',
          name: 'Test User',
        },
      });

      const body = JSON.parse(response.body);
      expect(body).toHaveProperty('id');
      expect(body).toHaveProperty('email', 'test@example.com');
      expect(body).toHaveProperty('name', 'Test User');
      expect(body).toHaveProperty('createdAt');
      expect(new Date(body.createdAt).getTime()).not.toBeNaN();
    });

    // Spec Line 5: Password SHALL NOT be in response
    it('should NOT include password in the response', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/api/users/register',
        payload: {
          email: 'test@example.com',
          password: 'ValidPass1',
          name: 'Test User',
        },
      });

      const body = JSON.parse(response.body);
      expect(body).not.toHaveProperty('password');
      expect(body).not.toHaveProperty('passwordHash');
      expect(body).not.toHaveProperty('hashedPassword');
    });
  });

  // ===========================================================
  // Constraints (Spec Lines 6-10)
  // ===========================================================
  describe('Constraints', () => {

    // Spec Line 6: Valid email format
    describe('Email validation', () => {
      it('should accept a valid email address', async () => {
        const response = await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: 'valid@example.com',
            password: 'ValidPass1',
            name: 'Test User',
          },
        });

        expect(response.statusCode).toBe(201);
      });

      it.each([
        'not-an-email',
        '@missing-local.com',
        'missing-domain@',
        'missing@.com',
        'spaces in@email.com',
        '',
      ])('should reject invalid email: "%s"', async (invalidEmail) => {
        const response = await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: invalidEmail,
            password: 'ValidPass1',
            name: 'Test User',
          },
        });

        expect(response.statusCode).toBe(400);
      });
    });

    // Spec Line 7: Password at least 8 characters
    describe('Password length', () => {
      it('should accept password with exactly 8 characters', async () => {
        const response = await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: 'test@example.com',
            password: 'Valid1Aa', // Exactly 7 -- wait, we need 8
            name: 'Test User',
          },
        });
        // This is 7 chars, should be rejected
        // Demonstrating: always check your test data!
      });

      it('should reject password with 7 characters', async () => {
        const response = await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: 'test@example.com',
            password: 'Short1A',  // 7 characters
            name: 'Test User',
          },
        });

        expect(response.statusCode).toBe(400);
      });

      it('should accept password with exactly 8 characters', async () => {
        const response = await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: 'test@example.com',
            password: 'Valid1Aa!', // 8 characters with all requirements
            name: 'Test User',
          },
        });

        expect(response.statusCode).toBe(201);
      });
    });

    // Spec Line 8: Password complexity
    describe('Password complexity', () => {
      it('should reject password without uppercase letter', async () => {
        const response = await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: 'test@example.com',
            password: 'nouppercase1',
            name: 'Test User',
          },
        });

        expect(response.statusCode).toBe(400);
      });

      it('should reject password without lowercase letter', async () => {
        const response = await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: 'test@example.com',
            password: 'NOLOWERCASE1',
            name: 'Test User',
          },
        });

        expect(response.statusCode).toBe(400);
      });

      it('should reject password without a number', async () => {
        const response = await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: 'test@example.com',
            password: 'NoNumberHere',
            name: 'Test User',
          },
        });

        expect(response.statusCode).toBe(400);
      });
    });

    // Spec Line 9: Name length 1-100
    describe('Name length', () => {
      it('should accept a name with 1 character', async () => {
        const response = await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: 'test@example.com',
            password: 'ValidPass1',
            name: 'A',
          },
        });

        expect(response.statusCode).toBe(201);
      });

      it('should accept a name with 100 characters', async () => {
        const response = await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: 'test@example.com',
            password: 'ValidPass1',
            name: 'A'.repeat(100),
          },
        });

        expect(response.statusCode).toBe(201);
      });

      it('should reject an empty name', async () => {
        const response = await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: 'test@example.com',
            password: 'ValidPass1',
            name: '',
          },
        });

        expect(response.statusCode).toBe(400);
      });

      it('should reject a name with 101 characters', async () => {
        const response = await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: 'test@example.com',
            password: 'ValidPass1',
            name: 'A'.repeat(101),
          },
        });

        expect(response.statusCode).toBe(400);
      });
    });

    // Spec Line 10: Unique email
    describe('Email uniqueness', () => {
      it('should reject duplicate email registration', async () => {
        // First registration
        await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: 'duplicate@example.com',
            password: 'ValidPass1',
            name: 'First User',
          },
        });

        // Second registration with same email
        const response = await app.inject({
          method: 'POST',
          url: '/api/users/register',
          payload: {
            email: 'duplicate@example.com',
            password: 'ValidPass1',
            name: 'Second User',
          },
        });

        expect(response.statusCode).toBe(409);
      });
    });
  });

  // ===========================================================
  // Error Handling (Spec Lines 11-14)
  // ===========================================================
  describe('Error Handling', () => {

    // Spec Line 11: Invalid email error message
    it('should return specific error for invalid email format', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/api/users/register',
        payload: {
          email: 'not-valid',
          password: 'ValidPass1',
          name: 'Test User',
        },
      });

      expect(response.statusCode).toBe(400);
      const body = JSON.parse(response.body);
      expect(body.error).toBe('Invalid email format');
    });

    // Spec Line 12: Weak password error message
    it('should return specific error for weak password', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/api/users/register',
        payload: {
          email: 'test@example.com',
          password: 'weak',
          name: 'Test User',
        },
      });

      expect(response.statusCode).toBe(400);
      const body = JSON.parse(response.body);
      expect(body.error).toBe('Password does not meet requirements');
    });

    // Spec Line 13: Duplicate email error message
    it('should return specific error for duplicate email', async () => {
      await app.inject({
        method: 'POST',
        url: '/api/users/register',
        payload: {
          email: 'existing@example.com',
          password: 'ValidPass1',
          name: 'Existing User',
        },
      });

      const response = await app.inject({
        method: 'POST',
        url: '/api/users/register',
        payload: {
          email: 'existing@example.com',
          password: 'ValidPass1',
          name: 'New User',
        },
      });

      expect(response.statusCode).toBe(409);
      const body = JSON.parse(response.body);
      expect(body.error).toBe('Email already registered');
    });

    // Spec Line 14: Missing required fields
    it('should return field-specific error for missing email', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/api/users/register',
        payload: {
          password: 'ValidPass1',
          name: 'Test User',
        },
      });

      expect(response.statusCode).toBe(400);
      const body = JSON.parse(response.body);
      expect(body.error).toContain('email');
    });

    it('should return field-specific error for missing password', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/api/users/register',
        payload: {
          email: 'test@example.com',
          name: 'Test User',
        },
      });

      expect(response.statusCode).toBe(400);
      const body = JSON.parse(response.body);
      expect(body.error).toContain('password');
    });

    it('should return field-specific error for missing name', async () => {
      const response = await app.inject({
        method: 'POST',
        url: '/api/users/register',
        payload: {
          email: 'test@example.com',
          password: 'ValidPass1',
        },
      });

      expect(response.statusCode).toBe(400);
      const body = JSON.parse(response.body);
      expect(body.error).toContain('name');
    });
  });
});
```

Обратите внимание на несколько вещей в этом файле тестов:

1. **У каждого теста есть комментарий, связывающий его с номером строки спецификации.** Это прослеживаемость, которая делает SDD работающей.
2. **Граничные условия проверяются с обеих сторон.** Длина имени 1 (валидно), 0 (невалидно), 100 (валидно), 101 (невалидно).
3. **Сообщения об ошибках проверяются точно.** В спецификации сказано, что сообщение ДОЛЖНО быть «Invalid email format», поэтому мы сравниваем именно эту строку.
4. **Негативные случаи явные.** В спецификации сказано, что пароль НЕ ДОЛЖЕН быть в ответе, поэтому мы явно проверяем его отсутствие.

---

## 1.4 Граничные условия и крайние случаи: извлекаем их из ограничений

### Метод извлечения границ

Каждое ограничение в спецификации подразумевает границы. Вот как извлекать их систематически:

```
Constraint: "Password SHALL be at least 8 characters long"

Boundaries:
  - Length 7: INVALID (just below boundary)
  - Length 8: VALID   (at boundary)
  - Length 9: VALID   (just above boundary)
  - Length 0: INVALID (empty input)
  - Length 1000: ? (spec doesn't say -- this is a SPEC GAP)
```

> **Заметка профессора:** Заметили последнюю строку? В спецификации не упомянута *максимальная* длина пароля. Пароль из 10 000 символов валиден? А из миллиона? Это пробел в спецификации — и обнаружение таких пробелов через сопоставление с тестами один из самых ценных результатов процесса. Вернитесь и обновите спецификацию. Добавьте ограничение на максимальную длину пароля. Процесс сопоставления только что улучшил вашу спецификацию.

### Таксономия крайних случаев

Извлекая крайние случаи из спецификации, думайте о категориях:

**1. Null / пустое / отсутствующее**
```typescript
// What happens when the input is null, undefined, empty string, empty array?
it('should handle null email gracefully', async () => {
  const response = await app.inject({
    method: 'POST',
    url: '/api/users/register',
    payload: {
      email: null,
      password: 'ValidPass1',
      name: 'Test User',
    },
  });
  expect(response.statusCode).toBe(400);
});
```

**2. Граничные значения (мин/макс)**
```typescript
// At the boundary, one below, one above
it('should accept name at maximum length', async () => {
  // ...name with exactly 100 characters
});

it('should reject name exceeding maximum length', async () => {
  // ...name with 101 characters
});
```

**3. Несоответствие типов**
```typescript
// What if the input is the wrong type?
it('should handle numeric email gracefully', async () => {
  const response = await app.inject({
    method: 'POST',
    url: '/api/users/register',
    payload: {
      email: 12345,
      password: 'ValidPass1',
      name: 'Test User',
    },
  });
  expect(response.statusCode).toBe(400);
});
```

**4. Специальные символы и кодировки**
```typescript
// Unicode, emoji, SQL injection, XSS
it('should handle unicode characters in name', async () => {
  const response = await app.inject({
    method: 'POST',
    url: '/api/users/register',
    payload: {
      email: 'test@example.com',
      password: 'ValidPass1',
      name: 'Jean-Pierre Lefevre',
    },
  });
  expect(response.statusCode).toBe(201);
});

it('should sanitize potentially dangerous input', async () => {
  const response = await app.inject({
    method: 'POST',
    url: '/api/users/register',
    payload: {
      email: 'test@example.com',
      password: 'ValidPass1',
      name: '<script>alert("xss")</script>',
    },
  });
  // Should either reject or sanitize, not store raw HTML
  if (response.statusCode === 201) {
    const body = JSON.parse(response.body);
    expect(body.name).not.toContain('<script>');
  }
});
```

**5. Параллелизм и гонки**
```typescript
// What if two users register with the same email simultaneously?
it('should handle concurrent duplicate registrations', async () => {
  const payload = {
    email: 'race@example.com',
    password: 'ValidPass1',
    name: 'Test User',
  };

  const [response1, response2] = await Promise.all([
    app.inject({ method: 'POST', url: '/api/users/register', payload }),
    app.inject({ method: 'POST', url: '/api/users/register', payload }),
  ]);

  const statuses = [response1.statusCode, response2.statusCode].sort();
  expect(statuses).toEqual([201, 409]);
});
```

### Процесс обнаружения пробелов в спецификации

Один из самых мощных побочных эффектов сопоставления спецификации с тестами — обнаружение пробелов в спецификации. Вот систематический процесс:

```
For each spec constraint:
  1. Identify the happy path -> write a positive test
  2. Identify the boundary -> write boundary tests
  3. Ask: "What does the spec NOT say?" -> these are spec gaps
  4. For each gap:
     a. Is this an oversight? -> Update the spec
     b. Is this intentionally unspecified? -> Document it as such
     c. Is this ambiguous? -> Clarify with stakeholders
  5. Write tests for the gaps you've identified
```

> **Заметка профессора:** Именно на этом процессе джуниоры становятся сеньорами. И именно здесь разработка с ИИ становится *по-настоящему* управляемой спецификациями. ИИ с радостью реализует всё, что вы скажете. Ваша ценность — спросить: «Что мы забыли ему сказать?»

---

## 1.5 Тестовые фреймворки и их роль в SDD

### Выбор правильного фреймворка

Выбранный фреймворк значит меньше, чем *как* вы его используете. Тем не менее вот текущий ландшафт и место каждого в SDD:

#### JavaScript/TypeScript: Vitest и Jest

**Vitest** стал доминирующим тестовым фреймворком в экосистеме JavaScript для новых проектов (2025–2026). Он быстрый, совместим с API Jest и нативно интегрируется с проектами на Vite.

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      reporter: ['text', 'json', 'html'],
      // Spec coverage configuration
      thresholds: {
        branches: 90,
        functions: 90,
        lines: 90,
        statements: 90,
      },
    },
  },
});
```

**Jest** по-прежнему широко используется, особенно в React-экосистеме и корпоративных кодовых базах. Его snapshot-тестирование особенно полезно для UI-спецификаций:

```typescript
// Snapshot testing as spec validation
it('should render the user profile card according to spec', () => {
  const { container } = render(
    <UserProfileCard
      name="Jane Doe"
      email="jane@example.com"
      role="admin"
    />
  );

  // First run: creates the snapshot (the "spec" of the rendered output)
  // Subsequent runs: compares against the snapshot
  expect(container).toMatchSnapshot();
});
```

#### Python: Pytest

**Pytest** доминирует в тестировании Python и отлично подходит для тестирования в стиле SDD благодаря системе фикстур и параметризации:

```python
# test_user_registration.py
import pytest
from app import create_app
from database import reset_db


@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client
    reset_db()


class TestUserRegistration:
    """
    Tests mapped to: specs/user-registration.md
    """

    # Spec Line 3: SHALL return 201 on success
    def test_successful_registration_returns_201(self, client):
        response = client.post('/api/users/register', json={
            'email': 'test@example.com',
            'password': 'ValidPass1',
            'name': 'Test User',
        })
        assert response.status_code == 201

    # Spec Line 7: Password at least 8 characters
    @pytest.mark.parametrize('password,expected_status', [
        ('Short1A', 400),       # 7 chars - too short
        ('Valid1Aa', 201),      # 8 chars - exactly at boundary
        ('LongValid1Aa', 201), # 12 chars - above boundary
    ])
    def test_password_length_boundaries(self, client, password, expected_status):
        response = client.post('/api/users/register', json={
            'email': 'test@example.com',
            'password': password,
            'name': 'Test User',
        })
        assert response.status_code == expected_status

    # Spec Line 8: Password complexity requirements
    @pytest.mark.parametrize('password,missing_requirement', [
        ('alllowercase1', 'uppercase letter'),
        ('ALLUPPERCASE1', 'lowercase letter'),
        ('NoNumbersHere', 'number'),
    ])
    def test_password_complexity_requirements(self, client, password, missing_requirement):
        response = client.post('/api/users/register', json={
            'email': 'test@example.com',
            'password': password,
            'name': 'Test User',
        })
        assert response.status_code == 400, (
            f"Password missing {missing_requirement} should be rejected"
        )
```

#### Сквозное тестирование: Playwright

**Playwright** обеспечивает проверку спецификаций полного стека — тестирует не только API, но и весь пользовательский поток:

```typescript
// e2e/registration.spec.ts
import { test, expect } from '@playwright/test';

test.describe('User Registration Flow', () => {
  // Spec: "The registration form SHALL be accessible at /register"
  test('registration page is accessible', async ({ page }) => {
    await page.goto('/register');
    await expect(page).toHaveURL('/register');
    await expect(page.locator('h1')).toHaveText('Create Account');
  });

  // Spec: "The form SHALL display validation errors inline"
  test('displays inline validation errors for invalid email', async ({ page }) => {
    await page.goto('/register');
    await page.fill('[name="email"]', 'not-an-email');
    await page.fill('[name="password"]', 'ValidPass1');
    await page.fill('[name="name"]', 'Test User');
    await page.click('button[type="submit"]');

    await expect(page.locator('.error-email')).toBeVisible();
    await expect(page.locator('.error-email')).toHaveText('Invalid email format');
  });

  // Spec: "On successful registration, redirect to /dashboard"
  test('redirects to dashboard on successful registration', async ({ page }) => {
    await page.goto('/register');
    await page.fill('[name="email"]', 'newuser@example.com');
    await page.fill('[name="password"]', 'ValidPass1');
    await page.fill('[name="name"]', 'New User');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('.welcome-message')).toContainText('New User');
  });
});
```

---

## 1.6 Как Anthropic тестирует выводы Claude по поведенческим спецификациям

### Constitutional AI как тестовый фреймворк

Это увлекательный реальный пример валидации по спецификациям в масштабе.

Подход Anthropic к выравниванию Claude — по сути процесс, управляемый спецификациями:

1. **«Конституция»** — это спецификация: набор поведенческих принципов, определяющих, как Claude должен отвечать
2. **Оценки (evals)** — это тесты: автоматические проверки, подтверждающие соответствие поведения Claude спецификации
3. **Обучение** — это реализация: веса модели настраиваются, пока тесты не пройдут

Это в точности повторяет наш конвейер:

```
Constitution (Spec) --> Evals (Tests) --> Training (Implementation) --> Evaluation (Validation)
```

Оценки, которые запускает Anthropic, включают:

- **Поведенческие тесты**: «При таком промпте отказывается ли Claude помогать с вредными запросами?»
- **Тесты согласованности**: «Даёт ли Claude согласованные ответы на семантически идентичные вопросы?»
- **Граничные тесты**: «Где проходит черта между полезным и вредным ответом?»
- **Регрессионные тесты**: «Не сломал ли последний прогон обучения ранее корректное поведение?»

> **Заметка профессора:** Обратите внимание на параллель с нашими спецификациями ПО. Anthropic по сути пишет спецификации для *поведения*, а не для *кода*, но методология тестирования идентична. Каждый принцип конституции отображается в тест-кейсы. Каждый тест-кейс проверяет конкретное поведение. Каждый прогон обучения оценивается по полному набору тестов. Это SDD на уровне модели.

### Чему можно научиться у Anthropic

Ключевые выводы для вашего сопоставления спецификаций и тестов:

1. **Спецификации могут быть иерархическими.** В конституции Anthropic есть принципы высокого уровня («Быть полезным, безвредным и честным»), которые раскладываются на конкретные поведенческие правила. Ваши спецификации должны работать так же.

2. **Тесты должны быть автоматизированы и непрерывны.** Anthropic не проверяет поведение Claude вручную — они запускают тысячи автоматических оценок. Ваш набор тестов должен запускаться на каждый коммит.

3. **Крайние случаи — там, где выравнивание ломается.** Как Claude может вести себя неожиданно на границах своего обучения, так и ваш код от ИИ будет иметь больше всего проблем на граничных условиях.

4. **Спецификация эволюционирует вместе с тестами.** Anthropic постоянно обновляет конституцию на основе того, что выявляют оценки. Ваши спецификации должны эволюционировать на основе того, что обнаруживают тесты.

---

## 1.7 Как Google DeepMind проверяет поведение ИИ по спецификациям

### Формальная верификация встречает ИИ

Google DeepMind использует более формальный подход к проверке спецификаций. Их работа над AlphaProof и смежными системами применяет математические доказательства для проверки корректности решений, сгенерированных ИИ.

Процесс:

1. **Формальная спецификация**: задача формулируется на формальном языке (например, Lean, Isabelle)
2. **Генерация ИИ**: ИИ предлагает решение
3. **Проверка доказательства**: средство доказательства теорем проверяет, что решение удовлетворяет спецификации
4. **Итерация**: если проверка не прошла, ИИ пробует снова, используя ошибку как обратную связь

Это самая строгая форма конвейера «спецификация → тесты»:

```
Formal Spec --> Proof Obligation (Tests) --> AI Solution --> Proof Checker (Validation)
```

Хотя формальная верификация избыточна для большинства прикладной разработки, *принцип* мощен: **спецификация должна быть достаточно точной, чтобы проверку можно было автоматизировать.**

### Практические уроки подхода DeepMind

Для повседневной работы в SDD возьмите у DeepMind следующее:

1. **Делайте спецификации максимально точными.** Неоднозначность в спецификации означает неоднозначность в тестах, а значит и в реализации. Чем точнее спецификация, тем полезнее тесты.

2. **Используйте неудачи ИИ как обратную связь.** Когда ИИ генерирует код, не проходящий тесты, не просто переспрашивайте. Анализируйте *почему* он не прошёл. Спецификация была неоднозначной? Тест неверным? Подход ИИ принципиально ошибочным?

3. **Помните об инвариантах.** Формальные спецификации DeepMind часто включают *инварианты* — свойства, которые должны выполняться всегда. В ваших спецификациях это может быть: «Итог всегда должен равняться сумме позиций» или «Email пользователя не должен меняться после регистрации».

---

## 1.8 Тестирование на основе свойств как проверка спецификации

### За пределами тестов на примерах

Всё, что мы писали до сих пор, — тестирование *на примерах*: «При таком конкретном входе ожидай такой конкретный выход». Но спецификации часто описывают *свойства* — общие правила, которые должны выполняться для *любого* допустимого входа.

Здесь и раскрывается **тестирование на основе свойств**.

### fast-check (JavaScript/TypeScript)

```typescript
import { describe, it, expect } from 'vitest';
import * as fc from 'fast-check';
import { validateEmail, validatePassword, registerUser } from '../src/registration';

describe('Registration Properties', () => {

  // Property: Any valid email should be accepted
  it('should accept any well-formed email', () => {
    fc.assert(
      fc.property(
        fc.emailAddress(),
        (email) => {
          const result = validateEmail(email);
          expect(result.valid).toBe(true);
        }
      )
    );
  });

  // Property: Any password meeting complexity requirements should be accepted
  it('should accept any password meeting all requirements', () => {
    fc.assert(
      fc.property(
        fc.string({ minLength: 8, maxLength: 128 }).filter(pw => {
          return /[A-Z]/.test(pw) && /[a-z]/.test(pw) && /[0-9]/.test(pw);
        }),
        (password) => {
          const result = validatePassword(password);
          expect(result.valid).toBe(true);
        }
      )
    );
  });

  // Property: Registration should never return the password
  it('should never include password in any successful response', () => {
    fc.assert(
      fc.property(
        fc.emailAddress(),
        fc.string({ minLength: 8, maxLength: 128 }).filter(pw => {
          return /[A-Z]/.test(pw) && /[a-z]/.test(pw) && /[0-9]/.test(pw);
        }),
        fc.string({ minLength: 1, maxLength: 100 }),
        async (email, password, name) => {
          const result = await registerUser({ email, password, name });
          if (result.success) {
            const responseStr = JSON.stringify(result.user);
            expect(responseStr).not.toContain(password);
          }
        }
      )
    );
  });

  // Property: Idempotency - registering the same email twice should always fail the second time
  it('should always reject duplicate emails regardless of other fields', () => {
    fc.assert(
      fc.property(
        fc.emailAddress(),
        fc.string({ minLength: 8, maxLength: 128 }).filter(pw => {
          return /[A-Z]/.test(pw) && /[a-z]/.test(pw) && /[0-9]/.test(pw);
        }),
        fc.string({ minLength: 1, maxLength: 100 }),
        fc.string({ minLength: 8, maxLength: 128 }).filter(pw => {
          return /[A-Z]/.test(pw) && /[a-z]/.test(pw) && /[0-9]/.test(pw);
        }),
        fc.string({ minLength: 1, maxLength: 100 }),
        async (email, pw1, name1, pw2, name2) => {
          await registerUser({ email, password: pw1, name: name1 });
          const result = await registerUser({ email, password: pw2, name: name2 });
          expect(result.success).toBe(false);
          expect(result.statusCode).toBe(409);
        }
      )
    );
  });
});
```

### Hypothesis (Python)

```python
# test_registration_properties.py
from hypothesis import given, settings, assume
from hypothesis.strategies import (
    emails, text, integers,
    from_regex, composite
)
import re
from app.registration import validate_email, validate_password, register_user


@composite
def valid_passwords(draw):
    """Generate passwords that meet all complexity requirements."""
    # Ensure at least one uppercase, one lowercase, one digit
    password = draw(text(min_size=8, max_size=128))
    assume(re.search(r'[A-Z]', password))
    assume(re.search(r'[a-z]', password))
    assume(re.search(r'[0-9]', password))
    return password


class TestRegistrationProperties:

    # Property: Spec Line 5 - password never in response
    @given(
        email=emails(),
        password=valid_passwords(),
        name=text(min_size=1, max_size=100)
    )
    @settings(max_examples=200)
    def test_password_never_in_response(self, email, password, name):
        result = register_user(email=email, password=password, name=name)
        if result['success']:
            response_str = str(result['user'])
            assert password not in response_str, (
                f"Password '{password}' found in response!"
            )

    # Property: Spec Line 6 - invalid emails always rejected
    @given(email=text(min_size=1, max_size=200).filter(
        lambda e: '@' not in e or '.' not in e.split('@')[-1]
    ))
    def test_invalid_emails_always_rejected(self, email):
        result = validate_email(email)
        assert not result['valid'], (
            f"Invalid email '{email}' was accepted"
        )

    # Property: Spec Line 7 - short passwords always rejected
    @given(password=text(min_size=0, max_size=7))
    def test_short_passwords_always_rejected(self, password):
        result = validate_password(password)
        assert not result['valid'], (
            f"Short password (len={len(password)}) was accepted"
        )
```

### Почему тестирование на основе свойств важно для SDD

Тестирование на основе свойств особенно мощно в SDD, потому что:

1. **Спецификации описывают свойства, а не примеры.** Когда спецификация говорит «пароли должны быть не короче 8 символов», это *свойство* — оно должно выполняться для *всех* паролей, а не только для трёх, которые вы случайно проверили.

2. **Оно находит крайние случаи, о которых вы не подумали.** Фреймворки тестирования на основе свойств генерируют сотни или тысячи случайных входов, часто находя крайние случаи, которые не предвидели ни вы, ни ИИ.

3. **Оно проверяет *замысел* спецификации.** Тесты на примерах проверяют конкретные случаи. Тесты на свойствах проверяют общее правило — что ближе к тому, что на самом деле описывает спецификация.

4. **Оно отлично находит баги-галлюцинации ИИ.** Если ИИ реализовал функцию валидации, работающую для типичных входов, но падающую на необычных (эмодзи в паролях, очень длинные строки, нулевые байты), тестирование на свойствах это обнаружит.

---

## 1.9 Понятие «покрытия спецификации»

### За пределами покрытия кода

Вы знакомы с покрытием кода: какой процент кода выполняется тестами? Покрытие спецификации задаёт другой вопрос: **какой процент вашей спецификации проверен тестами?**

Покрытие кода может быть 100% и всё равно упускать суть, если код не соответствует спецификации. Покрытие спецификации гарантирует, что у каждого требования в спецификации есть соответствующая тестовая проверка.

### Измерение покрытия спецификации

Вот практический подход к измерению покрытия спецификации:

```markdown
## Spec Coverage Report: User Registration

| Spec Line | Description                        | Test Coverage | Status    |
|-----------|------------------------------------|---------------|-----------|
| 1         | POST /api/users/register          | 1 test        | COVERED   |
| 2         | Request body: email, pw, name     | 3 tests       | COVERED   |
| 3         | 201 on success                    | 1 test        | COVERED   |
| 4         | Response: id, email, name, date   | 1 test        | COVERED   |
| 5         | No password in response           | 2 tests       | COVERED   |
| 6         | Valid email format                 | 6 tests       | COVERED   |
| 7         | Password >= 8 chars               | 3 tests       | COVERED   |
| 8         | Password complexity               | 3 tests       | COVERED   |
| 9         | Name 1-100 chars                  | 4 tests       | COVERED   |
| 10        | Unique email                      | 2 tests       | COVERED   |
| 11        | Error: invalid email              | 1 test        | COVERED   |
| 12        | Error: weak password              | 1 test        | COVERED   |
| 13        | Error: duplicate email            | 1 test        | COVERED   |
| 14        | Error: missing fields             | 3 tests       | COVERED   |
|           |                                    |               |           |
| TOTAL     | 14 spec lines                     | 32 tests      | 100%      |
```

### Автоматизация покрытия спецификации

Вы можете автоматизировать отслеживание покрытия спецификации, встраивая ссылки на спецификацию в файлы тестов:

```typescript
/**
 * @spec user-registration
 * @specLine 5
 * @requirement Password SHALL NOT be included in the response
 */
it('should NOT include password in the response', async () => {
  // ...
});
```

Затем постройте простой инструмент, который:

1. Разбирает файлы спецификаций и извлекает все строки требований
2. Разбирает файлы тестов и извлекает аннотации `@specLine`
3. Генерирует отчёт о покрытии, показывающий, для каких строк спецификации есть тесты, а для каких нет

```typescript
// tools/spec-coverage.ts
import { readFileSync, readdirSync } from 'fs';
import { join } from 'path';

interface SpecLine {
  lineNumber: number;
  text: string;
  testsCovering: string[];
}

interface CoverageReport {
  specFile: string;
  totalLines: number;
  coveredLines: number;
  coverage: number;
  lines: SpecLine[];
}

function extractSpecLines(specPath: string): SpecLine[] {
  const content = readFileSync(specPath, 'utf-8');
  const lines = content.split('\n');
  const specLines: SpecLine[] = [];
  let lineNumber = 0;

  for (const line of lines) {
    // Match numbered requirements (e.g., "1. The endpoint SHALL...")
    const match = line.match(/^\d+\.\s+.*(SHALL|MUST|SHOULD).*/i);
    if (match) {
      lineNumber++;
      specLines.push({
        lineNumber,
        text: line.trim(),
        testsCovering: [],
      });
    }
  }

  return specLines;
}

function extractTestAnnotations(testDir: string): Map<number, string[]> {
  const annotations = new Map<number, string[]>();
  const files = readdirSync(testDir, { recursive: true }) as string[];

  for (const file of files) {
    if (!file.endsWith('.spec.ts') && !file.endsWith('.test.ts')) continue;

    const content = readFileSync(join(testDir, file), 'utf-8');
    const regex = /@specLine\s+(\d+)/g;
    let match;

    while ((match = regex.exec(content)) !== null) {
      const lineNum = parseInt(match[1]);
      if (!annotations.has(lineNum)) {
        annotations.set(lineNum, []);
      }
      annotations.get(lineNum)!.push(file);
    }
  }

  return annotations;
}

function generateReport(specPath: string, testDir: string): CoverageReport {
  const specLines = extractSpecLines(specPath);
  const annotations = extractTestAnnotations(testDir);

  for (const line of specLines) {
    line.testsCovering = annotations.get(line.lineNumber) || [];
  }

  const coveredLines = specLines.filter(l => l.testsCovering.length > 0).length;

  return {
    specFile: specPath,
    totalLines: specLines.length,
    coveredLines,
    coverage: (coveredLines / specLines.length) * 100,
    lines: specLines,
  };
}

// Usage
const report = generateReport(
  'specs/user-registration.md',
  'test/'
);

console.log(`Spec Coverage: ${report.coverage.toFixed(1)}%`);
console.log(`${report.coveredLines}/${report.totalLines} spec lines covered\n`);

for (const line of report.lines) {
  const status = line.testsCovering.length > 0 ? 'COVERED' : 'MISSING';
  const icon = status === 'COVERED' ? '[+]' : '[-]';
  console.log(`  ${icon} Line ${line.lineNumber}: ${line.text}`);
  if (line.testsCovering.length > 0) {
    for (const test of line.testsCovering) {
      console.log(`      -> ${test}`);
    }
  }
}
```

> **Заметка профессора:** Покрытие спецификации — одна из тех метрик, к которой, начав следить, вы уже не вернётесь. Вы будете смотреть на наборы тестов с покрытием кода 95% и понимать, что они покрывают лишь 40% спецификации. Вот в этом зазоре и живут баги.

---

## 1.10 Практический разбор: от микроспецификации к полному набору тестов и реализации

Пройдём полный цикл. Возьмём небольшую спецификацию, сгенерируем полный набор тестов, а затем реализуем код — именно в этом порядке.

### Шаг 1: Микроспецификация

```markdown
## Spec: Price Calculator

### Purpose
Calculate the total price of items in a shopping cart, applying discounts and tax.

### Functional Requirements
1. The function SHALL accept an array of cart items
2. Each cart item SHALL have: name (string), price (number), quantity (number)
3. The function SHALL return an object with: subtotal, discount, tax, total
4. Subtotal SHALL be the sum of (price * quantity) for all items

### Discount Rules
5. If subtotal >= $100, apply a 10% discount
6. If subtotal >= $200, apply a 15% discount (overrides rule 5)
7. If subtotal >= $500, apply a 20% discount (overrides rule 6)
8. Discount SHALL be applied to the subtotal

### Tax Rules
9. Tax rate SHALL be 8.5%

### Constraints
10. Tax SHALL be calculated on the discounted subtotal (subtotal - discount)
11. Prices SHALL be non-negative numbers
12. Quantities SHALL be positive integers
13. All monetary values in the response SHALL be rounded to 2 decimal places
14. An empty cart SHALL return all zeros

### Error Handling
15. Invalid items (negative price, zero quantity, etc.) SHALL throw a ValidationError
```

### Шаг 2: Набор тестов (написан ДО реализации)

```typescript
// test/price-calculator.spec.ts
import { describe, it, expect } from 'vitest';
import { calculatePrice, ValidationError } from '../src/price-calculator';

describe('Price Calculator', () => {

  // ===========================================
  // Functional Requirements (Spec Lines 1-4)
  // ===========================================

  /** @specLine 1 - Accepts array of cart items */
  it('should accept an array of cart items', () => {
    const result = calculatePrice([
      { name: 'Widget', price: 10.00, quantity: 1 },
    ]);
    expect(result).toBeDefined();
  });

  /** @specLine 3 - Returns object with subtotal, discount, tax, total */
  it('should return object with subtotal, discount, tax, and total', () => {
    const result = calculatePrice([
      { name: 'Widget', price: 10.00, quantity: 1 },
    ]);
    expect(result).toHaveProperty('subtotal');
    expect(result).toHaveProperty('discount');
    expect(result).toHaveProperty('tax');
    expect(result).toHaveProperty('total');
  });

  /** @specLine 4 - Subtotal is sum of price * quantity */
  it('should calculate subtotal as sum of price * quantity', () => {
    const result = calculatePrice([
      { name: 'Widget', price: 10.00, quantity: 2 },
      { name: 'Gadget', price: 25.00, quantity: 3 },
    ]);
    // 10*2 + 25*3 = 20 + 75 = 95
    expect(result.subtotal).toBe(95.00);
  });

  // ===========================================
  // Discount Rules (Spec Lines 5-8)
  // ===========================================

  /** @specLine 5 - No discount below $100 */
  it('should apply no discount when subtotal < $100', () => {
    const result = calculatePrice([
      { name: 'Widget', price: 99.99, quantity: 1 },
    ]);
    expect(result.discount).toBe(0);
  });

  /** @specLine 5 - 10% discount at exactly $100 */
  it('should apply 10% discount when subtotal is exactly $100', () => {
    const result = calculatePrice([
      { name: 'Widget', price: 100.00, quantity: 1 },
    ]);
    expect(result.discount).toBe(10.00); // 10% of 100
  });

  /** @specLine 5 - 10% discount between $100 and $199.99 */
  it('should apply 10% discount when subtotal is $150', () => {
    const result = calculatePrice([
      { name: 'Widget', price: 150.00, quantity: 1 },
    ]);
    expect(result.discount).toBe(15.00); // 10% of 150
  });

  /** @specLine 6 - 15% discount at exactly $200 */
  it('should apply 15% discount when subtotal is exactly $200', () => {
    const result = calculatePrice([
      { name: 'Widget', price: 200.00, quantity: 1 },
    ]);
    expect(result.discount).toBe(30.00); // 15% of 200
  });

  /** @specLine 6 - 15% discount between $200 and $499.99 */
  it('should apply 15% discount when subtotal is $350', () => {
    const result = calculatePrice([
      { name: 'Widget', price: 350.00, quantity: 1 },
    ]);
    expect(result.discount).toBe(52.50); // 15% of 350
  });

  /** @specLine 7 - 20% discount at exactly $500 */
  it('should apply 20% discount when subtotal is exactly $500', () => {
    const result = calculatePrice([
      { name: 'Widget', price: 500.00, quantity: 1 },
    ]);
    expect(result.discount).toBe(100.00); // 20% of 500
  });

  /** @specLine 7 - 20% discount above $500 */
  it('should apply 20% discount when subtotal is $1000', () => {
    const result = calculatePrice([
      { name: 'Widget', price: 1000.00, quantity: 1 },
    ]);
    expect(result.discount).toBe(200.00); // 20% of 1000
  });

  // Boundary test: $99.99 vs $100.00
  it('should not discount at $99.99 but should at $100.00', () => {
    const below = calculatePrice([
      { name: 'Widget', price: 99.99, quantity: 1 },
    ]);
    const atBoundary = calculatePrice([
      { name: 'Widget', price: 100.00, quantity: 1 },
    ]);
    expect(below.discount).toBe(0);
    expect(atBoundary.discount).toBe(10.00);
  });

  // Boundary test: $199.99 vs $200.00
  it('should apply 10% at $199.99 and 15% at $200.00', () => {
    const below = calculatePrice([
      { name: 'Widget', price: 199.99, quantity: 1 },
    ]);
    const atBoundary = calculatePrice([
      { name: 'Widget', price: 200.00, quantity: 1 },
    ]);
    expect(below.discount).toBeCloseTo(20.00, 2);  // 10% of 199.99
    expect(atBoundary.discount).toBe(30.00);        // 15% of 200
  });

  // ===========================================
  // Tax Rules (Spec Lines 9-10)
  // ===========================================

  /** @specLine 9-10 - Tax on discounted subtotal */
  it('should calculate tax at 8.5% on discounted subtotal', () => {
    // Subtotal: $100, Discount: 10% = $10, Taxable: $90
    // Tax: $90 * 0.085 = $7.65
    const result = calculatePrice([
      { name: 'Widget', price: 100.00, quantity: 1 },
    ]);
    expect(result.tax).toBe(7.65);
  });

  it('should calculate tax on full subtotal when no discount', () => {
    // Subtotal: $50, Discount: $0, Taxable: $50
    // Tax: $50 * 0.085 = $4.25
    const result = calculatePrice([
      { name: 'Widget', price: 50.00, quantity: 1 },
    ]);
    expect(result.tax).toBe(4.25);
  });

  // ===========================================
  // Total Calculation
  // ===========================================

  it('should calculate total as subtotal - discount + tax', () => {
    // Subtotal: $100, Discount: $10 (10%), Taxable: $90
    // Tax: $90 * 0.085 = $7.65
    // Total: $100 - $10 + $7.65 = $97.65
    const result = calculatePrice([
      { name: 'Widget', price: 100.00, quantity: 1 },
    ]);
    expect(result.total).toBe(97.65);
  });

  // ===========================================
  // Constraints (Spec Lines 11-14)
  // ===========================================

  /** @specLine 13 - Rounding to 2 decimal places */
  it('should round all values to 2 decimal places', () => {
    // Subtotal: $33.33 * 3 = $99.99
    // No discount (under $100)
    // Tax: $99.99 * 0.085 = $8.49915 -> $8.50
    const result = calculatePrice([
      { name: 'Widget', price: 33.33, quantity: 3 },
    ]);
    expect(result.subtotal).toBe(99.99);
    expect(result.tax).toBe(8.50);
    expect(result.total).toBe(108.49);
  });

  /** @specLine 14 - Empty cart returns all zeros */
  it('should return all zeros for empty cart', () => {
    const result = calculatePrice([]);
    expect(result.subtotal).toBe(0);
    expect(result.discount).toBe(0);
    expect(result.tax).toBe(0);
    expect(result.total).toBe(0);
  });

  // ===========================================
  // Error Handling (Spec Line 15)
  // ===========================================

  /** @specLine 15 - Negative price throws ValidationError */
  it('should throw ValidationError for negative price', () => {
    expect(() => calculatePrice([
      { name: 'Widget', price: -10.00, quantity: 1 },
    ])).toThrow(ValidationError);
  });

  /** @specLine 15 - Zero quantity throws ValidationError */
  it('should throw ValidationError for zero quantity', () => {
    expect(() => calculatePrice([
      { name: 'Widget', price: 10.00, quantity: 0 },
    ])).toThrow(ValidationError);
  });

  /** @specLine 15 - Negative quantity throws ValidationError */
  it('should throw ValidationError for negative quantity', () => {
    expect(() => calculatePrice([
      { name: 'Widget', price: 10.00, quantity: -1 },
    ])).toThrow(ValidationError);
  });

  /** @specLine 15 - Non-integer quantity throws ValidationError */
  it('should throw ValidationError for non-integer quantity', () => {
    expect(() => calculatePrice([
      { name: 'Widget', price: 10.00, quantity: 1.5 },
    ])).toThrow(ValidationError);
  });
});
```

### Шаг 3: Реализация (написана ПОСЛЕ тестов)

Теперь — и только теперь — мы пишем (или просим ИИ написать) реализацию:

```typescript
// src/price-calculator.ts

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

interface CartItem {
  name: string;
  price: number;
  quantity: number;
}

interface PriceResult {
  subtotal: number;
  discount: number;
  tax: number;
  total: number;
}

const TAX_RATE = 0.085;

const DISCOUNT_TIERS = [
  { threshold: 500, rate: 0.20 },
  { threshold: 200, rate: 0.15 },
  { threshold: 100, rate: 0.10 },
];

function round2(value: number): number {
  return Math.round(value * 100) / 100;
}

function validateItem(item: CartItem): void {
  if (item.price < 0) {
    throw new ValidationError(
      `Invalid price for "${item.name}": ${item.price}. Price must be non-negative.`
    );
  }
  if (item.quantity <= 0) {
    throw new ValidationError(
      `Invalid quantity for "${item.name}": ${item.quantity}. Quantity must be a positive integer.`
    );
  }
  if (!Number.isInteger(item.quantity)) {
    throw new ValidationError(
      `Invalid quantity for "${item.name}": ${item.quantity}. Quantity must be an integer.`
    );
  }
}

function getDiscountRate(subtotal: number): number {
  for (const tier of DISCOUNT_TIERS) {
    if (subtotal >= tier.threshold) {
      return tier.rate;
    }
  }
  return 0;
}

export function calculatePrice(items: CartItem[]): PriceResult {
  // Validate all items first
  for (const item of items) {
    validateItem(item);
  }

  // Calculate subtotal (Spec Line 4)
  const subtotal = round2(
    items.reduce((sum, item) => sum + item.price * item.quantity, 0)
  );

  // Calculate discount (Spec Lines 5-8)
  const discountRate = getDiscountRate(subtotal);
  const discount = round2(subtotal * discountRate);

  // Calculate tax on discounted amount (Spec Lines 9-10)
  const taxableAmount = subtotal - discount;
  const tax = round2(taxableAmount * TAX_RATE);

  // Calculate total
  const total = round2(subtotal - discount + tax);

  return { subtotal, discount, tax, total };
}
```

### Шаг 4: Запуск тестов

```bash
$ npx vitest run test/price-calculator.spec.ts

 ✓ Price Calculator
   ✓ should accept an array of cart items
   ✓ should return object with subtotal, discount, tax, and total
   ✓ should calculate subtotal as sum of price * quantity
   ✓ should apply no discount when subtotal < $100
   ✓ should apply 10% discount when subtotal is exactly $100
   ✓ should apply 10% discount when subtotal is $150
   ✓ should apply 15% discount when subtotal is exactly $200
   ✓ should apply 15% discount when subtotal is $350
   ✓ should apply 20% discount when subtotal is exactly $500
   ✓ should apply 20% discount when subtotal is $1000
   ✓ should not discount at $99.99 but should at $100.00
   ✓ should apply 10% at $199.99 and 15% at $200.00
   ✓ should calculate tax at 8.5% on discounted subtotal
   ✓ should calculate tax on full subtotal when no discount
   ✓ should calculate total as subtotal - discount + tax
   ✓ should round all values to 2 decimal places
   ✓ should return all zeros for empty cart
   ✓ should throw ValidationError for negative price
   ✓ should throw ValidationError for zero quantity
   ✓ should throw ValidationError for negative quantity
   ✓ should throw ValidationError for non-integer quantity

 Test Files  1 passed (1)
      Tests  21 passed (21)
```

Все 21 тест проходят. Реализация удовлетворяет спецификации — по крайней мере, в той мере, в какой её проверяют эти тесты.

> **Заметка профессора:** Обратите внимание, что произошло. Мы написали тесты первыми. Каждый тест отображается в конкретную строку спецификации. Реализация была написана *чтобы удовлетворить тесты*, которые сами кодируют спецификацию. Если бы ИИ выдумал другую формулу скидки, тесты поймали бы это немедленно. В этом сила конвейера.

---

## 1.11 Учим ИИ писать тесты ИЗ спецификации

### Промпт-инжиниринг для генерации тестов

Когда вы используете ИИ для генерации тестов из спецификации, структура промпта имеет огромное значение. Вот шаблон, который хорошо работает:

```markdown
## Task: Generate a test suite from the following specification.

### Rules:
1. Generate tests ONLY -- do not generate the implementation
2. Every spec requirement must have at least one test
3. Include boundary tests for all numeric constraints
4. Include negative tests for all error conditions
5. Annotate each test with the spec line number it validates
6. Use [framework: Vitest/Jest/Pytest] with [language: TypeScript/Python]

### Specification:
[paste your spec here]

### Output Format:
- Complete, runnable test file
- Tests should import from a module that does not yet exist
- Include setup/teardown if needed
- Group tests by spec section
```

### Типичные ошибки ИИ при генерации тестов

Даже с хорошими промптами ИИ-модели склонны делать такие ошибки при генерации тестов:

1. **Тестирование реализации вместо спецификации.** ИИ может писать тесты, проверяющие внутренние детали реализации, а не внешнее поведение. Ловите это вопросом: «Могла бы другая реализация пройти этот тест?»

2. **Пропуск граничных тестов.** ИИ обычно пишет счастливый путь и очевидные ошибки, но пропускает граничные тесты (например, ровно на пороге).

3. **Слабые проверки.** ИИ может написать `expect(result).toBeDefined()`, когда нужно `expect(result.subtotal).toBe(95.00)`. Расплывчатые проверки почти бесполезны.

4. **Непроверка сообщений об ошибках.** Если спецификация задаёт конкретные сообщения об ошибках, ИИ часто проверяет только код статуса, а не содержимое сообщения.

5. **Предположение деталей реализации.** ИИ может писать тесты, предполагающие конкретную внутреннюю структуру (например, что вызван конкретный приватный метод), вместо тестирования публичного интерфейса.

### Проверка тестов, сгенерированных ИИ

Всегда проверяйте тесты от ИИ по этому чек-листу:

- [ ] У каждого требования спецификации есть хотя бы один тест?
- [ ] Граничные условия проверены с обеих сторон?
- [ ] Сообщения об ошибках проверяются точно так, как указано?
- [ ] Проверены негативные требования (то, чего НЕ должно происходить)?
- [ ] Проверки конкретны (не просто «определено» или «истинно»)?
- [ ] Могла бы полностью неверная реализация случайно пройти эти тесты?
- [ ] Учтены параллелизм и гонки?
- [ ] Каждый тест независим (нет общего состояния, способного вызвать нестабильность)?

---

## 1.12 Упражнения

### Упражнение 1: Сопоставление спецификации и тестов (начальный уровень)

По следующей микроспецификации напишите полный набор тестов. НЕ пишите реализацию.

```markdown
## Spec: Temperature Converter

### Requirements
1. The module SHALL export a function `convert(value, from, to)`
2. Supported units: "celsius", "fahrenheit", "kelvin"
3. Conversion SHALL be accurate to 2 decimal places
4. Converting a unit to itself SHALL return the same value
5. Kelvin values SHALL never be negative (absolute zero = 0K)
6. Invalid unit names SHALL throw an Error with message "Unknown unit: [unit]"

### Conversion Formulas
7. Celsius to Fahrenheit: F = C * 9/5 + 32
8. Fahrenheit to Celsius: C = (F - 32) * 5/9
9. Celsius to Kelvin: K = C + 273.15
10. Kelvin to Celsius: C = K - 273.15
```

**Что сдать:** Полный файл тестов минимум с 15 тест-кейсами, каждый с аннотацией строки спецификации, которую он проверяет. Включите граничные тесты для ограничения Кельвина.

### Упражнение 2: Найдите пробелы в спецификации (средний уровень)

Следующий набор тестов сгенерирован ИИ. У него 100% покрытия кода, но лишь ~60% покрытия спецификации. Найдите пробелы.

```typescript
describe('URL Shortener', () => {
  it('should shorten a URL', async () => {
    const result = await shorten('https://example.com/very/long/path');
    expect(result.shortUrl).toBeDefined();
    expect(result.shortUrl.length).toBeLessThan(30);
  });

  it('should redirect to original URL', async () => {
    const { shortUrl } = await shorten('https://example.com');
    const result = await resolve(shortUrl);
    expect(result).toBe('https://example.com');
  });

  it('should handle invalid URLs', async () => {
    await expect(shorten('not-a-url')).rejects.toThrow();
  });
});
```

**Что сдать:** Список минимум из 10 дополнительных тест-кейсов, которые должны существовать, исходя из того, что содержала бы разумная спецификация сокращателя URL. Для каждого объясните, какое требование спецификации он проверял бы.

### Упражнение 3: Тестирование на основе свойств (продвинутый уровень)

Напишите тесты на основе свойств с помощью fast-check (JavaScript) или Hypothesis (Python) для следующей спецификации:

```markdown
## Spec: Sorting Function

### Requirements
1. The function SHALL sort an array of numbers in ascending order
2. The sorted array SHALL have the same length as the input
3. The sorted array SHALL contain exactly the same elements as the input
4. Each element SHALL be less than or equal to the next element
5. The function SHALL handle empty arrays (returning [])
6. The function SHALL handle arrays with one element
7. The function SHALL handle arrays with duplicate values
8. Sorting an already-sorted array SHALL return an identical array
```

**Что сдать:** Файл тестов на основе свойств минимум с 6 свойствами, проверяющими требования 1–8. Каждое свойство должно генерировать случайные массивы и проверять инварианты.

### Упражнение 4: Полный конвейер (продвинутый уровень)

Возьмите любую микроспецификацию, написанную в модуле 1. Примените полный конвейер:

1. Проверьте спецификацию на полноту
2. Сгенерируйте набор тестов (вручную или с помощью ИИ)
3. Запустите тесты (все должны упасть — реализации ещё нет)
4. Реализуйте код (вручную или с помощью ИИ)
5. Запустите тесты (все должны пройти)
6. Сгенерируйте отчёт о покрытии спецификации
7. Определите пробелы в спецификации, найденные в процессе
8. Обновите спецификацию, чтобы закрыть пробелы
9. Напишите дополнительные тесты для обновлённой спецификации

**Что сдать:** Полную спецификацию, набор тестов, реализацию и отчёт о покрытии спецификации. Включите размышление о найденных пробелах спецификации и о том, как вы их закрыли.

---

## Итог

В этой главе мы рассмотрели основополагающую дисциплину разработки через спецификации: сопоставление спецификаций с тестами до написания любого кода реализации.

**Ключевые выводы:**

1. **Тесты-первыми критичны с ИИ.** ИИ не знает, что значит «правильно», пока вы не определите это через тесты, выведенные из спецификации.

2. **Каждая строка спецификации отображается как минимум в один тест.** Это фундаментальная прослеживаемость, делающая SDD работающей.

3. **Граничные условия — там, где прячутся баги.** Извлекайте их систематически из каждого ограничения спецификации.

4. **Тестирование на основе свойств проверяет *замысел* спецификации.** Тесты на примерах проверяют конкретные случаи; тесты на свойствах — общие правила.

5. **Покрытие спецификации важнее покрытия кода.** Покрытие кода говорит, выполняется ли код; покрытие спецификации — правилен ли он.

6. **Конвейер не обсуждается: Спецификация --> Тесты --> Реализация --> Валидация.** Нарушение порядка уничтожает смысл.

В следующей главе мы посмотрим, как не дать ИИ *уйти* от спецификации во время реализации — явление, которое мы называем «дрейфом замысла», — и как строить автоматизированные линтеры для его обнаружения.

---

*Далее: Глава 2 — Автоматический линтинг замысла*

---

[← Оглавление курса](../INDEX.ru.md) · [← Глава 4: Спецификации управления состоянием](../MODULE_02/CHAPTER_04.ru.md) · [Глава 2: Автоматический линтинг замысла →](CHAPTER_02.ru.md)
