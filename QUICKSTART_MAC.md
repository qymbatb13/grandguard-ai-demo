# GrandGuard AI — запуск в VS Code на Mac

1. Распакуйте ZIP и откройте папку `grandguard-ai` в VS Code.
2. Поместите ваш исходный архив `grand-support-copilot-handout-2026-10-27.tgz` в Downloads (не надо распаковывать вручную).
3. В терминале VS Code:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/setup_data.py --archive "$HOME/Downloads/grand-support-copilot-handout-2026-10-27.tgz"
GG_DATA_DIR=data python -m uvicorn app.main:app --reload
```

Откройте http://127.0.0.1:8000/docs

4. Во **втором** терминале VS Code:

```bash
source .venv/bin/activate
GG_DATA_DIR=data python -m streamlit run ui/dashboard.py
```

Откройте http://localhost:8501

5. Для проверки 1 000 обращений, в третьем терминале:

```bash
source .venv/bin/activate
make predict DATA_DIR=data IN=data/tickets_valid.jsonl OUT=artifacts/pred.jsonl
make evaluate DATA_DIR=data IN=data/tickets_valid.jsonl
python -m pytest -q
```

Если архив лежит не в Downloads, укажите его действительный путь после `--archive`.

**Важно:** папка `data/` не должна попадать в публичный GitHub. Этот MVP не отправляет ответы игрокам и не выдает наказания автоматически. Классификация эвристическая, опциональное ML-обучение использует слабую разметку; реальные gold accuracy/F1 отсутствуют.

## Обновление уже работающей версии (порты 8001 / 8502)

В обоих старых терминалах остановите серверы комбинацией **Control + C**.
Откройте **новую** распакованную папку `grandguard-ai` в VS Code и повторите команды установки.
Данные организаторов в новый проект подключаются отдельным запуском `setup_data.py`.

Первый терминал:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/setup_data.py --archive "$HOME/Downloads/grand-support-copilot-handout-2026-10-27.tgz"
GG_DATA_DIR=data python -m uvicorn app.main:app --reload --port 8001
```

Второй терминал:

```bash
source .venv/bin/activate
GG_DATA_DIR=data python -m streamlit run ui/dashboard.py --server.port 8502
```

Интерфейс: http://localhost:8502 · API: http://127.0.0.1:8001/docs

Третий терминал (необязательно):

```bash
source .venv/bin/activate
python -m pytest -q
python scripts/evaluate.py --input data/tickets_valid.jsonl --data-dir data
```


### V3 train model after setting up data

```bash
python scripts/train.py --input data/tickets_train.jsonl.gz --data-dir data --max-rows 30000
python -m pytest -q
```

Restart both servers (Ctrl+C then rerun launch commands) to load the trained model. Training may use substantial CPU and take several minutes, depending on your Mac.
