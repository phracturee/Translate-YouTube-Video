import asyncio
import logging
import os
import re
import json
import shutil
import glob
from pathlib import Path
from typing import Tuple, Optional

# ==============================================================================
# Константы
# ==============================================================================
# Настройка логирования для вывода информационных сообщений
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Регулярное выражение для извлечения ID видео из URL YouTube
YOUTUBE_URL_REGEX = re.compile(r"(?:https?://)?(?:www.)?(?:youtube.com/watch?v=|youtube.com/embed/|youtu.be/)([\w-]{11})")

# Каталоги
BASE_DIR = Path(__file__).parent
TRANSLATED_VIDEOS_DIR = BASE_DIR / "translated_videos"


# ==============================================================================
# Основные функции
# ==============================================================================

async def run_command(command: str) -> Tuple[bool, str]:
    """
    Выполняет асинхронную команду в оболочке и возвращает ее результат.

    Args:
        command: Команда для выполнения.

    Returns:
        Кортеж, где первый элемент - булево значение успеха,
        а второй - стандартный вывод или ошибка.
    """
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_message = stderr.decode().strip()
        logging.error(f"Команда '{command}' не удалась.")
        logging.error(f"Ошибка: {error_message}")
        return False, error_message
    
    return True, stdout.decode().strip()


async def download_video(url: str, output_dir: Path) -> Optional[str]:
    """
    Загружает видео с YouTube с помощью yt-dlp.

    Args:
        url: URL видео на YouTube.
        output_dir: Каталог для сохранения видео.

    Returns:
        Название видео в случае успеха, иначе None.
    """
    try:
        logging.info("Получение информации о видео...")
        info_command = f'yt-dlp --print-json "{url}"'
        success, info_output = await run_command(info_command)
        if not success:
            logging.error(f"Не удалось получить информацию о видео: {info_output}")
            return None
        
        video_info = json.loads(info_output)
        video_title = video_info.get("title", "Untitled_Video")
        
        logging.info(f"Начинаю загрузку видео: '{video_title}'")
        video_path = output_dir / "original_video.mp4"
        download_command = (
            f'yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" ' 
            f'--merge-output-format mp4 -o "{video_path}" "{url}"'
        )
        
        success, dl_output = await run_command(download_command)
        if not success:
            logging.error(f"Ошибка при загрузке видео: {dl_output}")
            return None
        
        logging.info(f"Видео успешно загружено в: {video_path}")
        return video_title
    except json.JSONDecodeError:
        logging.error("Не удалось разобрать JSON с информацией о видео.")
        return None
    except Exception as e:
        logging.error(f"Непредвиденная ошибка при загрузке видео: {e}")
        return None


def cleanup_temp_files(temp_dir: Path, video_id: str):
    """
    Удаляет временные каталоги и файлы.

    Args:
        temp_dir: Временный каталог для удаления.
        video_id: ID видео для поиска и удаления остаточных файлов.
    """
    logging.info("Очистка временных файлов...")
    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            logging.info(f"Временный каталог '{temp_dir}' удален.")
        
        # vot-cli может оставлять файлы в корневом каталоге
        for leftover_file in glob.glob(str(BASE_DIR / f"*{video_id}*.webm")):
            os.remove(leftover_file)
            logging.info(f"Удален остаточный файл: {leftover_file}")

    except Exception as e:
        logging.error(f"Ошибка во время очистки: {e}")


async def process_youtube_link(url: str):
    """
    Полный цикл обработки видео: загрузка, перевод аудио, объединение.

    Args:
        url: URL видео на YouTube.
    """
    match = YOUTUBE_URL_REGEX.search(url)
    if not match:
        logging.error("Введена недействительная ссылка YouTube.")
        return

    video_id = match.group(1)
    temp_dir = BASE_DIR / f"temp_{video_id}"
    temp_dir.mkdir(exist_ok=True)

    try:
        # --- Шаг 1: Загрузка оригинального видео ---
        print("\n[1/3] 📥 Загрузка оригинального видео...")
        video_title = await download_video(url, temp_dir)
        if not video_title:
            logging.error("Не удалось загрузить видео. Проверьте ссылку и попробуйте снова.")
            return

        # --- Шаг 2: Получение переведенной аудиодорожки ---
        print("[2/3] 🎤 Получение перевода аудио...")
        original_video_path = temp_dir / "original_video.mp4"
        translated_audio_path = temp_dir / f"{video_id}.mp3"
        
        vot_command = f'vot-cli --output="{temp_dir}" --output-file="{video_id}.mp3" "{url}"'
        success, vot_output = await run_command(vot_command)
        if not success:
            logging.error(f"Не удалось получить перевод аудио: {vot_output}")
            return
        logging.info("Аудио с переводом успешно получено.")

        # --- Шаг 3: Объединение видео и аудио ---
        print("[3/3] 🎞️  Объединение видео и аудио...")
        
        # Создаем безопасное имя файла из заголовка видео
        safe_title = re.sub(r'[^\w\s-]', '', video_title).strip()
        safe_title = re.sub(r'\s+', '_', safe_title)
        final_video_filename = f"{safe_title}_{video_id}.mp4"
        final_video_path = TRANSLATED_VIDEOS_DIR / final_video_filename

        # Создаем команду FFmpeg
        ffmpeg_command = (
            f'ffmpeg -y -i "{original_video_path}" -i "{translated_audio_path}" ' 
            f'-filter_complex "[0:a]volume=0.2[a1];[a1][1:a]amix=inputs=2:duration=longest[a_out]" ' 
            f'-map 0:v -map "[a_out]" -c:v copy -c:a aac -b:a 192k "{final_video_path}"'
        )
        
        TRANSLATED_VIDEOS_DIR.mkdir(exist_ok=True)
        success, ffmpeg_output = await run_command(ffmpeg_command)
        if not success:
            logging.error(f"Ошибка при объединении файлов: {ffmpeg_output}")
            return
        
        print("\n✅ Видео успешно переведено!")
        print(f"💽 Файл сохранен по пути: {final_video_path.resolve()}")

    except Exception as e:
        logging.critical(f"Произошла непредвиденная ошибка в процессе обработки: {e}")
    finally:
        cleanup_temp_files(temp_dir, video_id)


async def main():
    """
    Основная функция для запуска скрипта.
    """
    try:
        url = input("Введите ссылку на YouTube видео: ")
        if url.strip():
            await process_youtube_link(url)
        else:
            print("Ссылка не была введена. Выход.")
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем. Выход.")


if __name__ == "__main__":
    asyncio.run(main())
