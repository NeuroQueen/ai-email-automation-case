# Как выложить проект на GitHub

## 1. Настройте Git (один раз)

```powershell
git config --global user.email "ваш@email.com"
git config --global user.name "Ваше Имя"
```

## 2. Создайте репозиторий на GitHub

1. Откройте https://github.com/new
2. **Repository name:** `ref-2024-auto` (или любое)
3. **Description:** Генерация персонализированных писем (Campaign REF-2024-AUTO)
4. Выберите:
   - **Private** — доступ только у тех, кого вы добавите (Invite collaborators)
   - **Public** — любой с ссылкой сможет просматривать
5. **НЕ** ставьте галочки "Add README" и "Add .gitignore" — файлы уже есть
6. Нажмите **Create repository**

## 3. Подключите и отправьте код

Скопируйте команды с страницы созданного репозитория (раздел "…or push an existing repository") или выполните:

```powershell
cd "c:\тест задание"

# Добавить remote (замените YOUR_USERNAME и YOUR_REPO на свои)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Отправить
git branch -M main
git push -u origin main
```

## Доступ «по ссылке»

- **Private:** дайте ссылку `https://github.com/YOUR_USERNAME/YOUR_REPO` и нажмите **Settings → Collaborators → Add people** — добавьте по email тех, кому нужен доступ.
- **Public:** ссылка доступна всем, кто её знает; репозиторий может быть найден в поиске.
