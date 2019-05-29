# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from http.client import RemoteDisconnected
from json import JSONDecodeError

from requests.exceptions import Timeout as RequestsTimeout, HTTPError, TooManyRedirects, ConnectionError as RequestsConnectionError

from blockchainetl.executors.bounded_executor import BoundedExecutor
from blockchainetl.executors.fail_safe_executor import FailSafeExecutor
from blockchainetl.progress_logger import ProgressLogger
from blockchainetl.utils import dynamic_batch_iterator

RETRY_EXCEPTIONS = (RemoteDisconnected, ConnectionResetError, RequestsConnectionError, ConnectionError, HTTPError, RequestsTimeout, TooManyRedirects, OSError, JSONDecodeError)


# Executes the given work in batches, reducing the batch size exponentially in case of errors.
class BatchWorkExecutor:
    def __init__(self, starting_batch_size, max_workers, retry_exceptions=RETRY_EXCEPTIONS, exponential_backoff=True):
        self.batch_size = starting_batch_size
        self.max_workers = max_workers
        # Using bounded executor prevents unlimited queue growth
        # and allows monitoring in-progress futures and failing fast in case of errors.
        self.executor = FailSafeExecutor(BoundedExecutor(1, self.max_workers))
        self.retry_exceptions = retry_exceptions
        self.exponential_backoff = exponential_backoff
        self.progress_logger = ProgressLogger()
        self.counter = 0

    def execute(self, work_iterable, work_handler, total_items=None):
        self.progress_logger.start(total_items=total_items)
        for batch in dynamic_batch_iterator(work_iterable, lambda: self.batch_size):
            self.executor.submit(self._fail_safe_execute, work_handler, batch)
    # Check race conditions
    def _fail_safe_execute(self, work_handler, batch):
        try:
            self.counter+=1
            # print(f"Trying batch {batch}, workers: {self.counter}")
            print(".", end="", flush=True)
            work_handler(batch)
            self.counter-=1
        except self.retry_exceptions as e:
            self.counter-=1
            print(f"\nGot Exception: {e}")

            batch_size = self.batch_size
            # Reduce the batch size. Subsequent batches will be 2 times smaller
            if batch_size == len(batch) and batch_size > 1:
                if self.exponential_backoff:
                    self.batch_size = int(batch_size / 2)
                else:
                    self.batch_size = batch_size - 1
            # For the failed batch try handling items one by one
            for item in batch:
                work_handler([item])
        self.progress_logger.track(len(batch))

    def shutdown(self):
        self.executor.shutdown()
        self.progress_logger.finish()
