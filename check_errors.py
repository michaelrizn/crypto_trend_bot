import subprocess
import os


def run_flake8_and_save_output():
    # Определяем путь к файлу для сохранения результатов
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    output_file = os.path.join(log_dir, 'check_errors.txt')

    try:
        # Запускаем flake8 с фильтром по критичным ошибкам
        result = subprocess.run(['flake8', '--select=E,F'], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)

        # Отфильтровываем все сообщения, начинающиеся на E
        filtered_output = "\n".join(
            line for line in result.stdout.splitlines() if not line.startswith('E')
        )

        # Записываем результат в файл только если есть другие критичные ошибки
        if filtered_output.strip():
            with open(output_file, 'w') as file:
                file.write(filtered_output)
            print(f"Результаты анализа сохранены в {output_file}")
        else:
            print("Критичных ошибок, начинающихся с 'E', не обнаружено.")

    except subprocess.CalledProcessError as e:
        print(f"Возникла ошибка при выполнении flake8: {e}")
    except Exception as e:
        print(f"Возникла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    print("Запуск flake8 для анализа кода и сохранения результатов...")
    run_flake8_and_save_output()