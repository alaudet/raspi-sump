import time

def log_reading(water_depth):

    """Log time and water depth reading."""
    time_of_reading = time.strftime("%H:%M:%S,")
    filename = "/home/pi/raspi-sump/csv/waterlevel-{}.csv".format(
        time.strftime("%Y%m%d")
    )
    csv_file = open(filename, 'a')
    csv_file.write(time_of_reading),
    csv_file.write(str(water_depth)),
    csv_file.write("\n")
    csv_file.close()
