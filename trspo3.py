import concurrent.futures
import threading

# Глобальні змінні для атомарного збільшення
total_steps = 0
processed_count = 0
max_steps = 0
max_number = 0
lock = threading.Lock()


def calculate_collatz_steps(number):
    """
    Обчислює кількість кроків для досягнення 1 за гіпотезою Коллатца.

    :param number: Число, для якого обчислюється кількість кроків.
    :return: Кількість кроків для досягнення 1.
    """
    steps = 0
    while number != 1:
        number = number // 2 if number % 2 == 0 else 3 * number + 1
        steps += 1
    return steps


def process_number(number):
    """
    Обробляє одне число: обчислює кроки, оновлює глобальні змінні.

    :param number: Число для обробки.
    """
    global total_steps, processed_count, max_steps, max_number
    steps = calculate_collatz_steps(number)

    # Атомарно оновлюємо глобальні змінні
    with lock:
        total_steps += steps
        processed_count += 1
        if steps > max_steps:
            max_steps = steps
            max_number = number


def collatz_with_threadpool(numbers, num_threads):
    """
    Запускає обчислення для чисел з використанням ThreadPoolExecutor.

    :param numbers: Кількість чисел для обробки.
    :param num_threads: Кількість потоків для виконання паралельних завдань.
    :return: Середня кількість кроків, найбільша кількість кроків і число з найбільшими кроками.
    """
    global total_steps, processed_count, max_steps, max_number

    # Скидаємо глобальні змінні
    total_steps = 0
    processed_count = 0
    max_steps = 0
    max_number = 0

    if numbers <= 0 or num_threads <= 0:
        raise ValueError("Кількість чисел і кількість потоків мають бути додатними числами.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Додаємо завдання в пул потоків
        executor.map(process_number, range(1, numbers + 1))

    # Розрахунок середньої кількості кроків
    average_steps = total_steps / processed_count if processed_count > 0 else 0
    return average_steps, max_steps, max_number


if __name__ == "__main__":
    # Налаштування
    NUMBERS = 100000  # Кількість чисел для обчислення
    THREAD_COUNTS = [1, 2, 4, 8, 16]  # Кількість потоків для тестування

    for thread_count in THREAD_COUNTS:
        print(f"\nЗапуск з {thread_count} потоками...")
        try:
            average_steps, max_steps, max_number = collatz_with_threadpool(NUMBERS, thread_count)
            print(f"Середня кількість кроків: {average_steps:.2f}")
            print(f"Найбільше число: {max_number} з {max_steps} кроками")
        except ValueError as e:
            print(f"Помилка: {e}")
