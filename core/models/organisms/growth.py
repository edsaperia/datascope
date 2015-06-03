from __future__ import unicode_literals, absolute_import, print_function, division
import six

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, ContentType

from celery.result import AsyncResult

from datascope.configuration import PROCESS_CHOICE_LIST
from core.models.organisms.community import Community
import core.processors
from core.utils.configuration import ConfigurationField


class GrowthState(object):
    NEW = "New"
    PROCESSING = "Processing"
    FINISHED = "Finished"
    ERROR = "Error"
    RETRY = "Retry"

GROWTH_STATE_CHOICES = [
    (attr, value) for attr, value in six.iteritems(GrowthState.__dict__) if not attr.startswith("_")
]


class Growth(models.Model):

    #community = models.ForeignKey(Community)

    type = models.CharField(max_length=255)
    config = ConfigurationField()

    process = models.CharField(max_length=255, choices=PROCESS_CHOICE_LIST)
    success = models.CharField(max_length=255, choices=PROCESS_CHOICE_LIST)

    input = GenericForeignKey(ct_field="input_type", fk_field="input_id")
    input_type = models.ForeignKey(ContentType, related_name="+")
    input_id = models.PositiveIntegerField()
    output = GenericForeignKey(ct_field="output_type", fk_field="output_id")
    output_type = models.ForeignKey(ContentType, related_name="+")
    output_id = models.PositiveIntegerField()

    task_id = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, choices=GROWTH_STATE_CHOICES, default=GrowthState.NEW, db_index=True)
    is_finished = models.BooleanField(default=False, db_index=True)

    @property
    def task(self):
        if not self.task_id:
            raise ValueError("Growth does not have a task set")
        else:
            return AsyncResult(self.task_id)
    @task.setter
    def task(self, task):
        self.task_id = task.id
        self.status = self.state = GrowthState.PROCESSING

    def begin(self, *args, **kwargs):
        """
        Starts the Celery task that provides growth of the data pool and is stored under self.process.

        :param args: (optional) The positional arguments to pass through to the process of Growth
        :param kwargs: (optional) The keyword arguments to pass through the process of Growth
        :return: the input Organism
        """
        assert self.state in [GrowthState.NEW, GrowthState.RETRY], \
            "Can't begin a growth that is in state {}".format(self.state)

        processor, method = self.prepare_process(self.process)
        task = getattr(processor, method)
        self.task = task.delay(*args, **kwargs)
        self.save()

    def finish(self):
        """

        :return: the output Organism and unprocessed errors
        - Revives the process and calls get_results
        - Runs the success process for every success
        - Fills output with results from success process
        - Returns the output as well as the (unprocessed) errors
        """
        pass

    def prepare_process(self, process):
        """
        Creates an instance of the processor based on requested process with a correct config set.
        Processors get loaded from core.processors
        It returns the processor and the method that should be invoked.

        :param process: A dotted string indicating the processor and method that represent the process.
        :return: processor, method
        """
        processor_name, method_name = process.split(".")
        try:
            processor_class = getattr(core.processors, processor_name)
        except AttributeError:
            raise AssertionError(
                "Could not import a processor named {} from core.processors".format(processor_name)
            )
        processor = processor_class(config=self.config.to_dict(protected=True))
        return processor, method_name

    def save(self, *args, **kwargs):
        self.is_finished = self.state == GrowthState.FINISHED
        super(Growth, self).save(*args, **kwargs)