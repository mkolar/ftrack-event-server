# -*- coding: utf-8 -*-
#
# Copyright 2014 Thomas Amland <thomas.amland@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from watchdog.utils import BaseThread
from watchdog.utils.delayed_queue import DelayedQueue
from watchdog.observers.inotify_c import Inotify


class InotifyBuffer(BaseThread):
    """A wrapper for `Inotify` that holds events for `delay` seconds. During
    this time, IN_MOVED_FROM and IN_MOVED_TO events are paired.
    """

    delay = 0.5

    def __init__(self, path, recursive=False):
        BaseThread.__init__(self)
        self._queue = DelayedQueue(self.delay)
        self._inotify = Inotify(path, recursive)
        self.start()

    def read_event(self):
        """Returns a single event or a tuple of from/to events in case of a
        paired move event. If this buffer has been closed, immediately return
        None.
        """
        return self._queue.get()

    def on_thread_stop(self):
        self._inotify.close()
        self._queue.close()

    def close(self):
        self.stop()
        self.join()

    def run(self):
        """Read event from `inotify` and add them to `queue`. When reading a
        IN_MOVE_TO event, remove the previous added matching IN_MOVE_FROM event
        and add them back to the queue as a tuple.
        """
        while self.should_keep_running():
            inotify_events = self._inotify.read_events()
            for inotify_event in inotify_events:
                logging.debug("InotifyBuffer: in event %s", inotify_event)
                if inotify_event.is_moved_to:

                    def matching_from_event(event):
                        return (not isinstance(event, tuple) and event.is_moved_from
                                and event.cookie == inotify_event.cookie)

                    from_event = self._queue.remove(matching_from_event)
                    if from_event is not None:
                        self._queue.put((from_event, inotify_event))
                    else:
                        logging.debug("InotifyBuffer: could not find matching move_from event")
                        self._queue.put(inotify_event)
                else:
                    self._queue.put(inotify_event)

