from django.db import models
from django.contrib.auth.models import User

class TeleramReg(models.Model):
    '''
    '''

    user = models.ForeignKey(User)
    tel_name = models.CharField(max_length=50, unique=True, blank=True)
    token = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    verified = models.BooleanField(default=False, db_index=True)

    def __unicode__(self):
        return self.user.username
