from django.core import mail
from django.test import TestCase, Client

from bumerang.apps.accounts.models import Profile
from bumerang.apps.festivals.models import Festival


class FestivalsTest(TestCase):

    def test_register_festival(self):
        response = self.client.post('/accounts/register/', {
            'username': 'alexilorenz@gmail.com',
            'password1': 'test',
            'password2': 'test',
            'type': 4,
        })

        self.assertEqual(response.status_code, 200)



        self.assertEqual(len(mail.outbox), 1)

        fest_acounts = Profile.objects.all()
        self.assertEqual(fest_acounts.count(), 1)

        fest_acount = fest_acounts[0]
        self.assertEqual(fest_acount.is_active, False)

        self.assertTemplateUsed(response,
            template_name='accounts/regisration_event_info_form.html')

        self.assertIsNotNone(response.context['form'])
        form = response.context['form']
        self.assertEqual(form.data['username'], 'alexilorenz@gmail.com')

    def test_create_fest(self):
        self.test_register_festival()

        fests = Festival.objects.all()
        self.assertEqual(fests.count(), 1)

        fest = fests[0]
        fest_acount = Profile.objects.all()[0]
        self.assertEqual(fest.owner_account, fest_acount)


#    def test_login(self):
#        self.test_register_festival()
#
#        client = Client()
#
#        response = client.post('/accounts/login/', {
#            'username': 'alexilorenz@gmail.com',
#            'password': 'test',
#            'remember': False,
#        })
#
#        self.assertEqual(response.status_code, 200)

