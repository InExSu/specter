# Глава 2: Контракт компонента

## МОДУЛЬ 02 — Определение архитектуры («как») | Средний уровень

---

## Вступление к лекции

*Профессор выводит на проектор дизайн-макет — строку поиска с подсказками автодополнения, индикатором загрузки и кнопкой «очистить». Затем профессор закрывает макет и открывает пустой редактор кода.*

Забудьте про макет. Мне сейчас неинтересно, как выглядит эта строка поиска. Мне интересно, что она **делает**. Какие данные принимает, каким состоянием управляет, какие события порождает и какие внешние системы затрагивает. Мне интересен её **контракт**.

Это один из самых трудных уроков для фронтенд-разработчиков: визуальный дизайн компонента — **наименее важная** часть его спецификации. Пиксели могут измениться за ночь. Цвета субъективны. Отступы спорны. Но контракт — пропсы, состояние и побочные эффекты — это архитектура. Это то, что создаёт или разрушает ваше приложение.

Сегодня мы научимся писать **контракты компонентов**: спецификации, полностью определяющие поведение UI-компонента без описания хотя бы одного пикселя его внешнего вида. И когда мы передаём эти контракты ИИ, ИИ выдаёт компоненты, работающие правильно каждый раз — даже если стилизацию позже придётся скорректировать.

---

## 2.1 Что такое контракт компонента?

Контракт компонента — формальная спецификация, определяющая три вещи о UI-компоненте:

1. **Пропсы** — входные данные, которые компонент принимает от родителя
2. **Состояние** — внутренние данные, которыми компонент управляет
3. **Побочные эффекты** — внешние системы, с которыми компонент взаимодействует

Обратите внимание, чего в этом списке НЕТ: цвета, шрифты, отступы, анимации, радиусы скругления, тени и любые другие визуальные свойства. Они принадлежат **визуальной спецификации**, которая является отдельной заботой.

```typescript
// THIS is a component contract:
interface SearchBarContract {
  // Props (inputs from parent)
  props: {
    placeholder: string;
    initialValue?: string;
    maxLength?: number;
    onSearch: (query: string) => void;
    onClear: () => void;
    suggestions: Suggestion[];
    isLoading: boolean;
    disabled?: boolean;
  };

  // Internal state
  state: {
    inputValue: string;
    isFocused: boolean;
    selectedSuggestionIndex: number;  // -1 means none selected
    showSuggestions: boolean;
  };

  // Side effects
  sideEffects: {
    debounce: "Debounce input changes by 300ms before calling onSearch";
    focus: "Auto-focus input on mount if no initialValue provided";
    keyboard: "Handle ArrowUp, ArrowDown, Enter, Escape for suggestion navigation";
    clickOutside: "Close suggestions dropdown when clicking outside component";
  };
}

interface Suggestion {
  id: string;
  text: string;
  category?: string;
  icon?: string;  // Icon identifier, not a component
}
```

Этот контракт рассказывает разработчику (или ИИ) всё, что нужно для реализации SearchBar. Он ничего не говорит о том, появляются ли подсказки в выпадающем списке или модальном окне, круглый ли индикатор загрузки или полосатый, использует ли компонент Tailwind или CSS-модули. Это детали реализации, которым место в другом месте.

> **Заметка профессора:** У меня в проектах есть правило: если вы не можете описать контракт компонента, не упомянув CSS-свойство, вы смешиваете поведение с внешним видом. Разделяйте их беспощадно. Контракт кнопки — о том, что происходит при клике, а не о том, в какой цвет она окрашивается.

---

## 2.2 Разделение ответственности: спецификация поведения и визуальная спецификация

Различие между спецификацией поведения и визуальной спецификацией фундаментально для проектирования компонентов в SDD. Сделаю его предельно ясным.

### Спецификация поведения (контракт компонента)

Спецификация поведения отвечает на вопросы:

- Какие данные нужны компоненту?
- Что пользователь может делать с компонентом?
- Что происходит в ответ на действия пользователя?
- Какие внешние системы затрагивает компонент?
- Каковы крайние случаи и состояния ошибок?

```typescript
// Behavior spec for a QuantitySelector component
interface QuantitySelectorContract {
  props: {
    value: number;
    min: number;
    max: number;
    step: number;
    onChange: (newValue: number) => void;
    disabled?: boolean;
  };

  behavior: {
    increment: "Increase value by step, capped at max";
    decrement: "Decrease value by step, floored at min";
    directInput: "Allow typing a number; validate on blur";
    invalidInput: "If user types non-numeric or out-of-range, revert to previous valid value";
    disabledState: "All interactions disabled; visual indication of disabled state";
  };

  edgeCases: {
    "value exceeds max on mount": "Clamp to max";
    "value below min on mount": "Clamp to min";
    "step causes value to exceed max": "Set to max instead of max + remainder";
    "min equals max": "Both buttons disabled; input is read-only";
    "negative step": "Rejected — step must be positive";
  };
}
```

### Визуальная спецификация (дизайн-система)

Визуальная спецификация отвечает на другие вопросы:

- Как выглядит компонент?
- Каковы цвета, размеры и отступы?
- Как он анимируется?
- Как он реагирует на разные размеры экрана?

```
Visual Spec: QuantitySelector
- Height: 40px
- Button width: 40px each (square)
- Input width: 60px, centered between buttons
- Font: 14px, medium weight
- Border: 1px solid gray-300, rounded-md
- Hover state: border-gray-400
- Focus state: ring-2 ring-blue-500
- Disabled state: opacity-50, cursor-not-allowed
- Button icons: minus (left), plus (right)
- Mobile: full width of container
```

### Зачем их разделять?

Три причины:

**1. ИИ генерирует лучший код, когда ответственности разделены.**

Когда вы смешиваете спецификации поведения и визуала в одном промпте, модели ИИ часто жертвуют поведенческой правильностью ради визуальной точности. Они сделают цвета правильными, но упустят крайний случай. Разделив спецификации, вы можете проверять поведение независимо от внешнего вида.

**2. Поведение меняется реже, чем визуал.**

Контракт SearchBar (принимать запрос, показывать подсказки, обрабатывать навигацию с клавиатуры) стабилен годами. Его визуальный дизайн меняется с каждым ребрендингом. Разделение спецификаций позволяет обновлять визуальный слой, не трогая поведенческий контракт.

**3. Разные люди владеют разными спецификациями.**

Инженеры владеют спецификацией поведения. Дизайнеры владеют визуальной спецификацией. Когда они в одном документе, вы получаете конфликты слияния, путаницу в полномочиях и паралич «дизайна комитетом».

> **Заметка профессора:** Команда React в Meta усвоила этот урок тяжёлым путём при разработке внутренней библиотеки компонентов. В ранних версиях поведение и стилизация компонентов были так тесно переплетены, что изменение внешнего вида кнопки требовало понимания её машины состояний. Рефакторинг для разделения ответственностей — хуки поведения с одной стороны, визуальные примитивы с другой — в итоге стал тем шаблоном, который мы видим в headless-библиотеках вроде Radix, React Aria и Headless UI.

---

## 2.3 Интерфейс пропсов как контракт

В компонентных фреймворках (React, Vue, Svelte, Angular) интерфейс пропсов — **первичный контракт** между родительским и дочерним компонентами. Это поверхность API вашего компонента.

### Проектирование пропсов как контрактов

Хороший дизайн пропсов следует тем же принципам, что и хороший дизайн API:

```typescript
// ===================================================
// MODAL DIALOG — COMPONENT CONTRACT
// ===================================================

interface ModalProps {
  // --- Required Props ---
  /** Whether the modal is currently open */
  isOpen: boolean;

  /** Called when the modal requests to be closed */
  onClose: () => void;

  /** The main content of the modal */
  children: React.ReactNode;

  // --- Content Props ---
  /** Title displayed in the modal header */
  title: string;

  /** Optional description below the title */
  description?: string;

  // --- Behavior Props ---
  /** Whether clicking the overlay closes the modal. Default: true */
  closeOnOverlayClick?: boolean;

  /** Whether pressing Escape closes the modal. Default: true */
  closeOnEscape?: boolean;

  /** Whether to show the X close button. Default: true */
  showCloseButton?: boolean;

  /** Whether the modal can be dismissed at all. Default: true.
   *  When false: no X button, no overlay click, no Escape.
   *  Used for mandatory confirmations. */
  dismissible?: boolean;

  // --- Lifecycle Props ---
  /** Called after the modal open animation completes */
  onAfterOpen?: () => void;

  /** Called after the modal close animation completes */
  onAfterClose?: () => void;

  // --- Accessibility Props ---
  /** ARIA label for the modal (defaults to title) */
  ariaLabel?: string;

  /** ID of the element that describes the modal */
  ariaDescribedBy?: string;

  /** Where to return focus when modal closes. Default: trigger element */
  returnFocusTo?: HTMLElement | null;

  // --- Layout Props (behavior, not styling) ---
  /** Size preset affecting max-width. Default: "medium" */
  size?: "small" | "medium" | "large" | "fullscreen";

  /** Whether the modal content is scrollable. Default: true */
  scrollable?: boolean;
}
```

Обратите внимание на несколько важных принципов:

**Принцип 1: у булевых пропсов есть разумные значения по умолчанию.** `closeOnOverlayClick` по умолчанию `true`. Самому частому использованию не нужно это указывать.

**Принцип 2: колбэки используют префикс `on`.** `onClose`, `onAfterOpen`, `onAfterClose`. Это универсальная конвенция, которую модели ИИ понимают отлично.

**Принцип 3: доступность — часть контракта, а не запоздалая мысль.** `ariaLabel`, `ariaDescribedBy` и `returnFocusTo` — полноправные пропсы.

**Принцип 4: пропс `dismissible` — составное поведение.** Вместо того чтобы заставлять потребителя ставить три булевых значения (`closeOnOverlayClick={false} closeOnEscape={false} showCloseButton={false}`), мы даём один семантический пропс, управляющий всеми тремя. Это мышление на уровне контракта.

**Принцип 5: `size` — поведенческий пропс, а не стилевой.** Он влияет на ограничения максимальной ширины, а не на цвета или шрифты. Визуальная спецификация определяет, что значит «medium» в пикселях.

### Пропсы как документация

Когда вы пишете подробный интерфейс пропсов с JSDoc-комментариями, вы одновременно создаёте:

- Контракт TypeScript (принуждение во время компиляции)
- Документацию компонента (подсказки в VS Code)
- Промпт для ИИ (ИИ читает интерфейс и понимает компонент)
- Тестовую спецификацию (каждый пропс подсказывает тесты)

### Решение «контролируемый против неконтролируемого»

Одно из важнейших решений в контракте компонента — контролируется ли состояние или нет:

```typescript
// CONTROLLED: Parent owns the state
interface ControlledInputProps {
  value: string;
  onChange: (value: string) => void;
}

// UNCONTROLLED: Component owns the state
interface UncontrolledInputProps {
  defaultValue?: string;
  onChangeComplete?: (value: string) => void;
}

// HYBRID: Supports both patterns
interface FlexibleInputProps {
  value?: string;            // If provided, component is controlled
  defaultValue?: string;     // Used only if value is undefined
  onChange?: (value: string) => void;
}
```

В контракте компонента явно укажите, какой шаблон используется:

```typescript
interface DatePickerContract {
  // This is a CONTROLLED component.
  // The parent must manage the selected date.
  props: {
    selectedDate: Date | null;        // Controlled value
    onChange: (date: Date | null) => void;  // Required callback
    minDate?: Date;
    maxDate?: Date;
    disabled?: boolean;
    disabledDates?: Date[];           // Specific dates to disable
  };

  reasoning: {
    whyControlled:
      "Date selection typically needs to coordinate with other form fields " +
      "(e.g., check-in/check-out dates). Controlled pattern makes this " +
      "coordination explicit and predictable.";
  };
}
```

> **Заметка профессора:** Решение «контролируемый против неконтролируемого» должно приниматься на этапе спецификации, а не реализации. Если оставить это неоднозначным, ИИ угадает — и угадает по-разному в разных файлах. Я видел кодовые базы, где один и тот же DatePicker использовался в контролируемом режиме в одной форме и в неконтролируемом в другой, потому что никто не указал шаблон. Результат — два разных поведения одного компонента и неделя отладки.

---

## 2.4 Машины состояний как спецификации компонентов

Один из самых мощных инструментов спецификации поведения компонента — машина состояний. Машина состояний определяет:

- Все возможные **состояния**, в которых может быть компонент
- Все возможные **события** (триггеры), вызывающие переходы
- Какие **переходы** допустимы (а какие нет)
- Какие **действия** происходят во время переходов

Это основная философия XState, популярной библиотеки машин состояний для JavaScript. Но вам не нужен XState, чтобы мыслить машинами состояний — концепция универсальна.

### Пример: компонент загрузки файла

Опишем компонент загрузки файла, мысля машиной состояний:

```typescript
// ===================================================
// FILE UPLOAD COMPONENT — STATE MACHINE SPEC
// ===================================================

// All possible states
type FileUploadState =
  | { status: "idle" }
  | { status: "dragover" }
  | { status: "validating"; file: File }
  | { status: "uploading"; file: File; progress: number }
  | { status: "processing"; file: File }  // Server is processing
  | { status: "success"; file: File; url: string }
  | { status: "error"; file: File | null; errorCode: UploadErrorCode; message: string };

type UploadErrorCode =
  | "FILE_TOO_LARGE"
  | "INVALID_TYPE"
  | "NETWORK_ERROR"
  | "SERVER_ERROR"
  | "QUOTA_EXCEEDED"
  | "TIMEOUT";

// All possible events
type FileUploadEvent =
  | { type: "DRAG_ENTER" }
  | { type: "DRAG_LEAVE" }
  | { type: "DROP"; file: File }
  | { type: "SELECT_FILE"; file: File }
  | { type: "VALIDATION_SUCCESS"; file: File }
  | { type: "VALIDATION_FAILURE"; errorCode: UploadErrorCode; message: string }
  | { type: "UPLOAD_PROGRESS"; progress: number }
  | { type: "UPLOAD_COMPLETE"; file: File }
  | { type: "PROCESSING_COMPLETE"; url: string }
  | { type: "ERROR"; errorCode: UploadErrorCode; message: string }
  | { type: "RETRY" }
  | { type: "CANCEL" }
  | { type: "RESET" };

// Transition table — the heart of the spec
interface FileUploadTransitions {
  idle: {
    DRAG_ENTER: "dragover";
    SELECT_FILE: "validating";
  };
  dragover: {
    DRAG_LEAVE: "idle";
    DROP: "validating";
  };
  validating: {
    VALIDATION_SUCCESS: "uploading";
    VALIDATION_FAILURE: "error";
  };
  uploading: {
    UPLOAD_PROGRESS: "uploading";     // Self-transition with updated progress
    UPLOAD_COMPLETE: "processing";
    ERROR: "error";
    CANCEL: "idle";
  };
  processing: {
    PROCESSING_COMPLETE: "success";
    ERROR: "error";
    // Note: CANCEL is NOT valid here — server is already processing
  };
  success: {
    RESET: "idle";
  };
  error: {
    RETRY: "uploading";  // Only if file exists in error state
    RESET: "idle";
  };
}

// Validation rules (run during "validating" state)
interface FileValidationRules {
  maxSizeBytes: number;          // e.g., 10 * 1024 * 1024 (10MB)
  allowedMimeTypes: string[];    // e.g., ["image/jpeg", "image/png", "application/pdf"]
  allowedExtensions: string[];   // e.g., [".jpg", ".jpeg", ".png", ".pdf"]
}
```

Посмотрите, что даёт спецификация машины состояний:

1. **Перечислено каждое возможное состояние.** Нет неоднозначности, в каких состояниях может быть компонент.

2. **Перечислено каждое возможное событие.** Мы точно знаем, что может произойти.

3. **Недопустимые переходы исключены.** Нельзя CANCEL в состоянии «processing». Нельзя RETRY из «idle». Эти ограничения явны.

4. **Определены данные, связанные с каждым состоянием.** Состояние «uploading» несёт `progress`. Состояние «error» несёт `errorCode`. Состояние «success» несёт `url`.

5. **Это тестируемо.** Каждый переход — тестовый случай.

### Визуализация машины состояний

Спецификацию выше можно визуализировать как диаграмму состояний:

```
                    +-----------+
                    |   idle    |<---------+----------+
                    +-----------+          |          |
                     |       |             |          |
              DRAG_ENTER  SELECT_FILE    RESET      CANCEL
                     |       |             |          |
                     v       |             |          |
                +-----------+|    +--------+-+   +----+-----+
                | dragover  ||    | success  |   | uploading|
                +-----------+|    +----------+   +----------+
                 |      |    |         ^              |    |
            DRAG_LEAVE  DROP |  PROCESSING_COMPLETE   |    |
                 |      |    |         |           ERROR  UPLOAD_COMPLETE
                 |      v    v         |              |    |
                 |  +------------+  +------------+    |    |
                 |  | validating |  | processing |<---+----+
                 |  +------------+  +------------+    |
                 |    |       |          |            |
                 | SUCCESS  FAILURE    ERROR          |
                 |    |       |          |            |
                 |    |       v          |            |
                 |    |    +--------+    |            |
                 |    +--->| error  |<---+            |
                 |         +--------+                 |
                 |           |    |                    |
                 |         RETRY  RESET               |
                 |           |    |                    |
                 |           +----+-----> idle         |
                 +------------------------------------+
```

> **Заметка профессора:** Если вы используете XState, можете буквально взять эту спецификацию и перевести её в определение машины XState. Но даже если не используете XState, *мышление* машиной состояний бесценно. Оно заставляет перечислить все состояния и переходы до написания кода. Я видел, как этот приём предотвращал больше багов, чем любой другой подход к спецификации.

### Машины состояний для компонентов форм

Формы особенно хорошо подходят для спецификаций машин состояний:

```typescript
type FormState =
  | { status: "pristine" }                         // No changes yet
  | { status: "dirty"; changedFields: string[] }   // User has made changes
  | { status: "validating" }                       // Async validation in progress
  | { status: "invalid"; errors: FieldError[] }    // Validation failed
  | { status: "submitting" }                       // Form is being submitted
  | { status: "submitted"; response: unknown }     // Submission succeeded
  | { status: "submitError"; error: string }       // Submission failed

interface FieldError {
  field: string;
  code: string;          // Machine-readable: "REQUIRED", "TOO_SHORT", etc.
  message: string;       // Human-readable: "Email is required"
}

type FormEvent =
  | { type: "FIELD_CHANGE"; field: string; value: unknown }
  | { type: "FIELD_BLUR"; field: string }
  | { type: "SUBMIT" }
  | { type: "VALIDATION_START" }
  | { type: "VALIDATION_COMPLETE"; errors: FieldError[] }
  | { type: "SUBMIT_SUCCESS"; response: unknown }
  | { type: "SUBMIT_FAILURE"; error: string }
  | { type: "RESET" };
```

---

## 2.5 Побочные эффекты: какие внешние вещи затрагивает компонент?

Побочные эффекты — самая часто недоописанная часть компонента. Побочный эффект — любое взаимодействие с миром вне собственного состояния компонента. Это включает:

- **Вызовы API** — получение или изменение данных
- **API браузера** — localStorage, sessionStorage, буфер обмена, геолокация
- **Таймеры** — setTimeout, setInterval, debounce, throttle
- **Манипуляции с DOM** — управление фокусом, позиция прокрутки, наблюдение за размером
- **Слушатели событий** — горячие клавиши, клик снаружи, прокрутка, изменение размера
- **Сторонние сервисы** — аналитика, логирование, отслеживание ошибок
- **Навигация** — смена маршрута, обновление параметров URL

Каждый побочный эффект компонента должен быть объявлен в контракте:

```typescript
// ===================================================
// AUTOCOMPLETE SEARCH — COMPLETE COMPONENT CONTRACT
// ===================================================

interface AutocompleteSearchContract {
  name: "AutocompleteSearch";
  description: "A search input with autocomplete suggestions fetched from an API";

  props: {
    /** API endpoint for fetching suggestions */
    endpoint: string;

    /** Minimum characters before triggering search */
    minChars: number;  // Default: 2

    /** Maximum number of suggestions to display */
    maxSuggestions: number;  // Default: 10

    /** Called when user selects a suggestion */
    onSelect: (suggestion: Suggestion) => void;

    /** Called when user submits the search (Enter without selecting) */
    onSubmit: (query: string) => void;

    /** Placeholder text */
    placeholder?: string;

    /** Whether the input is disabled */
    disabled?: boolean;

    /** Custom header to include in API requests (e.g., auth token) */
    requestHeaders?: Record<string, string>;
  };

  state: {
    query: string;
    suggestions: Suggestion[];
    isLoading: boolean;
    isFocused: boolean;
    isOpen: boolean;  // Whether suggestions dropdown is visible
    highlightedIndex: number;  // -1 = none highlighted
    error: string | null;
  };

  sideEffects: {
    apiCalls: {
      trigger: "query changes AND query.length >= minChars";
      endpoint: "GET ${props.endpoint}?q=${encodeURIComponent(query)}";
      debounce: "300ms";
      cancellation: "Cancel previous request when new one starts";
      errorHandling: "Set error state; do not throw; show inline error message";
      headers: "Include props.requestHeaders if provided";
    };

    keyboardListeners: {
      ArrowDown: "Highlight next suggestion (wrap to first after last)";
      ArrowUp: "Highlight previous suggestion (wrap to last before first)";
      Enter: "Select highlighted suggestion, or submit query if none highlighted";
      Escape: "Close suggestions dropdown; clear highlight";
      Tab: "Close suggestions dropdown; allow normal tab behavior";
    };

    clickOutside: {
      trigger: "Click anywhere outside the component";
      action: "Close suggestions dropdown";
      implementation: "useRef + document click listener";
    };

    focusManagement: {
      onMount: "Do NOT auto-focus (let parent decide)";
      onFocus: "Set isFocused=true; show suggestions if query.length >= minChars";
      onBlur: "Set isFocused=false; close suggestions after 150ms delay";
      blurDelay: "150ms delay allows click on suggestion to register before closing";
    };

    analytics: {
      trackSearch: "Fire analytics event when user submits search";
      trackSuggestionSelect: "Fire analytics event with suggestion.id when selected";
      trackNoResults: "Fire analytics event when API returns 0 suggestions";
    };
  };

  edgeCases: {
    "rapid typing": "Debounce ensures only final query triggers API call; previous requests cancelled";
    "empty response": "Show 'No results found' message; do not hide dropdown";
    "API error": "Show inline error; allow retry on next keystroke";
    "very long query": "Truncate display in input; send full query to API";
    "special characters": "URL-encode query before sending to API";
    "suggestion selected while loading": "Cancel pending request; use selected suggestion";
    "component unmount during request": "Cancel pending request; no state updates after unmount";
  };
}

interface Suggestion {
  id: string;
  label: string;         // Display text
  value: string;         // Actual value (may differ from label)
  category?: string;     // Optional grouping
  metadata?: Record<string, unknown>;  // Additional data for parent
}
```

Раздел побочных эффектов плотный. Так и должно быть. Побочные эффекты — там, где живут баги. Выделю неочевидные решения:

- **Задержка blur 150 мс**: без неё клик по подсказке вызывает blur раньше, чем регистрируется клик, закрывая выпадающий список и проглатывая клик. Это классический баг, который ловит спецификация машины состояний.
- **Отмена предыдущего запроса**: без отмены медленный запрос по «hel» может завершиться после быстрого запроса по «hello», показав неверные подсказки.
- **Размонтирование компонента во время запроса**: без очистки вы получаете предупреждение React «Can't perform a state update on an unmounted component».

Каждый из этих крайних случаев потребовал бы от ИИ (или человека-разработчика) независимого обнаружения, если не специфицирован. Включив их в контракт, мы обеспечиваем правильное поведение с первой реализации.

---

## 2.6 Как дизайн-системы используют контракты компонентов

Крупнейшие технологические компании мира усвоили — часто через болезненный опыт, — что контракты компонентов необходимы для построения согласованных надёжных UI-систем в масштабе.

### Компоненты Material Design от Google

Дизайн-система Google Material Design (сейчас в третьей мажорной версии, Material 3 / Material You) определяет компоненты через многослойную спецификацию:

1. **Анатомия** — структурные части компонента (например, у диалога есть контейнер, заголовок, область содержимого, кнопки действий)
2. **Поведение** — шаблоны взаимодействия (например, как диалог удерживает фокус, обрабатывает Escape, клики по оверлею)
3. **Состояния** — возможные состояния и переходы (например, кнопка может быть активной, отключённой, в фокусе, нажатой, под курсором)
4. **Доступность** — ARIA-роли, взаимодействие с клавиатуры, поведение скринридеров

Спецификации компонентов Material явно разделяют поведение и темизацию. Библиотека Material Web Components даёт поведение и структуру; слой темы даёт цвета, типографику и высоту.

Это разделение — причина, по которой компоненты Material можно «перетемизировать» для разных продуктов Google (Gmail, Docs, Calendar используют Material, но выглядят по-разному), не меняя поведенческие контракты.

### Экосистема React-компонентов Meta

Внутренняя библиотека React-компонентов Meta — на которой работают Facebook, Instagram, WhatsApp Web и другие продукты — использует подход, управляемый контрактами. У каждого компонента есть:

- **Интерфейс TypeScript**, определяющий все пропсы
- **Спецификация поведения**, определяющая взаимодействия и состояние
- **Визуальные варианты**, определённые через систему дизайн-токенов
- **Требования доступности** как часть контракта

Подход Meta к проектированию компонентов сильно повлиял на всю экосистему React. Шаблоны, которые вы видите в библиотеках вроде Radix UI, Headless UI и React Aria, восходят к урокам Meta: **отделяйте поведенческий контракт от визуальной реализации.**

React Aria (от Adobe) доводит это до крайности. Она предоставляет хуки, реализующие поведение компонента (навигация с клавиатуры, управление фокусом, ARIA-атрибуты) без какой-либо стилизации. Контракт — чистое поведение:

```typescript
// React Aria's approach: behavior contract as a hook
import { useComboBox } from "react-aria";
import { useComboBoxState } from "react-stately";

// The state spec
const state = useComboBoxState({
  items: suggestions,
  onSelectionChange: (key) => onSelect(key),
  // ... behavioral configuration
});

// The behavior contract — returns props to spread onto DOM elements
const { inputProps, listBoxProps, labelProps } = useComboBox(
  {
    label: "Search",
    items: suggestions,
    onSelectionChange: (key) => onSelect(key),
  },
  state,
  inputRef
);

// You provide ALL the rendering:
return (
  <div>
    <label {...labelProps}>Search</label>
    <input {...inputProps} ref={inputRef} />
    <ul {...listBoxProps}>
      {/* Your custom rendering of suggestions */}
    </ul>
  </div>
);
```

Контракт (что `useComboBox` ожидает и возвращает) полностью отделён от визуальной реализации (как вы рендерите HTML).

### Шаблон Headless UI

Этот подход — предоставление поведения без мнений о рендеринге — стал известен как шаблон «headless UI». Это чистейшее выражение философии контрактов компонентов:

| Библиотека     | Компания | Подход                                         |
|----------------|---------|-----------------------------------------------|
| React Aria     | Adobe   | Хуки, возвращающие ARIA-совместимые пропсы      |
| Radix UI       | WorkOS  | Безстилевые примитивы с полным поведением       |
| Headless UI    | Tailwind| Безстилевые компоненты для пользователей Tailwind|
| Downshift      | Paypal  | Headless combobox/select (Kent C. Dodds)        |
| TanStack Table | Tanner L.| Headless-таблица с полным набором функций       |

Все эти библиотеки по сути — **опубликованные контракты компонентов**: они определяют поведение, вы предоставляете визуал.

> **Заметка профессора:** Вот прогноз для этого класса: к концу 2026 года доминирующим шаблоном для ИИ-генерируемого UI будет headless-first. Вы напишете контракт компонента (пропсы, состояние, побочные эффекты), передадите его ИИ, и ИИ сгенерирует headless-реализацию со стилизованной обёрткой. Контракт остаётся стабильным; слой стилизации можно перегенерировать для разных дизайн-систем. Именно так уже работают самые искушённые команды ИИ-разработки.

---

## 2.7 Реальный пример: спецификация компонента SearchBar

Пройдём полный пример продакшн-уровня. Специфицируем компонент SearchBar с нуля, покрывая каждый аспект его контракта.

### Шаг 1: определить требования

Прежде чем писать интерфейс, перечислите, что должен делать SearchBar:

1. Принимать текстовый ввод от пользователя
2. Показывать подсказки автодополнения по мере ввода
3. Поддерживать навигацию по подсказкам с клавиатуры
4. Позволять пользователю выбрать подсказку или отправить свободный запрос
5. Показывать состояние загрузки при получении подсказок
6. Поддерживать «недавние запросы»
7. Позволять очистить ввод
8. Быть полностью доступным (скринридеры, пользователи только с клавиатурой)

### Шаг 2: написать контракт пропсов

```typescript
// ===================================================
// SEARCHBAR COMPONENT — FULL SPECIFICATION
// ===================================================

// --- Props ---

interface SearchBarProps {
  // --- Core Behavior ---
  /** The current search query (controlled component) */
  value: string;

  /** Called on every input change */
  onChange: (value: string) => void;

  /** Called when the user submits a search (Enter key or submit button) */
  onSubmit: (query: string) => void;

  /** Called when the user selects a suggestion */
  onSuggestionSelect: (suggestion: SearchSuggestion) => void;

  /** Called when the user clears the input */
  onClear: () => void;

  // --- Data ---
  /** Autocomplete suggestions to display */
  suggestions: SearchSuggestion[];

  /** Recent searches to display when input is focused but empty */
  recentSearches: RecentSearch[];

  /** Whether suggestions are currently loading */
  isLoading: boolean;

  // --- Configuration ---
  /** Placeholder text for the input. Default: "Search..." */
  placeholder?: string;

  /** Maximum length of the search query. Default: 200 */
  maxLength?: number;

  /** Whether to show the recent searches section. Default: true */
  showRecentSearches?: boolean;

  /** Maximum number of suggestions to display. Default: 8 */
  maxSuggestions?: number;

  /** Maximum number of recent searches to display. Default: 5 */
  maxRecentSearches?: number;

  // --- State ---
  /** Whether the search bar is disabled */
  disabled?: boolean;

  /** Whether to auto-focus on mount. Default: false */
  autoFocus?: boolean;

  // --- Accessibility ---
  /** ARIA label for the search input */
  ariaLabel?: string;

  /** ID of the search input (for label association) */
  inputId?: string;

  // --- Callbacks ---
  /** Called when the input gains focus */
  onFocus?: () => void;

  /** Called when the input loses focus */
  onBlur?: () => void;

  /** Called when a recent search is removed */
  onRecentSearchRemove?: (searchId: string) => void;

  /** Called when all recent searches are cleared */
  onRecentSearchesClear?: () => void;
}

// --- Supporting Types ---

interface SearchSuggestion {
  id: string;
  type: "product" | "category" | "query" | "user";
  label: string;            // Display text
  sublabel?: string;        // Secondary text (e.g., category name)
  iconUrl?: string;         // Optional icon/thumbnail URL
  highlightRanges?: Array<{
    start: number;
    end: number;
  }>;  // Character ranges to bold in the label (matching the query)
}

interface RecentSearch {
  id: string;
  query: string;
  timestamp: string;  // ISO 8601
}
```

### Шаг 3: написать контракт состояния

```typescript
// --- Internal State ---

interface SearchBarState {
  /** Whether the input is focused */
  isFocused: boolean;

  /** Whether the dropdown is open */
  isDropdownOpen: boolean;

  /** Which section of the dropdown is active */
  activeSection: "suggestions" | "recent" | null;

  /** Index of the currently highlighted item (-1 = none) */
  highlightedIndex: number;

  /** The composite list used for keyboard navigation.
   *  Merges suggestions and recent searches into a single navigable list. */
  navigableItems: NavigableItem[];
}

type NavigableItem =
  | { type: "suggestion"; index: number; data: SearchSuggestion }
  | { type: "recent"; index: number; data: RecentSearch }
  | { type: "action"; id: "clear-recent"; label: "Clear recent searches" };
```

### Шаг 4: написать контракт поведения

```typescript
// --- Behavior Specification ---

interface SearchBarBehavior {
  // --- Dropdown Visibility ---
  dropdown: {
    openWhen: [
      "Input is focused AND (suggestions.length > 0 OR recentSearches.length > 0)",
      "Input is focused AND isLoading is true",
    ];
    closeWhen: [
      "Input loses focus (after 150ms delay for click registration)",
      "User presses Escape",
      "User selects a suggestion",
      "User submits the search",
    ];
    content: {
      "when query is empty and showRecentSearches":
        "Show recent searches section";
      "when query is not empty and suggestions exist":
        "Show suggestions section";
      "when query is not empty and isLoading":
        "Show loading indicator";
      "when query is not empty and not loading and suggestions empty":
        "Show 'No results' message";
    };
  };

  // --- Keyboard Navigation ---
  keyboard: {
    ArrowDown: [
      "If dropdown closed: open dropdown",
      "If dropdown open: move highlight to next item (wrap from last to first)",
    ];
    ArrowUp: [
      "If dropdown open: move highlight to previous item (wrap from first to last)",
      "If at first item: remove highlight (return to input)",
    ];
    Enter: [
      "If item highlighted: select that item (suggestion or recent search)",
      "If no item highlighted: submit the current query via onSubmit",
    ];
    Escape: [
      "If dropdown open: close dropdown, clear highlight",
      "If dropdown closed: clear input value, call onClear",
    ];
    Tab: [
      "Close dropdown",
      "Allow normal tab behavior (move focus to next element)",
    ];
  };

  // --- Input Behavior ---
  input: {
    onChange: [
      "Update value via props.onChange",
      "Reset highlightedIndex to -1",
      "Open dropdown if it was closed",
    ];
    onFocus: [
      "Set isFocused to true",
      "Open dropdown if there are items to show",
      "Call props.onFocus if provided",
    ];
    onBlur: [
      "After 150ms delay:",
      "  Set isFocused to false",
      "  Close dropdown",
      "  Clear highlight",
      "  Call props.onBlur if provided",
    ];
  };

  // --- Clear Button ---
  clearButton: {
    visible: "When value.length > 0 AND not disabled";
    onClick: [
      "Clear input value via onClear callback",
      "Return focus to input",
    ];
  };

  // --- Recent Searches ---
  recentSearches: {
    itemClick: "Set input value to search.query, call onSubmit";
    removeClick: "Call onRecentSearchRemove with search.id; do NOT close dropdown";
    clearAll: "Call onRecentSearchesClear; close recent section";
  };
}
```

### Шаг 5: написать контракт доступности

```typescript
// --- Accessibility Specification ---

interface SearchBarAccessibility {
  roles: {
    container: "role='combobox'";
    input: "role='searchbox' (implicit with type='search')";
    dropdown: "role='listbox'";
    suggestionItem: "role='option'";
    recentItem: "role='option'";
  };

  ariaAttributes: {
    input: {
      "aria-expanded": "true when dropdown is open, false otherwise";
      "aria-activedescendant": "ID of highlighted item, empty when none highlighted";
      "aria-autocomplete": "'list'";
      "aria-controls": "ID of the dropdown listbox";
      "aria-label": "props.ariaLabel or 'Search'";
    };
    dropdown: {
      "aria-label": "'Search suggestions' or 'Recent searches' based on content";
    };
    suggestionItem: {
      "aria-selected": "true when this item is highlighted";
    };
    clearButton: {
      "aria-label": "'Clear search'";
    };
    removeRecentButton: {
      "aria-label": "'Remove recent search: {query}'";
    };
  };

  focusManagement: {
    "keyboard navigation": "Focus stays on input; aria-activedescendant indicates visual highlight";
    "suggestion selection": "Focus returns to input after selection";
    "clear button": "Focus returns to input after clearing";
    "mount with autoFocus": "Input receives focus on mount";
  };

  screenReaderAnnouncements: {
    suggestionsLoaded: "'N suggestions available' announced via aria-live region";
    suggestionHighlighted: "Handled via aria-activedescendant (no extra announcement needed)";
    noResults: "'No results found' announced via aria-live region";
    searchCleared: "'Search cleared' announced via aria-live region";
  };
}
```

### Шаг 6: написать крайние случаи

```typescript
// --- Edge Cases ---

interface SearchBarEdgeCases {
  "empty submit": "If value is empty and user presses Enter, do NOT call onSubmit";
  "whitespace-only submit": "Trim value; if empty after trim, do NOT call onSubmit";
  "disabled state": "All interactions disabled; dropdown never opens; clear button hidden";
  "suggestions update while navigating": "Reset highlightedIndex to -1; keep dropdown open";
  "value prop changes externally": "Update input display; if new value is empty, close suggestions";
  "very long suggestion label": "Truncate with ellipsis; full text in title attribute";
  "HTML in suggestion label": "Escape HTML; only render highlightRanges as bold";
  "duplicate suggestion IDs": "Use array index as fallback key; log warning in development";
  "rapid typing": "Parent is responsible for debouncing API calls; component just renders what it gets";
  "mobile behavior": "No hover states; tap to select; virtual keyboard should not obscure dropdown";
  "RTL languages": "Component must support right-to-left text direction";
}
```

Эта полная спецификация — пропсы, состояние, поведение, доступность, крайние случаи — примерно 200 строк. Реализация будет 400–600 строк. Но эти 200 строк гарантируют, что 400–600 строк реализации верны, согласованы и полны.

---

## 2.8 Антишаблоны спецификации компонентов

### Антишаблон 1: избыточная спецификация визуальных деталей

```typescript
// BAD: This is a visual spec pretending to be a behavior spec
interface ButtonContract {
  props: {
    label: string;
    onClick: () => void;
    // These are VISUAL concerns, not behavioral:
    backgroundColor: string;      // NO
    hoverBackgroundColor: string;  // NO
    borderRadius: number;          // NO
    fontSize: number;              // NO
    fontWeight: string;            // NO
    padding: string;               // NO
    boxShadow: string;             // NO
  };
}
```

**Исправление:** замените визуальные пропсы семантическими вариантами:

```typescript
// GOOD: Behavior-focused with semantic variants
interface ButtonContract {
  props: {
    label: string;
    onClick: () => void;
    variant: "primary" | "secondary" | "destructive" | "ghost";
    size: "sm" | "md" | "lg";
    disabled?: boolean;
    loading?: boolean;
    iconBefore?: IconName;
    iconAfter?: IconName;
    fullWidth?: boolean;
  };
}
```

Визуальный смысл «primary» или «destructive» определяется в дизайн-системе, а не в контракте компонента.

### Антишаблон 2: недостаточная спецификация поведения

```typescript
// BAD: Missing critical behavioral details
interface DropdownContract {
  props: {
    options: string[];
    onSelect: (option: string) => void;
  };
  // That is it? What about:
  // - Keyboard navigation?
  // - Multi-select?
  // - Search/filter?
  // - Accessibility?
  // - Loading state?
  // - Empty state?
  // - Positioning (what if it overflows the viewport)?
}
```

**Исправление:** перечислите все поведения, даже если некоторые «по умолчанию»:

```typescript
// GOOD: Complete behavioral specification
interface DropdownContract {
  props: {
    options: DropdownOption[];
    value: string | string[] | null;  // Current selection
    onChange: (value: string | string[]) => void;
    multiple?: boolean;               // Default: false
    searchable?: boolean;             // Default: false
    loading?: boolean;
    disabled?: boolean;
    placeholder?: string;
    emptyMessage?: string;            // Default: "No options available"
    maxHeight?: number;               // Max dropdown height in px
    placement?: "bottom" | "top" | "auto";  // Default: "auto"
  };

  behavior: {
    keyboard: { /* ... full keyboard spec ... */ };
    positioning: "Auto-flip to top if insufficient space below";
    virtualScroll: "If options > 100, use virtualized list";
    search: "Filter options client-side; highlight matching text";
  };

  accessibility: {
    role: "listbox";
    ariaAttributes: { /* ... */ };
  };
}
```

### Антишаблон 3: неявные побочные эффекты

```typescript
// BAD: Side effects are hidden in the implementation
interface UserProfileContract {
  props: {
    userId: string;
  };
  // Where does the user data come from?
  // Is there a fetch on mount?
  // Does it cache? Refetch on window focus?
  // Does it update the document title?
  // Does it track a page view?
}
```

**Исправление:** объявите все побочные эффекты явно:

```typescript
// GOOD: All side effects are visible in the contract
interface UserProfileContract {
  props: {
    userId: string;
    onError?: (error: ApiError) => void;
  };

  sideEffects: {
    dataFetching: {
      endpoint: "GET /api/users/${userId}";
      trigger: "On mount and when userId changes";
      caching: "Cache for 5 minutes; stale-while-revalidate";
      refetch: "On window focus; on network reconnect";
    };
    documentTitle: {
      action: "Set document.title to '${user.displayName} — Profile'";
      cleanup: "Restore previous title on unmount";
    };
    analytics: {
      pageView: "Track 'profile_view' event with userId on mount";
      condition: "Only track once per mount (not on refetch)";
    };
  };
}
```

### Антишаблон 4: спецификация протаскивания пропсов

```typescript
// BAD: Specifying props that are just passed through to children
interface PageLayoutContract {
  props: {
    // These are all just passed to child components:
    headerTitle: string;
    headerSubtitle: string;
    headerShowLogo: boolean;
    sidebarItems: MenuItem[];
    sidebarCollapsed: boolean;
    sidebarOnToggle: () => void;
    footerLinks: Link[];
    footerCopyright: string;
    // ... 20 more pass-through props
  };
}
```

**Исправление:** используйте композицию и ссылайтесь на контракты детей:

```typescript
// GOOD: Compose child contracts
interface PageLayoutContract {
  props: {
    header: React.ReactNode;     // Parent renders <Header> with its own props
    sidebar: React.ReactNode;    // Parent renders <Sidebar> with its own props
    footer: React.ReactNode;     // Parent renders <Footer> with its own props
    children: React.ReactNode;   // Main content area
  };

  behavior: {
    layout: "CSS Grid with header, sidebar, main, footer regions";
    responsive: "Sidebar collapses to overlay on screens < 768px";
    scrolling: "Main content scrolls independently; header is sticky";
  };
}
```

---

## 2.9 От контракта к реализации: передача

Когда контракт компонента готов, передача в реализацию (человеку или ИИ) становится простой.

### Передача ИИ

Вот шаблон для передачи контракта компонента ИИ:

```markdown
## Implementation Request

Implement the following React component based on this contract.

### Component: SearchBar

### Contract:
[paste full contract here]

### Implementation Requirements:
- React 19 with TypeScript
- Use `useState` and `useEffect` (no external state library)
- Use `useRef` for DOM references
- Use `useCallback` for stable callback references
- Tailwind CSS for styling (utility classes only)
- Follow the accessibility spec exactly
- Handle all listed edge cases
- Include JSDoc comments on the component and its props

### Testing Requirements:
- Write tests using Vitest + React Testing Library
- Test every keyboard interaction
- Test every edge case listed in the contract
- Test accessibility (use @testing-library/jest-dom matchers)
- Use `userEvent` instead of `fireEvent` for realistic interactions

### File Structure:
- `SearchBar.tsx` — the component
- `SearchBar.test.tsx` — the tests
- `SearchBar.types.ts` — the TypeScript interfaces (from the contract)
```

Теперь у ИИ есть всё. Контракт устраняет догадки. Требования к реализации устраняют неоднозначность инструментов. Требования к тестированию обеспечивают проверку контракта.

### Передача между командами

Тот же контракт облегчает передачу между людьми:

- **Бэкенд-команда** читает пропсы, чтобы понять, какая форма данных нужна фронтенду
- **Команда дизайна** читает спецификацию поведения, чтобы понять требования взаимодействия
- **QA** читает крайние случаи как план тестирования
- **Команда доступности** читает спецификацию доступности как чек-лист аудита

Контракт компонента — единственный документ, на который ссылаются все заинтересованные стороны.

---

## 2.10 Упражнения

### Упражнение 1: специфицировать компонент DataTable

Напишите полный контракт компонента DataTable, поддерживающего:
- Определения колонок (сортируемые, фильтруемые, изменяемые по ширине)
- Пагинацию (клиентскую и серверную)
- Выбор строк (одиночный и множественный)
- Раскрываемые строки
- Редактирование на месте
- Переключение видимости колонок
- Экспорт в CSV

Контракт должен включать: пропсы, состояние, поведение, взаимодействие с клавиатуры, доступность и крайние случаи. НЕ пишите реализацию — только контракт.

### Упражнение 2: специфицировать компонент NotificationCenter

Напишите контракт компонента NotificationCenter (иконка колокольчика + выпадающий список уведомлений):
- Показывает бейдж непрочитанных
- Выпадающий список уведомлений (сгруппированных по дате)
- Поддержка разных типов уведомлений (info, warning, error, success)
- Отметка отдельного или всех как прочитанных
- Клик по уведомлению для перехода
- Обновления в реальном времени (новые уведомления без перезагрузки)
- Пустое состояние
- Состояние загрузки

### Упражнение 3: задача «спецификация → реализация»

Возьмите контракт SearchBar из раздела 2.7 и передайте его ИИ-ассистенту (Claude, GPT, Gemini). Затем возьмите только естественно-языковое описание из шага 1 раздела 2.7 (список из 8 требований) и передайте ЕГО тому же ИИ.

Сравните две реализации:
- В какой полнее навигация с клавиатуры?
- Какая обрабатывает больше крайних случаев?
- У какой лучше доступность?
- Какая потребовала больше последующих промптов, чтобы стать правильной?

Задокументируйте выводы. Это упражнение продемонстрирует конкретную ценность контрактов компонентов в ИИ-разработке.

### Упражнение 4: отрефакторить «божественный» компонент

Вот избыточно специфицированный компонент. Отрефакторите его в правильный контракт:

```typescript
// Refactor this into a proper component contract
interface BadModalProps {
  show: boolean;
  title: string;
  message: string;
  okText: string;
  cancelText: string;
  okColor: string;
  cancelColor: string;
  width: string;
  height: string;
  borderRadius: string;
  overlayColor: string;
  overlayOpacity: number;
  animationDuration: number;
  zIndex: number;
  onOk: () => void;
  onCancel: () => void;
  className: string;
  style: React.CSSProperties;
  headerClassName: string;
  bodyClassName: string;
  footerClassName: string;
}
```

Отделите поведенческие пропсы от визуальных. Добавьте недостающие поведенческие заботы (обработка клавиатуры, удержание фокуса, доступность). Удалите визуальные пропсы, которым место в дизайн-системе.

---

## 2.11 Ключевые выводы

1. **Контракт компонента** определяет пропсы, состояние и побочные эффекты — НЕ визуальную стилизацию.

2. **Отделяйте спецификации поведения от визуальных.** Они меняются с разной скоростью, принадлежат разным людям и служат разным целям.

3. **Пропсы — контракты** между родителем и ребёнком. Проектируйте их как API: с ясными типами, разумными значениями по умолчанию и явной документацией.

4. **Машины состояний** — самый строгий способ специфицировать поведение компонента. Они перечисляют все состояния, события и допустимые переходы.

5. **Побочные эффекты должны объявляться явно.** Вызовы API, таймеры, слушатели событий, аналитика — если компонент затрагивает внешний мир, это принадлежит контракту.

6. **Крупные дизайн-системы** (Material, React Aria, Radix) отделяют поведенческие контракты от визуальной реализации. Это не случайность — это шаблон, который масштабируется.

7. **Избыточная спецификация визуала** и **недостаточная спецификация поведения** — два самых частых антишаблона. Ошибайтесь в сторону большей поведенческой детализации.

8. **Контракты компонентов — лучшие промпты для ИИ.** Полный контракт даёт радикально лучшие ИИ-реализации, чем прозаические описания.

---

## Взгляд вперёд

В следующей главе мы перейдём от отдельных компонентов к связям между ними: **чертежи API**. Вы узнаете, как специфицировать контракты запросов/ответов, соединяющие фронтенд-компоненты с бэкенд-сервисами. Если контракты компонентов — органы, чертежи API — кровеносная система.

---

*Конец главы 2 — Контракт компонента*
