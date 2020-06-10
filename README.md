# rsyncBackup For NAS

rsycBackup is a script for helping create a redundant copy of your data from one SOURCE NAS to a DESTINATION NAS, as an automated script run from the DESTINATION system, not altering any of the data from the SOURCE.

This differs from current solutions, as this process is run completely from the DESTINATION unit, allowing the user to automate power-on, backup process, and shutdown of the NAS unit.

## Getting Started

There are a few prerequisites and safety precautions to consider before running the script.
By default, the script is set to TEST, which will help you with the setup and testing before implementation.

### Prerequisites

Some things you should have in place before you get started:
* basic working knowledge of linux
* knowledge of ssh and key-pair authentication
* knowledge of scp, tar, vi/vim
* Python 2.7 installed on the NAS running the script
* Pyyaml (version 3.11)


You will need SSH enabled on both NAS units, with [key-based authentication](https://stamler.ca/enable-passwordless-ssh-on-synology-dsm6/) set up for the user specified in the settings.yaml file.

* It's recommended to add a custom ssh port number for security if your NAS unit is open to the internet.

* If you're having issues with key-based authentication, Copy the sshd_config into the homes/[USER]/.ssh directory


### Installing

Once key-based ssh is working, script installation is simple.
There are 4 files included:
* sources.conf        A line-by-line text file of backup paths
* exclusions.conf     A line-by-line text file of path and expression based exclusions
* settings.yaml       A YAML file of values to control the syncing operation. MUST BE IN THE SAME DIRECTORY AS THE MAIN PYTHON SCRIPT
* rsyncBackup.py      The python script that will execute the backup

1) Copy the files into a subdirectory that will be excluded from the process in step 4:
```
/volume1/homes/rsync/rsyncBackup
```

2) Edit the settings.yaml file to conform to your file system and setup. Each variable has a descriptive comment explaining it's function.

3) Add the source directories you wish to copy into the sources.conf file, excluding the /volume#/ root specified in the settings.yaml:
```
Public/
Private/
TimeMachine/
```

4) Verify the exclusions set in the exclusions.conf file, using:
* literal string, wildcard, or character range
* lines beginning with / will be explicit exclusions, and are listed relative to the source directory.
```
#If the source directory is Public/
/Public/Documents           <- BAD!!!
/volume1/Public/Documents   <- BAD!!!
/Documents                  <- GOOD
```
* Trailing slash is a directory (not a file).  No trailing slash can be a directory or a file.
```
lost+found
.ssh*
*recycle
/path/to/exclusion
```



## Deployment

This can be run as a manual process from the terminal with admin privilages, or launched as an automated task from a task scheduler.
Keeping an offline backup is easy to automate:

1) The SOURCE system runs a scheduled task to wake the DESTINATION system.
Ensure that your WOL ports are accessible for this to work.
```
#!/usr/bin/env bash
# On a Synology NAS unit - Wake On LAN commands will vary between systems.
synonet --wake [MAC ADDRESS] eth0;
```
2) The DESTINATION system begins running the on-boot scheduled rsyncBackup.py process
3) The DESTINATION system settings.yaml is set to shutdown after completion
4) Logs are compressed and archived for reference

## Built With

* [python](https://www.python.org) - if you don't know, now you know.
* [pyYaml](https://pyyaml.org) - PyYAML is a YAML parser and emitter for Python (3.11).
* [rsync](https://linux.die.net/man/1/rsync) - a fast, versatile, remote (and local) file-copying tool
* [ssh](https://www.openssh.com/) - OpenSSH SSH client (remote login program)
* tar - GNU 'tar' saves many files together into a single tape or disk archive, and can restore individual files from the archive.

## Contributing

Please contact me with any pull requests!

## Authors
[Pixelpicnic](https://github.com/pixelpicnic)

## License

This project is licensed under the GNU GPLv3 License - see the [GNU GPLv3 License](https://gist.github.com/pixelpicnic/c70188fd562126a03d240a5120733f8a) for details

## Acknowledgments

https://primalcortex.wordpress.com/2016/01/25/synology-installing-python-pip-package-installer/

https://stamler.ca/enable-passwordless-ssh-on-synology-dsm6/

https://sites.google.com/site/rsync2u/home/rsync-tutorial/the-exclude-from-option

https://www.endpoint.com/blog/2015/01/28/getting-realtime-output-using-python

[Purplebooth README.md template](https://github.com/PurpleBooth)
