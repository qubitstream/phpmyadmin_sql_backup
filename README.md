phpmyadmin_sql_backup.py
==============================

What is it?
-----------

A Python 3 script to automate the download of SQL backups via a [phpMyAdmin](https://www.phpmyadmin.net/) web interface.

This is useful when your web hosting provider does not grant you access the the console but you want to automate the backup of your database (without having to manually use the browser). 

It has been tested with Python 3.5 and phpMyAdmin 4.3.6 + 4.5.4.1 + 4.7.0-dev

_Note_: The web interface of phpMyAdmin may change in the future and break this script. Please file a bug report (including your version of phpMyAdmin) if you encounter this issue.

### Usage

    usage: phpmyadmin_sql_backup.py [-h] [-o OUTPUT_DIRECTORY] [-p]
                                    [-e EXCLUDE_DBS]
                                    [--compression {none,zip,gzip}]
                                    [--basename BASENAME] [--timeout TIMEOUT]
                                    [--overwrite-existing] [--dry-run]
                                    url user password

    Automates the download of SQL dump backups via a phpMyAdmin web interface.

    positional arguments:
      url                   phpMyAdmin login page url
      user                  phpMyAdmin login user
      password              phpMyAdmin login password

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                            output directory for the SQL dump file
      -p, --prepend-date    prepend the current UTC date + time to the filename:
                            "YYYY-MM-DD--HH-MM-SS-UTC_"
      -e EXCLUDE_DBS, --exclude-dbs EXCLUDE_DBS
                            comma separated list for database names to exclude
                            from the dump
      --compression {none,zip,gzip}
                            compression method of the output file (default: none)
      --basename BASENAME   the desired basename (without extension) of the SQL
                            dump file (default: the name given by phpMyAdmin
      --timeout TIMEOUT     timeout in seconds for the requests (default: 60)
      --overwrite-existing  overwrite existing backup files (instead of appending
                            a number to the name)
      --dry-run             dry run, do not actually download the dump

    Written by Christoph Haunschmidt. Version: 2016-03-10.0

#### Examples

`phpmyadmin_sql_backup.py "http://www.example.com/phpmyadmin/" your_user your_password`

Downloads a plain text `.sql` backup of all tables to the current working directory.

---

`phpmyadmin_sql_backup.py "http://www.example.com/phpmyadmin/" your_user your_password --exclude mydb2,mydb4 -p --basename example_dump -o /tmp --compression zip`

Downloads a zipped dump with databases `mydb2` & `mydb4` excluded, the base name `example_dump` and a prepended UTC date / time to the directory `/tmp`, e.g. `/tmp/2016-03-11--15-19-04-UTC_example_dump.zip`.

Requirements
------------

 - [Grab - python web-scraping framework](http://grablib.org/) - install via ``pip install -U grab``

Changelog
---------

Currently, there is no changelog; the best option at the moment is to read the commit messages.

License
-------

GNU GPL

Acknowledgements
----------------

### Authors

- Christoph Haunschmidt
