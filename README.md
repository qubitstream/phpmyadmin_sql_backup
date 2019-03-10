# phpmyadmin_sql_backup.py


## What is it?

A Python 3 script to __automate the download of SQL backups via a [phpMyAdmin](https://www.phpmyadmin.net/) web interface__.

This is useful when your web hosting provider does not grant you access the the console (for `mysqldump`) but you want to automate the backup of your database (without having to manually use the browser).

It has been tested with Python 3.4+ on Linux and Windows and phpMyAdmin 4.3.6, 4.5.4.1 and 4.7.0-dev

_Note_: The web interface of phpMyAdmin may change in the future and break this script. Please file a bug report (including your version of phpMyAdmin) if you encounter this issue.

## Usage

    usage: phpmyadmin_sql_backup.py [-h] [-o OUTPUT_DIRECTORY] [-p]
                                    [-e EXCLUDE_DBS]
                                    [--compression {none,zip,gzip}]
                                    [--basename BASENAME] [--timeout TIMEOUT]
                                    [--overwrite-existing]
                                    [--prefix-format PREFIX_FORMAT] [--dry-run]
                                    URL USERNAME PASSWORD

    Automates the download of SQL dump backups via a phpMyAdmin web interface.

    positional arguments:
      URL                   phpMyAdmin login page url
      USERNAME              phpMyAdmin login username
      PASSWORD              phpMyAdmin login password

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                            output directory for the SQL dump file (default: the
                            current working directory)
      -p, --prepend-date    prepend current UTC date & time to the filename; see
                            the --prefix-format option for custom formatting
      -e EXCLUDE_DBS, --exclude-dbs EXCLUDE_DBS
                            comma-separated list of database names to exclude from
                            the dump
      -s SERVER_NAME, --server-name SERVER_NAME
                            mysql server hostname to supply if enabled as field on login page
      --compression {none,zip,gzip}
                            compression method for the output file - must be
                            supported by the server (default: none)
      --basename BASENAME   the desired basename (without extension) of the SQL
                            dump file (default: the name given by phpMyAdmin); you
                            can also set an empty basename "" in combination with
                            --prepend-date and --prefix-format
      --timeout TIMEOUT     timeout in seconds for the requests (default: 60)
      --overwrite-existing  overwrite existing SQL dump files (instead of
                            appending a number to the name)
      --prefix-format PREFIX_FORMAT
                            the prefix format for --prepend-date (default:
                            "%Y-%m-%d--%H-%M-%S-UTC_"); in Python's strftime
                            format. Must be used with --prepend-date to be in
                            effect
      --dry-run             dry run, do not actually download any file
      --http-auth           Basic http authentication, using format
                            "username:password"

    Written by Christoph Haunschmidt, version: 2016-03-12.3

### Examples

    phpmyadmin_sql_backup.py "http://www.example.com/phpmyadmin/" your_user your_password

Downloads a plain text `.sql` backup of all databases to the current working directory.

---

    phpmyadmin_sql_backup.py "http://www.example.com/phpmyadmin/" your_user your_password --exclude-dbs mydb2,mydb4 --prepend-date --basename example_dump --output-directory /tmp --compression zip

Downloads a zipped dump with databases `mydb2` & `mydb4` excluded, the base name `example_dump` and a prepended UTC date / time to the directory `/tmp`, e.g. `/tmp/2016-03-11--15-19-04-UTC_example_dump.zip`.

## Requirements

 - A [Python 3.4+](https://www.python.org/) installation on your system
 - [Grab - python web-scraping framework](http://grablib.org/): Install via `pip install -U Grab` or see the [installation instructions](http://docs.grablib.org/en/latest/usage/installation.html) if you run into problems.

## Changelog

Currently, there is no changelog; the best option at the moment is to read the commit messages.

## License

[GNU GPL3](https://www.gnu.org/licenses/gpl-3.0.html)

## Author

- Christoph Haunschmidt
