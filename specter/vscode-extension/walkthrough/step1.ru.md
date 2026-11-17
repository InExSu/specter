# Генерация черновиков спецификаций

Specter CLI скачивается автоматически при активации этого расширения — устанавливать вручную не нужно.

## Направьте Specter на свой исходный код

Откройте встроенный терминал (**Ctrl+`**) и выполните:

```bash
specter reverse src/        # TypeScript / JavaScript
specter reverse app/        # Python / Django / FastAPI
specter reverse ./          # Go
```

Будет создан каталог `specs/` с одним файлом `.spec.yaml` на модуль. У некоторых AC в каждой спецификации будет `gap: true` — это значит, что Specter извлёк структуру, но для её завершения нужен ваш замысел.

## Инициализируйте манифест рабочего пространства

```bash
specter init
```

Создаёт `specter.yaml` — он необходим для полной активации расширения. Как только файл появится, в панели активности появится значок **Sp**, а панель Coverage покажет ваши спецификации.

> **Уже есть спецификации в другом формате?** См. [руководство по миграции](https://github.com/Hanalyx/specter/blob/main/specter/docs/GETTING_STARTED.ru.md#what-specter-is-not) о преобразовании спецификаций Gherkin, OpenAPI или простого текста в схему Specter.

> **Автозагрузка отключена?** Если ваша среда блокирует загрузки (корпоративный прокси, изолированная сеть), установите `specter.autoDownload` в `false` и настройте `specter.binaryPath` на вручную установленный бинарник. Бинарники скачивайте из [GitHub Releases](https://github.com/Hanalyx/specter/releases).
