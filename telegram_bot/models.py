from django.db import models


class TeleramReg(models.Model):
    '''
    '''

    username = models.CharField(max_length=50, unique=True)
    telname = models.CharField(max_length=50, unique=True)
    token = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    verified = models.BooleanField(default=False)

    def __unicode__(self):
        return self.username
