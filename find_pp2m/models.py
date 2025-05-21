from django.db import models


class City(models.Model):
    name = models.CharField(max_length=200, verbose_name='nom')
    slug = models.CharField(max_length=200, default='')
    num_department = models.CharField(max_length=3, verbose_name='département')
    postal_code = models.CharField(max_length=5, verbose_name='code postal')
    is_pref = models.BooleanField(default=False, verbose_name='préfecture')
    is_sous_pref = models.BooleanField(default=False, verbose_name='sous-préfecture')
    pref_name = models.CharField(max_length=200, default=name)
    code_insee = models.CharField(max_length=200, default='')
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    polygon = models.TextField(null=True)

    class Meta:
        verbose_name = 'ville'
        ordering = ['-is_pref', '-is_sous_pref', 'name']

    def __str__(self):
        return_str = '{} ({})'.format(self.name, self.num_department)
        return return_str


class Department(models.Model):
    name = models.CharField(max_length=200)
    num_department = models.CharField(max_length=3)
    polygon = models.TextField(null=True)

    class Meta:
        verbose_name = 'département'
        ordering = ['num_department']

    def __str__(self):
        return_str = '{} ({})'.format(self.name, self.num_department)
        return return_str


class Journey(models.Model):
    departure = models.CharField(max_length=200)
    arrival = models.CharField(max_length=200)
    car_distance = models.IntegerField(default=0.0)
    car_duration = models.IntegerField(default=0.0)
    train_distance = models.IntegerField(default=0.0)
    train_duration = models.IntegerField(default=0.0)

    class Meta:
        verbose_name = 'trajet'

    def __str__(self):
        return_str = '{}/{}: {} m - {} sec'.format(self.departure, self.arrival, self.car_distance, self.car_duration)
        return return_str
