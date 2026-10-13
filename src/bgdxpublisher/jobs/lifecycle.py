"""Controlled publisher job status transitions."""

from dataclasses import replace

from .exceptions import InvalidJobTransitionError
from .models import JobStatus, PublisherJob


class JobLifecycle:
    """Apply only the documented transitions to immutable jobs."""

    _TRANSITIONS = {
        JobStatus.CREATED: {JobStatus.VALIDATED, JobStatus.FAILED},
        JobStatus.VALIDATED: {JobStatus.QUEUED, JobStatus.FAILED},
        JobStatus.QUEUED: {JobStatus.RUNNING, JobStatus.FAILED},
        JobStatus.RUNNING: {JobStatus.COMPLETED, JobStatus.FAILED},
        JobStatus.COMPLETED: set(),
        JobStatus.FAILED: set(),
    }

    def transition(self, job: PublisherJob, status: JobStatus) -> PublisherJob:
        """Return a new job in the requested permitted state.

        Args:
            job: Current immutable publisher job.
            status: Requested next state.

        Raises:
            InvalidJobTransitionError: If the requested transition is forbidden.
        """
        if not isinstance(status, JobStatus):
            raise InvalidJobTransitionError(
                f"Unsupported target job status: {status!r}."
            )
        if status not in self._TRANSITIONS[job.status]:
            raise InvalidJobTransitionError(
                f"Cannot transition from {job.status.name} to {status.name}."
            )
        return replace(job, status=status)
