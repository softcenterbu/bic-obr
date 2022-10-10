from django.db import models

class AssTransfertPNB(models.Model):
    """
    Modele  Assurance  
    """
    reference = models.CharField(db_column='Reference', max_length=100, db_collation='French_CI_AS', blank=True, null=True)
    assurance = models.CharField(db_column='Assurance', max_length=1024, db_collation='French_CI_AS', blank=True, null=True)
    
    
    class Meta:
        managed = False
        db_table = 'AssTransfertPNB'

    def __str__(self):
        return self.reference