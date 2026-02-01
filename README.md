# Перевод видео с YouTube

Этот скрипт автоматизирует процесс перевода видео с YouTube. Он загружает оригинальное видео, получает аудиодорожку с переводом и объединяет их в один файл, понижая громкость оригинального звука.

## Возможности

-   Загрузка видео с YouTube в лучшем качестве.
-   Получение переведенной аудиодорожки с помощью [vot-cli-live](https://github.com/FOSWLY/vot-cli-live).
-   Объединение оригинального видео и переведенного аудио с помощью FFmpeg.
-   Автоматическая очистка временных файлов.

## Требования

### Зависимости Python

-   `yt-dlp`: для загрузки видео с YouTube.

Устанавливаются автоматически при выполнении команды:
```bash
pip install -r requirements.txt
```

### Внешние зависимости

Для работы скрипта требуются следующие утилиты:

1.  **Node.js** и **npm**: для установки и работы `vot-cli-live`.
2.  **vot-cli-live**: для получения переведенной аудиодорожки.
3.  **FFmpeg**: для обработки видео и аудио.

#### Инструкции по установке

<details>
<summary><b>Ubuntu / Debian</b></summary>

```bash
# Установка Node.js и npm
sudo apt update
sudo apt install -y nodejs npm

# Установка vot-cli-live
sudo npm install -g vot-cli-live --unsafe-perm

# Установка FFmpeg
sudo apt install -y ffmpeg
```
</details>

<details>
<summary><b>Arch Linux</b></summary>

```bash
# Установка Node.js и npm
sudo pacman -Syu nodejs npm

# Установка vot-cli-live
sudo npm install -g vot-cli-live --unsafe-perm

# Установка FFmpeg
sudo pacman -Syu ffmpeg
```
</details>

<details>
<summary><b>Fedora</b></summary>

```bash
# Установка Node.js и npm
sudo dnf install -y nodejs npm

# Установка vot-cli-live
sudo npm install -g vot-cli-live --unsafe-perm

# Установка FFmpeg (требуется репозиторий RPM Fusion)
sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install -y ffmpeg
```
</details>

## Установка

1.  Клонируйте репозиторий:
    ```bash
    git clone <URL-репозитория>
    cd <имя-папки>
    ```

2.  Создайте и активируйте виртуальное окружение:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  Установите зависимости Python:
    ```bash
    pip install -r requirements.txt
    ```

4.  Установите внешние зависимости, следуя инструкциям для вашего дистрибутива.

## Использование

Активируйте виртуальное окружение:
```bash
source venv/bin/activate
```
Запустите скрипт из корневого каталога проекта:
```bash
python main.py
```

Скрипт запросит у вас ссылку на видео с YouTube. После завершения работы переведенное видео будет сохранено в папке `translated_videos`.
