import gasprices
import time
from datetime import datetime
from sched import scheduler

def exit_schedule():
    answer = input("Type (y)es/(n)o: ")
    if answer[0] in ['y', 'Y']:
        return True
    elif answer[0] in ['n', 'N']:
        return False
    else:
        print("invalid response. Try again")
        return exit_schedule()

def continuous_gas_prices(driver, interval=1800, location="me", num_stations=40):
    schedule = scheduler(time.time, time.sleep)
    my_kwargs = {
        "location": location,
        "num_stations": num_stations
    }

    gasprices.get_current_prices(driver)
    print("Hit CTRL+C to exit this program")
    while True:
        try:
            args = (driver,)
            schedule.enter(interval, 1, gasprices.get_current_prices,argument=args, kwargs=my_kwargs)
            schedule.run()
        except KeyboardInterrupt:
            print("Are you sure you want to exit this program?")
            if exit_schedule():
                break
            else:
                continue

def main():
    driver = gasprices.createDriver()
    continuous_gas_prices(driver)

main()