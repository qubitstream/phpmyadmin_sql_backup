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
# tested on Python 3.5
#
# Christoph Haunschmidt 2016-03

import argparse
import os
import re
import datetime

import grab

__version__ = '2016-03-10.0'

CONTENT_DISPOSITION_FILENAME_RE = re.compile(r'^.*filename="(?P<filename>[^"]+).*$')


def download_sql_backup(url, user, password, dry_run=False, overwrite_existing=False, prepend_date=True, basename='',
                        output_directory=os.getcwd(), exclude_dbs=None, compression='none', timeout=60, **kwargs):
    exclude_dbs = exclude_dbs.split(',') or []
    encoding = '' if compression == 'gzip' else 'gzip'

    g = grab.Grab(encoding=encoding, timeout=timeout)
    g.go(url)

    g.doc.set_input_by_id('input_username', user)
    g.doc.set_input_by_id('input_password', password)
    g.doc.submit()

    g.doc.text_assert('server_export.php')
    export_url = g.doc.select("id('topmenu')//a[contains(@href,'server_export.php')]/@href").text()
    g.go(export_url)

    dbs_available = [option.attrib['value'] for option in g.doc.form.inputs['db_select[]']]

    file_response = g.doc.submit(
        extra_post=[('db_select[]', db_name) for db_name in dbs_available if db_name not in exclude_dbs] + [
            ('compression', compression)])

    m = CONTENT_DISPOSITION_FILENAME_RE.match(g.response.headers['Content-Disposition'])
    if not m:
        raise ValueError(
            'Could not determine SQL backup filename from {}'.format(g.response.headers['Content-Disposition']))

    content_filename = m.group('filename')
    filename = content_filename if not basename else basename + os.path.splitext(content_filename)[1]
    if prepend_date:
        prefix = datetime.datetime.utcnow().strftime(r'%Y-%m-%d--%H-%M-%S-UTC_')
        filename = prefix + filename
    out_filename = os.path.join(output_directory, filename)

    if os.path.isfile(out_filename) and not overwrite_existing:
        basename, ext = os.path.splitext(out_filename)
        n = 1
        print('File {} already exists, to overwrite it use: --overwrite-existing'.format(out_filename))
        while True:
            alternate_out_filename = basename + '_({})'.format(n) + ext
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
        epilog='Written by Christoph Haunschmidt. Version: {}'.format(__version__))

    parser.add_argument('url', help='phpMyAdmin login page url')
    parser.add_argument('user', help='phpMyAdmin login user')
    parser.add_argument('password', help='phpMyAdmin login password')
    parser.add_argument('-o', '--output-directory', default=os.getcwd(), help='output directory for the SQL dump file')
    parser.add_argument('-p', '--prepend-date', action='store_true', default=False,
        help='prepend the current UTC date + time to the filename: "YYYY-MM-DD--HH-MM-SS-UTC_"')
    parser.add_argument('-e', '--exclude-dbs', default='',
        help='comma separated list for database names to exclude from the dump')
    parser.add_argument('--compression', default='none', choices=['none', 'zip', 'gzip'],
        help='compression method of the output file (default: %(default)s)')
    parser.add_argument('--basename',
        help='the desired basename (without extension) of the SQL dump file (default: the name given by phpMyAdmin')
    parser.add_argument('--timeout', type=int, default=60,
        help='timeout in seconds for the requests (default: %(default)s)')
    parser.add_argument('--overwrite-existing', action='store_true', default=False,
        help='overwrite existing backup files (instead of appending a number to the name)')
    parser.add_argument('--dry-run', action='store_true', default=False,
        help='dry run, do not actually download the dump')

    ARGS = parser.parse_args()

    dump_fn = download_sql_backup(**vars(ARGS))

    print('{} saved SQL dump to: {}'.format(('Would have' if ARGS.dry_run else 'Successfully'), dump_fn))
