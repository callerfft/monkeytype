# Original User Request

## Initial Request — 2026-10-17T05:28:29Z

Contract-first workflow (contracts/api_v1.json), 2 parallel isolated workers (/backend and /frontend), followed by sequential integration and verification.

LinguaType — быстрый клавиатурный тренажер перевода и построения предложений на базе Monkeytype с потоковой оценкой через LLM задержкой менее 3 секунд.

Working directory: c:\Users\Yohanson\Documents\FastTextAnalyser\monkeytype
Integrity mode: development

## Architecture & Execution Plan
Сначала фиксируется контракт `contracts/api_v1.json`. Затем параллельно разрабатываются изолированные модули `/backend` (Python/FastAPI) и `/frontend` (Monkeytype / SolidJS). В завершение — последовательная сквозная интеграция, бенчмарк задержки и a11y-тестирование.

## Requirements

### R1. API Contract Definition (`contracts/api_v1.json`)
Создать формальный JSON Schema / OpenAPI контракт `contracts/api_v1.json` для взаимодействия фронтенда и бэкенда: схемы сессий (Mode A/B, таймеры 15/30/60s, лимиты слов), потоковой оценки (SSE/WebSocket), формата грамматических ошибок, семантической проверки и одного стилистического варианта.

### R2. Backend Service (`backend/` — Python / FastAPI)
Реализовать асинхронный сервис на FastAPI с поддержкой:
- Потокового эндпоинта оценки текста пользователя через быстрые LLM (Gemini Flash) со строгим JSON/структурированным выводом.
- Извлечения спанов грамматических ошибок, валидации смысла и генерации ровно одной альтернативы под выбранный стиль.
- Автоматического бенчмарка/теста задержки, подтверждающего TTFT и суммарное время инференса < 2.5s.

### R3. Frontend Integration (`frontend/` / Monkeytype Core)
Интегрировать режим LinguaType в клиент Monkeytype (SolidJS/TypeScript/Vite):
- Режим A (перевод фразы) и Режим B (описание ситуации/картинки).
- Настройки сессий: таймер, лимит слов, счетчик слов в реальном времени.
- Потоковый рендеринг результатов оценки с подсветкой ошибок и выводом рекомендованного варианта.
- Доступность (a11y): полное управление с клавиатуры (Tab+Enter рестарт, Esc сброс, фокус ввода), корректные ARIA-атрибуты.

### R4. Auth & Settings (Firebase Auth)
Интеграция Firebase Auth (Google OAuth и Magic Link / passwordless) для сохранения настроек пользователя (родной/целевой языки, предпочтительный стиль) и истории сессий.

### R5. Sequential Integration, E2E Verification & Deployment Readiness
- Сквозные тесты интеграции фронтенда с бэкендом.
- Проверка доступности (a11y) и контрастности интерфейса без перегруженных элементов и без стикеров.
- Подготовка конфигурации для Firebase App Hosting (`apphosting.yaml` / настройки развертывания).

## Acceptance Criteria

### API Contract & Structure
- [ ] Файл `contracts/api_v1.json` создан и валиден, покрывает все эндпоинты сессии и потоковой оценки.
- [ ] Исходный код изолирован по каталогам `backend/` и `frontend/`.

### Performance & Latency
- [ ] Тест производительности подтверждает суммарную задержку пайплайна оценки < 3.0 секунд.

### Gameplay & UI/A11y
- [ ] Рабочий игровой цикл: получение задания -> ввод текста с таймером -> отправка -> получение и отображение оценки.
- [ ] Полное управление сценарием без мыши (keyboard-first) и отсутствие критических проблем доступности по WCAG.
- [ ] Минималистичный интерфейс в стиле Monkeytype без избыточных декоративных элементов.

### Auth & Config
- [ ] Клиентский и серверный модули Firebase Auth поддерживают Google OAuth и Magic Link.
- [ ] Наличие конфигурации сборки и развертывания для Firebase App Hosting.

### Automated Verification
- [ ] Автоматические тесты бэкенда (`pytest`) проходят успешно.
- [ ] Линтеры и тесты фронтенда (`pnpm vitest run`, `oxlint`) выполняются без критических ошибок.
- [ ] Сквозной тест (E2E) проверяет отправку текста и корректный парсинг потокового ответа.
