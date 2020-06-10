#! /usr/bin/env python2

import errno
import os
import shlex
import yaml
import subprocess as sp
from datetime import datetime as dt


def importSettings():
    """
    Import settings from the settings.yaml file
    and return a dict of values.
    """
    working_directory = os.path.dirname(os.path.realpath(__file__))
    with open('{0}/settings.yaml'.format(working_directory)) as data_file:
        settings = yaml.load(data_file, Loader=yaml.Loader)
    settings['working_directory'] = working_directory
    return settings


def getTime():
    """
    Get the current time
    """
    now = dt.now().strftime
    time = now('%H:%M:%S')
    return time


def getDate():
    """
    Get the current date
    """
    now = dt.now().strftime
    date = now('%y/%m/%d')
    return date


def writeLog(log_file, data):
    """
    Open the specified log file, get the current time,
    print it to the screen and append it to the log.
    """
    with open(log_file, 'a') as out_file:
        time = getTime()
        data_line = '{0} ->  {1}\n'.format(time, data)
        print(data_line)
        out_file.write(data_line)


def logDirCheck(log_dir):
    """
    Check if the logdir exists.
    If not, create it!
    """
    print('Checking Log Directory')
    if not os.path.exists(log_dir):
        print("Log directory doesn't exist!")
        print('Attempting to create it.')
        try:
            os.mkdir(log_dir)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
            pass
    else:
        print('Log directory exists. Continuing.')


def initLog(log_file, start_time, date):
    """
    Open the specified log file, get the current time/date,
    print it to the screen and append it to the log file with a
    --- START LOG --- opening tag.
    """
    with open(log_file, 'w') as out_file:
        date_time = '{0}  {1}'.format(date, start_time)
        print(date_time)
        print('Starting Log: {0}'.format(log_file))
        start_log = '\n\n{0}\n--- START LOG ---\n\n'.format(date_time)
        out_file.write(start_log)


def createLog(source, log_dir):
    """
    Construct directory and file names,
    Check if directory exists and return the log file path
    """
    # Get the starting time and date
    start_time = getTime()
    date = getDate()
    # Format the log name and create the file structure if needed
    source_directory = source.split('/')[-2]
    log_name = '{0}_{1}_{2}.log'.format(date.replace('/', '_'),
                                        start_time.replace(':', '.'),
                                        source_directory)
    log = "{0}/{1}".format(log_dir, log_name)
    logDirCheck(log_dir)
    initLog(log, start_time, date)
    return log


def closeLog(log_file, end_time):
    """
    Open the specified log file, get the current time
    print it to the screen and append it to the log with a
    --- END OF LOG --- tag. Close the file.
    """
    with open(log_file, 'a') as out_file:
        print('End Log: {0}'.format(log_file))
        endLog = '\n\n{0}\n--- END OF LOG ---\n'.format(end_time)
        out_file.write(endLog)


def compressLog(log_file):
    """
    Compress the log file to save space!
    """
    file_base = os.path.splitext(log_file)[0]
    compressed_log = '{0}.tar'.format(file_base)
    tar_command = ['tar', '-zcvf', compressed_log,
                   '--remove-file', log_file]
    process = sp.Popen(tar_command, stdout=sp.PIPE)
    process.communicate()


def shutdown(settings):
    """
    Shutdown the NAS unit if the 'shutdown' flag is present.
    """
    if settings['shutdown']:
        print('Backup Process Complete.\nShutting Down...')
        if not settings['test']:
            process = sp.Popen([settings['shutdown_command']])
            process.communicate()


def run():
    """
    Run the program!
    """
    # Import the settings from the yaml file
    settings = importSettings()

    # Set the flags for the rsync process
    test = settings['test']
    flags = '-htrlPcvv'
    if test:
        flags += 'n'

    # Gather the ssh connection settings
    server_user = settings['server_user']
    server = settings['server']
    port = settings['port']

    # Import the paths necessary for including and excluding during the process
    sources = '{0}/{1}'.format(settings['working_directory'],
                               settings['sources'])
    exclusions = '{0}/{1}'.format(settings['working_directory'],
                                  settings['exclusions'])
    source_root = settings['source_root']
    target_root = settings['target_root']

    # Import the log directory and max size before compression
    log_dir = '{0}/{1}'.format(settings['working_directory'],
                               settings['log_dir'])

    # Setting up the rsync options
    exclude = '--exclude-from={0}'.format(exclusions)
    options = '--super --delete-during -e'
    ssh_command = "\'ssh -p {0}\'".format(port)
    command = 'rsync'

    # Iterate over the sources specified in the sources.conf file
    with open(sources) as source_file:
        for source in source_file:
            # Create a source log
            print('Processing: {0}'.format(source))
            log = createLog(source, log_dir)

            # Create the source and target paths
            target_path = "{0}{1}".format(source_root, source.rstrip())
            source_path = "{0}@{1}:{2}{3}".format(server_user, server,
                                                  target_root.rstrip(),
                                                  source.rstrip())

            # Print to the shell and log the sources
            writeLog(log, 'source: {0}'.format(source.strip()))
            writeLog(log, 'source path: {0}'.format(source_path))
            writeLog(log, 'target path: {0}'.format(target_path))
            writeLog(log, '-'*80)

            # Compile rsync Command
            rsyncCommand = '{0} {1} {2} {3} {4} {5} {6}'.format(command,
                                                                flags,
                                                                exclude,
                                                                options,
                                                                ssh_command,
                                                                source_path,
                                                                target_path)
            writeLog(log, '\nrsyncCommand: {0}\n'.format(rsyncCommand))

            # Run the rsync command and log the output to a file
            process = sp.Popen(shlex.split(rsyncCommand), stdout=sp.PIPE)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    if 'uptodate' not in output.strip():
                        if 'because of pattern' not in output.strip():
                            writeLog(log, output.strip())
            writeLog(log, '\n\n')

            # Get the end time and close the log, compressing if necessary
            end_time = getTime()
            closeLog(log, end_time)
            log_size = os.path.getsize(log) >> 20
            print('log size: {0}MB'.format(log_size))
            compressLog(log)

    #  Shutdown the NAS unit after iterating through the sources.
    shutdown(settings)


if __name__ == "__main__":
    run()

# EOF
