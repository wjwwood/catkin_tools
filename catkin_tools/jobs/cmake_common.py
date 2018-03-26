# Copyright 2014 Open Source Robotics Foundation, Inc.
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

import os
import re
import subprocess

from osrf_pycommon.process_utils import which

CMAKE_EXECUTABLE_ENV = 'CMAKE_COMMAND'
CTEST_EXECUTABLE_ENV = 'CTEST_COMMAND'


def which_executable(env_var, executable_names):
    env_value = os.getenv(env_var)
    if env_value:
        executable = which(env_value)
        if executable:
            return executable
    for executable_name in executable_names:
        executable = which(executable_name)
        if executable:
            return executable
    return None


CMAKE_EXECUTABLE = which_executable(CMAKE_EXECUTABLE_ENV, ['cmake3', 'cmake'])
CTEST_EXECUTABLE = which_executable(CTEST_EXECUTABLE_ENV, ['ctest3', 'ctest'])
MAKE_EXECUTABLE = which('make')
MSBUILD_EXECUTABLE = which('msbuild')
NINJA_EXECUTABLE = which('ninja')
XCODEBUILD_EXECUTABLE = which('xcodebuild')

__target_re = re.compile(r'^([a-zA-Z0-9][a-zA-Z0-9_\.]*):')


def has_make_target(path, target):
    global __target_re
    output = subprocess.check_output([MAKE_EXECUTABLE, '-pn'], cwd=path)
    lines = output.decode().splitlines()
    targets = [m.group(1) for m in [__target_re.match(l) for l in lines] if m]
    return target in targets


def cmakecache_exists_at(path):
    cmakecache = os.path.join(path, 'CMakeCache.txt')
    return os.path.isfile(cmakecache)


def makefile_exists_at(path):
    makefile = os.path.join(path, 'Makefile')
    return os.path.isfile(makefile)


def ninjabuild_exists_at(path):
    ninjabuild = os.path.join(path, 'build.ninja')
    return os.path.isfile(ninjabuild)


def solution_file_exists_at(path, package_name):
    solution_file = os.path.join(path, package_name + '.sln')
    # TODO(wjwwood): this check is made before cmake is run
    # if not os.path.isfile(solution_file):
    #     return None
    return solution_file


def project_file_exists_at(path, target):
    project_file = os.path.join(path, target + '.vcxproj')
    # TODO(wjwwood): this check is made before cmake is run
    # if not os.path.isfile(project_file):
    #     return None
    return project_file


def get_visual_studio_version():
    vsv = os.environ.get('VisualStudioVersion', None)
    return vsv

def get_configuration_from_cmake(cmake_args, build_space):
        # check for CMake build type in the command line arguments
        arg_prefix = '-DCMAKE_BUILD_TYPE='
        build_type = None
        for cmake_arg in cmake_args:
            if cmake_arg.startswith(arg_prefix):
                build_type = cmake_arg[len(arg_prefix):]
                break
        else:
            # get for CMake build type from the CMake cache
            line_prefix = 'CMAKE_BUILD_TYPE:'
            cmake_cache = os.path.join(build_space, 'CMakeCache.txt')
            if os.path.exists(cmake_cache):
                with open(cmake_cache, 'r') as h:
                    lines = h.read().splitlines()
                for line in lines:
                    if line.startswith(line_prefix):
                        try:
                            index = line.index('=')
                        except ValueError:
                            continue
                        build_type = line[index + 1:]
                        break
        if build_type in ['Debug']:
            return 'Debug'
        return 'Release'
