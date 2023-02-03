from dataclasses import dataclass, asdict
from typing import Dict, Type


@dataclass
class InfoMessage:
    """
    Информационное сообщение о тренировке.

    Дополнительные входные переменные:
    training_type: Название тренировки;
    duration: Длительность (в часах);
    distance: Дистанция в (в км);
    speed: Скорость (в км/ч);
    calories: Килокалории.
    """

    training_type: str
    duration: float
    distance: float
    speed: float
    calories: float
    message: str = ('Тип тренировки: {training_type}; '
                    'Длительность: {duration:.3f} ч.; '
                    'Дистанция: {distance:.3f} км; '
                    'Ср. скорость: {speed:.3f} км/ч; '
                    'Потрачено ккал: {calories:.3f}.')

    def get_message(self) -> str:
        """Метод возвращает строку сообщения"""
        return self.message.format(**asdict(self))


class Training:
    """Базовый класс тренировки.

    Дополнительные входные переменные:
    LEN_STEP: Длина шага,
    M_IN_KM: Километры,
    MIN_IN_HOUR: Часы,
    action: количество совершённых действий (число шагов при ходьбе
    и беге либо гркбков - при плавании);
    duration: длительность тренировки в часах;
    weight: вес спортсмена.
    """

    LEN_STEP: float = 0.65
    M_IN_KM: int = 1000
    MIN_IN_HOUR: int = 60

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float
                 ) -> None:
        self.action = action
        self.duration = duration
        self.weight = weight

    def get_distance(self) -> float:
        """Получить дистанцию в км."""
        return self.action * self.LEN_STEP / self.M_IN_KM

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения."""
        mean_speed = self.get_distance() / self.duration
        return mean_speed

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        raise NotImplementedError("Требуется определить get_spent_calories()")

    def show_training_info(self) -> InfoMessage:
        """Вернуть информационное сообщение о выполненной тренировке."""
        return InfoMessage(self.__class__.__name__,
                           self.duration,
                           self.get_distance(),
                           self.get_mean_speed(),
                           self.get_spent_calories())


class Running(Training):
    """Тренировка: бег.

    Дополнительные входные переменные:
    calories_m: первый коэффицент:
    calories_s: второй коэффицент.
    """

    calories_m = 18
    calories_s = 1.79

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        return ((self.calories_m * self.get_mean_speed()
                + self.calories_s) * self.weight / self.M_IN_KM
                * self.duration * self.MIN_IN_HOUR)


@dataclass
class SportsWalking(Training):
    """Тренировка: спортивная ходьба.

    Дополнительные входные переменные:
    CALORIES_WEIGHT_MULTIPLIER: первый коэффицент;
    CALORIES_SPEED_HEIGHT_MULTIPLIER: второй коэффицент;
    KMH_IN_MSEC: перевод скорости в метрах в секунду;
    CM_IN_M: 100 см. в 1 м.
    """

    CALORIES_WEIGHT_MULTIPLIER = 0.035
    CALORIES_SPEED_HEIGHT_MULTIPLIER = 0.029
    KMH_IN_MSEC = 0.278
    CM_IN_M = 100

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 height: int) -> None:
        super().__init__(action, duration, weight)
        self.height = height

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        return ((self.CALORIES_WEIGHT_MULTIPLIER * self.weight
                + (self.get_mean_speed() * self.KMH_IN_MSEC)**2 / (self.height
                 / self.CM_IN_M) * self.CALORIES_SPEED_HEIGHT_MULTIPLIER
                 * self.weight) * (self.duration * self.MIN_IN_HOUR))


@dataclass
class Swimming(Training):
    """Тренировка: плавание.

    Дополнительные входные переменные:
    lenght_pool - длина бассейна в метрах;
    count_pool - сколько раз пользователь переплыл бассейн;
    LEN_STEP: переопределение расстояния, пройденного за один гребок.
    """

    CALORIES_SWIMMING_1 = 1.1
    CALORIES_SWIMMING_2 = 2
    LEN_STEP: float = 1.38

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 length_pool: float,
                 count_pool: int) -> None:
        super().__init__(action, duration, weight)
        self.length_pool = length_pool
        self.count_pool = count_pool

    def get_distance(self) -> float:
        """ Расчитать расстояние в бассейне."""
        return self.action * self.LEN_STEP / self.M_IN_KM

    def get_mean_speed(self) -> float:
        """ Расчитать среднюю скорость в бассейне."""
        return ((self.length_pool * self.count_pool)
                / self.M_IN_KM / self.duration)

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        return ((self.get_mean_speed() + self.CALORIES_SWIMMING_1)
                * self.CALORIES_SWIMMING_2 * self.weight * self.duration)


def read_package(workout_type: str, data: list) -> Training:
    """Прочитать данные полученные от датчиков."""

    training_type: Dict[str, Type[Training]] = {
        'SWM': Swimming,
        'RUN': Running,
        'WLK': SportsWalking}
    if workout_type in training_type:
        return training_type[workout_type](*data)
    raise ValueError(f"Такой тренировки - {workout_type}, не найдено")


def main(training: Training) -> None:
    """Главная функция."""

    info: InfoMessage = training.show_training_info().get_message()
    print(info)


if __name__ == '__main__':
    packages = [
        ('SWM', [720, 1, 80, 25, 40]),
        ('RUN', [15000, 1, 75]),
        ('WLK', [9000, 1, 75, 180]),
    ]

    for workout_type, data in packages:
        training = read_package(workout_type, data)
        main(training)
