import threading
import queue
import hashlib
import logging


class ThreadPool(object):

    def __init__(self, thread_num, data):

        self.data = data
        self.work_queue = queue.Queue()
        self.threads = []
        self.running = 0
        self.failure = 0
        self.success = 0
        self.tasks = {}
        self.thread_name = threading.current_thread().getName()
        self.__init_thread_pool(thread_num)

    def __init_thread_pool(self, thread_num):
        for i in range(thread_num):
            work_thread=WorkThread(self)
            self.threads.append(WorkThread(work_thread))
            work_thread.start()


    def add_task(self, task):
       
        self.work_queue.put(task)
        logging.info("{0} add task {1}".format(self.thread_name))

    def get_task(self):

        task = self.work_queue.get(block=False)

        return task

    def task_done(self):
        self.work_queue.task_done()

    def start_task(self):
        for item in self.threads:
            item.start()

        logging.debug("Work start")

    def increase_success(self):
        self.success += 1

    def increase_failure(self):
        self.failure += 1

    def increase_running(self):
        self.running += 1

    def decrease_running(self):
        self.running -= 1

    def get_running(self):
        return self.running

    def get_progress_info(self):
        progress_info = {}
        progress_info['work_queue_number'] = self.work_queue.qsize()
        progress_info['tasks_number'] = len(self.tasks)
        progress_info['save_queue_number'] = self.save_queue.qsize()
        progress_info['success'] = self.success
        progress_info['failure'] = self.failure

        return progress_info

    def add_save_task(self, url, html):
        self.save_queue.put((url, html))

    def get_save_task(self):
        save_task = self.save_queue.get(block=False)

        return save_task

    def wait_all_complete(self):
        for item in self.threads:
            if item.isAlive():
                item.join()

class Task:
    def __init__(self):
        id=''
    def run(self):
        return True

class WorkThread(threading.Thread):

    def __init__(self, thread_pool):
        threading.Thread.__init__(self)
        self.thread_pool = thread_pool

    def run(self):
        print (threading.current_thread().getName())
        while True:
            try:
            
                task= self.thread_pool.get_task()
                self.thread_pool.increase_running()
                ret=task.run()

                if not ret:
                    self.thread_pool.increase_failure()
                    self.thread_pool.add_task(task)
                else:
                    self.thread_pool.increase_success()

                self.thread_pool.decrease_running()
                self.thread_pool.task_done()
            except Queue.Empty:
                if self.thread_pool.get_running() <= 0:
                    break
            except Exception as e:
                self.thread_pool.decrease_running()
                # print str(e)
                break