# Глава 4: Спецификации управления состоянием

## МОДУЛЬ 02 — Определение архитектуры («как») | Средний уровень

---

## Вступление к лекции

*Профессор рисует на доске диаграмму: пользователь нажимает кнопку, срабатывает вызов API, появляется индикатор загрузки, приходят данные, UI обновляется, всплывает уведомление. Стрелки связывают эти события в паутину зависимостей.*

Посмотрите на эту диаграмму. Это упрощённая версия того, что происходит, когда пользователь нажимает «Назначить задачу на меня» в нашем приложении управления задачами. Один клик запускает каскад: оптимистичное обновление UI, вызов API, состояние загрузки, ответ об успехе или ошибке, уведомление, инвалидация кеша и, возможно, обновление в реальном времени для других пользователей, смотрящих ту же задачу.

Если не специфицировать этот каскад до реализации, наступает хаос. Оптимистичное обновление показывает не того пользователя. Индикатор загрузки появляется не там. Состояние ошибки не откатывает оптимистичное обновление. Инвалидация кеша упускает связанный запрос. Обновление в реальном времени конфликтует с локальным состоянием.

Это проблема управления состоянием, и это последний кусок нашей головоломки архитектурной спецификации. В этой главе вы научитесь **специфицировать поток данных через приложение** — хранилища, действия, селекторы и побочные эффекты, превращающие намерения пользователя в изменения UI.

Когда вы передаёте ИИ спецификацию управления состоянием, вы точно говорите, как каждый кусок данных движется, преобразуется и вызывает реакции в приложении. Без этой спецификации ИИ изобретёт собственную архитектуру состояния — и она будет разной в каждом компоненте.

---

## 4.1 Почему управление состоянием требует спецификации

Управление состоянием — самая часто «придумываемая по ходу» часть разработки приложений. Команды начинают с нескольких хуков useState, затем добавляют провайдер контекста, затем понимают, что нужен глобальный store, затем прикручивают слой кеширования, затем добавляют оптимистичные обновления, и вскоре у них монстр Франкенштейна из состояния, размазанного по пяти разным механизмам.

ИИ-разработка делает это хуже, а не лучше. Каждый раз, когда вы просите ИИ построить функцию, он выбирает подход к управлению состоянием, который кажется разумным для этой функции в изоляции. После десяти функций у вас десять разных шаблонов состояния.

Решение то же, что для схем, компонентов и API: **сначала специфицируйте.**

Спецификация управления состоянием определяет:

1. **Форму хранилища** — какие данные хранятся и в какой структуре
2. **Действия** — какие операции могут изменять состояние
3. **Селекторы** — как компоненты читают производные данные из хранилища
4. **Побочные эффекты** — что происходит вне хранилища при отправке действий
5. **Поток данных** — как ответы API, события пользователя и обновления в реальном времени взаимодействуют

### Прозрение Redux

Даже если вы никогда не используете Redux, его ключевая мысль фундаментальна для спецификации управления состоянием: **изменения состояния описываются действиями, а действия — контракты.**

Когда Redux в 2015 году ввёл концепцию «действий», он на самом деле ввёл концепцию **спецификаций изменения состояния**. Действие говорит: «Произошло это конкретное событие, и вот связанные с ним данные». Редьюсер говорит: «Учитывая текущее состояние и это действие, вот новое состояние».

Это чистое мышление спецификациями:

```typescript
// This is a SPEC, not just code:
// "When a task is assigned, these are the inputs and this is the result"

type Action =
  | { type: "TASK_ASSIGNED"; taskId: string; assigneeId: string }
  | { type: "TASK_UNASSIGNED"; taskId: string }
  | { type: "TASK_STATUS_CHANGED"; taskId: string; newStatus: TaskStatus }
  | { type: "TASK_CREATED"; task: Task }
  | { type: "TASK_DELETED"; taskId: string };

// The reducer is a STATE TRANSITION FUNCTION — a formalization of "given this state and this event, produce this state"
function taskReducer(state: TaskState, action: Action): TaskState {
  switch (action.type) {
    case "TASK_ASSIGNED":
      // Spec: set task.assigneeId to the new value; update task.updatedAt
      return {
        ...state,
        tasks: state.tasks.map((t) =>
          t.id === action.taskId
            ? { ...t, assigneeId: action.assigneeId, updatedAt: new Date().toISOString() }
            : t
        ),
      };
    // ... other cases
  }
}
```

> **Заметка профессора:** Хочу быть ясным: я не говорю использовать Redux. У Redux есть своё место, но современные React-приложения имеют много вариантов — Zustand, Jotai, Valtio, MobX, React Context и всё более мощную комбинацию React Server Components с серверным состоянием. Я говорю, что *концептуальная модель* Redux — состояние + действие = новое состояние — правильный способ *специфицировать* управление состоянием, независимо от библиотеки.

---

## 4.2 Определение форм хранилища

Первый шаг спецификации управления состоянием — определение формы хранилищ. Форма хранилища — схема (глава 1), применённая к состоянию приложения.

### Принцип: нормализуйте состояние

Прежде чем писать формы хранилищ, установим критический принцип: **нормализуйте состояние**. Как реляционная база данных нормализует данные, чтобы избежать дублирования, ваше хранилище должно нормализовать сущности.

```typescript
// BAD: Denormalized (nested) state
interface BadTaskState {
  projects: Array<{
    id: string;
    name: string;
    tasks: Array<{           // Tasks are nested inside projects
      id: string;
      title: string;
      assignee: {            // User data is duplicated in every task
        id: string;
        name: string;
        email: string;
      } | null;
      comments: Array<{     // Comments nested inside tasks
        id: string;
        content: string;
        author: {            // User data duplicated AGAIN
          id: string;
          name: string;
        };
      }>;
    }>;
  }>;
}
// Problem: If a user changes their name, you must update it
// in every task and every comment where they appear.
```

```typescript
// GOOD: Normalized state
interface NormalizedState {
  // Each entity type gets its own flat collection
  users: {
    byId: Record<string, User>;
    allIds: string[];
  };
  projects: {
    byId: Record<string, Project>;
    allIds: string[];
  };
  tasks: {
    byId: Record<string, Task>;
    // Index by project for fast lookups
    idsByProject: Record<string, string[]>;
  };
  comments: {
    byId: Record<string, Comment>;
    // Index by task for fast lookups
    idsByTask: Record<string, string[]>;
  };
}
```

### Полная спецификация формы хранилища

Вот полная спецификация формы хранилища для нашего приложения управления задачами:

```typescript
// ===================================================
// TASK MANAGEMENT APP — STATE MANAGEMENT SPECIFICATION
// ===================================================

// --- Root Store Shape ---

interface RootStore {
  auth: AuthStore;
  workspace: WorkspaceStore;
  projects: ProjectsStore;
  tasks: TasksStore;
  ui: UIStore;
}

// --- Auth Store ---

interface AuthStore {
  /** The authenticated user, or null if not logged in */
  currentUser: User | null;

  /** Authentication status */
  status: "idle" | "authenticating" | "authenticated" | "error";

  /** Auth error message, if any */
  error: string | null;

  /** JWT access token (stored in memory, NOT localStorage) */
  accessToken: string | null;

  /** When the access token expires (for proactive refresh) */
  tokenExpiresAt: number | null;  // Unix timestamp
}

// --- Workspace Store ---

interface WorkspaceStore {
  /** The active workspace */
  activeWorkspace: Workspace | null;

  /** All workspaces the user belongs to */
  workspaces: Workspace[];

  /** Members of the active workspace */
  members: {
    byId: Record<string, WorkspaceMember>;
    allIds: string[];
    loading: boolean;
    error: string | null;
  };

  /** Labels in the active workspace */
  labels: {
    byId: Record<string, Label>;
    allIds: string[];
    loading: boolean;
    error: string | null;
  };
}

// --- Projects Store ---

interface ProjectsStore {
  /** Normalized project entities */
  byId: Record<string, Project>;

  /** Ordered list of project IDs */
  allIds: string[];

  /** Currently selected project ID */
  activeProjectId: string | null;

  /** Loading state for the project list */
  loading: boolean;

  /** Error from the last project operation */
  error: string | null;
}

// --- Tasks Store ---

interface TasksStore {
  /** Normalized task entities */
  byId: Record<string, Task>;

  /** Task IDs indexed by project */
  idsByProject: Record<string, string[]>;

  /** Task IDs indexed by current view/filter.
   *  This is the "active query result" — the task IDs
   *  that match the current filter/sort/search criteria. */
  activeQueryResult: {
    taskIds: string[];
    totalCount: number;
    nextCursor: string | null;
    loading: boolean;
    error: string | null;
  };

  /** Active filters for the task list */
  filters: TaskFilters;

  /** Sort configuration */
  sort: {
    field: "created_at" | "updated_at" | "priority" | "due_date";
    order: "asc" | "desc";
  };

  /** Optimistic updates in flight.
   *  Maps taskId -> the pending changes.
   *  Used to revert on failure. */
  optimisticUpdates: Record<string, {
    previousState: Task;
    pendingAction: string;
    timestamp: number;
  }>;

  /** Task currently being edited (for detail view) */
  activeTaskId: string | null;
}

interface TaskFilters {
  status: TaskStatus[] | null;        // null = all statuses
  priority: TaskPriority[] | null;    // null = all priorities
  assigneeId: string | null;          // null = all assignees
  labelIds: string[] | null;          // null = all labels
  search: string;                     // empty string = no search
  dueBefore: string | null;           // YYYY-MM-DD
  dueAfter: string | null;            // YYYY-MM-DD
}

// --- UI Store ---

interface UIStore {
  /** Sidebar state */
  sidebar: {
    isOpen: boolean;
    width: number;         // In pixels, for resize support
  };

  /** Modal state */
  modal: {
    type: ModalType | null;
    props: Record<string, unknown>;
  };

  /** Command palette state */
  commandPalette: {
    isOpen: boolean;
    query: string;
  };

  /** Toast notifications */
  toasts: Toast[];

  /** Theme preference */
  theme: "light" | "dark" | "system";

  /** Whether the app is in offline mode */
  isOffline: boolean;
}

type ModalType =
  | "createTask"
  | "editTask"
  | "deleteTask"
  | "createProject"
  | "editProject"
  | "inviteMember"
  | "settings";

interface Toast {
  id: string;
  type: "success" | "error" | "warning" | "info";
  title: string;
  message?: string;
  duration: number;        // Milliseconds, 0 = persistent
  action?: {
    label: string;
    onClick: () => void;
  };
  createdAt: number;       // Unix timestamp
}
```

> **Заметка профессора:** Посмотрите на поле `optimisticUpdates` в хранилище Tasks. Это одно из важнейших проектных решений в любой спецификации управления состоянием. Оптимистичные обновления делают UI мгновенным: пользователь сразу видит изменение, а вызов API происходит в фоне. Но если вызов API не удался, нужно откатиться к предыдущему состоянию. Включив `previousState` в спецификацию, мы обеспечиваем правильный откат. Без этого девять из десяти ИИ-реализаций оптимистично обновят, но никогда не откатят при ошибке.

---

## 4.3 Определение действий

Действия — события, вызывающие изменения состояния. В спецификации управления состоянием каждое действие должно определять:

1. **Имя** — что произошло
2. **Payload** — данные, связанные с событием
3. **Изменения состояния** — какие именно поля меняются и как
4. **Побочные эффекты** — внешние операции, вызываемые действием

### Формат спецификации действия

```typescript
// ===================================================
// TASK ACTIONS — COMPLETE SPECIFICATION
// ===================================================

// --- Action Types ---

type TaskAction =
  // --- CRUD Actions ---
  | { type: "tasks/fetchList"; payload: FetchTasksPayload }
  | { type: "tasks/fetchListSuccess"; payload: FetchTasksSuccessPayload }
  | { type: "tasks/fetchListError"; payload: { error: string } }

  | { type: "tasks/fetchOne"; payload: { taskId: string } }
  | { type: "tasks/fetchOneSuccess"; payload: { task: Task } }
  | { type: "tasks/fetchOneError"; payload: { taskId: string; error: string } }

  | { type: "tasks/create"; payload: CreateTaskPayload }
  | { type: "tasks/createSuccess"; payload: { task: Task } }
  | { type: "tasks/createError"; payload: { error: string; tempId: string } }

  | { type: "tasks/update"; payload: UpdateTaskPayload }
  | { type: "tasks/updateSuccess"; payload: { task: Task } }
  | { type: "tasks/updateError"; payload: { taskId: string; error: string } }

  | { type: "tasks/delete"; payload: { taskId: string } }
  | { type: "tasks/deleteSuccess"; payload: { taskId: string } }
  | { type: "tasks/deleteError"; payload: { taskId: string; error: string } }

  // --- Filter/Sort Actions ---
  | { type: "tasks/setFilters"; payload: Partial<TaskFilters> }
  | { type: "tasks/clearFilters" }
  | { type: "tasks/setSort"; payload: { field: string; order: "asc" | "desc" } }

  // --- Pagination Actions ---
  | { type: "tasks/loadMore" }
  | { type: "tasks/loadMoreSuccess"; payload: FetchTasksSuccessPayload }
  | { type: "tasks/loadMoreError"; payload: { error: string } }

  // --- Selection Actions ---
  | { type: "tasks/setActiveTask"; payload: { taskId: string | null } }

  // --- Optimistic Actions ---
  | { type: "tasks/optimisticUpdate"; payload: { taskId: string; changes: Partial<Task> } }
  | { type: "tasks/revertOptimistic"; payload: { taskId: string } }

  // --- Real-time Actions ---
  | { type: "tasks/realtime/created"; payload: { task: Task } }
  | { type: "tasks/realtime/updated"; payload: { task: Task } }
  | { type: "tasks/realtime/deleted"; payload: { taskId: string } };

// --- Payload Types ---

interface FetchTasksPayload {
  projectId: string;
  filters?: Partial<TaskFilters>;
  sort?: { field: string; order: "asc" | "desc" };
  cursor?: string;
  limit?: number;
}

interface FetchTasksSuccessPayload {
  tasks: Task[];
  nextCursor: string | null;
  totalCount: number;
  append: boolean;  // true for "load more", false for fresh fetch
}

interface CreateTaskPayload {
  projectId: string;
  title: string;
  description?: string;
  priority?: TaskPriority;
  assigneeId?: string | null;
  labelIds?: string[];
  dueDate?: string | null;
  parentTaskId?: string | null;
  tempId: string;  // Temporary ID for optimistic UI
}

interface UpdateTaskPayload {
  taskId: string;
  changes: Partial<{
    title: string;
    description: string;
    status: TaskStatus;
    priority: TaskPriority;
    assigneeId: string | null;
    labelIds: string[];
    dueDate: string | null;
    estimatePoints: number | null;
  }>;
}
```

### Спецификация изменения состояния для каждого действия

Для каждого действия документально зафиксируйте, как именно меняется состояние:

```typescript
// ===================================================
// STATE CHANGE SPECIFICATIONS
// ===================================================

const stateChangeSpecs = {
  "tasks/fetchList": {
    stateChanges: {
      "activeQueryResult.loading": "set to true",
      "activeQueryResult.error": "set to null",
    },
    sideEffects: [
      "Make GET /api/v1/projects/{projectId}/tasks with current filters and sort",
      "On success: dispatch tasks/fetchListSuccess",
      "On failure: dispatch tasks/fetchListError",
    ],
  },

  "tasks/fetchListSuccess": {
    stateChanges: {
      "byId": "merge tasks into the normalized map (add or update)",
      "idsByProject[projectId]": "update to reflect returned task IDs",
      "activeQueryResult.taskIds": "payload.append ? append : replace",
      "activeQueryResult.totalCount": "set to payload.totalCount",
      "activeQueryResult.nextCursor": "set to payload.nextCursor",
      "activeQueryResult.loading": "set to false",
      "activeQueryResult.error": "set to null",
    },
    sideEffects: [],
  },

  "tasks/fetchListError": {
    stateChanges: {
      "activeQueryResult.loading": "set to false",
      "activeQueryResult.error": "set to payload.error",
    },
    sideEffects: [
      "Dispatch ui/showToast with type 'error' and message from payload",
    ],
  },

  "tasks/create": {
    stateChanges: {
      // Optimistic: add a temporary task to the store immediately
      "byId[tempId]": "create temporary task with tempId, status 'backlog', provided fields",
      "idsByProject[projectId]": "prepend tempId to the list",
      "activeQueryResult.taskIds": "prepend tempId if it matches current filters",
      "activeQueryResult.totalCount": "increment by 1",
    },
    sideEffects: [
      "Make POST /api/v1/projects/{projectId}/tasks",
      "On success: dispatch tasks/createSuccess",
      "On failure: dispatch tasks/createError",
    ],
  },

  "tasks/createSuccess": {
    stateChanges: {
      // Replace temporary task with real task from server
      "byId": "remove entry for tempId; add entry for real task.id",
      "idsByProject[projectId]": "replace tempId with real task.id",
      "activeQueryResult.taskIds": "replace tempId with real task.id",
    },
    sideEffects: [
      "Dispatch ui/showToast with type 'success': 'Task created'",
      "Close 'createTask' modal if open",
    ],
  },

  "tasks/createError": {
    stateChanges: {
      // Remove the optimistic temporary task
      "byId": "remove entry for tempId",
      "idsByProject[projectId]": "remove tempId from list",
      "activeQueryResult.taskIds": "remove tempId from list",
      "activeQueryResult.totalCount": "decrement by 1",
    },
    sideEffects: [
      "Dispatch ui/showToast with type 'error': payload.error",
    ],
  },

  "tasks/update": {
    stateChanges: {
      // Optimistic: apply changes immediately
      "optimisticUpdates[taskId]": "store { previousState: current task, pendingAction: 'update', timestamp: now }",
      "byId[taskId]": "merge payload.changes into existing task; update updatedAt",
    },
    sideEffects: [
      "Make PATCH /api/v1/tasks/{taskId} with payload.changes",
      "On success: dispatch tasks/updateSuccess",
      "On failure: dispatch tasks/updateError",
    ],
  },

  "tasks/updateSuccess": {
    stateChanges: {
      "byId[taskId]": "replace with server response (authoritative state)",
      "optimisticUpdates[taskId]": "remove entry",
    },
    sideEffects: [],
  },

  "tasks/updateError": {
    stateChanges: {
      // Revert to previous state
      "byId[taskId]": "restore from optimisticUpdates[taskId].previousState",
      "optimisticUpdates[taskId]": "remove entry",
    },
    sideEffects: [
      "Dispatch ui/showToast with type 'error': payload.error",
      "Dispatch ui/showToast with action: { label: 'Retry', onClick: re-dispatch original update }",
    ],
  },

  "tasks/setFilters": {
    stateChanges: {
      "filters": "merge payload into existing filters",
      "activeQueryResult.taskIds": "clear (will be repopulated by fetch)",
      "activeQueryResult.nextCursor": "set to null",
    },
    sideEffects: [
      "Debounce 300ms, then dispatch tasks/fetchList with new filters",
    ],
  },

  "tasks/realtime/updated": {
    stateChanges: {
      "byId[task.id]": "update if task.updatedAt > current task.updatedAt (last-write-wins)",
    },
    sideEffects: [
      "If task.id === activeTaskId, check if another user modified fields the current user is editing — if so, show conflict notification",
    ],
    note: "Do NOT apply if there is a pending optimistic update for this task",
  },
};
```

---

## 4.4 Определение селекторов

Селекторы — функции, выводящие данные из хранилища. Они отвечают на вопрос: «Что этому компоненту на самом деле нужно из состояния?»

### Зачем селекторам спецификации

Без спецификаций селекторов каждый компонент тянется напрямую в хранилище и вычисляет свои производные данные. Это ведёт к:

- Дублированию логики между компонентами
- Несогласованным вычислениям (один компонент фильтрует иначе, чем другой)
- Проблемам производительности (пересчёт при каждом рендере)
- Путанице ИИ (ИИ не может предсказать, какую форму данных ожидает компонент)

### Спецификация селекторов

```typescript
// ===================================================
// SELECTORS — SPECIFICATION
// ===================================================

/**
 * selectActiveProject
 *
 * Returns: Project | null
 * Depends on: projects.byId, projects.activeProjectId
 * Used by: ProjectHeader, TaskList, TaskCreateModal
 *
 * Logic:
 *   If activeProjectId is null, return null.
 *   Otherwise, return projects.byId[activeProjectId].
 *   If the project is not in the store (should not happen), return null.
 */

/**
 * selectFilteredTasks
 *
 * Returns: Task[]
 * Depends on: tasks.byId, tasks.activeQueryResult.taskIds
 * Used by: TaskList, TaskBoard
 *
 * Logic:
 *   Map activeQueryResult.taskIds to Task objects from tasks.byId.
 *   Filter out any IDs that no longer exist in byId
 *   (handles race conditions with deletions).
 *   Apply sort from tasks.sort (client-side re-sort of server results).
 *
 * Memoization: Memoize on taskIds array reference and byId reference.
 */

/**
 * selectTaskById
 *
 * Input: taskId: string
 * Returns: Task | undefined
 * Depends on: tasks.byId
 * Used by: TaskDetailView, TaskCard, TaskRow
 *
 * Logic: Direct lookup: tasks.byId[taskId]
 * Memoization: Memoize per taskId (returns same reference if task unchanged).
 */

/**
 * selectTaskCounts
 *
 * Returns: { total: number, byStatus: Record<TaskStatus, number>, byPriority: Record<TaskPriority, number> }
 * Depends on: tasks.byId, tasks.idsByProject, projects.activeProjectId
 * Used by: ProjectSidebar, TaskFilterBar
 *
 * Logic:
 *   Get all task IDs for the active project.
 *   Count tasks by status and priority.
 *   Return the counts object.
 *
 * Memoization: Recompute only when tasks in the active project change.
 */

/**
 * selectOverdueTasks
 *
 * Returns: Task[]
 * Depends on: tasks.byId, tasks.idsByProject, projects.activeProjectId
 * Used by: ProjectDashboard, OverdueWidget
 *
 * Logic:
 *   Get all tasks for the active project.
 *   Filter to tasks where:
 *     - dueDate is not null
 *     - dueDate < today
 *     - status is NOT "done" or "cancelled"
 *   Sort by dueDate ascending (most overdue first).
 *
 * Edge cases:
 *   - "today" is determined by the workspace timezone setting
 *   - Tasks with due date of today are NOT overdue (they are due today)
 */

/**
 * selectAssigneesForActiveProject
 *
 * Returns: Array<{ user: User, taskCount: number }>
 * Depends on: workspace.members, tasks.byId, tasks.idsByProject
 * Used by: AssigneeFilter, TaskAssigneeDropdown
 *
 * Logic:
 *   Get all members of the workspace.
 *   For each member, count tasks assigned to them in the active project.
 *   Sort by task count descending (busiest first).
 *   Include members with 0 tasks.
 */

/**
 * selectIsTaskListLoading
 *
 * Returns: boolean
 * Depends on: tasks.activeQueryResult.loading
 * Used by: TaskList, TaskBoard
 *
 * Note: Simple selector, but specified to ensure consistent loading
 * behavior across views that show the same data.
 */

/**
 * selectCanLoadMore
 *
 * Returns: boolean
 * Depends on: tasks.activeQueryResult.nextCursor, tasks.activeQueryResult.loading
 * Used by: TaskList (infinite scroll trigger)
 *
 * Logic: nextCursor is not null AND not currently loading.
 */

/**
 * selectHasOptimisticUpdates
 *
 * Input: taskId: string
 * Returns: boolean
 * Depends on: tasks.optimisticUpdates
 * Used by: TaskCard (to show "saving..." indicator)
 *
 * Logic: taskId exists in optimisticUpdates map.
 */
```

### Пример реализации селекторов (Zustand)

Вот как эти спецификации селекторов переводятся в реализацию на Zustand:

```typescript
import { create } from "zustand";
import { createSelector } from "reselect";

// The store (simplified)
const useTaskStore = create<TasksStore>((set, get) => ({
  byId: {},
  idsByProject: {},
  activeQueryResult: {
    taskIds: [],
    totalCount: 0,
    nextCursor: null,
    loading: false,
    error: null,
  },
  filters: {
    status: null,
    priority: null,
    assigneeId: null,
    labelIds: null,
    search: "",
    dueBefore: null,
    dueAfter: null,
  },
  sort: { field: "created_at", order: "desc" },
  optimisticUpdates: {},
  activeTaskId: null,

  // Actions (implemented per action specs above)
  // ...
}));

// Selectors (implemented per selector specs above)

const selectFilteredTasks = createSelector(
  (state: TasksStore) => state.activeQueryResult.taskIds,
  (state: TasksStore) => state.byId,
  (taskIds, byId) =>
    taskIds
      .map((id) => byId[id])
      .filter((task): task is Task => task !== undefined)
);

const selectTaskById = (taskId: string) =>
  createSelector(
    (state: TasksStore) => state.byId,
    (byId) => byId[taskId]
  );

const selectCanLoadMore = createSelector(
  (state: TasksStore) => state.activeQueryResult.nextCursor,
  (state: TasksStore) => state.activeQueryResult.loading,
  (nextCursor, loading) => nextCursor !== null && !loading
);
```

---

## 4.5 Серверное состояние против клиентского

Одно из важнейших различий в современной фронтенд-архитектуре — между **серверным состоянием** и **клиентским состоянием**. Это различие должно быть явным в вашей спецификации управления состоянием.

### Что такое серверное состояние?

Серверное состояние — данные, которые:
- Происходят из сервера и принадлежат ему
- Могут устареть (другой пользователь или процесс мог их изменить)
- Нуждаются в получении, кешировании и синхронизации
- Разделяются между несколькими клиентами

Примеры: данные пользователей, задачи, проекты, комментарии, уведомления.

### Что такое клиентское состояние?

Клиентское состояние — данные, которые:
- Происходят из клиента и принадлежат ему
- Всегда актуальны (по определению)
- Не нуждаются в синхронизации
- Специфичны для сессии этого пользователя

Примеры: открыт/закрыт сайдбар, текущие фильтры, видимость модального окна, значения полей формы, предпочтение темы.

### Спецификация границы

В вашей спецификации управления состоянием явно категоризируйте каждый кусок состояния:

```typescript
// ===================================================
// STATE OWNERSHIP SPECIFICATION
// ===================================================

/**
 * SERVER STATE (managed by TanStack Query / React Query)
 *
 * These are fetched from the API, cached, and automatically
 * refetched when stale. The query cache is the source of truth.
 *
 * Entity queries:
 *   - tasks: GET /api/v1/projects/{projectId}/tasks
 *   - task detail: GET /api/v1/tasks/{taskId}
 *   - projects: GET /api/v1/workspaces/{workspaceId}/projects
 *   - workspace members: GET /api/v1/workspaces/{workspaceId}/members
 *   - labels: GET /api/v1/workspaces/{workspaceId}/labels
 *   - comments: GET /api/v1/tasks/{taskId}/comments
 *   - notifications: GET /api/v1/notifications
 *   - current user: GET /api/v1/users/me
 *
 * Cache configuration:
 *   - staleTime: 30 seconds (data is considered fresh for 30s)
 *   - gcTime: 5 minutes (unused cache entries removed after 5min)
 *   - refetchOnWindowFocus: true (refetch when user returns to tab)
 *   - refetchOnReconnect: true (refetch when network reconnects)
 *
 * Mutations:
 *   - All write operations (create, update, delete) go through mutations
 *   - Mutations use optimistic updates (see section 4.3)
 *   - On mutation success: invalidate related queries
 *   - On mutation failure: revert optimistic update + show error toast
 */

/**
 * CLIENT STATE (managed by Zustand)
 *
 * This state exists only in the client and is not persisted
 * to the server (unless explicitly noted).
 *
 * UI state:
 *   - sidebar.isOpen: boolean (persisted to localStorage)
 *   - sidebar.width: number (persisted to localStorage)
 *   - theme: string (persisted to localStorage)
 *   - commandPalette.isOpen: boolean
 *   - commandPalette.query: string
 *   - modal.type: ModalType | null
 *   - modal.props: Record<string, unknown>
 *   - toasts: Toast[]
 *
 * Navigation state:
 *   - activeProjectId: string | null (derived from URL params)
 *   - activeTaskId: string | null (derived from URL params)
 *
 * Filter/sort state:
 *   - filters: TaskFilters (persisted to URL query params)
 *   - sort: { field, order } (persisted to URL query params)
 *
 * Ephemeral state:
 *   - isOffline: boolean (derived from navigator.onLine)
 *   - optimisticUpdates: Record<string, ...> (cleared on page reload)
 */
```

### Шаблон TanStack Query / React Query

Вот как спецификация серверного состояния переводится в TanStack Query:

```typescript
// ===================================================
// SERVER STATE — TANSTACK QUERY SPECIFICATION
// ===================================================

// --- Query Keys ---
// Every query key is a tuple that uniquely identifies the data.
// This spec prevents key collisions and enables precise cache invalidation.

const queryKeys = {
  tasks: {
    all: ["tasks"] as const,
    lists: () => [...queryKeys.tasks.all, "list"] as const,
    list: (projectId: string, filters: TaskFilters, sort: SortConfig) =>
      [...queryKeys.tasks.lists(), projectId, filters, sort] as const,
    details: () => [...queryKeys.tasks.all, "detail"] as const,
    detail: (taskId: string) =>
      [...queryKeys.tasks.details(), taskId] as const,
  },

  projects: {
    all: ["projects"] as const,
    lists: () => [...queryKeys.projects.all, "list"] as const,
    list: (workspaceId: string) =>
      [...queryKeys.projects.lists(), workspaceId] as const,
    details: () => [...queryKeys.projects.all, "detail"] as const,
    detail: (projectId: string) =>
      [...queryKeys.projects.details(), projectId] as const,
  },

  comments: {
    all: ["comments"] as const,
    list: (taskId: string) =>
      [...queryKeys.comments.all, "list", taskId] as const,
  },

  notifications: {
    all: ["notifications"] as const,
    list: () => [...queryKeys.notifications.all, "list"] as const,
    unreadCount: () =>
      [...queryKeys.notifications.all, "unread-count"] as const,
  },
};

// --- Cache Invalidation Rules ---
// When a mutation succeeds, these queries must be invalidated.

const invalidationRules = {
  "tasks/create": [
    "queryKeys.tasks.lists()",    // Refetch task list
    "queryKeys.tasks.all",        // Invalidate all task queries
  ],

  "tasks/update": (taskId: string) => [
    "queryKeys.tasks.detail(taskId)",  // Refetch updated task
    "queryKeys.tasks.lists()",          // Refetch task list (status/priority may have changed filter results)
  ],

  "tasks/delete": (taskId: string) => [
    "queryKeys.tasks.detail(taskId)",  // Remove from cache
    "queryKeys.tasks.lists()",          // Refetch task list
    "queryKeys.comments.list(taskId)", // Remove associated comments from cache
  ],

  "comments/create": (taskId: string) => [
    "queryKeys.comments.list(taskId)",  // Refetch comment list
    "queryKeys.tasks.detail(taskId)",   // Refetch task (commentCount changed)
  ],
};

// --- Optimistic Update Spec for Mutations ---

/**
 * updateTask mutation — optimistic update specification
 *
 * BEFORE API call:
 *   1. Cancel any in-flight queries for queryKeys.tasks.detail(taskId)
 *   2. Snapshot current task data from cache
 *   3. Optimistically update cache with new values
 *   4. Return snapshot for rollback
 *
 * ON SUCCESS:
 *   1. Replace cached task with server response (authoritative)
 *   2. Invalidate queryKeys.tasks.lists() (to update list views)
 *
 * ON ERROR:
 *   1. Restore snapshot to cache (rollback)
 *   2. Show error toast
 *
 * ON SETTLE (success or error):
 *   1. Refetch queryKeys.tasks.detail(taskId) to ensure consistency
 */
```

```typescript
// Implementation of the optimistic update spec:

function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: UpdateTaskPayload) =>
      api.patch(`/tasks/${payload.taskId}`, payload.changes),

    onMutate: async (payload) => {
      // Cancel in-flight queries
      await queryClient.cancelQueries({
        queryKey: queryKeys.tasks.detail(payload.taskId),
      });

      // Snapshot previous value
      const previousTask = queryClient.getQueryData<Task>(
        queryKeys.tasks.detail(payload.taskId)
      );

      // Optimistically update
      queryClient.setQueryData(
        queryKeys.tasks.detail(payload.taskId),
        (old: Task | undefined) =>
          old ? { ...old, ...payload.changes, updatedAt: new Date().toISOString() } : old
      );

      return { previousTask };
    },

    onError: (_error, payload, context) => {
      // Rollback
      if (context?.previousTask) {
        queryClient.setQueryData(
          queryKeys.tasks.detail(payload.taskId),
          context.previousTask
        );
      }
    },

    onSettled: (_data, _error, payload) => {
      // Always refetch to ensure consistency
      queryClient.invalidateQueries({
        queryKey: queryKeys.tasks.detail(payload.taskId),
      });
      queryClient.invalidateQueries({
        queryKey: queryKeys.tasks.lists(),
      });
    },
  });
}
```

> **Заметка профессора:** Шаблон TanStack Query решает одну из самых трудных проблем фронтенд-разработки: синхронизацию серверного состояния с UI. Но обратите внимание, сколько спецификации он требует. Ключи запросов, правила инвалидации кеша, жизненный цикл оптимистичного обновления — всё это нужно определить до реализации. Когда вы передаёте ИИ «используй React Query для получения данных» без правил инвалидации кеша, ИИ сделает успешный путь правильно, а каждый крайний случай упустит. Когда передаёте полную спецификацию, он делает всё правильно.

---

## 4.6 Как специфицировать потоки данных в реальном времени

Функции реального времени (события WebSocket, Server-Sent Events) — одни из самых трудных для правильной спецификации. Они вносят проблемы параллелизма, порядка и разрешения конфликтов, которых нет в архитектурах запрос-ответ.

### События WebSocket как контракты

```typescript
// ===================================================
// REAL-TIME EVENT SPECIFICATION
// ===================================================

// --- Connection Lifecycle ---

interface WebSocketSpec {
  endpoint: "wss://api.example.com/v1/ws";
  authentication: "JWT token sent as query parameter: ?token={jwt}";
  reconnection: {
    strategy: "Exponential backoff with jitter";
    initialDelay: 1000;     // 1 second
    maxDelay: 30000;        // 30 seconds
    maxAttempts: "unlimited (keep trying until connection restored)";
    jitter: "Add random 0-500ms to each delay";
  };
  heartbeat: {
    clientSendsEvery: 30000;  // Client pings every 30 seconds
    serverTimeout: 10000;     // If no pong in 10 seconds, reconnect
  };
  subscriptions: {
    method: "Send subscription messages after connection established";
    format: '{ "type": "subscribe", "channel": "project:{projectId}" }';
    unsubscribe: '{ "type": "unsubscribe", "channel": "project:{projectId}" }';
  };
}

// --- Event Types ---

type ServerEvent =
  | TaskCreatedEvent
  | TaskUpdatedEvent
  | TaskDeletedEvent
  | CommentCreatedEvent
  | UserPresenceEvent
  | TypingIndicatorEvent;

interface TaskCreatedEvent {
  type: "task.created";
  timestamp: string;        // ISO 8601
  channel: string;          // "project:{projectId}"
  payload: {
    task: Task;             // Full task object
    actorId: string;        // Who created it
  };
}

interface TaskUpdatedEvent {
  type: "task.updated";
  timestamp: string;
  channel: string;
  payload: {
    task: Task;             // Full updated task
    actorId: string;        // Who updated it
    changedFields: string[];// Which fields changed: ["status", "assigneeId"]
  };
}

interface TaskDeletedEvent {
  type: "task.deleted";
  timestamp: string;
  channel: string;
  payload: {
    taskId: string;
    actorId: string;
  };
}

interface CommentCreatedEvent {
  type: "comment.created";
  timestamp: string;
  channel: string;
  payload: {
    comment: Comment;
    taskId: string;
    actorId: string;
  };
}

interface UserPresenceEvent {
  type: "presence.update";
  timestamp: string;
  channel: string;
  payload: {
    userId: string;
    status: "online" | "away" | "offline";
    lastActiveAt: string;
    currentView: {
      type: "task" | "project" | "dashboard";
      entityId: string | null;
    } | null;
  };
}

interface TypingIndicatorEvent {
  type: "typing.indicator";
  timestamp: string;
  channel: string;
  payload: {
    userId: string;
    taskId: string;
    field: "title" | "description" | "comment";
    isTyping: boolean;
  };
}

// --- Event Handling Specification ---

interface EventHandlingSpec {
  "task.created": {
    action: "Add task to local cache if it belongs to the active project";
    conflict: "Check if task with this ID already exists (from optimistic create)";
    conflictResolution: "Server version wins — replace optimistic version";
    uiUpdate: "Append to task list if matches current filters; update totalCount";
    notification: "Show toast 'New task: {title}' if actorId !== currentUser.id";
    selfEvent: "If actorId === currentUser.id, ignore (already handled optimistically)";
  };

  "task.updated": {
    action: "Update task in local cache";
    conflict: "Check if we have a pending optimistic update for this task";
    conflictResolution: {
      noPendingUpdate: "Apply server version directly";
      pendingUpdateSameFields: "Server wins — discard optimistic, apply server version";
      pendingUpdateDifferentFields: "Merge — keep optimistic fields, apply server's other fields";
    };
    uiUpdate: "Re-evaluate filter membership (status change might add/remove from list)";
    notification: "Show toast if assigneeId changed to currentUser.id: 'You were assigned to {title}'";
    selfEvent: "If actorId === currentUser.id, only apply if server version is newer than our optimistic";
  };

  "task.deleted": {
    action: "Remove task from local cache";
    conflict: "If task is currently being edited, show 'This task was deleted' warning";
    uiUpdate: "Remove from task list; decrement totalCount";
    notification: "Show toast if task was assigned to currentUser: 'Task {displayId} was deleted'";
  };

  "presence.update": {
    action: "Update user presence in workspace members store";
    uiUpdate: "Update avatar indicators (green dot = online, yellow = away)";
    debounce: "Batch presence updates — process at most once per second";
  };

  "typing.indicator": {
    action: "Update typing indicators for the specified task/field";
    uiUpdate: "Show '{userName} is typing...' below the relevant field";
    timeout: "Clear typing indicator after 5 seconds of no typing events";
    selfEvent: "Ignore typing events from currentUser";
  };
}
```

### Спецификация разрешения конфликтов

Самая критичная часть спецификаций реального времени — разрешение конфликтов. Когда пользователь вносит изменение локально, а приходит обновление в реальном времени для той же сущности, что происходит?

```typescript
// ===================================================
// CONFLICT RESOLUTION SPECIFICATION
// ===================================================

interface ConflictResolutionSpec {
  strategy: "Last Write Wins with Optimistic Priority";

  rules: {
    rule1: {
      name: "Self-events are ignored";
      description: "If event.actorId === currentUser.id, the event is from our own action. We already have the optimistic state; ignore the echo.";
      exception: "Unless we received an error for our action — then the server event takes precedence.";
    };

    rule2: {
      name: "No pending optimistic update";
      description: "If there is no pending optimistic update for this entity, apply the server event directly.";
    };

    rule3: {
      name: "Optimistic update is pending, same fields changed";
      description: "If the server event changes the same fields as our pending optimistic update, this likely means another user modified the same thing. Show a conflict notification: 'Someone else changed the status of this task. Your change may be overwritten.'";
      resolution: "Keep our optimistic state for now. When our API response arrives, it will be the final arbiter.";
    };

    rule4: {
      name: "Optimistic update is pending, different fields changed";
      description: "If the server event changes different fields than our optimistic update, merge them. Example: we changed the title (optimistic), and someone else changed the status (server event). Apply the status change without reverting our title change.";
    };

    rule5: {
      name: "Stale event detection";
      description: "Compare event.timestamp with the entity's updatedAt in our cache. If the event is older than our cached version, discard it.";
    };
  };

  edgeCases: {
    "rapid successive updates": "Buffer events for 100ms and process only the latest per entity";
    "reconnection flood": "After reconnection, request full state refresh for subscribed channels instead of replaying missed events";
    "out of order events": "Always compare timestamps; never assume events arrive in order";
    "duplicate events": "Deduplicate by event ID (each event must have a unique ID)";
  };
}
```

---

## 4.7 Связь спецификаций API и спецификаций управления состоянием

Спецификации API (глава 3) и спецификации управления состоянием — два взгляда на один поток данных. Вот как они соединяются:

```
User Action
    |
    v
[State Management: Dispatch Action]
    |
    ├── Optimistic Update (immediate)
    |       |
    |       v
    |   [Store Updated] --> [UI Re-renders]
    |
    └── Side Effect: API Call
            |
            v
        [API Blueprint: Request]
            |
            v
        [Server Processes]
            |
            v
        [API Blueprint: Response]
            |
            ├── Success
            |       |
            |       v
            |   [State Management: Success Action]
            |       |
            |       v
            |   [Store Updated with Server Data] --> [UI Re-renders]
            |   [Cache Invalidation]
            |
            └── Error
                    |
                    v
                [State Management: Error Action]
                    |
                    v
                [Revert Optimistic Update] --> [UI Re-renders]
                [Show Error Toast]
```

### Трассировка потока: «Назначить задачу на меня»

Проследим полный поток через все наши спецификации:

```
1. USER clicks "Assign to me" button on TaskCard

2. COMPONENT CONTRACT (Chapter 2)
   - TaskCard.props.onAssign(taskId, currentUser.id)
   - Button shows loading state

3. STATE MANAGEMENT (this chapter)
   - Dispatch: { type: "tasks/update", payload: { taskId, changes: { assigneeId: currentUser.id } } }
   - Optimistic update: task.assigneeId = currentUser.id in store
   - UI immediately shows current user as assignee

4. API BLUEPRINT (Chapter 3)
   - PATCH /api/v1/tasks/{taskId}
   - Body: { "assigneeId": "current-user-uuid" }
   - Headers: Authorization: Bearer {token}

5a. SUCCESS PATH
   - API returns 200 with updated Task
   - Dispatch: { type: "tasks/updateSuccess", payload: { task: serverTask } }
   - Store updates with server response (authoritative)
   - Cache invalidation: tasks.detail(taskId), tasks.lists()
   - UI shows confirmed assignment

5b. ERROR PATH
   - API returns 422: "User is not a member of this project"
   - Dispatch: { type: "tasks/updateError", payload: { taskId, error: "..." } }
   - Store reverts to previous assigneeId
   - Toast: "Could not assign task: User is not a member of this project"
   - Button returns to original state

6. REAL-TIME (this chapter)
   - Server broadcasts: { type: "task.updated", payload: { task, changedFields: ["assigneeId"] } }
   - Other users viewing the same task see the assignment change
   - If actorId === currentUser.id, event is ignored (already handled optimistically)
```

Это одно действие пользователя. Когда вы трассируете его через все четыре слоя спецификаций (схема, компонент, API, состояние), вы точно видите, как данные текут от клика до финального состояния UI. Ни для человека-разработчика, ни для ИИ нет неоднозначности.

---

## 4.8 Спецификация хранилища Zustand: полный пример

Соберём всё вместе в конкретной спецификации хранилища Zustand, которую ИИ может реализовать напрямую.

```typescript
// ===================================================
// ZUSTAND STORE SPECIFICATION — TASK MANAGEMENT
// ===================================================

/**
 * STORE: useTaskStore
 *
 * This store manages client-side state for the task management views.
 * Server state (task entities) is managed by TanStack Query.
 * This store handles: UI state, filters, sort, optimistic updates,
 * and coordination between components.
 *
 * PERSISTENCE: None (ephemeral — resets on page reload)
 * DEVTOOLS: Enable Zustand devtools in development mode
 */

interface TaskStore {
  // === STATE ===

  /** Currently active project (derived from URL, set by router) */
  activeProjectId: string | null;

  /** Currently active task (for detail view) */
  activeTaskId: string | null;

  /** Current filter configuration */
  filters: TaskFilters;

  /** Current sort configuration */
  sort: {
    field: "created_at" | "updated_at" | "priority" | "due_date";
    order: "asc" | "desc";
  };

  /** Task IDs selected for bulk operations */
  selectedTaskIds: Set<string>;

  /** Whether bulk selection mode is active */
  isBulkSelectMode: boolean;

  /** Optimistic updates in flight */
  optimisticUpdates: Map<string, {
    previousData: unknown;
    action: string;
    timestamp: number;
  }>;

  // === ACTIONS ===

  /** Set the active project (called by router integration) */
  setActiveProject: (projectId: string | null) => void;

  /** Set the active task (for detail view) */
  setActiveTask: (taskId: string | null) => void;

  /** Update filters (merges with existing filters) */
  setFilters: (filters: Partial<TaskFilters>) => void;

  /** Clear all filters to defaults */
  clearFilters: () => void;

  /** Set sort configuration */
  setSort: (field: string, order: "asc" | "desc") => void;

  /** Toggle selection of a single task */
  toggleTaskSelection: (taskId: string) => void;

  /** Select all tasks in the current view */
  selectAllTasks: (taskIds: string[]) => void;

  /** Clear all selections */
  clearSelection: () => void;

  /** Toggle bulk select mode */
  toggleBulkSelectMode: () => void;

  /** Register an optimistic update */
  registerOptimistic: (entityId: string, previousData: unknown, action: string) => void;

  /** Clear an optimistic update (on success or after revert) */
  clearOptimistic: (entityId: string) => void;

  /** Check if an entity has a pending optimistic update */
  hasOptimisticUpdate: (entityId: string) => boolean;
}

/**
 * STORE: useUIStore
 *
 * This store manages global UI state that is shared across
 * multiple components and is not tied to a specific feature.
 *
 * PERSISTENCE: sidebar and theme are persisted to localStorage
 * DEVTOOLS: Enable Zustand devtools in development mode
 */

interface UIStore {
  // === STATE ===

  sidebar: {
    isOpen: boolean;
    width: number;  // 200-400px, default 260
  };

  modal: {
    type: ModalType | null;
    props: Record<string, unknown>;
  };

  commandPalette: {
    isOpen: boolean;
    query: string;
  };

  toasts: Toast[];

  theme: "light" | "dark" | "system";

  isOffline: boolean;

  // === ACTIONS ===

  /** Toggle sidebar open/closed */
  toggleSidebar: () => void;

  /** Set sidebar width (for drag-resize) */
  setSidebarWidth: (width: number) => void;

  /** Open a modal with props */
  openModal: (type: ModalType, props?: Record<string, unknown>) => void;

  /** Close the current modal */
  closeModal: () => void;

  /** Toggle command palette */
  toggleCommandPalette: () => void;

  /** Set command palette query */
  setCommandPaletteQuery: (query: string) => void;

  /** Show a toast notification */
  showToast: (toast: Omit<Toast, "id" | "createdAt">) => void;

  /** Dismiss a toast notification */
  dismissToast: (toastId: string) => void;

  /** Set theme preference */
  setTheme: (theme: "light" | "dark" | "system") => void;

  /** Set offline status (called by network listener) */
  setOffline: (isOffline: boolean) => void;
}

// === ACTION BEHAVIOR SPECIFICATIONS ===

const actionBehaviors = {
  "useUIStore.showToast": {
    behavior: [
      "Generate a unique ID (uuid or nanoid)",
      "Set createdAt to Date.now()",
      "Add toast to the beginning of the toasts array",
      "If toast.duration > 0, set a timeout to auto-dismiss",
      "Maximum 5 toasts visible at once — if adding a 6th, dismiss the oldest",
    ],
  },

  "useUIStore.openModal": {
    behavior: [
      "If a modal is already open, close it first (no stacking)",
      "Set modal.type and modal.props",
      "Add 'overflow: hidden' to document.body (prevent background scroll)",
      "Trap focus within the modal",
    ],
  },

  "useUIStore.closeModal": {
    behavior: [
      "Set modal.type to null and modal.props to {}",
      "Remove 'overflow: hidden' from document.body",
      "Return focus to the element that was focused before the modal opened",
    ],
  },

  "useTaskStore.setFilters": {
    behavior: [
      "Merge provided filters with existing filters (shallow merge)",
      "Reset selectedTaskIds (filter change invalidates selection)",
      "Serialize filters to URL query parameters",
      "Trigger TanStack Query refetch with new filters (via query key change)",
    ],
    note: "Do NOT debounce filter changes — let TanStack Query handle deduplication",
  },

  "useTaskStore.clearFilters": {
    behavior: [
      "Reset all filter fields to defaults",
      "Clear URL query parameters",
      "Reset selectedTaskIds",
    ],
    defaults: {
      status: null,
      priority: null,
      assigneeId: null,
      labelIds: null,
      search: "",
      dueBefore: null,
      dueAfter: null,
    },
  },
};
```

---

## 4.9 Упражнение: полная спецификация управления состоянием для приложения чата

Это итоговое упражнение модуля 2. Вы напишете полную спецификацию управления состоянием для приложения чата в реальном времени. Упражнение объединяет схемы, контракты компонентов, спецификации API и управление состоянием.

### Приложение

Вы строите приложение чата вроде Slack со следующими функциями:

1. Несколько каналов (публичные и приватные)
2. Личные сообщения между пользователями
3. Отправка сообщений с оптимистичными обновлениями
4. Редактирование и удаление сообщений
5. Индикаторы набора текста
6. Счётчики непрочитанных сообщений
7. Реакции на сообщения (эмодзи)
8. Вложения файлов
9. Присутствие пользователей (в сети, отошёл, не в сети)
10. Поиск сообщений

### Ваша задача

Напишите полную спецификацию управления состоянием, включая:

#### Часть 1: формы хранилищ

Определите формы хранилищ для:

- **MessagesStore** — нормализованные сообщения с индексами по каналам
- **ChannelsStore** — каналы со счётчиками непрочитанного
- **UsersStore** — пользователи с информацией о присутствии
- **UIStore** — состояние UI, специфичное для чата (активный канал, ввод сообщения, позиция прокрутки)

Для каждого хранилища задокументируйте:
- Каждое поле с типом
- Серверное это состояние или клиентское
- Как оно инициализируется
- Как оно сохраняется (если сохраняется)

#### Часть 2: действия

Определите все действия для системы чата:

- Отправка сообщения (с оптимистичным обновлением)
- Получение сообщения (через WebSocket)
- Редактирование сообщения
- Удаление сообщения
- Переключение каналов
- Отметка канала как прочитанного
- Добавление/удаление реакций
- Начало/остановка набора текста
- Загрузка файлового вложения

Для каждого действия задокументируйте:
- Тип действия и payload
- Изменения состояния (какие поля хранилища меняются и как)
- Побочные эффекты (вызовы API, сообщения WebSocket, уведомления)
- Обработку ошибок (что откатить, что показать)

#### Часть 3: селекторы

Определите селекторы для:

- Сообщений в активном канале (отсортированных по времени)
- Счётчика непрочитанного для каждого канала
- Общего счётчика непрочитанного по всем каналам
- Пользователей, печатающих в активном канале
- Пользователей в сети в активном канале
- Результатов поиска
- Деталей активного канала

Для каждого селектора задокументируйте:
- Входные зависимости (какие поля хранилища)
- Форму вывода
- Стратегию мемоизации
- Какие компоненты используют этот селектор

#### Часть 4: события реального времени

Определите контракты событий WebSocket для:

- `message.created` — новое сообщение в канале
- `message.updated` — сообщение отредактировано
- `message.deleted` — сообщение удалено
- `reaction.added` / `reaction.removed` — изменения реакций
- `typing.start` / `typing.stop` — индикаторы набора
- `presence.update` — изменения присутствия пользователя
- `channel.updated` — изменения метаданных канала

Для каждого события задокументируйте:
- Форму события (интерфейс TypeScript)
- Как оно обновляет локальное состояние
- Разрешение конфликтов с ожидающими оптимистичными обновлениями
- Вызывает ли оно уведомление

#### Часть 5: диаграмма потока данных

Проследите полный поток данных для «Пользователь отправляет сообщение»:

1. Пользователь печатает в поле ввода и нажимает Enter
2. Оптимистичное обновление добавляет сообщение в локальное состояние
3. Вызов API отправляет сообщение на сервер
4. Сервер транслирует сообщение через WebSocket
5. Другие клиенты получают и отображают сообщение
6. Исходный клиент получает эхо и согласует

Задокументируйте каждое изменение состояния, каждый побочный эффект и каждый крайний случай (сбой сети, дубликат сообщения, доставка не по порядку).

> **Заметка профессора:** Это упражнение намеренно требовательное. Полная спецификация управления состоянием для приложения чата — реальная задача, занимающая у опытного инженера несколько часов. Но когда вы передаёте эту спецификацию ИИ, ИИ выдаёт работающее приложение чата с правильным поведением в реальном времени, корректными оптимистичными обновлениями и надёжным разрешением конфликтов. Без спецификации ИИ выдаст нечто похожее на чат, но ломающееся в реальных условиях: сообщения появляются дважды, индикаторы набора застревают навсегда, счётчики непрочитанного неверны после переподключения. Спецификация — разница между демо и продуктом.

---

## 4.10 Ключевые выводы

1. **Спецификации управления состоянием** определяют, как данные текут через приложение: хранилища, действия, селекторы и побочные эффекты.

2. **Мышление в стиле Redux** — состояние + действие = новое состояние — правильная ментальная модель для спецификации изменений состояния, независимо от используемой библиотеки.

3. **Нормализуйте состояние.** Плоские индексированные коллекции предотвращают дублирование данных и упрощают обновления.

4. **Отделяйте серверное состояние от клиентского.** Серверное состояние принадлежит кешу запросов (TanStack Query). Клиентское — хранилищу (Zustand, Jotai и т.п.).

5. **Оптимистичные обновления требуют явных спецификаций.** Определите: что меняется сразу, что откатывать при ошибке и как согласовывать с ответами сервера.

6. **Селекторы — часть спецификации.** Определите, какие производные данные нужны каждому компоненту, как они вычисляются и как мемоизируются.

7. **События реального времени — контракты.** Определите каждый тип события, его payload, как он обновляет состояние и как разрешает конфликты с локальным состоянием.

8. **Спецификации API и спецификации управления состоянием — два взгляда на один поток данных.** Трассируйте действия пользователя через оба, чтобы обеспечить согласованность.

9. **Правила инвалидации кеша должны быть явными.** Когда мутация успешна, какие запросы нужно перезапросить? Это не деталь, которую можно оставить воображению ИИ.

10. **Спецификация предотвращает дрейф архитектуры состояния.** Без спецификации каждая ИИ-функция использует свой шаблон состояния. Со спецификацией каждая функция следует одной архитектуре.

---

## Заключение модуля 2

Вы завершили модуль 2: определение архитектуры. За четыре главы вы научились специфицировать четыре столпа архитектуры приложения:

| Глава | Столп | Что специфицирует |
|---------|--------|-------------------|
| 1. Проектирование от схем | Данные | Формы и ограничения данных |
| 2. Контракты компонентов | UI | Поведение UI-компонентов |
| 3. Чертежи API | Связи | Контракты запросов/ответов между системами |
| 4. Спецификации управления состоянием | Поток | Как данные движутся через приложение |

Вместе эти четыре спецификации дают ИИ (или человеческой команде) всё необходимое для построения полного, правильного, согласованного приложения. Схема определяет, какие данные существуют. Контракты компонентов определяют, как пользователи с ними взаимодействуют. Чертежи API определяют, как системы обмениваются ими. Спецификация управления состоянием определяет, как они текут.

В модуле 3 мы перейдём от архитектуры к процессу: как писать промпты реализации, использующие эти спецификации, как рецензировать ИИ-код на соответствие спецификациям и как итеративно достигать продакшн-качества.

---

*Конец главы 4 — Спецификации управления состоянием*

*Конец модуля 2 — Определение архитектуры («как»)*
