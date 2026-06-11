from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from inventory.models import Medicine

class AlternateMedicine(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='alternate_of')
    alternate_medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='is_alternate_of')
    salt_match_percentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)], default=100)
    notes = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-salt_match_percentage', 'created_at']
        indexes = [models.Index(fields=['medicine', 'is_active']), models.Index(fields=['salt_match_percentage'])]
        constraints = [models.UniqueConstraint(fields=['medicine', 'alternate_medicine'], name='unique_alternate_pair')]
    
    def __str__(self):
        return f'{self.medicine.medicine_name} → {self.alternate_medicine.medicine_name} ({self.salt_match_percentage}%)'
    
    @classmethod
    def get_alternates_for_medicine(cls, medicine_id, min_match_percentage=70):
        return cls.objects.filter(medicine_id=medicine_id, is_active=True, salt_match_percentage__gte=min_match_percentage).select_related('alternate_medicine', 'alternate_medicine__company')
    
    @classmethod
    def calculate_salt_match(cls, salt1, salt2):
        if not salt1 or not salt2:
            return 0
        salts1 = set(s.strip().split()[0].lower() for s in salt1.split('+'))
        salts2 = set(s.strip().split()[0].lower() for s in salt2.split('+'))
        common = salts1 & salts2
        total = salts1 | salts2
        return int((len(common) / len(total)) * 100) if total else 0
