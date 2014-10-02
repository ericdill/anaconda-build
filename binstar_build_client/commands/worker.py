'''
Build worker 
'''

from __future__ import (print_function, unicode_literals, division,
    absolute_import)

import logging
import platform

from binstar_build_client import BinstarBuildAPI
from binstar_build_client.worker.worker import Worker
from binstar_client.utils import get_binstar


log = logging.getLogger('binstar.build')


def main(args):
    bs = get_binstar(args, cls=BinstarBuildAPI)

    if not args.username:
        current_user = bs.user()
        args.username = current_user['login']

    log.info('Starting worker:')
    log.info('User: %s' % args.username)
    log.info('Queue: %s' % args.queue)
    log.info('Platform: %s' % args.platform)
    woker = Worker(bs, args)
    woker.work_forever()


OS_MAP = {'darwin': 'osx', 'windows':'win'}
ARCH_MAP = {'x86': '32',
            'x86_64': '64',
			'amd64' : '64'
            }

def get_platform():
    operating_system = platform.system().lower()
    arch = platform.machine().lower()
    return '%s-%s' % (OS_MAP.get(operating_system, operating_system),
                      ARCH_MAP.get(arch, arch))
def get_dist():
    if platform.dist()[0]:
        return platform.dist()[0].lower()
    elif platform.mac_ver()[0]:
        darwin_version = platform.mac_ver()[0].rsplit('.', 1)[0]
        return 'darwin%s' % darwin_version
    elif platform.win32_ver()[0]:
        return platform.win32_ver()[0].lower()
    return 'unknown'


def add_parser(subparsers):
    parser = subparsers.add_parser('worker',
                                      help='Build Worker',
                                      description=__doc__,
                                      )

    parser.add_argument('queue',
                        help='The queue to pull builds from')
    parser.add_argument('-p', '--platform',
                        default=get_platform(),
                        help='The platform this worker is running on (default: %(default)s)')

    parser.add_argument('--hostname', default=platform.node(),
                        help='The host name the worker should use (default: %(default)s)')

    parser.add_argument('--dist', default=get_dist(),
                        help='The operating system distribution the worker should use (default: %(default)s)')

    parser.add_argument('--cwd', default='.',
                        help='The root directory this build should use (default: "%(default)s")')
    parser.add_argument('-u', '--username', '--owner',
                        help='The queue\'s owner (defaults to your currently logged in binstar user account)')
    parser.add_argument('-t', '--max-job-duration', type=int, metavar='SECONDS',
                        dest='timeout',
                        help='Force jobs to stop after they exceed duration (default: %(default)s)', default=60 * 60 * 60)
    parser.add_argument('-c', '--clean', action='store_true',
                        help='Clean up an existing workers session')
    parser.add_argument('-f', '--fail', action='store_true',
                        help='Exit main loop on any un-handled exception')
    parser.add_argument('-1', '--one', action='store_true',
                        help='Exit main loop after only one build')
    parser.add_argument('--push-back', action='store_true',
                        help='Developers only, always push the build *back* onto the build queue')

    parser.set_defaults(main=main)
