#!/usr/bin/python
import raspisump.checkpid as checkpid

def main():
    process = 'rsump.py'
    checkpid.check_pid(process)

if __name__ == "__main__":
    main()
