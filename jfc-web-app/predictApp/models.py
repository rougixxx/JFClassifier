from django.db import models

# Create your models here.

class PredictionHistory(models.Model):
    java_code = models.TextField()
    prediction = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        db_table = "prediction_history"                                #
        verbose_name_plural = "Prediction History" 
    def __str__(self):
        return f"Prediction: {self.prediction} at {self.timestamp}"