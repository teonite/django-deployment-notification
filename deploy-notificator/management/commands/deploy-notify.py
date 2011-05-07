#
#   django deployment notification
#   ------------------------------
#
#   A simple utility that will send a notification email to all superusers
#   (from current database) that new version of application was deployed.
#   All my deployment systems are automated (usually I use Makefiles) so
#   typically I use this app by adding the following line after the
#   application has been deployed:
#
#   manage.py django-notify -V XYZ -n app.teonite.com -S "Deploy notification"
#
#   Author: Robert Olejnik <robert@teonite.com>
#
#   Copyright 2011 by TEONITE. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.utils import DatabaseError
from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.validators import email_re
from optparse import make_option
import logging, traceback, os, sys

# setup logger {{{
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s: %(message)s')
console.setFormatter(formatter)
log = logging.getLogger()
log.addHandler(console)
# }}}

settings.TEMPLATE_DIRS += ('',
    os.path.join(os.path.basename(__file__), '../../templates')
)

def valid_email(email):
    return True if email_re.match(email) else False

# right now we only support one template
template = "deployment-notification.en.tpl"

class Command(BaseCommand):
    help = 'Notify all superusers that new version of the application has been deployed'
    option_list = BaseCommand.option_list + (
        make_option('--app-version', '-V', dest='version',
            help='REQUIRED: Set application version that is right now deployed.'),
        make_option('--app-name', '-n', dest='name',
            help='REQUIRED: Set the application that is right now deployed name'),
        make_option('--subject', '-s', dest='subject',
            help='REQUIRED: Email subject'),
        make_option('--from', '-f', dest='from',
            help='Email sender name and email address'),
    )

    def handle(self, *args, **options):
        "Handle management command"
        version = options.get('version')
        name = options.get('name')
        subject = options.get('subject')
        sender = options.get('from')

        if not version and not name and not subject:
            log.error("ERROR: running with no command-line options specified.")
            log.error("Please consult the documentation or use --help for more information.")
            return

        if not sender:
            sender = "TEONITE Deployment Notificator <no-reply@teonite.net>"

        try:
            people = User.objects.filter(is_superuser=True).order_by('last_name')
        except User.DoesNotExist:
            log.error("Odd! There are no admins in the database...")
            return None

        for person in people:

            first_name = person.first_name
            last_name = person.last_name
            email = person.email
            
            if not valid_email(email):
                log.error("%s %s, has an invalid email address: '%s'" %
                        (first_name, last_name, email))
                continue

            context = Context({
                'app_name': name,
                'app_version': version,
                'first_name': first_name,
                'last_name': last_name,
                'email': email
            })

            plaintext = get_template(template)
            html = get_template(template)

            text_content = plaintext.render(context)
    	    html_content = html.render(context)
            msg = EmailMultiAlternatives(subject, text_content, sender, [email])
            msg.attach_alternative(html_content, "text/html")

            try:
                log.info("sending deployment notification email to: '%s'" % email)
                msg.send()
            except:
                exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
                log.error("exception caught during email sending '%s'",
    	            repr(traceback.format_exception(exceptionType,
                        exceptionValue, exceptionTraceback)))

# vim: set sw=4 ts=4 sts=0 et:
