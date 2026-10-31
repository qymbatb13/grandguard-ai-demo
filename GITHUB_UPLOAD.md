# Публикация на GitHub (Mac / VS Code)

**Важное:** файлы организаторов (`data/`), обученная модель (`artifacts/`), пользовательские тикеты и результаты ручной разметки **не публикуются**. `.gitignore` это исключает. Не используйте `git add -f`.

1. Откройте распакованную папку `grandguard-ai` в VS Code.
2. Установите Git, войдите в свой GitHub-аккаунт; создайте **пустой** репозиторий на платформе хакатона (если организаторы выдали отдельный репозиторий, используйте именно его).
3. В терминале внутри папки проекта:

```bash
git init
git add .
git status --short
```

**ПРОВЕРЬТЕ** `git status --short`: нет `data/`, `tickets_train`, `tickets_valid`, `.tgz`, `weak_classifier.joblib`, `.venv`. Только затем:

```bash
git commit -m "GrandGuard AI final MVP"
git branch -M main
git remote add origin https://github.com/YOUR-ACCOUNT/YOUR-REPOSITORY.git
git push -u origin main
```

Замените URL своим URL репозитория. Если там уже есть коммиты, **не** перезаписывайте историю командой `--force`; сначала разберитесь с ветками.

Сдавайте ссылку на коммит, demo видео и результаты, измеренные локально. В README указывайте точные ограничения.
