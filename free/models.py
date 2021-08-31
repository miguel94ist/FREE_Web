from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Experiment(models.Model):
    name = models.CharField(_('Name'), max_length=64)
    description = models.TextField(_('Description'))
    config = models.JSONField(_('Configuration'), default=dict, blank=True)
    scientific_area = models.CharField(_('Scientific area'), max_length=64)
    lab_type = models.CharField(_('Lab type'), max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Experiment')
        verbose_name_plural = _('Experiments')
        ordering = ['name']

class Apparatus(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.PROTECT) # or CASCADE?
    localization = models.CharField(_('Localization'), max_length=32)
    secret = models.CharField(_('Secret'), max_length=32)
    owner = models.CharField(_('Owner'), max_length=32)

    def __str__(self):
        return self.experiment.name + ' in ' + self.localization

    class Meta:
        verbose_name = _('Experimental apparatus')
        verbose_name_plural = _('Experimental apparatuses')
        ordering = ['localization']

STATUS_CHOICES = (
    ('1', _('Online')),
    ('0', _('Offline')),
    ('R', _('Running')),
)

class Status(models.Model):
    apparatus = models.OneToOneField(Apparatus, on_delete=models.CASCADE)
    time = models.DateTimeField(_('Time'), auto_now=True)
    status = models.CharField(_('Status'), max_length=1, choices=STATUS_CHOICES)

    def __str__(self):
        return str(self.apparatus) + ' ' + self.get_status_display() + ' at ' + str(self.time)

    class Meta:
        verbose_name = _('Status')
        verbose_name_plural = _('Statuses')

class Protocol(models.Model):
    apparatus = models.ForeignKey(Apparatus, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    config = models.JSONField(_('Configuration'), default=dict, blank=True)

    def __str__(self):
        return self.name + ' at ' + str(self.apparatus)

    class Meta:
        verbose_name = _('Experimental protocol')
        verbose_name_plural = _('Experimental protocols')
        ordering = ['name']

class Execution(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    protocol = models.ForeignKey(Protocol, on_delete=models.DO_NOTHING) # Really do nothing?
    config = models.JSONField(_('Configuration'), default=dict, blank=True)
    status = models.CharField(_('Status'), max_length=32)

    def __str__(self):
        return str(self.protocol) + ' with ' + str(self.config)

    class Meta:
        verbose_name = _('Protocol execution')
        verbose_name_plural = _('Protocol executions')

class Result(models.Model):
    execution = models.OneToOneField(Execution, on_delete=models.CASCADE)
    time = models.DateTimeField(_('Time'), auto_now=True)
    result_type = models.CharField(_('Result type'), max_length=64)
    value = models.JSONField(_('Value'), default=dict, blank=True)

    def __str__(self):
        return str(self.execution) + ' at ' + str(self.time)

    class Meta:
        verbose_name = _('Experiment result')
        verbose_name_plural = _('Experiment results')