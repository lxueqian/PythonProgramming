#!/usr/bin/python -3.6
# ‐*‐ coding: utf‐8 ‐*‐

import json
import os
import numpy as np
import subprocess
import shlex
import time
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


class ideas1_multiple_processing():
    """ This class is designed to run multiple jobs with given cpu number.
        The cpu usage of each job could be different. Input example:

        example for run_all_for_executable
        cpu_provided = 4
        input_job_list = ["eclrun visage --np=1 D:/Project.Personal/python/_Simulation3/gullfaks_1_CASE_3D_STATIC/CASE_3D_STATICPRE.MII",
                          "eclrun visage --np=3 D:/Project.Personal/python/_Simulation3/gullfaks_2_CASE_3D_STATIC/CASE_3D_STATICPRE.MII",
                          "eclrun visage --np=2 D:/Project.Personal/python/_Simulation3/gullfaks_3_CASE_3D_STATIC/CASE_3D_STATICPRE.MII",
                          "eclrun visage --np=1 D:/Project.Personal/python/_Simulation3/gullfaks_4_CASE_3D_STATIC/CASE_3D_STATICPRE.MII"]
        input_cpu_usage_list = [1,
                                3,
                                2,
                                1]
    """
    def __init__(self, cpu_provided, input_job_list, input_cpu_usage_list=None, env=None):
        super().__init__()
        self.cpu_used = 0
        self.cpu_provided = cpu_provided
        self.input_job_list = input_job_list
        self.env = env
        self.job_list = []
        self.input_cpu_usage_list = input_cpu_usage_list
        self.cpu_usage_list = []
        self.working_job_list = []
        self.working_job_end_time_list = []
        self.working_job_cpu_usage_list = []

        self.finished_job_list = []

        self.init_command_line_list()
        self.init_cpu_usage_list()

    def init_command_line_list(self):
        if np.less(len(self.input_job_list), 1):
            print("<?> The job_list is empty!")
            return
        else:
            print("    Preparing the jobs to be run ...")
            for job_i in self.input_job_list:
                # print("    |  " + job_i)
                self.job_list.append(shlex.split(job_i))

    def init_cpu_usage_list(self):
        if np.less(len(self.input_job_list), 1):
            return
        else:
            if self.input_cpu_usage_list is None:
                self.cpu_usage_list = [1 for _ in range(len(self.job_list))]
            elif np.less_equal(len(self.input_cpu_usage_list), len(self.job_list)):
                self.cpu_usage_list = [1 for _ in range(len(self.job_list))]
                for i in range(len(self.input_cpu_usage_list)):
                    self.cpu_usage_list[i] = self.input_cpu_usage_list[i]
            else:
                for i in range(len(self.job_list)):
                    self.cpu_usage_list.append(self.input_cpu_usage_list[i])

            print("    The number of available cpus is: {}".format(self.cpu_provided))
            print("    Preparing the job cpu usage list ...")
            # for cpu_usage_i in self.cpu_usage_list:
            #     print("    |  " + str(cpu_usage_i))

            self.cpu_usage_max = np.max(self.cpu_usage_list)
            if np.less(self.cpu_provided, self.cpu_usage_max):
                print("<?> The number of available cpus is less than the max usage of one job!")

    def log_process_output(self,
                           process,
                           log_file):
        outs, errs = process.communicate()
        if log_file is not None:
            log_file.write("\n==> Subprocess: \n" + str(process.args))
            log_file.write("\n--> Outputs: \n" + outs.decode("utf-8"))
            if process.poll() != -9:
                log_file.write("\n--> Errors: {}\n".format(len(errs)) + errs.decode("utf-8") + "\n")
            else:
                log_file.write("\n--> Errors: Timeout\n\n")
        else:
            print("\n==> Subprocess: \n" + str(process.args))
            print("\n--> Outputs: \n" + outs.decode("utf-8"))
            if process.poll() != -9:
                print("\n--> Errors: {}\n".format(len(errs)) + errs.decode("utf-8") + "\n")
            else:
                print("\n--> Errors: Timeout\n\n")

    def run_all_for_executable(self,
                               log_file_path=None,
                               timeout=None):
        print(time.time())
        print("    Running the given {0} jobs on given {1} cpus ...".format(len(self.job_list), self.cpu_provided))
        if log_file_path is not None:
            my_log_file = open(log_file_path, 'w')
        else:
            my_log_file = None

        self.cpu_used = 0
        for i in range(len(self.job_list)):
            self.cpu_used += self.cpu_usage_list[i]
            while np.greater(self.cpu_used, self.cpu_provided):
                for j in range(len(self.working_job_list)):
                    if self.working_job_end_time_list[j] < time.time():
                        self.working_job_list[j].kill()
                    if self.working_job_list[j].poll() is not None:
                        self.log_process_output(self.working_job_list.pop(j), my_log_file)
                        self.cpu_used -= self.working_job_cpu_usage_list.pop(j)
                        self.working_job_end_time_list.pop(j)
                        break
            print("    |  ({0}/{1}) Run job: {2}".format(i+1, len(self.job_list), self.input_job_list[i]))
            # print("    |  The number of used cpus: {}".format(self.cpu_used))
            # print("    |  The number of available cpus: {}".format(self.cpu_provided-self.cpu_used))
            self.working_job_list.append(subprocess.Popen(self.job_list[i],
                                                          stdout=subprocess.PIPE,
                                                          stderr=subprocess.PIPE,
                                                          env=self.env))
            self.working_job_cpu_usage_list.append(self.cpu_usage_list[i])
            self.working_job_end_time_list.append(time.time() + timeout)
        for job_i in self.working_job_list:
            try:
                job_i.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                job_i.kill()
        while np.greater(self.cpu_used, 0):
            for j in range(len(self.working_job_list)):
                if self.working_job_list[j].poll() is not None:
                    self.log_process_output(self.working_job_list.pop(j), my_log_file)
                    self.cpu_used -= self.working_job_cpu_usage_list.pop(j)
                    break

        if my_log_file is not None:
            my_log_file.close()

        print("    All {0} jobs have been run on given {1} cpus...".format(len(self.job_list), self.cpu_provided))
        print(time.time())
