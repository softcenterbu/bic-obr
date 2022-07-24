from django.db import models

class AssFactureObr(models.Model):
    """
    Modele Facture OBR
    """
    reference = models.CharField(max_length=50)
    facture = models.TextField(max_length=1024)
    details = models.TextField(max_length=1024)
    
    class Meta:
        #manage = False
        db_table='ass_facture_obr'
        ordering = ['reference',]

    def __str__(self):
        return self.reference