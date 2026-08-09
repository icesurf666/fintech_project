import sys
from collections.abc import Callable

from demos.day1 import run_demo as run_day1
from demos.day2 import run_demo as run_day2
from demos.day3 import run_demo as run_day3
from demos.day4 import run_demo as run_day4
from demos.day5 import run_demo as run_day5
from demos.day6 import run_demo as run_day6

DEMOS: dict[str, Callable[[], None]] = {
    "1": run_day1,
    "2": run_day2,
    "3": run_day3,
    "4": run_day4,
    "5": run_day5,
    "6": run_day6,
}


def main() -> None:
    if len(sys.argv) == 2:
        day = sys.argv[1]

        if day not in DEMOS:
            available_days = ", ".join(DEMOS)
            print(f"Unknown day: {day}. Available days: {available_days}")
            return

        DEMOS[day]()
        return

    for day, run_demo in DEMOS.items():
        print(f"\n=== DAY {day} ===")
        run_demo()


if __name__ == "__main__":
    main()
