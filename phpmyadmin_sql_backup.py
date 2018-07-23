#!/usr/bin/env python3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################
#
# A Python script to automate the download of SQL dump backups
# via a phpMyAdmin web interface.
#
# tested on Python 3.4+
# requires: grab (http://grablib.org/)
#
# Christoph Haunschmidt 2016-03

import argparse
import os
import re
import sys
import datetime

import grab


__version__ = '2016-03-12.3'

CONTENT_DISPOSITION_FILENAME_RE = re.compile(r'^.*filename="(?P<filename>[^"]+)".*$')
DEFAULT_PREFIX_FORMAT = r'%Y-%m-%d--%H-%M-%S-UTC_'


def download_sql_backup(url, user, password, dry_run=False, overwrite_existing=False, prepend_date=True, basename=None,
                        output_directory=os.getcwd(), exclude_dbs=None, compression='none', prefix_format=None,
                        timeout=60, http_auth=None, **kwargs):
    prefix_format = prefix_format or DEFAULT_PREFIX_FORMAT
    exclude_dbs = exclude_dbs.split(',') or []
    encoding = '' if compression == 'gzip' else 'gzip'

    g = grab.Grab(encoding=encoding, timeout=timeout)
    if http_auth:
        g.setup(userpwd=http_auth)
    g.go(url)

    g.doc.set_input_by_id('input_username', user)
    g.doc.set_input_by_id('input_password', password)
    g.submit()

    try:
        g.doc.text_assert('server_export.php')
    except Exception as e:
        raise ValueError('Could not login - did you provide the correct username / password? ({})'.format(e))
    export_url = g.doc.select("id('topmenu')//a[contains(@href,'server_export.php')]/@href").text()
    g.go(export_url)

    dbs_available = [option.attrib['value'] for option in g.doc.form.inputs['db_select[]']]
    dbs_to_dump = [db_name for db_name in dbs_available if db_name not in exclude_dbs]
    if not dbs_to_dump:
        print('Warning: no databases to dump (databases available: "{}")'.format('", "'.join(dbs_available)),
            file=sys.stderr)

    file_response = g.submit(
        extra_post=[('db_select[]', db_name) for db_name in dbs_to_dump] + [('compression', compression)])

    re_match = CONTENT_DISPOSITION_FILENAME_RE.match(g.doc.headers['Content-Disposition'])
    if not re_match:
        raise ValueError(
            'Could not determine SQL backup filename from {}'.format(g.doc.headers['Content-Disposition']))

    content_filename = re_match.group('filename')
    filename = content_filename if basename is None else basename + os.path.splitext(content_filename)[1]
    if prepend_date:
        prefix = datetime.datetime.utcnow().strftime(prefix_format)
        filename = prefix + filename
    out_filename = os.path.join(output_directory, filename)

    if os.path.isfile(out_filename) and not overwrite_existing:
        basename, ext = os.path.splitext(out_filename)
        n = 1
        print('File {} already exists, to overwrite it use --overwrite-existing'.format(out_filename), file=sys.stderr)
        while True:
            alternate_out_filename = '{}_({}){}'.format(basename, n, ext)
            if not os.path.isfile(alternate_out_filename):
                out_filename = alternate_out_filename
                break
            n += 1

    if not dry_run:
        file_response.save(out_filename)

    return out_filename


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Automates the download of SQL dump backups via a phpMyAdmin web interface.',
        epilog='Written by Christoph Haunschmidt, version: {}'.format(__version__))

    parser.add_argument('url', metavar='URL', help='phpMyAdmin login page url')
    parser.add_argument('user', metavar='USERNAME', help='phpMyAdmin login username')
    parser.add_argument('password', metavar='PASSWORD', help='phpMyAdmin login password')
    parser.add_argument('-o', '--output-directory', default=os.getcwd(),
        help='output directory for the SQL dump file (default: the current working directory)')
    parser.add_argument('-p', '--prepend-date', action='store_true', default=False,
        help='prepend current UTC date & time to the filename; see the --prefix-format option for custom formatting')
    parser.add_argument('-e', '--exclude-dbs', default='',
        help='comma-separated list of database names to exclude from the dump')
    parser.add_argument('--compression', default='none', choices=['none', 'zip', 'gzip', 'bzip2'],
        help='compression method for the output file - must be supported by the server (default: %(default)s)')
    parser.add_argument('--basename', default=None,
        help='the desired basename (without extension) of the SQL dump file (default: the name given by phpMyAdmin); '
        'you can also set an empty basename "" in combination with --prepend-date and --prefix-format')
    parser.add_argument('--timeout', type=int, default=60,
        help='timeout in seconds for the requests (default: %(default)s)')
    parser.add_argument('--overwrite-existing', action='store_true', default=False,
        help='overwrite existing SQL dump files (instead of appending a number to the name)')
    parser.add_argument('--prefix-format', default='',
        help=str('the prefix format for --prepend-date (default: "{}"); in Python\'s strftime format. '
                 'Must be used with --prepend-date to be in effect'.format(DEFAULT_PREFIX_FORMAT.replace('%', '%%'))))
    parser.add_argument('--dry-run', action='store_true', default=False,
        help='dry run, do not actually download any file')
    parser.add_argument('--http-auth', default=None,
        help='Basic http authentication, using format "username:password"')

    args = parser.parse_args()

    if args.prefix_format and not args.prepend_date:
        print('Error: --prefix-format given without --prepend-date', file=sys.stderr)
        sys.exit(2)

    try:
        dump_fn = download_sql_backup(**vars(args))
    except Exception as e:
        print('Error: {}'.format(e), file=sys.stderr)
        sys.exit(1)

    print('{} saved SQL dump to: {}'.format(('Would have' if args.dry_run else 'Successfully'), dump_fn),
        file=sys.stdout)
